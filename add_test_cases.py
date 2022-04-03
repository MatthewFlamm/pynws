import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, TypeVar
from copy import deepcopy

import aiohttp

from pynws import SimpleNWS
from pynws.const import Detail
from tests.helpers_forecast import (
    FORECAST_TEST_CASES_FNAME,
    ICON_TEST_CASES_FNAME,
    forecast_key,
    icon_key,
    read_test_cases,
)

CITY_COORDS = {
    "Appleton, WI": (44.287, -88.467),
    "Death Valley, CA": (36.587, -117.331),
    "Denver, CO": (39.764, -104.995),
    "Dushore, PA": (41.524, -76.405),
    "Gainesville, FL": (29.686, -82.389),
    "Harrisburg, PA": (40.282, -76.915),
    "Hilo, HI": (19.719, -155.369),
    "International Falls, MN": (48.586, -93.452),
    "New York, NY": (40.697, -74.119),
    "Omaha, NE": (41.292, -96.221),
    "Portland, OR": (45.542, -122.794),
    "Prudhoe Bay, AK": (70.326, -149.382),
    "Red Lodge, MT": (45.193, -109.267),
    "San Juan, PRI": (18.389, -66.131),
    "Tabor City, NC": (34.158, -78.890),
    "Uvalde, TX": (29.212, -99.792),
    "Washington, DC": (38.893, -77.084),
}

USERID = "testing@example.com"

T = TypeVar("T")

MINIMAL_DETAILS = {
    Detail.WEATHER,
    Detail.IS_DAYTIME,
    Detail.SKY_COVER,
    Detail.WIND_SPEED,
}


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]], *, retries=5, backoff_seconds=1
) -> T:
    x = 0
    while True:
        try:
            return await func()
        except:
            if x == retries:
                raise
            sleep = backoff_seconds * 2**x
            await asyncio.sleep(sleep)
            x += 1


def write_test_cases(file_name: str, test_cases: Dict[str, Dict[str, Any]]):
    with open(file_name, "w") as output_file:
        test_cases = dict(sorted(test_cases.items(), key=lambda x: x[0]))
        json.dump(list(test_cases.values()), output_file, indent=2)


def reindex(
    name: str, test_cases: Dict[str, Dict[str, Any]], create_key=callable
) -> Dict[str, Dict[str, Any]]:
    result = {}
    for test_case in test_cases.values():
        details = test_case["input"]
        key = create_key(details)
        if key not in result:
            result[key] = test_case
    if len(test_cases) != len(result):
        print(f"{name} test cases: before {len(test_cases)}; after {len(result)}")
    return result


def minimize(details: Dict[Detail, Any]) -> Dict[Detail, Any]:
    result = {k: deepcopy(v) for k, v in details.items() if k in MINIMAL_DETAILS}
    for x in result.get(Detail.WEATHER) or []:
        del x["visibility"]
        del x["attributes"]
    return result


async def add_test_cases():
    async with aiohttp.ClientSession() as session:
        forecast_cases = read_test_cases(FORECAST_TEST_CASES_FNAME, key=forecast_key)
        icon_cases = read_test_cases(ICON_TEST_CASES_FNAME, key=icon_key)

        forecast_cases = reindex("Forecast", forecast_cases, create_key=forecast_key)
        icon_cases = reindex("Icon", icon_cases, create_key=icon_key)

        for city, coord in CITY_COORDS.items():
            nws = SimpleNWS(*coord, USERID, session)

            try:
                await retry_with_backoff(nws.set_station)
                await retry_with_backoff(nws.update_forecast_hourly)
                await retry_with_backoff(nws.update_detailed_forecast)
            except:
                print(f"Skipping {city} due to multiple errors")
                continue

            start_time = datetime.now(tz=timezone.utc).astimezone()
            detailed_forecast = list(
                nws.detailed_forecast.get_details_by_hour(
                    start_time, hours=len(nws.forecast_hourly)
                )
            )

            index = 0
            for hourly, details in zip(nws.forecast_hourly, detailed_forecast):
                index += 1

                if details.get(Detail.WEATHER) is None:
                    print(f"Skipping hour without weather conditions array: {city}")
                    continue

                key = forecast_key(details)
                if key not in forecast_cases:
                    print(f"Adding forecast test case: {key}")
                    expected = hourly.get("shortForecast")
                    forecast_cases[key] = {
                        "input": minimize(details),
                        "expected": expected,
                    }

                key = icon_key(details)
                if key not in icon_cases:
                    print(f"Adding icon test case: {key}")
                    expected = hourly.get("icon")
                    if "," in expected:
                        expected = re.sub(r",\d+", "", expected)  # remove POP
                    icon_cases[key] = {"input": minimize(details), "expected": expected}

        write_test_cases(FORECAST_TEST_CASES_FNAME, forecast_cases)
        write_test_cases(ICON_TEST_CASES_FNAME, icon_cases)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(add_test_cases())
