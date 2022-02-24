"""url formatter."""
from .const import (
    API_ALERTS_ACTIVE_ZONE,
    API_FORECAST_ALL,
    API_FORECAST_DAILY,
    API_FORECAST_HOURLY,
    API_POINTS,
    API_POINTS_STATIONS,
    API_STATIONS_OBSERVATIONS,
    API_URL,
)


def stations_observations_url(station):
    """Formats observation url."""
    return API_URL + API_STATIONS_OBSERVATIONS.format(station)


def points_stations_url(lat, lon):
    """formats station url"""
    return API_URL + API_POINTS_STATIONS.format(str(lat), str(lon))


def forecast_all_url(wfo, x, y):
    """gridpoint observation and forecast."""
    return API_URL + API_FORECAST_ALL.format(wfo, x, y)


def forecast_daily_url(wfo, x, y):
    """gridpoint forecast."""
    return API_URL + API_FORECAST_DAILY.format(wfo, x, y)


def forecast_hourly_url(wfo, x, y):
    """gridpoint forecast hpurly."""
    return API_URL + API_FORECAST_HOURLY.format(wfo, x, y)


def points_url(lat, lon):
    """ Formats point metadata url."""
    return API_URL + API_POINTS.format(lat, lon)


def alerts_active_zone_url(zone):
    """Formats alerts url with zone."""
    return API_URL + API_ALERTS_ACTIVE_ZONE.format(zone)
