"""
pynws module
"""

import pynws.urls
from pynws.const import API_HEADER


async def get_obs_from_stn(station, websession, limit=0):
    """Get observation response from station"""
    if limit == 0:
        params = None
    else:
        params = {'limit': limit}

    url = pynws.urls.obs_url(station)
    async with websession.get(url, headers=API_HEADER, params=params) as res:
        res.raise_for_status()
        obs = await res.json()
    return obs

async def observations(station, websession, limit=0):
    """Observations from station"""
    res = await get_obs_from_stn(station, websession, limit)
    return [o['properties'] for o in res['features']]

async def get_stn_from_pnt(lat, lon, websession):
    """Get list of stations for lat/lon"""

    url = pynws.urls.stn_url(lat, lon)
    async with websession.get(url, headers=API_HEADER) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres

async def stations(lat, lon, websession):
    """Returns list of stations for a point."""
    res = await get_stn_from_pnt(lat, lon, websession)
    return [s['properties']['stationIdentifier']
            for s in res['features']]

async def get_forc_from_pnt(lat, lon, websession):
    """update forecast"""

    url = pynws.urls.forc_url(lat, lon)
    async with websession.get(url, headers=API_HEADER) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres

async def forecast(lat, lon, websession):
    """Returns forecast as list """
    res = await get_forc_from_pnt(lat, lon, websession)
    return res['properties']['periods']
