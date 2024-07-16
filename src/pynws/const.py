"""
Constants for pynws
"""

from enum import unique
import os
import sys
from typing import Final

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from .backports.enum import StrEnum

file_dir = os.path.join(os.path.dirname(__file__), "..")

API_URL: Final = "https://api.weather.gov/"
API_GRIDPOINTS_STATIONS: Final = "gridpoints/{}/{},{}/stations"
API_STATIONS_OBSERVATIONS: Final = "stations/{}/observations/"
API_STATIONS_OBSERVATIONS_LATEST: Final = "stations/{}/observations/latest"
API_ACCEPT: Final = "application/geo+json"
API_USER: Final = "pynws {}"
API_DETAILED_FORECAST: Final = "gridpoints/{}/{},{}"
API_GRIDPOINTS_FORECAST: Final = "gridpoints/{}/{},{}/forecast"
API_GRIDPOINTS_FORECAST_HOURLY: Final = "gridpoints/{}/{},{}/forecast/hourly"
API_POINTS: Final = "points/{},{}"
API_ALERTS_ACTIVE_ZONE: Final = "alerts/active/zone/{}"

DEFAULT_USERID: Final = "CODEemail@address"

ALERT_ID: Final = "id"

API_WEATHER_CODE: Final = {
    "skc": "Fair/clear",
    "few": "A few clouds",
    "sct": "Partly cloudy",
    "bkn": "Mostly cloudy",
    "ovc": "Overcast",
    "wind_skc": "Fair/clear and windy",
    "wind_few": "A few clouds and windy",
    "wind_sct": "Partly cloudy and windy",
    "wind_bkn": "Mostly cloudy and windy",
    "wind_ovc": "Overcast and windy",
    "snow": "Snow",
    "rain_snow": "Rain/snow",
    "rain_sleet": "Rain/sleet",
    "snow_sleet": "Snow/sleet",
    "fzra": "Freezing rain",
    "rain_fzra": "Rain/freezing rain",
    "snow_fzra": "Freezing rain/snow",
    "sleet": "Sleet",
    "rain": "Rain",
    "rain_showers": "Rain showers (high cloud cover)",
    "rain_showers_hi": "Rain showers (low cloud cover)",
    "tsra": "Thunderstorm (high cloud cover)",
    "tsra_sct": "Thunderstorm (medium cloud cover)",
    "tsra_hi": "Thunderstorm (low cloud cover)",
    "tornado": "Tornado",
    "hurricane": "Hurricane conditions",
    "tropical_storm": "Tropical storm conditions",
    "dust": "Dust",
    "smoke": "Smoke",
    "haze": "Haze",
    "hot": "Hot",
    "cold": "Cold",
    "blizzard": "Blizzard",
    "fog": "Fog/mist",
}


@unique
class Detail(StrEnum):
    """Detailed forecast value names"""

    START_TIME = "startTime"
    END_TIME = "endTime"
    TEMPERATURE = "temperature"
    DEWPOINT = "dewpoint"
    MAX_TEMPERATURE = "maxTemperature"
    MIN_TEMPERATURE = "minTemperature"
    RELATIVE_HUMIDITY = "relativeHumidity"
    APPARENT_TEMPERATURE = "apparentTemperature"
    HEAT_INDEX = "heatIndex"
    WIND_CHILL = "windChill"
    SKY_COVER = "skyCover"
    WIND_DIRECTION = "windDirection"
    WIND_SPEED = "windSpeed"
    WIND_GUST = "windGust"
    WEATHER = "weather"
    HAZARDS = "hazards"
    PROBABILITY_OF_PRECIPITATION = "probabilityOfPrecipitation"
    QUANTITATIVE_PRECIPITATION = "quantitativePrecipitation"
    ICE_ACCUMULATION = "iceAccumulation"
    SNOWFALL_AMOUNT = "snowfallAmount"
    SNOW_LEVEL = "snowLevel"
    CEILING_HEIGHT = "ceilingHeight"
    VISIBILITY = "visibility"
    TRANSPORT_WIND_SPEED = "transportWindSpeed"
    TRANSPORT_WIND_DIRECTION = "transportWindDirection"
    MIXING_HEIGHT = "mixingHeight"
    HAINES_INDEX = "hainesIndex"
    LIGHTNING_ACTIVITY_LEVEL = "lightningActivityLevel"
    TWENTY_FOOT_WIND_SPEED = "twentyFootWindSpeed"
    TWENTY_FOOT_WIND_DIRECTION = "twentyFootWindDirection"
    WAVE_HEIGHT = "waveHeight"
    WAVE_PERIOD = "wavePeriod"
    WAVE_DIRECTION = "waveDirection"
    PRIMARY_SWELL_HEIGHT = "primarySwellHeight"
    PRIMARY_SWELL_DIRECTION = "primarySwellDirection"
    SECONDARY_SWELL_HEIGHT = "secondarySwellHeight"
    SECONDARY_SWELL_DIRECTION = "secondarySwellDirection"
    WAVE_PERIOD2 = "wavePeriod2"
    WIND_WAVE_HEIGHT = "windWaveHeight"
    DISPERSION_INDEX = "dispersionIndex"
    PRESSURE = "pressure"
    PROBABILITY_OF_TROPICAL_STORM_WINDS = "probabilityOfTropicalStormWinds"
    PROBABILITY_OF_HURRICANE_WINDS = "probabilityOfHurricaneWinds"
    POTENTIAL_OF_15MPH_WINDS = "potentialOf15mphWinds"
    POTENTIAL_OF_25MPH_WINDS = "potentialOf25mphWinds"
    POTENTIAL_OF_35MPH_WINDS = "potentialOf35mphWinds"
    POTENTIAL_OF_45MPH_WINDS = "potentialOf45mphWinds"
    POTENTIAL_OF_20MPH_WIND_GUSTS = "potentialOf20mphWindGusts"
    POTENTIAL_OF_30MPH_WIND_GUSTS = "potentialOf30mphWindGusts"
    POTENTIAL_OF_40MPH_WIND_GUSTS = "potentialOf40mphWindGusts"
    POTENTIAL_OF_50MPH_WIND_GUSTS = "potentialOf50mphWindGusts"
    POTENTIAL_OF_60MPH_WIND_GUSTS = "potentialOf60mphWindGusts"
    GRASSLAND_FIRE_DANGER_INDEX = "grasslandFireDangerIndex"
    PROBABILITY_OF_THUNDER = "probabilityOfThunder"
    DAVIS_STABILITY_INDEX = "davisStabilityIndex"
    ATMOSPHERIC_DISPERSION_INDEX = "atmosphericDispersionIndex"
    LOW_VISIBILITY_OCCURRENCE_RISK_INDEX = "lowVisibilityOccurrenceRiskIndex"
    STABILITY = "stability"
    RED_FLAG_THREAT_INDEX = "redFlagThreatIndex"


MetadataKeys = ["updateTime", "generatedAt", "validTimes"]
