"""Forecast classes"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Generator, Iterable
from pynws.const import Detail
from pynws.units import Unit, convert_unit


ISO8601_PERIOD_REGEX = re.compile(
    r"^P"
    r"((?P<weeks>\d+)W)?"
    r"((?P<days>\d+)D)?"
    r"((?:T)"
    r"((?P<hours>\d+)H)?"
    r"((?P<minutes>\d+)M)?"
    r"((?P<seconds>\d+)S)?"
    r")?$"
)

ONE_HOUR = timedelta(hours=1)


class Value:
    """Class to store a value within a forecast."""

    def __init__(self, value: Any, unit: Unit | str | None):
        self._value = value
        self._unit = unit if isinstance(unit, Unit) else Unit(unit or "")

    @property
    def value(self) -> Any:
        """The item value"""
        return self._value

    @property
    def unit(self) -> Unit:
        """The item unit of measurement"""
        return self._unit

    def __eq__(self, other):
        return self.value == other.value and self.unit == other.unit

    def __str__(self):
        return f"{self.value} {self.unit}"

    def __repr__(self):
        return f"Value({self.value}, {self.unit})"

    def value_as_unit(self, to_unit: Unit) -> float:
        """Convert the item value to specified unit of measurement"""
        return convert_unit(self._value, self._unit, to_unit)


class DetailedForecast:
    """Class to retrieve forecast values for a point in time."""

    def __init__(self, properties: dict[str, Any]):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self.update_time = datetime.fromisoformat(properties["updateTime"])
        self.details = details = {}

        for prop_name, prop_value in properties.items():
            if not isinstance(prop_value, dict) or "values" not in prop_value:
                continue

            time_values = []

            for value in prop_value["values"]:
                isodatetime, duration_str = value["validTime"].split("/")
                start_time = datetime.fromisoformat(isodatetime)
                end_time = start_time + self._parse_duration(duration_str)
                time_values.append((start_time, end_time, value["value"]))

            units = prop_value.get("uom")
            units = units.split(":")[-1] if units else None
            details[prop_name] = time_values, units

    @staticmethod
    def _parse_duration(duration_str: str) -> timedelta:
        match = ISO8601_PERIOD_REGEX.match(duration_str)
        groups = match.groupdict()

        for key, val in groups.items():
            groups[key] = int(val or "0")

        return timedelta(
            weeks=groups["weeks"],
            days=groups["days"],
            hours=groups["hours"],
            minutes=groups["minutes"],
            seconds=groups["seconds"],
        )

    @property
    def last_update(self) -> datetime:
        """When the forecast was last updated"""
        return self.update_time

    @staticmethod
    def _find_detail_for_time(
        when, time_values: tuple[datetime, datetime, Any], units: str | None
    ) -> Value | None:
        for start_time, end_time, value in time_values:
            if start_time <= when < end_time:
                return Value(value, units)
        return None

    def get_details_for_time(self, when: datetime) -> dict[Detail, Value | None]:
        """Retrieve all forecast details for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        details = {}
        for detail, (time_values, units) in self.details.items():
            details[Detail(detail)] = self._find_detail_for_time(when, time_values, units)
        return details

    def get_details_for_times(
        self, iterable_when: Iterable[datetime]
    ) -> Generator[dict[Detail, Value | None]]:
        """Retrieve all forecast details for a list of times."""

        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not an Iterable")

        for when in iterable_when:
            yield self.get_details_for_time(when)

    def get_detail_for_time(self, detail: Detail, when: datetime) -> Value | None:
        """Retrieve single forecast detail for a point in time."""

        if not isinstance(detail, Detail):
            raise TypeError(f"{detail!r} is not a Detail")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        time_values, units = self.details.get(detail)
        if time_values and units:
            return self._find_detail_for_time(when, time_values, units)
        return None

    def get_details_by_hour(
        self, start_time: datetime, hours: int = 12
    ) -> Generator[dict[Detail, Value | str | None]]:
        """Retrieve a sequence of hourly forecast details"""

        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for hour in range(hours):
            yield self.get_details_for_time(start_time + timedelta(hours=hour))
