"""
nws module
"""

import logging
import pynws.urls
from pynws.const import API_HEADER

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def get_obs_from_stn(station, websession, limit=None):
    """Get observation from NWS"""
    if limit is None:
        params = None
    else:
        params = {'limit': limit}

    url = pynws.urls.obs_url(station)
    async with websession.get(url, headers=API_HEADER, params=params) as res:
        status = res.status
        if status != 200:
            _LOGGER.error('failed to update observation of station %s with status %s',
                          station, status)
            return None
        else:
            obs = await res.json()
    return obs

async def observations(station, websession, limit=None):
    """Returns observations from station as list"""
    res = await get_obs_from_stn(station, websession, limit)
    return [o['properties'] for o in res['features']]

async def get_stn_from_pnt(lat, lon, websession):
    """get list of stations for lat/lon"""

    url = pynws.urls.stn_url(lat, lon)
    async with websession.get(url, headers=API_HEADER) as res:
        status = res.status
        if status != 200:
            _LOGGER.error('failed to get station list from %s with status %s',
                          url, status)
            return None
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
        status = res.status
        if status != 200:
            _LOGGER.error('failed to update forecast with status %s',
                          status)
            return None
        jres = await res.json()
    return jres

async def forecast(lat, lon, websession):
    """Returns forecast as list """
    res = await get_forc_from_pnt(lat, lon, websession)
    return res['properties']['periods']
