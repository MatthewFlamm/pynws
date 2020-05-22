"""url formatter."""
from pynws.const import (
    API_ALERTS_ZONE,
    API_FORECAST,
    API_FORECAST_HOURLY,
    API_GRID_FORECAST,
    API_GRID_FORECAST_HOURLY,
    API_OBSERVATION,
    API_POINT,
    API_STATIONS,
    API_URL,
)


def stations_observations_url(station):
    """Formats observation url."""
    return API_URL + API_STATIONS_OBSERVATION.format(station)


def points_stations_url(lat, lon):
    """formats station url"""
    return API_URL + API_POINTS_STATIONS.format(str(lat), str(lon))


def gridpoints_forecast_url(wfo, x, y):
    """gridpoint forecast."""
    return API_URL + API_GRIDPOINTS_FORECAST.format(wfo, x, y)


def gridpoints_forecast_hourly_url(wfo, x, y):
    """gridpoint forecast hpurly."""
    return API_URL + API_GRIDPOINTS_FORECAST_HOURLY.format(wfo, x, y)


def points_url(lat, lon):
    """ Formats point metadata url."""
    return API_URL + API_POINT.format(lat, lon)


def alerts_zone_url(zone):
    """Formats alerts url with zone."""
    return API_URL + API_ALERTS_ZONE.format(zone)
