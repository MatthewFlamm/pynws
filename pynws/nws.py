"""pynws module."""
from datetime import datetime, timedelta, timezone

from pynws.const import API_ACCEPT, API_USER, DEFAULT_USERID
import pynws.urls


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

        self.wfo = None
        self.x = None
        self.y = None

        self.forecast_zone = None
        self.county_zone = None
        self.fire_weather_zone = None

    async def stations(self):
        """Returns station list"""
        if self.latlon is None:
            raise NwsError("Need to set lattitude and longitude")
        return await stations(*self.latlon, self.session, self.userid)

    async def observations(self, limit=0, start_time=None):
        """Returns observation list"""
        if self.station is None:
            raise NwsError("Need to set station")
        return await observations(
            self.station, self.session, self.userid, limit, start_time
        )

    async def get_pointdata(self):
        """Saves griddata from latlon."""
        data = await get_pointdata(*self.latlon, self.session, self.userid)

        properties = data.get("properties")
        if properties:
            self.wfo = properties.get("cwa")
            self.x = properties.get("gridX")
            self.y = properties.get("gridY")
            self.forecast_zone = properties.get("forecastZone").split("/")[-1]
            self.county_zone = properties.get("county").split("/")[-1]
            self.fire_weather_zone = properties.get("fireWeatherZone").split("/")[-1]

    async def grid_forecast(self):
        """Return forecast from grid."""
        if self.wfo is None:
            await self.get_pointdata()
        raw_forecast = await grid_forecast_raw(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return raw_forecast["properties"]["periods"]

    async def grid_forecast_hourly(self):
        """Return hourly forecast from grid."""
        if self.wfo is None:
            await self.get_pointdata()
        raw_forecast = await grid_forecast_hourly_raw(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return raw_forecast["properties"]["periods"]

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

    async def alerts_forecast_zone(self):
        """Returns alerts dict for forecast_l zone."""
        if self.forecast_zone is None:
            await self.get_pointdata()
        alerts = await alerts_zone_raw(self.forecast_zone, self.session, self.userid)
        return [alert["properties"] for alert in alerts["features"]]

    async def alerts_county_zone(self):
        """Returns alerts dict for county zone."""
        if self.county_zone is None:
            await self.get_pointdata()
        alerts = await alerts_zone_raw(self.county_zone, self.session, self.userid)
        return [alert["properties"] for alert in alerts["features"]]

    async def alerts_fire_weather_zone(self):
        """Returns alerts dict for fire weather zone."""
        if self.fire_weather_zone is None:
            await self.get_pointdata()
        alerts = await alerts_zone_raw(
            self.fire_weather_zone, self.session, self.userid
        )
        return [alert["properties"] for alert in alerts["features"]]


def get_header(userid):
    """Get header.

    NWS recommends including an email in userid.
    """
    return {"accept": API_ACCEPT, "User-Agent": API_USER.format(userid)}


async def get_obs_from_stn(station, websession, userid, limit=5, start_time=None):
    """Get observation response from station"""
    params = {}
    if limit > 0:
        params["limit"] = limit

    if start_time:
        if not isinstance(start_time, timedelta):
            raise ValueError
        now = datetime.now(timezone.utc)
        request_time = now - start_time
        params["start"] = request_time.isoformat(timespec="seconds")

    url = pynws.urls.obs_url(station)
    header = get_header(userid)
    async with websession.get(url, headers=header, params=params) as res:
        res.raise_for_status()
        obs = await res.json()
    return obs


async def observations(station, websession, userid, limit=5, start_time=None):
    """Observations from station"""
    res = await get_obs_from_stn(station, websession, userid, limit, start_time)
    return [o["properties"] for o in res["features"]]


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
    return [s["properties"]["stationIdentifier"] for s in res["features"]]


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
    return res["properties"]["periods"]


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
    return res["properties"]["periods"]


async def get_pointdata(lat, lon, websession, userid):
    """Return griddata response."""

    url = pynws.urls.point_url(lat, lon)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def grid_forecast_raw(wfo, x, y, websession, userid):
    """Return griddata response."""

    url = pynws.urls.grid_forecast_url(wfo, x, y)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def grid_forecast_hourly_raw(wfo, x, y, websession, userid):
    """Return griddata response."""

    url = pynws.urls.grid_forecast_hourly_url(wfo, x, y)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres


async def alerts_zone_raw(zone, websession, userid):
    """Return griddata response."""

    url = pynws.urls.alerts_zone_url(zone)
    header = get_header(userid)
    async with websession.get(url, headers=header) as res:
        res.raise_for_status()
        jres = await res.json()
    return jres
