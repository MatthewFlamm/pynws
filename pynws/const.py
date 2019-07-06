"""
Constants for pynws
"""
import os

file_dir = os.path.join(os.path.dirname(__file__), '..')

with open(os.path.join(file_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

API_URL = 'https://api.weather.gov/'
API_STATIONS = 'points/{},{}/stations'
API_OBSERVATION = 'stations/{}/observations/'
API_ACCEPT = 'application/geo+json'
API_USER = 'pynws {}'
API_FORECAST = 'points/{},{}/forecast'
API_FORECAST_HOURLY = '/points/{},{}/forecast/hourly'

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
