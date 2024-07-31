import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum, auto
else:
    from .backports.enum import StrEnum, auto


class NwsForecastUnits(StrEnum):
    """Values accepted as forecast_units."""

    US = auto()
    SI = auto()
