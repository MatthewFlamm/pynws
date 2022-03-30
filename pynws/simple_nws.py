"""Support for NWS weather service."""
from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple, Union

from aiohttp import ClientSession
from metar import Metar

from .const import ALERT_ID, API_WEATHER_CODE, Final
from .forecast import DetailedForecast
from .nws import Nws, NwsError
from .units import convert_unit

WIND_DIRECTIONS: Final = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]


WIND: Final = {name: idx * 360 / 16 for idx, name in enumerate(WIND_DIRECTIONS)}


class MetarParam(NamedTuple):
    """METAR conversion parameter"""

    attr: str
    units: Optional[str] = None
    multiplier: Optional[float] = None


OBSERVATIONS: Final[Dict[str, Optional[MetarParam]]] = {
    "temperature": MetarParam("temp", "C"),
    "barometricPressure": None,
    "seaLevelPressure": MetarParam("press", "HPA", 100.0),
    "relativeHumidity": None,
    "windSpeed": MetarParam("wind_speed", "MPS", 3.6),
    "windDirection": MetarParam("wind_dir"),
    "visibility": MetarParam("vis", "M"),
    "elevation": None,
    "textDescription": None,
    "dewpoint": None,
    "windGust": None,
    "station": None,
    "timestamp": None,
    "icon": None,
    "maxTemperatureLast24Hours": None,
    "minTemperatureLast24Hours": None,
    "precipitationLastHour": None,
    "precipitationLast3Hours": None,
    "precipitationLast6Hours": None,
    "windChill": None,
    "heatIndex": None,
}

_WeatherCodes = List[Tuple[str, Optional[int]]]


def convert_weather(weather: _WeatherCodes) -> _WeatherCodes:
    """Convert short code to readable name."""
    return [(API_WEATHER_CODE.get(w[0], w[0]), w[1]) for w in weather]


def parse_icon(icon: str) -> Tuple[str, _WeatherCodes]:
    """
    Parse icon url to NWS weather codes.

    Example:
    https://api.weather.gov/icons/land/day/skc/tsra,40?size=medium

    Example return:
    ('day', (('skc', None), ('tsra', 40),))
    """
    icon_list = icon.split("/")
    time = icon_list[5]
    weather = [i.split("?")[0] for i in icon_list[6:]]
    code = [w.split(",")[0] for w in weather]
    chance = [int(w.split(",")[1]) if len(w.split(",")) == 2 else None for w in weather]
    return time, list(zip(code, chance))


class SimpleNWS(Nws):
    """
    NWS simplified data.

    Uses normal api first.  If value is None, use metar info.

    By default, forecasts that end before now will be filtered out.
    """

    def __init__(
        self: SimpleNWS,
        lat: float,
        lon: float,
        api_key: str,
        session: ClientSession,
        filter_forecast: bool = True,
    ):
        """Set up simplified NWS class."""
        super().__init__(session, api_key, (lat, lon))

        self.filter_forecast = filter_forecast
        self._observation: Optional[List[Dict[str, Any]]] = None
        self._metar_obs: Optional[List[Metar.Metar]] = None
        self.station: Optional[str] = None
        self.stations: Optional[List[str]] = None
        self._forecast: Optional[List[Dict[str, Any]]] = None
        self._forecast_hourly: Optional[List[Dict[str, Any]]] = None
        self._detailed_forecast: Optional[DetailedForecast] = None
        self._alerts_forecast_zone: List[Dict[str, Any]] = []
        self._alerts_county_zone: List[Dict[str, Any]] = []
        self._alerts_fire_weather_zone: List[Dict[str, Any]] = []
        self._alerts_all_zones: List[Dict[str, Any]] = []
        self._all_zones: List[str] = []

    async def set_station(self: SimpleNWS, station: Optional[str] = None) -> None:
        """
        Set station or retrieve station list.
        If no station is supplied, the first retrieved value is set.
        """
        if station:
            self.station = station
            if not self.stations:
                self.stations = [self.station]
        else:
            self.stations = await self.get_points_stations()
            self.station = self.stations[0]

    @staticmethod
    def extract_metar(obs: Dict[str, Any]) -> Optional[Metar.Metar]:
        """Return parsed metar if available."""
        metar_msg = obs.get("rawMessage")
        if metar_msg:
            try:
                metar_obs = Metar.Metar(metar_msg)
            except Metar.ParserError:
                metar_obs = None
        else:
            metar_obs = None
        return metar_obs

    async def update_observation(
        self: SimpleNWS, limit: int = 0, start_time: Optional[datetime] = None
    ) -> None:
        """Update observation."""
        obs = await self.get_stations_observations(limit, start_time=start_time)
        if obs:
            self._observation = obs
            self._metar_obs = [self.extract_metar(iobs) for iobs in self._observation]

    async def update_forecast(self: SimpleNWS) -> None:
        """Update forecast."""
        self._forecast = await self.get_gridpoints_forecast()

    async def update_forecast_hourly(self: SimpleNWS) -> None:
        """Update forecast hourly."""
        self._forecast_hourly = await self.get_gridpoints_forecast_hourly()

    async def update_detailed_forecast(self: SimpleNWS) -> None:
        """Update forecast."""
        self._detailed_forecast = await self.get_detailed_forecast()

    @staticmethod
    def _unique_alert_ids(alerts: List[Dict[str, Any]]) -> Set[str]:
        """Return set of unique alert_ids."""
        return {alert[ALERT_ID] for alert in alerts}

    def _new_alerts(
        self: SimpleNWS,
        alerts: List[Dict[str, Any]],
        current_alerts: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Return new alerts."""
        current_alert_ids = self._unique_alert_ids(current_alerts)
        return [alert for alert in alerts if alert[ALERT_ID] not in current_alert_ids]

    async def update_alerts_forecast_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Update alerts zone."""
        alerts = await self.get_alerts_forecast_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_forecast_zone)
        self._alerts_forecast_zone = alerts
        return new_alerts

    async def update_alerts_county_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Update alerts zone."""
        alerts = await self.get_alerts_county_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_county_zone)
        self._alerts_county_zone = alerts
        return new_alerts

    async def update_alerts_fire_weather_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Update alerts zone."""
        alerts = await self.get_alerts_fire_weather_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_fire_weather_zone)
        self._alerts_fire_weather_zone = alerts
        return new_alerts

    async def update_alerts_all_zones(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Update all alerts zones."""
        if not self.forecast_zone:
            await self.get_points()
        if not self.forecast_zone:
            raise NwsError("Forecast zone is missing")
        if not self._all_zones:
            # Use Set[str] to de-dupe zones
            zones_set = {self.forecast_zone, self.county_zone, self.fire_weather_zone}
            self._all_zones = [zone for zone in zones_set if zone]
        alerts_data = [
            await self.get_alerts_active_zone(zone) for zone in self._all_zones
        ]

        alerts: List[Dict[str, Any]] = []
        for alert_list in alerts_data:
            for alert in alert_list:
                if alert["id"] not in self._unique_alert_ids(alerts):
                    alerts.append(alert)

        new_alerts = self._new_alerts(alerts, self._alerts_all_zones)
        self._alerts_all_zones = alerts
        return new_alerts

    @property
    def all_zones(self: SimpleNWS) -> List[str]:
        """All alert zones."""
        return self._all_zones

    @staticmethod
    def extract_observation_value(
        observation: Dict[str, Any], value: str
    ) -> Union[None, Tuple[float, str], str]:
        """Returns observation or observation value."""
        obs_value = observation.get(value)
        if obs_value is None:
            return None
        if isinstance(observation[value], dict):
            obs_sub_value = observation[value].get("value")
            if obs_sub_value is None:
                return None
            return float(obs_sub_value), observation[value].get("unitCode")
        return observation[value]

    @property
    def observation(self: SimpleNWS) -> Optional[Dict[str, Any]]:
        """Observation dict"""

        if self._observation is None or self._observation == []:
            return None

        data: Dict[str, Any] = {}
        for obs, metar_param in OBSERVATIONS.items():
            obs_list = [
                self.extract_observation_value(o, obs) for o in self._observation
            ]
            obs_item = next(iter([o for o in obs_list if o]), None)
            if isinstance(obs_item, tuple):
                data[obs] = convert_unit(obs_item[1], obs_item[0])
            else:
                data[obs] = obs_item

            if (
                data[obs] is None
                and metar_param is not None
                and self._metar_obs is not None
                and self._metar_obs[0] is not None
            ):
                met_prop = getattr(self._metar_obs[0], metar_param.attr)
                if met_prop:
                    if metar_param.units:
                        data[obs] = met_prop.value(units=metar_param.units)
                    else:
                        data[obs] = met_prop.value()
                    if metar_param.multiplier is not None:
                        data[obs] = data[obs] * metar_param.multiplier

        if data.get("icon"):
            time, weather = parse_icon(data["icon"])
            data["iconTime"] = time
            data["iconWeather"] = convert_weather(weather)
        else:
            data["iconTime"] = None
            data["iconWeather"] = None
        return data

    @property
    def forecast(self: SimpleNWS) -> Optional[List[Dict[str, Any]]]:
        """Return forecast."""
        return self._convert_forecast(self._forecast, self.filter_forecast)

    @property
    def forecast_hourly(self: SimpleNWS) -> Optional[List[Dict[str, Any]]]:
        """Return forecast hourly."""
        return self._convert_forecast(self._forecast_hourly, self.filter_forecast)

    @property
    def detailed_forecast(self: SimpleNWS) -> Optional[DetailedForecast]:
        """Return detailed forecast.

        Returns:
            Optional[DetailedForecast]: Returns None if update_detailed_forecast
            hasn't been called.
        """
        return self._detailed_forecast

    @staticmethod
    def _convert_forecast(
        input_forecast: Optional[List[Dict[str, Any]]],
        filter_forecast: bool,
    ) -> List[Dict[str, Any]]:
        """Converts forecast to common dict."""
        if not input_forecast:
            return []
        forecast = []
        now = datetime.now(timezone.utc)
        for forecast_entry in input_forecast:
            # get weather
            if filter_forecast:
                end_time = forecast_entry.get("endTime")
                if not end_time:
                    continue
                if now > datetime.fromisoformat(end_time):
                    continue
            if forecast_entry.get("temperature"):
                forecast_entry["temperature"] = int(forecast_entry["temperature"])

            if forecast_entry.get("icon"):
                time, weather = parse_icon(forecast_entry["icon"])
                weather = convert_weather(weather)
            else:
                time, weather = (None, None)
            forecast_entry["iconTime"] = time
            forecast_entry["iconWeather"] = weather
            if forecast_entry.get("windDirection"):
                forecast_entry["windBearing"] = WIND[forecast_entry["windDirection"]]
            else:
                forecast_entry["windBearing"] = None

            # wind speed reported as '7 mph' or '7 to 10 mph'
            # if range, take average
            if forecast_entry.get("windSpeed"):
                wind_speed = forecast_entry["windSpeed"].split(" ")[0::2]
                wind_speed_avg = mean(int(w) for w in wind_speed)
                forecast_entry["windSpeedAvg"] = wind_speed_avg
            else:
                forecast_entry["windSpeedAvg"] = None

            forecast.append(forecast_entry)
        return forecast

    @property
    def alerts_forecast_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return alerts as a list of dict."""
        return self._alerts_forecast_zone

    @property
    def alerts_county_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return alerts as a list of dict."""
        return self._alerts_county_zone

    @property
    def alerts_fire_weather_zone(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return alerts as a list of dict."""
        return self._alerts_fire_weather_zone

    @property
    def alerts_all_zones(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return alerts as a list of dict."""
        return self._alerts_all_zones
