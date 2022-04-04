import json
import os
from typing import Any, Callable, Dict, List

from pynws.const import Detail
from pynws.summary import conditions_key

from .helpers import DIR

FORECAST_TEST_CASES_FNAME = os.path.join(DIR, "summary_forecast.json")
ICON_TEST_CASES_FNAME = os.path.join(DIR, "summary_icon.json")


def read_test_cases(
    file_name: str, *, key=Callable[[Dict[Detail, Any]], str]
) -> Dict[str, Dict[str, Any]]:
    try:
        with open(file_name) as input_file:
            return {
                key(test_case.get("input")): test_case
                for test_case in json.load(input_file)
            }
    except:
        return {}


def forecast_key(details: Dict[Detail, Any]) -> str:
    key = conditions_key(details.get(Detail.WEATHER) or [])
    if not key:
        sky_cover = details.get(Detail.SKY_COVER) or 0
        sky_cover = (sky_cover // 5) * 5
        key = f"{sky_cover:03}"
    return key


def icon_key(details: Dict[Detail, Any]) -> str:
    key = conditions_key(details.get(Detail.WEATHER) or [])
    if not key:
        sky_cover = details.get(Detail.SKY_COVER) or 0
        sky_cover = (sky_cover // 5) * 5
        wind_speed = round(details.get(Detail.WIND_SPEED) or 0)
        key = f"{sky_cover:03}-{'windy' if wind_speed > 32 else 'calm'}"
    day_night = "day" if details.get(Detail.IS_DAYTIME) else "night"
    return f"{day_night}-{key}"
