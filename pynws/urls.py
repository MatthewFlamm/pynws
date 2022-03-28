"""url formatter."""
from .const import (
    API_ALERTS_ACTIVE_ZONE,
    API_DETAILED_FORECAST,
    API_GRIDPOINTS_FORECAST,
    API_GRIDPOINTS_FORECAST_HOURLY,
    API_POINTS,
    API_POINTS_STATIONS,
    API_STATIONS_OBSERVATIONS,
    API_STATIONS_OBSERVATIONS_LATEST,
    API_URL,
)


def stations_observations_url(station: str) -> str:
    """Formats observation url."""
    return API_URL + API_STATIONS_OBSERVATIONS.format(station)


def stations_observations_latest_url(station: str) -> str:
    """Formats observation url."""
    return API_URL + API_STATIONS_OBSERVATIONS_LATEST.format(station)


def points_stations_url(lat: float, lon: float) -> str:
    """formats station url"""
    return API_URL + API_POINTS_STATIONS.format(str(lat), str(lon))


def detailed_forecast_url(wfo: str, x: int, y: int) -> str:
    """gridpoint observation and forecast."""
    return API_URL + API_DETAILED_FORECAST.format(wfo, x, y)


def gridpoints_forecast_url(wfo: str, x: int, y: int) -> str:
    """gridpoint forecast."""
    return API_URL + API_GRIDPOINTS_FORECAST.format(wfo, x, y)


def gridpoints_forecast_hourly_url(wfo: str, x: int, y: int) -> str:
    """gridpoint forecast hpurly."""
    return API_URL + API_GRIDPOINTS_FORECAST_HOURLY.format(wfo, x, y)


def points_url(lat: float, lon: float) -> str:
    """Formats point metadata url."""
    return API_URL + API_POINTS.format(lat, lon)


def alerts_active_zone_url(zone: str) -> str:
    """Formats alerts url with zone."""
    return API_URL + API_ALERTS_ACTIVE_ZONE.format(zone)
