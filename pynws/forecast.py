"""Forecast class"""
import re
from datetime import datetime, timedelta, timezone


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


class Forecast:  # pylint: disable=too-few-public-methods
    """Class to retrieve forecast layer values for a point in time."""

    def __init__(self, properties):
        if not isinstance(properties, dict):
            raise TypeError(f"{properties!r} is not a dictionary")

        self._layers = layers = {}

        for prop_name, prop_value in properties.items():
            if not isinstance(prop_value, dict) or "values" not in prop_value:
                continue

            layer_values = []

            units = prop_value.get("uom", None)

            for value in prop_value["values"]:
                isodatetime, duration_str = value["validTime"].split("/")
                start_time = datetime.fromisoformat(isodatetime)
                end_time = start_time + Forecast._parse_duration(duration_str)
                layer_values.append((start_time, end_time, value["value"]))

            layers[prop_name] = (layer_values, units)

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

    def get_forecast_for_time(self, when):
        """Retrieve all forecast layers for a point in time."""

        if not isinstance(when, datetime):
            raise TypeError(f"{when!r} is not a datetime")

        when = when.astimezone(timezone.utc)

        result = {}

        for layer_name, (layer_values, units) in self._layers.items():
            for start_time, end_time, value in layer_values:
                if start_time <= when < end_time:
                    result[layer_name] = (value, units)
                    break

        return result
