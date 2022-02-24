"""Functions to retrieve raw data."""
from datetime import datetime

from .const import API_ACCEPT, API_USER
from . import urls


def get_header(userid):
    """Get header.

    NWS recommends including an email in userid.
    """
    return {"accept": API_ACCEPT, "User-Agent": API_USER.format(userid)}


async def raw_stations_observations(station, websession, userid, limit=0, start=None):
    """Get observation response from station"""
    params = {}
    if limit > 0:
        params["limit"] = limit

    if start:
        if not isinstance(start, datetime):
            raise ValueError
        params["start"] = start.isoformat(timespec="seconds")

    url = urls.stations_observations_url(station)
    header = get_header(userid)
    async with websession.get(url, headers=header, params=params) as res:
        res.raise_for_status()
        obs = await res.json()
    return obs


async def raw_points_stations(lat, lon, websession, userid):
    """Get list of stations for lat/lon"""
    url = urls.points_stations_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def raw_points(lat, lon, websession, userid):
    """Return griddata response."""
    url = urls.points_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def raw_all_forecast(wfo, x, y, websession, userid):
    """Return griddata response."""
    url = urls.all_forecast_url(wfo, x, y)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def raw_daily_forecast(wfo, x, y, websession, userid):
    """Return griddata response."""
    url = urls.daily_forecast_url(wfo, x, y)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def raw_hourly_forecast(wfo, x, y, websession, userid):
    """Return griddata response."""
    url = urls.hourly_forecast_url(wfo, x, y)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def raw_alerts_active_zone(zone, websession, userid):
    """Return griddata response."""
    url = urls.alerts_active_zone_url(zone)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres
