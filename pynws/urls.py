"""
url formattera
"""

from pynws.const import API_URL, API_STATIONS, API_OBSERVATION, API_FORECAST, API_FORECAST_HOURLY

def obs_url(station):
    """Formats observation url."""
    return API_URL + API_OBSERVATION.format(station)

def stn_url(lat, lon):
    """formats station url"""
    return API_URL + API_STATIONS.format(str(lat), str(lon))

def forc_url(lat, lon):
    """Formats forecast url"""
    return API_URL + API_FORECAST.format(lat, lon)

def hour_forc_url(lat, lon):
    """Formats forecast url"""
    return API_URL + API_FORECAST_HOURLY.format(lat, lon)
