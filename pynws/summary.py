"""NWS forecast summary and icon emulation"""
from __future__ import annotations

from typing import Any, Dict, List

from .const import Detail, Final

WEATHER_IGNORE_MULTI: Final = {
    "fog",
    "freezing_fog",
}

WEATHER_REPLACEMENTS: Final = {
    "rain_showers_and_snow_showers": "rain_and_snow_showers",
    "rain_showers_and_thunderstorms": "showers_and_thunderstorms",
}

COVERAGE_REPLACEMENTS: Final = {
    "numerous": "chance",
    "areas": "areas_of",
}

WEATHER_INTENSITIES: Final = {
    "rain": ("light", "heavy"),
    "snow": ("light", "heavy"),
}

WEATHER_PREFIXES: Final = {
    "areas_of",
    "chance",
    "isolated",
    "scattered",
    "slight_chance",
}

WEATHER_SUFFIXES: Final = {"likely"}

ICON_WEATHER_PRIORITY = [
    "thunderstorms",
    "blizzard",
    "blowing_snow",
    "snow",
    "snow_showers",
    "rain",
    "rain_showers",
]

ICON_WEATHER_REPLACEMENTS: Final = {
    "blowing_snow": "blizzard",
    "freezing_fog": "fog",
    "snow_showers": "snow",
}


def create_short_forecast(detailed: Dict[Detail, Any]) -> str:
    """Create short weather forecast that emulates NWS hourly short forecast.

    Args:
        detailed (Dict[Detail, Any]): NWS grid data

    Returns:
        str: Short forecast that emulates NWS hourly short forecast.
    """

    return (
        (
            _create_forecast_from_weather(detailed)
            or _create_forecast_from_sky_cover(detailed)
        )
        .replace("_", " ")
        .title()
    )


def _create_forecast_from_weather(detailed: Dict[Detail, Any]) -> str | None:
    weather_arr: List[str] = []
    intensity_arr: List[str] = []
    coverage_arr: List[str] = []

    for entry in detailed.get(Detail.WEATHER, []):
        weather = entry.get("weather")
        if weather:
            weather_arr.append(weather)
            intensity_arr.append(entry.get("intensity"))
            coverage_arr.append(entry.get("coverage"))

    if not weather_arr:
        return None

    if len(weather_arr) == 1:
        weather, intensity, coverage = weather_arr[0], intensity_arr[0], coverage_arr[0]
        allowed_intensities = WEATHER_INTENSITIES.get(weather)
        if allowed_intensities:
            if intensity in allowed_intensities:
                weather = f"{intensity} {weather}"
    else:
        weather_arr = sorted([w for w in weather_arr if w not in WEATHER_IGNORE_MULTI])
        weather = "_and_".join(weather_arr)
        coverage = coverage_arr[0]

    weather = WEATHER_REPLACEMENTS.get(weather, weather)
    coverage = COVERAGE_REPLACEMENTS.get(coverage, coverage)

    if coverage in WEATHER_PREFIXES:
        weather = f"{coverage} {weather}"
    elif coverage in WEATHER_SUFFIXES:
        weather = f"{weather} {coverage}"
    return weather


# pylint: disable=too-many-return-statements
def _create_forecast_from_sky_cover(detailed: Dict[Detail, Any]) -> str:
    sky_cover = detailed.get(Detail.SKY_COVER, 0)

    if detailed.get(Detail.IS_DAYTIME):
        if sky_cover <= 25:
            return "sunny"
        if sky_cover <= 50:
            return "mostly_sunny"
        if sky_cover <= 69:
            return "partly_sunny"
    else:
        if sky_cover <= 5:
            return "clear"
        if sky_cover <= 25:
            return "mostly_clear"
        if sky_cover <= 50:
            return "partly_cloudy"

    return "mostly_cloudy" if sky_cover <= 87 else "cloudy"


def create_icon_url(detailed: Dict[Detail, Any], *, show_pop: bool):
    """Create weather icon URL that emulates NWS hourly weather icon.

    Args:
        detailed (Dict[Detail, Any]): NWS grid data.
        show_pop (bool): Include probability of precipitation in URL.

    Returns:
        str: Weather icon URL that emulates NWS hourly weather icon.
    """

    day_night = "day" if detailed.get(Detail.IS_DAYTIME) else "night"
    sky_cover = detailed.get(Detail.SKY_COVER, 0)

    weather_arr: List[str] = []

    for entry in detailed.get(Detail.WEATHER, []):
        weather = entry.get("weather")
        if weather:
            weather_arr.append(weather)

    if len(weather_arr) > 1:
        weather_arr = [w for w in weather_arr if w not in WEATHER_IGNORE_MULTI]
        weather_arr = sorted(
            weather_arr,
            key=lambda x: ICON_WEATHER_PRIORITY.index(x)
            if x in ICON_WEATHER_PRIORITY
            else 100,
        )

    if weather_arr:
        weather = weather_arr[0]
        if weather == "thunderstorms":
            if sky_cover < 60:
                weather = "tsra_hi"
            elif sky_cover < 75:
                weather = "tsra_sct"
            else:
                weather = "tsra"
        else:
            weather = ICON_WEATHER_REPLACEMENTS.get(weather, weather)

        if show_pop:
            pop = round(detailed.get(Detail.PROBABILITY_OF_PRECIPITATION, 0) / 10) * 10
            if pop:
                weather += f",{pop}"
    else:
        if sky_cover <= 5:
            weather = "skc"
        elif sky_cover <= 25:
            weather = "few"
        elif sky_cover <= 50:
            weather = "sct"
        elif sky_cover < 88:
            weather = "bkn"
        else:
            weather = "ovc"

        if detailed.get(Detail.WIND_SPEED, 0) > 32:  # 32 km/h ≈ 20 mph
            weather = "wind_" + weather

    return f"https://api.weather.gov/icons/land/{day_night}/{weather}?size=small"
