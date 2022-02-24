"""Forecast class"""
import re
from datetime import datetime, timedelta, timezone
from .layer import Layer

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


class Forecast:
    """Class to retrieve forecast layer values for a point in time."""

    def __init__(self, properties):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self._properties = properties
        self._layers = {}

    @staticmethod
    def _parse_duration(duration_str):
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

    def get_layer_values(self, layer):
        """Retrieve all forecast layer values."""

        if not isinstance(layer, Layer):
            raise TypeError(f"{layer!r} is not a Layer enum")

        if layer in self._layers:
            return self._layers[layer]

        layer_props = self._properties[layer]
        layer_values = []

        for value in layer_props["values"]:
            isodatetime, duration_str = value["validTime"].split("/")
            start_time = datetime.fromisoformat(isodatetime)
            end_time = start_time + self._parse_duration(duration_str)
            layer_values.append((start_time, end_time, float(value["value"])))

        retval = self._layers[layer] = (layer_values, layer_props["uom"])
        return retval

    def get_layer_value(self, layer, when):
        """Retrieve a forecast layer value for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)
        layer_values, units = self.get_layer_values(layer)

        for start_time, end_time, value in layer_values:
            if start_time <= when < end_time:
                return (value, units)

        return (None, None)
