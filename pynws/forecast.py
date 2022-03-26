"""Forecast classes"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, Generator, Iterable, Union

from pynws.const import Detail

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

_T_Detail_str = Union[Detail, str]


class DetailedForecast:
    """Class to retrieve forecast values for a point in time."""

    def __init__(self, properties: Dict[_T_Detail_str, Any]):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self.update_time = datetime.fromisoformat(properties["updateTime"])
        self.details: Dict[_T_Detail_str, Any] = {}
        details = self.details

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
        if not match:
            raise ValueError(f"duration_str not recognized: got {duration_str}")
        groups = match.groupdict()
        groups_int = {key: int(val or "0") for key, val in groups.items()}

        return timedelta(
            weeks=groups_int["weeks"],
            days=groups_int["days"],
            hours=groups_int["hours"],
            minutes=groups_int["minutes"],
            seconds=groups_int["seconds"],
        )

    @property
    def last_update(self) -> datetime:
        """When the forecast was last updated"""
        return self.update_time

    @staticmethod
    def _find_detail_for_time(
        when, time_values: tuple[datetime, datetime, Any], units: str | None
    ) -> tuple[Any, str | None]:
        for start_time, end_time, value in time_values:
            if start_time <= when < end_time:
                return value, units
        return None, None

    def get_details_for_time(
        self, when: datetime
    ) -> Dict[_T_Detail_str, tuple[Any, str | None]]:
        """Retrieve all forecast details for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        details = {}
        for detail, (time_values, units) in self.details.items():
            details[detail] = self._find_detail_for_time(when, time_values, units)
        return details

    def get_details_for_times(
        self, iterable_when: Iterable[datetime]
    ) -> Generator[Dict[_T_Detail_str, tuple[Any, Any]], None, None]:
        """Retrieve all forecast details for a list of times."""

        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not an Iterable")

        for when in iterable_when:
            yield self.get_details_for_time(when)

    def get_detail_for_time(
        self, detail: _T_Detail_str, when: datetime
    ) -> tuple[Any, str | None]:
        """Retrieve single forecast detail for a point in time."""

        if not isinstance(detail, Detail):
            raise TypeError(f"{detail!r} is not a Detail")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        time_values, units = self.details[detail]
        if time_values and units:
            return self._find_detail_for_time(when, time_values, units)
        return None, None

    def get_details_by_hour(
        self, start_time: datetime, hours: int = 12
    ) -> Generator[Dict[_T_Detail_str, Any], None, None]:
        """Retrieve a sequence of hourly forecast details"""

        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for _ in range(hours):
            end_time = start_time + ONE_HOUR
            details: Dict[_T_Detail_str, Any] = {
                Detail.START_TIME: datetime.isoformat(start_time),
                Detail.END_TIME: datetime.isoformat(end_time),
            }
            details.update(self.get_details_for_time(start_time))
            yield details
            start_time = end_time
