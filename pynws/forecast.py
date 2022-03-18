"""Forecast classes"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Generator, Iterable
from pynws.const import Detail
from pynws.units import get_converter


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

            unit_code = prop_value.get("uom")
            converter = get_converter(unit_code) if unit_code else None

            time_values = []

            for value in prop_value["values"]:
                isodatetime, duration_str = value["validTime"].split("/")
                start_time = datetime.fromisoformat(isodatetime)
                end_time = start_time + self._parse_duration(duration_str)
                value = value["value"]
                if converter and value:
                    value = converter(value)
                time_values.append((start_time, end_time, value))

            details[prop_name] = time_values

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
    def _get_value_for_time(when, time_values: tuple[datetime, datetime, Any]) -> Any:
        for start_time, end_time, value in time_values:
            if start_time <= when < end_time:
                return value
        return None

    def get_details_for_time(self, when: datetime) -> dict[Detail, Any]:
        """Retrieve all forecast details for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        details = {}
        for detail, time_values in self.details.items():
            details[detail] = self._get_value_for_time(when, time_values)
        return details

    def get_details_for_times(
        self, iterable_when: Iterable[datetime]
    ) -> Generator[dict[Detail, tuple[Any, Any]]]:
        """Retrieve all forecast details for a list of times."""

        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not an Iterable")

        for when in iterable_when:
            yield self.get_details_for_time(when)

    def get_detail_for_time(
        self, detail: Detail, when: datetime
    ) -> tuple[Any, str | None]:
        """Retrieve single forecast detail for a point in time."""

        if not isinstance(detail, Detail):
            raise TypeError(f"{detail!r} is not a Detail")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        time_values = self.details.get(detail)
        return self._get_value_for_time(when, time_values) if time_values else None

    def get_details_by_hour(
        self, start_time: datetime, hours: int = 12
    ) -> Generator[dict[Detail, Any]]:
        """Retrieve a sequence of hourly forecast details"""

        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for hour in range(hours):
            yield self.get_details_for_time(start_time + timedelta(hours=hour))
