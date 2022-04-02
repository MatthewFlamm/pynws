"""NWS forecast summary and icon emulation"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, cast

from .const import Detail, Final

FORECAST_COVERAGE_PRIORITY: Final[Dict[str, int]] = {
    "definite": 0,
    "likely": 10,
    "chance": 20,
    "scattered": 30,
    "patchy": 40,
    "areas": 50,
    "isolated": 60,
    "slight_chance": 70,
}

FORECAST_COVERAGE_REPLACEMENTS: Final = {
    "numerous": "chance",
    "areas": "areas_of",
}

FORECAST_INTENSITIES: Final = [
    "very_light",
    "light",
    "heavy",
    "very_heavy",
]

FORECAST_WEATHER_INTENSITIES: Final[Dict[str, List[str]]] = {
    "rain": FORECAST_INTENSITIES,
    "snow": FORECAST_INTENSITIES,
}

FORECAST_WEATHER_COMBINATIONS: Final[List[Tuple[Set[str], str]]] = [
    ({"rain", "freezing_rain"}, "freezing_rain"),
    ({"snow", "freezing_rain"}, "freezing_rain"),
    ({"rain_showers", "snow_showers"}, "rain_and_snow_showers"),
    ({"rain_showers", "thunderstorms"}, "showers_and_thunderstorms"),
]

FORECAST_WEATHER_PREFIXES: Final = {
    "areas_of",
    "chance",
    "isolated",
    "patchy",
    "scattered",
    "slight_chance",
}

FORECAST_WEATHER_SUFFIXES: Final = {"likely"}

ICON_WEATHER_REPLACEMENTS: Final[List[Tuple[Set[str], str]]] = [
    # convert
    ({"blowing_snow"}, "blizzard"),
    ({"freezing_fog"}, "fog"),
    ({"freezing_rain"}, "fzra"),
    ({"snow_showers"}, "snow"),
    # combine
    ({"snow", "rain"}, "snow"),
    ({"snow", "rain_showers"}, "snow"),
    ({"snow", "fzra"}, "snow_fzra"),
    ({"snow", "sleet"}, "snow_sleet"),
    ({"rain", "fzra"}, "rain_fzra"),
    ({"rain", "sleet"}, "rain_sleet"),
    ({"rain_showers", "fzra"}, "rain_fzra"),
    ({"rain_showers", "sleet"}, "rain_sleet"),
]

ICON_WEATHER_IGNORE_MULTI: Final = {
    "fog",
    "freezing_fog",
}


def create_short_forecast(detailed: Dict[Detail, Any]) -> str:
    """Create short weather forecast that emulates NWS hourly short forecast.

    Args:
        detailed (Dict[Detail, Any]): NWS grid data

    Returns:
        str: Short forecast that emulates NWS hourly short forecast.
    """

    forecast = _forecast_from_weather(detailed) or _forecast_from_sky_cover(detailed)
    return forecast.replace("_", " ").title()


def _forecast_from_weather(detailed: Dict[Detail, Any]) -> Optional[str]:
    # remove empty entries
    entries: List[Dict[str, Any]] = [
        x for x in detailed.get(Detail.WEATHER, []) if x.get("weather")
    ]
    if not entries:
        return None

    weather, coverage = (
        _forecast_from_single(entries[0])
        if len(entries) == 1
        else _forecast_from_multiple(entries)
    )

    if coverage:
        coverage = FORECAST_COVERAGE_REPLACEMENTS.get(coverage, coverage)
        if coverage in FORECAST_WEATHER_PREFIXES:
            weather = f"{coverage} {weather}"
        elif coverage in FORECAST_WEATHER_SUFFIXES:
            weather = f"{weather} {coverage}"

    return weather


def _forecast_from_single(entry: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    weather = cast(str, entry.get("weather"))
    intensity: Optional[str] = entry.get("intensity")
    coverage: Optional[str] = entry.get("coverage")

    if intensity:
        allowed_intensities = FORECAST_WEATHER_INTENSITIES.get(weather, [])
        if intensity in allowed_intensities:
            weather = f"{intensity} {weather}"
    return weather, coverage


def _forecast_from_multiple(entries: List[Dict[str, Any]]) -> Tuple[str, Optional[str]]:
    index = {cast(str, x.get("weather")): x for x in entries}
    weather_set = set(index.keys())

    def coverage_key(coverage: str) -> int:
        return FORECAST_COVERAGE_PRIORITY.get(coverage, 999)

    for search, replace in FORECAST_WEATHER_COMBINATIONS:
        if not search.issubset(weather_set):
            continue

        weather_set.difference_update(search)
        weather_set.add(replace)

        if replace not in search:
            # When everything in search is replaced, find the highest priority
            # coverage from the replaced entries for the new entry.
            coverages = [cast(str, index[x].get("coverage")) for x in search]
            coverages = sorted(coverages, key=coverage_key)
            index[replace] = {"weather": replace, "coverage": coverages[0]}

        for key in search.difference([replace]):
            del index[key]

    weather = "_and_".join(sorted(weather_set))
    coverages = [cast(str, x.get("coverage")) for x in index.values()]
    coverages = sorted(coverages, key=coverage_key)
    return weather, coverages[0]


# pylint: disable=too-many-return-statements
def _forecast_from_sky_cover(detailed: Dict[Detail, Any]) -> str:
    sky_cover = detailed.get(Detail.SKY_COVER) or 0

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
    weather = _create_icon_from_weather(
        detailed, show_pop
    ) or _create_icon_from_sky_cover(detailed)

    return f"https://api.weather.gov/icons/land/{day_night}/{weather}?size=small"


def _create_icon_from_weather(detailed, show_pop):
    weather_set: Set[str] = set()
    for entry in detailed.get(Detail.WEATHER, []):
        weather = entry.get("weather")
        if weather:
            weather_set.add(weather)

    if not weather_set:
        return None

    if "thunderstorms" in weather_set:
        sky_cover = detailed.get(Detail.SKY_COVER) or 0
        if sky_cover < 60:
            weather = "tsra_hi"
        elif sky_cover < 75:
            weather = "tsra_sct"
        else:
            weather = "tsra"
    else:
        for search, replace in ICON_WEATHER_REPLACEMENTS:
            if search.issubset(weather_set):
                weather_set -= search
                weather_set.add(replace)

        if len(weather_set) > 1:
            weather_set -= ICON_WEATHER_IGNORE_MULTI

        weather = weather_set.pop()

    if show_pop:
        pop = detailed.get(Detail.PROBABILITY_OF_PRECIPITATION) or 0
        pop = round(pop / 10 + 0.01) * 10
        if pop > 10:
            weather += f",{pop}"

    return weather


def _create_icon_from_sky_cover(detailed) -> str:
    sky_cover = detailed.get(Detail.SKY_COVER) or 0
    wind_kmh = detailed.get(Detail.WIND_SPEED) or 0

    if sky_cover <= 5:
        weather = "skc"
    elif sky_cover <= 25:
        weather = "few"
    elif sky_cover <= 50:
        weather = "sct"
    elif sky_cover <= 87:
        weather = "bkn"
    else:
        weather = "ovc"

    if wind_kmh > 32:  # 32 km/h ≈ 20 mph
        weather = "wind_" + weather

    return weather
