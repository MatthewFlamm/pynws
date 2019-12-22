"""
Constants for pynws
"""
import os

from .version import __version__

file_dir = os.path.join(os.path.dirname(__file__), '..')

version = __version__

API_URL = 'https://api.weather.gov/'
API_STATIONS = 'points/{},{}/stations'
API_OBSERVATION = 'stations/{}/observations/'
API_ACCEPT = 'application/geo+json'
API_USER = 'pynws {}'
API_FORECAST = 'points/{},{}/forecast'
API_FORECAST_HOURLY = '/points/{},{}/forecast/hourly'
API_GRID_FORECAST = 'gridpoints/{}/{},{}/forecast'
API_GRID_FORECAST_HOURLY = 'gridpoints/{}/{},{}/forecast/hourly'
API_POINT = 'points/{},{}'
API_ALERTS_ZONE = 'alerts/active/zone/{}'

DEFAULT_USERID = 'CODEemail@address'

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
    "fog": "Fog/mist"
    }
