"""Unit conversion"""

from tokenize import Number
from typing import Callable


UNIT_CONVERSION = {
    "degC": lambda x: x,
    "degF": lambda x: (x - 32.0) / 1.8,  # convert to celsius
    "km_h-1": lambda x: x,
    "m_s-1": lambda x: x * 3.6,  # convert to km/h
    "m": lambda x: x,
    "mm": lambda x: x,
    "Pa": lambda x: x,
    "percent": lambda x: x,
    "degree_(angle)": lambda x: x,
    "s": lambda x: x,
}


def get_converter(unit_code: str) -> Callable[[Number], Number]:
    """Get method to convert value with unit code to preferred unit."""
    converter = UNIT_CONVERSION.get(unit_code.split(":")[-1])
    if not converter:
        raise ValueError(f"unit code: '{unit_code}' not recognized.")
    return converter


def convert_unit(unit_code: str, value: Number) -> Number:
    """Convert value with unit code to preferred unit."""
    converter = get_converter(unit_code)
    return converter(value)
