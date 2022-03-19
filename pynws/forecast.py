"""Forecast classes"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Generator, Iterable, Union
from .const import Detail
from .units import get_converter


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

DetailValue = Union[int, float, list, None]


class DetailedForecast:
    """Class to retrieve forecast values for a point in time."""

    def __init__(self, properties: dict[str, Any]):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self.update_time = datetime.fromisoformat(properties["updateTime"])
        self.details = details = {}

        for prop_name, prop_value in properties.items():
            try:
                detail = Detail(prop_name)
            except ValueError:
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

            details[detail] = time_values

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
        """When the forecast was last updated."""
        return self.update_time

    @staticmethod
    def _get_value_for_time(
        when, time_values: tuple[datetime, datetime, DetailValue]
    ) -> DetailValue:
        for start_time, end_time, value in time_values:
            if start_time <= when < end_time:
                return value
        return None

    def get_details_for_time(self, when: datetime) -> dict[Detail, DetailValue]:
        """Retrieve all forecast details for a point in time.

        Args:
            when (datetime): Point in time of requested forecast.

        Raises:
            TypeError: If 'when' argument is not a 'datetime'.

        Returns:
            dict[Detail, DetailValue]: All forecast details for the specified time.
        """
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        details = {}
        for detail, time_values in self.details.items():
            details[detail] = self._get_value_for_time(when, time_values)
        return details

    def get_details_for_times(
        self, iterable_when: Iterable[datetime]
    ) -> Generator[dict[Detail, DetailValue]]:
        """Retrieve all forecast details for a list of times.

        Args:
            iterable_when (Iterable[datetime]): List of times to retrieve.

        Raises:
            TypeError: If 'iterable_when' argument is not a collection.

        Yields:
            Generator[dict[Detail, DetailValue]]: Sequence of forecast details
            corresponding with the list of times to retrieve.
        """
        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not iterable")

        for when in iterable_when:
            yield self.get_details_for_time(when)

    def get_detail_for_time(self, detail: Detail, when: datetime) -> DetailValue:
        """Retrieve single forecast detail for a point in time.

        Args:
            detail (Detail): Forecast detail to retrieve.
            when (datetime): Point in time of requested forecast detail.

        Raises:
            TypeError: If 'detail' argument is not a 'Detail'.
            TypeError: If 'when' argument is not a 'datetime'.

        Returns:
            DetailValue: Requested forecast detail value for the specified time.
        """
        if not isinstance(detail, Detail):
            raise TypeError(f"{detail!r} is not a Detail")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        time_values = self.details.get(detail)
        return self._get_value_for_time(when, time_values) if time_values else None

    def get_details_by_hour(
        self, start_time: datetime, hours: int = 24
    ) -> Generator[dict[Detail, DetailValue]]:
        """Retrieve a sequence of hourly forecast details

        Args:
            start_time (datetime): First time to retrieve.
            hours (int, optional): Number of hours to retrieve.

        Raises:
            TypeError: If 'start_time' argument is not a 'datetime'.

        Yields:
            Generator[dict[Detail, DetailValue]]: Sequence of forecast detail
            values with one details dictionary per requested hour.
        """
        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for _ in range(hours):
            end_time = start_time + ONE_HOUR
            details = {
                Detail.START_TIME: datetime.isoformat(start_time),
                Detail.END_TIME: datetime.isoformat(end_time),
            }
            details.update(self.get_details_for_time(start_time))
            yield details
            start_time = end_time
