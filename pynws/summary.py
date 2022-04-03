"""NWS forecast summary and icon emulation"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, cast

from .const import Detail, Final

FORECAST_COVERAGE_PRIORITY: Final = {
    "definite": 0,
    "likely": 1,
    "scattered": 2,
    "patchy": 3,
    "areas": 4,
    "isolated": 5,
    "chance": 6,
    "slight_chance": 7,
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

FORECAST_WEATHER_INTENSITIES: Final = {
    "rain": FORECAST_INTENSITIES,
    "snow": FORECAST_INTENSITIES,
}

FORECAST_WEATHER_REPLACEMENTS: Final = {
    # values within keys must be alphabetical
    "blowing_snow|snow": "blowing_snow",
    "fog|rain": "fog",
    "fog|rain|snow": "fog",
    "fog|snow": "snow",
    "freezing_fog|snow": "freezing_fog",
    "freezing_fog|snow_showers": "snow_showers",
    "freezing_rain|rain|snow": "freezing_rain",
    "rain_showers|snow_showers": "rain_and_snow_showers",
    "rain_showers|thunderstorms": "showers_and_thunderstorms",
}

# canned results when rules can't be found
FORECAST_CANNED_RESULTS: Final = {
    "blowing_snow--areas|snow-light-definite": "Light Snow And Areas Of Blowing Snow",
    "blowing_snow--areas|snow-light-likely": "Light Snow Likely And Areas Of Blowing Snow",
    "rain-light-chance|thunderstorms--isolated": "Chance Light Rain",
    "rain-light-likely|thunderstorms--slight_chance": "Light Rain Likely",
}

FORECAST_COVERAGE_PREFIXES: Final = {
    "areas_of",
    "chance",
    "isolated",
    "patchy",
    "scattered",
    "slight_chance",
}

FORECAST_COVERAGE_SUFFIXES: Final = {"likely"}

ICON_WEATHER_REPLACEMENTS: Final = {
    # values within keys must be alphabetical
    "blowing_snow|snow": "blizzard",
    "fog|rain": "rain",
    "fog|rain|snow": "snow",
    "fog|snow": "snow",
    "freezing_fog": "fog",
    "freezing_fog|snow_showers": "snow",
    "freezing_rain": "fzra",
    "freezing_rain|rain": "rain_fzra",
    "freezing_rain|rain|snow": "snow_fzra",
    "rain_showers|snow_showers": "snow",
    "rain|snow": "snow",
    "snow_showers": "snow",
}

ICON_VALID_WEATHER_ICONS: Final = {
    "blizzard",
    "cold",
    "dust",
    "fog",
    "fzra",
    "haze",
    "hot",
    "hurricane",
    "rain",
    "rain_fzra",
    "rain_showers",
    "rain_showers_hi",
    "rain_sleet",
    "rain_snow",
    "sleet",
    "smoke",
    "snow",
    "snow_fzra",
    "snow_sleet",
    "tornado",
    "tropical_storm",
    "tsra",
    "tsra_hi",
    "tsra_sct",
}


def conditions_key(entries: List[Dict[str, Any]]) -> Optional[str]:
    """Create key from array of weather conditions"""
    results = []
    for entry in entries:
        if condition := entry.get("weather"):
            intensity = entry.get("intensity") or ""
            coverage = entry.get("coverage") or ""
            results.append(f"{condition}-{intensity}-{coverage}")

    return "|".join(sorted(results)) if results else None


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
        x for x in detailed.get(Detail.WEATHER) or [] if x.get("weather")
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
        if coverage in FORECAST_COVERAGE_PREFIXES:
            weather = f"{coverage} {weather}"
        elif coverage in FORECAST_COVERAGE_SUFFIXES:
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
    key = conditions_key(entries)
    if key:
        weather = FORECAST_CANNED_RESULTS.get(key)
        if weather:
            return weather, None

    index = {cast(str, x.get("weather")): x for x in entries}
    weather_set = set(index.keys())

    def coverage_sort_key(coverage: str) -> int:
        return FORECAST_COVERAGE_PRIORITY.get(coverage, 999)

    replace = FORECAST_WEATHER_REPLACEMENTS.get("|".join(sorted(weather_set)))
    if replace:
        if replace in weather_set:
            return _forecast_from_single(index[replace])

        # result requires merging list entries
        coverages = [cast(str, index[x].get("coverage")) for x in weather_set]
        coverages = sorted(coverages, key=coverage_sort_key)
        index[replace] = {"weather": replace, "coverage": coverages[0]}

        for key in weather_set.difference([replace]):
            del index[key]

        weather_set = {replace}

    weather = "_and_".join(sorted(weather_set))
    coverages = [cast(str, x.get("coverage")) for x in index.values()]
    coverages = sorted(coverages, key=coverage_sort_key)
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
    for entry in detailed.get(Detail.WEATHER) or []:
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
        replace = ICON_WEATHER_REPLACEMENTS.get("|".join(sorted(weather_set)))
        if replace:
            weather_set = {replace}

        weather_set.intersection_update(ICON_VALID_WEATHER_ICONS)
        weather = weather_set.pop() if len(weather_set) == 1 else None

    if weather and show_pop:
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
