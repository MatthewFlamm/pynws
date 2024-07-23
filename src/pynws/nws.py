"""pynws module."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast

from aiohttp import ClientSession

from .forecast import DetailedForecast
from .raw_data import (
    raw_alerts_active_zone,
    raw_detailed_forecast,
    raw_gridpoints_forecast,
    raw_gridpoints_forecast_hourly,
    raw_gridpoints_stations,
    raw_points,
    raw_stations_observations,
    raw_stations_observations_latest,
)


class NwsError(Exception):
    """Error in Nws Class"""

    def __init__(self: NwsError, message: str):
        super().__init__(message)
        self.message = message


class NwsNoDataError(NwsError):
    """No data was returned."""


class Nws:
    """Class to more easily get data for one location."""

    def __init__(
        self: Nws,
        session: ClientSession,
        userid: str,
        latlon: Optional[Tuple[float, float]] = None,
        station: Optional[str] = None,
    ):
        if not session:
            raise NwsError(f"{session!r} is required")
        if not isinstance(userid, str) or not userid:
            raise NwsError(f"{userid!r} is required")
        if latlon and (not isinstance(latlon, tuple) or len(latlon) != 2):
            raise NwsError(f"{latlon!r} is required to be tuple[float, float]")

        self.session: ClientSession = session
        self.userid: str = userid
        self.latlon: Optional[Tuple[float, float]] = latlon
        self.station: Optional[str] = station

        self.wfo: Optional[str] = None
        self.x: Optional[int] = None
        self.y: Optional[int] = None

        self.forecast_zone: Optional[str] = None
        self.county_zone: Optional[str] = None
        self.fire_weather_zone: Optional[str] = None

    async def get_points_stations(self: Nws) -> List[str]:
        """Returns station list"""
        if not (self.wfo and self.x and self.y):
            await self.get_points()
        if not (self.wfo and self.x and self.y):
            raise NwsError(f"Error fetching gridpoint identifiers for {self.latlon!r}")
        res = await raw_gridpoints_stations(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return [s["properties"]["stationIdentifier"] for s in res["features"]]

    async def get_stations_observations(
        self: Nws, limit: int = 0, start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Returns observation list"""
        if self.station is None:
            raise NwsError("Need to set station")
        res = await raw_stations_observations(
            self.station, self.session, self.userid, limit, start_time
        )
        observations = [o["properties"] for o in res["features"]]
        return sorted(
            observations, key=lambda o: cast(str, o.get("timestamp")), reverse=True
        )

    async def get_stations_observations_latest(self: Nws) -> Dict[str, Any]:
        """Returns latest observation"""
        if self.station is None:
            raise NwsError("Need to set station")
        res = await raw_stations_observations_latest(
            self.station, self.session, self.userid
        )
        return cast(Dict[str, Any], res.get("properties"))

    async def get_points(self: Nws) -> None:
        """Saves griddata from latlon."""
        if self.latlon is None:
            raise NwsError("Latitude and longitude are required")
        data = await raw_points(*self.latlon, self.session, self.userid)

        properties = data.get("properties")
        if properties:
            self.wfo = properties.get("cwa")
            self.x = properties.get("gridX")
            self.y = properties.get("gridY")
            self.forecast_zone = properties.get("forecastZone").split("/")[-1]
            self.county_zone = properties.get("county").split("/")[-1]
            self.fire_weather_zone = properties.get("fireWeatherZone").split("/")[-1]
        return properties

    async def get_detailed_forecast(self: Nws) -> DetailedForecast:
        """Return all forecast data from grid.

        Returns:
            DetailedForecast: Object with all forecast details for all available times.
        """
        if self.wfo is None:
            await self.get_points()
        if self.wfo is None or self.x is None or self.y is None:
            raise NwsError("Error retrieving points")
        raw_forecast = await raw_detailed_forecast(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return DetailedForecast(raw_forecast["properties"])

    async def get_gridpoints_forecast(self: Nws) -> Dict[str, Any]:
        """Return daily forecast from grid."""
        if self.wfo is None:
            await self.get_points()
        if self.wfo is None or self.x is None or self.y is None:
            raise NwsError("Error retrieving points")
        raw_forecast = await raw_gridpoints_forecast(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return raw_forecast["properties"]

    async def get_gridpoints_forecast_hourly(self: Nws) -> Dict[str, Any]:
        """Return hourly forecast from grid."""
        if self.wfo is None:
            await self.get_points()
        if self.wfo is None or self.x is None or self.y is None:
            raise NwsError("Error retrieving points")
        raw_forecast = await raw_gridpoints_forecast_hourly(
            self.wfo, self.x, self.y, self.session, self.userid
        )
        return raw_forecast["properties"]

    async def get_alerts_active_zone(self: Nws, zone: str) -> List[Dict[str, Any]]:
        """Returns alerts dict for zone."""
        alerts = await raw_alerts_active_zone(zone, self.session, self.userid)
        return [alert["properties"] for alert in alerts["features"]]

    async def get_alerts_forecast_zone(self: Nws) -> List[Dict[str, Any]]:
        """Returns alerts dict for forecast zone."""
        if self.forecast_zone is None:
            await self.get_points()
        if self.forecast_zone is None:
            raise NwsError("Error retrieving points")
        return await self.get_alerts_active_zone(self.forecast_zone)

    async def get_alerts_county_zone(self: Nws) -> List[Dict[str, Any]]:
        """Returns alerts dict for county zone."""
        if self.county_zone is None:
            await self.get_points()
        if self.county_zone is None:
            raise NwsError("Error retrieving points")
        return await self.get_alerts_active_zone(self.county_zone)

    async def get_alerts_fire_weather_zone(self: Nws) -> List[Dict[str, Any]]:
        """Returns alerts dict for fire weather zone."""
        if self.fire_weather_zone is None:
            await self.get_points()
        if self.fire_weather_zone is None:
            raise NwsError("Error retrieving points")
        return await self.get_alerts_active_zone(self.fire_weather_zone)
