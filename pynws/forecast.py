"""Forecast classes"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, Iterable, Iterator, List, Tuple, Union

from .const import Detail, Final
from .units import get_converter

ISO8601_PERIOD_REGEX: Final = re.compile(
    r"^P"
    r"((?P<weeks>\d+)W)?"
    r"((?P<days>\d+)D)?"
    r"((?:T)"
    r"((?P<hours>\d+)H)?"
    r"((?P<minutes>\d+)M)?"
    r"((?P<seconds>\d+)S)?"
    r")?$"
)

ONE_HOUR: Final = timedelta(hours=1)

DetailValue = Union[int, float, list, str, None]
_TimeValue = Tuple[datetime, datetime, DetailValue]


class DetailedForecast:
    """Class to retrieve forecast values for a point in time."""

    def __init__(self: DetailedForecast, properties: Dict[str, Any]):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self.update_time = datetime.fromisoformat(properties["updateTime"])
        self.details: Dict[Detail, List[_TimeValue]] = {}

        for prop_name, prop_value in properties.items():
            try:
                detail = Detail(prop_name)
            except ValueError:
                continue

            unit_code = prop_value.get("uom")
            converter = get_converter(unit_code) if unit_code else None

            time_values: List[_TimeValue] = []

            for value in prop_value["values"]:
                isodatetime, duration_str = value["validTime"].split("/")
                start_time = datetime.fromisoformat(isodatetime)
                end_time = start_time + self._parse_duration(duration_str)
                value = value["value"]
                if converter and value:
                    value = converter(value)
                time_values.append((start_time, end_time, value))

            self.details[detail] = time_values

    @staticmethod
    def _parse_duration(duration_str: str) -> timedelta:
        match = ISO8601_PERIOD_REGEX.match(duration_str)
        if not match:
            raise ValueError(f"{duration_str!r} is not an ISO 8601 string")
        groups = match.groupdict()

        values: Dict[str, float] = {}
        for key, val in groups.items():
            values[key] = float(val or "0")

        return timedelta(
            weeks=values["weeks"],
            days=values["days"],
            hours=values["hours"],
            minutes=values["minutes"],
            seconds=values["seconds"],
        )

    @property
    def last_update(self: DetailedForecast) -> datetime:
        """When the forecast was last updated."""
        return self.update_time

    @staticmethod
    def _get_value_for_time(
        when: datetime, time_values: List[_TimeValue]
    ) -> DetailValue:
        for start_time, end_time, value in time_values:
            if start_time <= when < end_time:
                return value
        return None

    def get_details_for_time(
        self: DetailedForecast, when: datetime
    ) -> Dict[Detail, DetailValue]:
        """Retrieve all forecast details for a point in time.

        Args:
            when (datetime): Point in time of requested forecast.

        Raises:
            TypeError: If 'when' argument is not a 'datetime'.

        Returns:
            Dict[Detail, DetailValue]: All forecast details for the specified time.
        """
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)

        details: Dict[Detail, DetailValue] = {}
        for detail, time_values in self.details.items():
            value = self._get_value_for_time(when, time_values)
            if value is not None:
                details[detail] = value
        return details

    def get_details_for_times(
        self: DetailedForecast, iterable_when: Iterable[datetime]
    ) -> Iterator[Dict[Detail, DetailValue]]:
        """Retrieve all forecast details for a list of times.

        Args:
            iterable_when (Iterable[datetime]): List of times to retrieve.

        Raises:
            TypeError: If 'iterable_when' argument is not a collection.

        Yields:
            Iterator[Dict[Detail, DetailValue]]: Sequence of forecast details
            corresponding with the list of times to retrieve.
        """
        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not iterable")

        for when in iterable_when:
            yield self.get_details_for_time(when)

    def get_detail_for_time(
        self: DetailedForecast, detail_arg: Union[Detail, str], when: datetime
    ) -> DetailValue:
        """Retrieve single forecast detail for a point in time.

        Args:
            detail_arg (Union[Detail, str]): Forecast detail to retrieve.
            when (datetime): Point in time of requested forecast detail.

        Raises:
            TypeError: If 'detail' argument is not a 'Detail' or 'str'.
            TypeError: If 'when' argument is not a 'datetime'.

        Returns:
            DetailValue: Requested forecast detail value for the specified time.
        """
        if not isinstance(detail_arg, Detail) and not isinstance(detail_arg, str):
            raise TypeError(f"{detail_arg!r} is not a Detail or str")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        detail = detail_arg if isinstance(detail_arg, Detail) else Detail(detail_arg)
        time_values = self.details.get(detail)
        return self._get_value_for_time(when, time_values) if time_values else None

    def get_details_by_hour(
        self: DetailedForecast, start_time: datetime, hours: int = 24
    ) -> Iterator[Dict[Detail, DetailValue]]:
        """Retrieve a sequence of hourly forecast details

        Args:
            start_time (datetime): First time to retrieve.
            hours (int, optional): Number of hours to retrieve.

        Raises:
            TypeError: If 'start_time' argument is not a 'datetime'.

        Yields:
            Iterator[Dict[Detail, DetailValue]]: Sequence of forecast detail
            values with one details dictionary per requested hour.
        """
        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for _ in range(hours):
            end_time = start_time + ONE_HOUR
            details: Dict[Detail, DetailValue] = {
                Detail.START_TIME: datetime.isoformat(start_time),
                Detail.END_TIME: datetime.isoformat(end_time),
            }
            details.update(self.get_details_for_time(start_time))
            yield details
            start_time = end_time
