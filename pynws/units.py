"""Units of measurement"""
from .backports.enum import StrEnum


# Canonical conversion values
KILOMETERS_PER_MILE = 1.609344
METERS_PER_FOOT = 0.3048
METERS_PER_MILE = 1609.344
MILLIMETERS_PER_INCH = 25.4
PASCALS_PER_PSI = 6894.76
SECONDS_PER_HOUR = 3600


class Unit(StrEnum):
    """Unit of measurement names"""

    CELSIUS = "degC"
    DEGREE = "degree_(angle)"
    FAHRENHEIT = "degF"
    FOOT = "ft"
    INCH = "in"
    KILOMETERS_PER_HOUR = "km_h-1"
    METER = "m"
    METERS_PER_SECOND = "m_s-1"
    MILES_PER_HOUR = "mi_h-1"
    MILLIMETER = "mm"
    NONE = ""
    PASCAL = "Pa"
    PERCENT = "percent"
    PSI = "psi"
    SECONDS = "s"


# fmt: off
UNIT_CONVERTERS = {
    # Temperature
    (Unit.CELSIUS, Unit.FAHRENHEIT): lambda x: (x * 1.8) + 32,
    (Unit.FAHRENHEIT, Unit.CELSIUS): lambda x: (x - 32) / 1.8,

    # Length
    (Unit.MILLIMETER, Unit.INCH): lambda x: x / MILLIMETERS_PER_INCH,
    (Unit.INCH, Unit.MILLIMETER): lambda x: x * MILLIMETERS_PER_INCH,
    (Unit.METER, Unit.FOOT): lambda x: x / METERS_PER_FOOT,
    (Unit.FOOT, Unit.METER): lambda x: x * METERS_PER_FOOT,

    # Speed
    (Unit.KILOMETERS_PER_HOUR, Unit.MILES_PER_HOUR): lambda x: x / KILOMETERS_PER_MILE,
    (Unit.MILES_PER_HOUR, Unit.KILOMETERS_PER_HOUR): lambda x: x * KILOMETERS_PER_MILE,
    (Unit.METERS_PER_SECOND, Unit.MILES_PER_HOUR): lambda x: x / METERS_PER_MILE * SECONDS_PER_HOUR,
    (Unit.MILES_PER_HOUR, Unit.METERS_PER_SECOND): lambda x: x * METERS_PER_MILE / SECONDS_PER_HOUR,

    # Pressure
    (Unit.PASCAL, Unit.PSI): lambda x: x / PASCALS_PER_PSI,
    (Unit.PSI, Unit.PASCAL): lambda x: x * PASCALS_PER_PSI,
}
# fmt: on


def convert_unit(value, from_unit: Unit, to_unit: Unit) -> float:
    """Convert a value from one unit system to another unit system"""
    if not isinstance(value, int) and not isinstance(value, float):
        raise TypeError(f"{value!r} must be an 'int' or a 'float'")

    if from_unit == to_unit:
        return value

    converter = UNIT_CONVERTERS.get((from_unit, to_unit))
    if not converter:
        raise ValueError(f"No conversion available from {from_unit} to {to_unit}")

    return converter(value)
