"""
pynws module
"""

import pynws.urls
from pynws.const import API_ACCEPT, API_USER, DEFAULT_USERID

class NwsError(Exception):
    """Error in Nws Class"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Nws:
    """Nws object for simple use"""
    def __init__(self, session, latlon=None, station=None, userid=DEFAULT_USERID):
        self.session = session
        self.latlon = latlon
        self.station = station
        self.userid = userid

    async def stations(self):
        """Returns station list"""
        if self.latlon is None:
            raise NwsError("Need to set lattitude and longitude")
        return await stations(*self.latlon, self.session, self.userid)

    async def observations(self, limit=5):
        """Returns observation list"""
        if self.station is None:
            raise NwsError("Need to set station")
        return await observations(self.station, self.session, self.userid, limit)

    async def forecast(self):
        """Returns forecast list"""
        if self.latlon is None:
            raise NwsError("Need to set lattitude and longitude")
        return await forecast(*self.latlon, self.session, self.userid)

    async def forecast_hourly(self):
        """returns hourly forecast list"""
        if self.latlon is None:
            raise NwsError("Need to set lattitude and longitude")
        return await forecast_hourly(*self.latlon, self.session, self.userid)


def get_header(userid):
    """Get header.

    NWS recommends including an email in userid.
    """
    return {'accept': API_ACCEPT,
            'User-Agent': API_USER.format(userid)}


async def get_obs_from_stn(station, websession, userid, limit=5):
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


async def observations(station, websession, userid, limit=5):
    """Observations from station"""
    res = await get_obs_from_stn(station, websession, userid, limit)
    return [o['properties'] for o in res['features']]


async def get_stn_from_pnt(lat, lon, websession, userid):
    """Get list of stations for lat/lon"""

    url = pynws.urls.stn_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def stations(lat, lon, websession, userid):
    """Returns list of stations for a point."""
    res = await get_stn_from_pnt(lat, lon, websession, userid)
    return [s['properties']['stationIdentifier']
            for s in res['features']]


async def get_forc_from_pnt(lat, lon, websession, userid):
    """update forecast"""

    url = pynws.urls.forc_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def forecast(lat, lon, websession, userid):
    """Returns forecast as list """
    res = await get_forc_from_pnt(lat, lon, websession, userid)
    return res['properties']['periods']


async def get_hour_forc_from_pnt(lat, lon, websession, userid):
    """update forecast"""

    url = pynws.urls.hour_forc_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def forecast_hourly(lat, lon, websession, userid):
    """Returns hourly forecast as list """
    res = await get_hour_forc_from_pnt(lat, lon, websession, userid)
    return res['properties']['periods']
