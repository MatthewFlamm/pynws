"""Constants for pynws"""
import os

from .version import __version__

file_dir = os.path.join(os.path.dirname(__file__), "..")

version = __version__

API_URL = "https://api.weather.gov/"
API_POINTS_STATIONS = "points/{},{}/stations"
API_STATIONS_OBSERVATIONS = "stations/{}/observations/"
API_ACCEPT = "application/geo+json"
API_USER = "pynws {}"
API_FORECAST_ALL = "gridpoints/{}/{},{}"
API_FORECAST_DAILY = "gridpoints/{}/{},{}/forecast"
API_FORECAST_HOURLY = "gridpoints/{}/{},{}/forecast/hourly"
API_POINTS = "points/{},{}"
API_ALERTS_ACTIVE_ZONE = "alerts/active/zone/{}"

DEFAULT_USERID = "CODEemail@address"

ALERT_ID = "id"

API_WEATHER_CODE = {
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

LAYER_TEMPERATURE = "temperature"
LAYER_DEWPOINT = "dewpoint"
LAYER_MAX_TEMPERATURE = "maxTemperature"
LAYER_MIN_TEMPERATURE = "minTemperature"
LAYER_RELATIVE_HUMIDITY = "relativeHumidity"
LAYER_APPARENT_TEMPERATURE = "apparentTemperature"
LAYER_HEAT_INDEX = "heatIndex"
LAYER_WIND_CHILL = "windChill"
LAYER_SKY_COVER = "skyCover"
LAYER_WIND_DIRECTION = "windDirection"
LAYER_WIND_SPEED = "windSpeed"
LAYER_WIND_GUST = "windGust"
LAYER_WEATHER = "weather"
LAYER_HAZARDS = "hazards"
LAYER_PROBABILITY_OF_PRECIPITATION = "probabilityOfPrecipitation"
LAYER_QUANTITATIVE_PRECIPITATION = "quantitativePrecipitation"
LAYER_ICE_ACCUMULATION = "iceAccumulation"
LAYER_SNOWFALL_AMOUNT = "snowfallAmount"
LAYER_SNOW_LEVEL = "snowLevel"
LAYER_CEILING_HEIGHT = "ceilingHeight"
LAYER_VISIBILITY = "visibility"
LAYER_TRANSPORT_WIND_SPEED = "transportWindSpeed"
LAYER_TRANSPORT_WIND_DIRECTION = "transportWindDirection"
LAYER_MIXING_HEIGHT = "mixingHeight"
LAYER_HAINES_INDEX = "hainesIndex"
LAYER_LIGHTNING_ACTIVITY_LEVEL = "lightningActivityLevel"
LAYER_TWENTY_FOOT_WIND_SPEED = "twentyFootWindSpeed"
LAYER_TWENTY_FOOT_WIND_DIRECTION = "twentyFootWindDirection"
LAYER_WAVE_HEIGHT = "waveHeight"
LAYER_WAVE_PERIOD = "wavePeriod"
LAYER_WAVE_DIRECTION = "waveDirection"
LAYER_PRIMARY_SWELL_HEIGHT = "primarySwellHeight"
LAYER_PRIMARY_SWELL_DIRECTION = "primarySwellDirection"
LAYER_SECONDARY_SWELL_HEIGHT = "secondarySwellHeight"
LAYER_SECONDARY_SWELL_DIRECTION = "secondarySwellDirection"
LAYER_WAVE_PERIOD2 = "wavePeriod2"
LAYER_WIND_WAVE_HEIGHT = "windWaveHeight"
LAYER_DISPERSION_INDEX = "dispersionIndex"
LAYER_PRESSURE = "pressure"
LAYER_PROBABILITY_OF_TROPICAL_STORM_WINDS = "probabilityOfTropicalStormWinds"
LAYER_PROBABILITY_OF_HURRICANE_WINDS = "probabilityOfHurricaneWinds"
LAYER_POTENTIAL_OF_15MPH_WINDS = "potentialOf15mphWinds"
LAYER_POTENTIAL_OF_25MPH_WINDS = "potentialOf25mphWinds"
LAYER_POTENTIAL_OF_35MPH_WINDS = "potentialOf35mphWinds"
LAYER_POTENTIAL_OF_45MPH_WINDS = "potentialOf45mphWinds"
LAYER_POTENTIAL_OF_20MPH_WIND_GUSTS = "potentialOf20mphWindGusts"
LAYER_POTENTIAL_OF_30MPH_WIND_GUSTS = "potentialOf30mphWindGusts"
LAYER_POTENTIAL_OF_40MPH_WIND_GUSTS = "potentialOf40mphWindGusts"
LAYER_POTENTIAL_OF_50MPH_WIND_GUSTS = "potentialOf50mphWindGusts"
LAYER_POTENTIAL_OF_60MPH_WIND_GUSTS = "potentialOf60mphWindGusts"
LAYER_GRASSLAND_FIRE_DANGER_INDEX = "grasslandFireDangerIndex"
LAYER_PROBABILITY_OF_THUNDER = "probabilityOfThunder"
LAYER_DAVIS_STABILITY_INDEX = "davisStabilityIndex"
LAYER_ATMOSPHERIC_DISPERSION_INDEX = "atmosphericDispersionIndex"
LAYER_LOW_VISIBILITY_OCCURRENCE_RISK_INDEX = "lowVisibilityOccurrenceRiskIndex"
LAYER_STABILITY = "stability"
LAYER_RED_FLAG_THREAT_INDEX = "redFlagThreatIndex"
