"""Functions to retrieve raw data."""
from datetime import datetime
import logging
from typing import Any, Mapping, MutableMapping, Optional
from aiohttp import ClientSession

from . import urls
from .const import API_ACCEPT, API_USER

_LOGGER = logging.getLogger(__name__)


def get_header(userid: str) -> Mapping[str, str]:
    """Get header.

    NWS recommends including an email in userid.
    """
    return {"accept": API_ACCEPT, "User-Agent": API_USER.format(userid)}


async def _make_request(
    websession: ClientSession,
    url: str,
    header: Mapping[str, str],
    params: Optional[Mapping[str, Any]] = None,
) -> Mapping[str, Any]:
    """Make request."""
    async with websession.get(url, headers=header, params=params) as res:
        _LOGGER.debug("Request for %s returned code: %s", url, res.status)
        _LOGGER.debug("Request for %s returned header: %s", url, res.headers)
        res.raise_for_status()
        obs = await res.json()
        _LOGGER.debug("Request for %s returned data: %s", url, obs)
    return obs


async def raw_stations_observations(
    station: str,
    websession: ClientSession,
    userid: str,
    limit: int = 0,
    start: Optional[datetime] = None,
) -> Mapping[str, Any]:
    """Get observation response from station"""
    params: MutableMapping[str, Any] = {}
    if limit > 0:
        params["limit"] = limit

    if start:
        if not isinstance(start, datetime):
            raise ValueError
        params["start"] = start.isoformat(timespec="seconds")

    url = urls.stations_observations_url(station)
    header = get_header(userid)
    return await _make_request(websession, url, header, params)


async def raw_stations_observations_latest(
    station: str, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Get observation response from station"""
    url = urls.stations_observations_latest_url(station)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_points_stations(
    lat: float, lon: float, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Get list of stations for lat/lon"""
    url = urls.points_stations_url(lat, lon)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_points(
    lat: float, lon: float, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Return griddata response."""
    url = urls.points_url(lat, lon)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_detailed_forecast(
    wfo: str, x: int, y: int, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Return griddata response."""
    url = urls.detailed_forecast_url(wfo, x, y)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_gridpoints_forecast(
    wfo: str, x: int, y: int, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Return griddata response."""
    url = urls.gridpoints_forecast_url(wfo, x, y)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_gridpoints_forecast_hourly(
    wfo: str, x: int, y: int, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Return griddata response."""
    url = urls.gridpoints_forecast_hourly_url(wfo, x, y)
    header = get_header(userid)
    return await _make_request(websession, url, header)


async def raw_alerts_active_zone(
    zone: str, websession: ClientSession, userid: str
) -> Mapping[str, Any]:
    """Return griddata response."""
    url = urls.alerts_active_zone_url(zone)
    header = get_header(userid)
    return await _make_request(websession, url, header)
