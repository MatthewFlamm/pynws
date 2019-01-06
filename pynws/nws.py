"""
pynws module
"""

import pynws.urls
from pynws.const import API_ACCEPT, API_USER, DEFAULT_USERID


def get_header(userid=DEFAULT_USERID):
    """Get header.

    NWS recommends including an email in userid.
    """
    return {'accept': API_ACCEPT,
            'User-Agent': API_USER.format(userid)}

async def get_obs_from_stn(station, websession, limit=0,
                           userid=DEFAULT_USERID):
    """Get observation response from station"""
    if limit == 0:
        params = None
    else:
        params = {'limit': limit}

    url = pynws.urls.obs_url(station)
    header = get_header(userid)
    async with websession.get(url, headers=header, params=params) as res:
        res.raise_for_status()
        obs = await res.json()
    return obs

async def observations(station, websession, limit=0, userid=DEFAULT_USERID):
    """Observations from station"""
    res = await get_obs_from_stn(station, websession, limit, userid)
    return [o['properties'] for o in res['features']]

async def get_stn_from_pnt(lat, lon, websession, userid=DEFAULT_USERID):
    """Get list of stations for lat/lon"""

    url = pynws.urls.stn_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres

async def stations(lat, lon, websession, userid=DEFAULT_USERID):
    """Returns list of stations for a point."""
    res = await get_stn_from_pnt(lat, lon, websession, userid)
    return [s['properties']['stationIdentifier']
            for s in res['features']]

async def get_forc_from_pnt(lat, lon, websession, userid=DEFAULT_USERID):
    """update forecast"""

    url = pynws.urls.forc_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres

async def forecast(lat, lon, websession, userid=DEFAULT_USERID):
    """Returns forecast as list """
    res = await get_forc_from_pnt(lat, lon, websession, userid)
    return res['properties']['periods']
