import json
from typing import Any, Dict

import pytest
from pynws.const import Detail

from pynws.summary import create_icon_url, create_short_forecast

from .helpers_forecast import (
    FORECAST_TEST_CASES_FNAME,
    ICON_TEST_CASES_FNAME,
    conditions_key,
    forecast_key,
    icon_key,
    read_test_cases,
)

forecast_test_cases = read_test_cases(FORECAST_TEST_CASES_FNAME, key=forecast_key)
icon_test_cases = read_test_cases(ICON_TEST_CASES_FNAME, key=icon_key)


@pytest.mark.parametrize("test_case", forecast_test_cases.values())
def test_summary_forecast(test_case: Dict[str, Any]):
    input = test_case["input"]
    expected = test_case["expected"]

    forecast = create_short_forecast(input)
    if forecast != expected:
        print(f"   Actual: {forecast}")
        print(f" Expected: {expected}")
        print(f"Condition: {conditions_key(input.get(Detail.WEATHER) or [])}")
        print(json.dumps(input, indent=2))
    assert forecast == expected


@pytest.mark.parametrize("test_case", icon_test_cases.values())
def test_summary_icon(test_case: Dict[str, Any]):
    input = test_case["input"]
    expected = test_case["expected"]

    icon_url = create_icon_url(input, show_pop=False)
    if icon_url != expected:
        print(f"   Actual: {icon_url}")
        print(f" Expected: {expected}")
        print(f"Condition: {conditions_key(input.get(Detail.WEATHER) or [])}")
        print(json.dumps(input, indent=2))
    assert icon_url == expected
