"""Forecast class"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Generator, Iterable
from pynws.layer import Layer


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


class Forecast:
    """Class to retrieve forecast layer values for a point in time."""

    def __init__(self, properties: dict[str, Any]):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self.update_time = datetime.fromisoformat(properties["updateTime"])
        self.layers = layers = {}

        for prop_name, prop_value in properties.items():
            if not isinstance(prop_value, dict) or "values" not in prop_value:
                continue

            layer_values = []

            for value in prop_value["values"]:
                isodatetime, duration_str = value["validTime"].split("/")
                start_time = datetime.fromisoformat(isodatetime)
                end_time = start_time + self._parse_duration(duration_str)
                layer_values.append((start_time, end_time, value["value"]))

            units = prop_value.get("uom")
            units = units.split(":")[-1] if units else None
            layers[prop_name] = (layer_values, units)

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
    def _get_layer_value_for_time(
        when, layer_values: tuple[datetime, datetime, Any], units: str | None
    ) -> tuple[Any, str | None]:
        for start_time, end_time, value in layer_values:
            if start_time <= when < end_time:
                return (value, units)
        return (None, None)

    def get_forecast_for_time(self, when: datetime) -> dict[Any, str | None]:
        """Retrieve all forecast layers for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        forecast = {}
        for layer_name, (layer_values, units) in self.layers.items():
            forecast[layer_name] = self._get_layer_value_for_time(
                when, layer_values, units
            )
        return forecast

    def get_forecast_for_times(
        self, iterable_when: Iterable[datetime]
    ) -> Generator[dict[str, Any]]:
        """Retrieve all forecast layers for a list of times."""

        if not isinstance(iterable_when, Iterable):
            raise TypeError(f"{iterable_when!r} is not an Iterable")

        for when in iterable_when:
            yield self.get_forecast_for_time(when)

    def get_forecast_layer_for_time(
        self, layer: Layer, when: datetime
    ) -> tuple[Any, str | None]:
        """Retrieve single forecast layer for a point in time."""

        if not isinstance(layer, Layer):
            raise TypeError(f"{layer!r} is not a Layer")
        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        values_and_unit = self.layers.get(layer)
        if values_and_unit:
            return self._get_layer_value_for_time(when, *values_and_unit)
        return (None, None)

    def get_hourly_forecasts(
        self, start_time: datetime, hours: int = 12
    ) -> Generator[dict[str, Any]]:
        """Retrieve a sequence of hourly forecasts with all layers"""

        if not isinstance(start_time, datetime):
            raise TypeError(f"{start_time!r} is not a datetime")

        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        for hour in range(hours):
            yield self.get_forecast_for_time(start_time + timedelta(hours=hour))
