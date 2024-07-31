import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from .backports.enum import StrEnum


class NwsForecastUnits(StrEnum):
    """Values accepted as forecast_units."""

    US = "us"
    SI = "si"
