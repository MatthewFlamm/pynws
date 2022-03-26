"""Python 3.11 Enum backports from https://github.com/home-assistant/core/tree/dev/homeassistant/backports"""
from __future__ import annotations

from enum import Enum
from typing import Any, List, TypeVar

_StrEnumT = TypeVar("_StrEnumT", bound="StrEnum")


class StrEnum(str, Enum):
    """Partial backport of Python 3.11's StrEnum for our basic use cases."""

    def __new__(
        cls: type[_StrEnumT], value: str, *args: Any, **kwargs: Any
    ) -> _StrEnumT:
        """Create a new StrEnum instance."""
        if not isinstance(value, str):
            raise TypeError(f"{value!r} is not a string")
        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self) -> str:
        """Return self.value."""
        return str(self.value)

    @staticmethod
    def _generate_next_value_(  # pylint: disable=arguments-differ # https://github.com/PyCQA/pylint/issues/5371
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        """
        Make `auto()` explicitly unsupported.

        We may revisit this when it's very clear that Python 3.11's
        `StrEnum.auto()` behavior will no longer change.
        """
        raise TypeError("auto() is not supported by this implementation")
