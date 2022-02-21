"""
Constants for pynws
"""
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
API_GRIDPOINTS_FORECAST = "gridpoints/{}/{},{}/forecast"
API_GRIDPOINTS_FORECAST_HOURLY = "gridpoints/{}/{},{}/forecast/hourly"
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

OBS_TEMPERATURE = "temperature"
OBS_BARO_PRESSURE = "barometricPressure"
OBS_SEA_PRESSURE = "seaLevelPressure"
OBS_REL_HUMIDITY = "relativeHumidity"
OBS_WIND_SPEED = "windSpeed"
OBS_WIND_DIRECTION = "windDirection"
OBS_VISIBILITY = "visibility"
OBS_ELEVATION = "elevation"
OBS_DESCRIPTION = "textDescription"
OBS_DEWPOINT = "dewpoint"
OBS_WIND_GUST = "windGust"
OBS_STATION = "station"
OBS_TIMESTAMP = "timestamp"
OBS_ICON = "icon"
OBS_MAX_TEMP_24H = "maxTemperatureLast24Hours"
OBS_MIN_TEMP_24H = "minTemperatureLast24Hours"
OBS_PRECIPITATION_1H = "precipitationLastHour"
OBS_PRECIPITATION_3H = "precipitationLast3Hours"
OBS_PRECIPITATION_6H = "precipitationLast6Hours"
OBS_WIND_CHILL = "windChill"
OBS_HEAT_INDEX = "heatIndex"
OBS_RAW_MESSAGE = "rawMessage"

OBS_ITEM_VALUE = "value"
OBS_ITEM_UNIT_CODE = "unitCode"

# derived observations
OBS_ICON_TIME = "iconTime"
OBS_ICON_WEATHER = "iconWeather"
