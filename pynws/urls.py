"""
url formattera
"""

from pynws.const import (API_URL, API_ALERTS_ZONE, API_STATIONS, API_OBSERVATION, API_FORECAST,
                         API_FORECAST_HOURLY, API_GRID_FORECAST, API_GRID_FORECAST_HOURLY,
                         API_POINT)

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

def grid_forecast_url(wfo, x, y):
    """gridpoint forecast."""
    return API_URL + API_GRID_FORECAST.format(wfo, x, y)

def grid_forecast_hourly_url(wfo, x, y):
    """gridpoint forecast hpurly."""
    return API_URL + API_GRID_FORECAST_HOURLY.format(wfo, x, y)

def point_url(lat, lon):
    """ Formats point metadata url."""
    return API_URL + API_POINT.format(lat, lon)

def alerts_zone_url(zone):
    """Formats alerts url with zone."""
    return API_URL + API_ALERTS_ZONE.format(zone)
