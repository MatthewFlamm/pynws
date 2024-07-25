"""Support for NWS weather service."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    from datetime import timedelta

from aiohttp import ClientResponseError, ClientSession
from metar import Metar
from yarl import URL

from .const import ALERT_ID, API_WEATHER_CODE, Final, MetadataKeys
from .forecast import DetailedForecast
from .nws import Nws, NwsError, NwsNoDataError
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


def _nws_retry_func(retry_no_data: bool):
    """
    Return function used for tenacity.retry.

    Retry if:
        - if error is ClientResponseError and has a 5xx status.
        - if error is NwsNoDataError, the behavior is determined by retry_no_data

    Parameters
    ----------
    retry_no_data : bool
        Whether to retry when `NwsNoDataError` is raised.

    """

    def _retry(error: BaseException) -> bool:
        """Whether to retry based on execptions."""
        if isinstance(error, ClientResponseError) and error.status >= 500:
            return True
        return bool(retry_no_data) and isinstance(error, NwsNoDataError)

    return _retry


def _setup_retry_func(
    func: Callable[[Any, Any], Awaitable[Any]],
    interval: Union[float, timedelta],
    stop: Union[float, timedelta],
    *,
    retry_no_data=False,
) -> Callable[..., Awaitable[Any]]:
    from tenacity import retry, retry_if_exception, stop_after_delay, wait_fixed

    retry_func = _nws_retry_func(retry_no_data=retry_no_data)

    return retry(
        reraise=True,
        wait=wait_fixed(interval),
        stop=stop_after_delay(stop),
        retry=retry_if_exception(retry_func),
    )(func)


async def call_with_retry(
    func: Callable[[Any, Any], Awaitable[Any]],
    interval: Union[float, timedelta],
    stop: Union[float, timedelta],
    /,
    *args,
    retry_no_data=False,
    **kwargs,
) -> Callable[[Any, Any], Awaitable[Any]]:
    """Call an update function with retries.

    Parameters
    ----------
    func : Callable
        An awaitable coroutine to retry.
    interval : float, datetime.datetime.timedelta
        Time interval for retry.
    stop : float, datetime.datetime.timedelta
        Time interval to stop retrying.
    retry_no_data : bool
         Whether to retry when no data is returned.
    args : Any
        Positional args to pass to func.
    kwargs : Any
        Keyword args to pass to func.
    """
    retried_func = _setup_retry_func(func, interval, stop, retry_no_data=retry_no_data)
    return await retried_func(*args, raise_no_data=retry_no_data, **kwargs)


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
    icon_url = URL(icon)
    icon_parts = icon_url.parts
    time = icon_parts[3]
    weather = icon_parts[4:]
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
        self._metar_obs: Optional[List[Optional[Metar.Metar]]] = None
        self.station: Optional[str] = None
        self.stations: Optional[List[str]] = None
        self._forecast: Optional[List[Dict[str, Any]]] = None
        self._forecast_metadata: Dict[str, str | None] = {}
        self._forecast_hourly: Optional[List[Dict[str, Any]]] = None
        self._forecast_hourly_metadata: Dict[str, str | None] = {}
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
            if not self.stations:
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
        self: SimpleNWS,
        limit: int = 0,
        start_time: Optional[datetime] = None,
        *,
        raise_no_data: bool = False,
    ) -> None:
        """Update observation."""
        obs = await self.get_stations_observations(limit, start_time=start_time)
        if obs:
            self._observation = obs
            self._metar_obs = [self.extract_metar(iobs) for iobs in self._observation]
        elif raise_no_data:
            raise NwsNoDataError("Observation received with no data.")

    async def update_forecast(self: SimpleNWS, *, raise_no_data: bool = False) -> None:
        """Update forecast."""
        forecast_with_metadata = await self.get_gridpoints_forecast()
        forecast = forecast_with_metadata["periods"]
        if self._filter_forecast(forecast):
            self._forecast = forecast
            self._forecast_metadata = {
                metadataKey: forecast_with_metadata.get(metadataKey)
                for metadataKey in MetadataKeys
            }
        elif raise_no_data:
            raise NwsNoDataError("Forecast received with no data.")

    async def update_forecast_hourly(
        self: SimpleNWS, *, raise_no_data: bool = False
    ) -> None:
        """Update forecast hourly."""
        forecast_hourly_with_metadata = await self.get_gridpoints_forecast_hourly()
        forecast_hourly = forecast_hourly_with_metadata["periods"]
        if self._filter_forecast(forecast_hourly):
            self._forecast_hourly = forecast_hourly
            self._forecast_hourly_metadata = {
                metadataKey: forecast_hourly_with_metadata.get(metadataKey)
                for metadataKey in MetadataKeys
            }
        elif raise_no_data:
            raise NwsNoDataError("Forecast hourly received with no data.")

    async def update_detailed_forecast(
        self: SimpleNWS, *, raise_no_data: bool = False
    ) -> None:
        """Update forecast.

        Note:
        `raise_no_data`currently can only be set to `False`.
        """
        if raise_no_data:
            raise NotImplementedError(
                "raise_no_data=True not implemented for update_detailed_forecast"
            )

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

    async def update_alerts_forecast_zone(
        self: SimpleNWS, *, raise_no_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Update alerts zone.

        Note:
        `raise_no_data`currently can only be set to `False`.
        """
        if raise_no_data:
            raise NotImplementedError(
                "raise_no_data=True not implemented for update_alerts_forecast_zone"
            )
        alerts = await self.get_alerts_forecast_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_forecast_zone)
        self._alerts_forecast_zone = alerts
        return new_alerts

    async def update_alerts_county_zone(
        self: SimpleNWS, *, raise_no_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Update alerts zone.

        Note:
        `raise_no_data`currently can only be set to `False`.
        """
        if raise_no_data:
            raise NotImplementedError(
                "raise_no_data=True not implemented for update_alerts_county_zone"
            )
        alerts = await self.get_alerts_county_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_county_zone)
        self._alerts_county_zone = alerts
        return new_alerts

    async def update_alerts_fire_weather_zone(
        self: SimpleNWS, *, raise_no_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Update alerts zone.

        Note:
        `raise_no_data`currently can only be set to `False`.
        """
        if raise_no_data:
            raise NotImplementedError(
                "raise_no_data=True not implemented for update_alerts_fire_weather_zone"
            )
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
    def extract_value(
        values: Dict[str, Any], key: str
    ) -> Union[None, Tuple[float, Any], str]:
        """Returns observation or observation value."""
        value = values.get(key)
        if value is None:
            return None
        if isinstance(value, dict):
            sub_value = value.get("value")
            if sub_value is None:
                return None
            return float(sub_value), value.get("unitCode")
        return value

    @property
    def observation(self: SimpleNWS) -> Optional[Dict[str, Any]]:
        """Observation dict"""

        if self._observation is None or self._observation == []:
            return None

        data: Dict[str, Any] = {}
        for obs, metar_param in OBSERVATIONS.items():
            obs_list = [self.extract_value(o, obs) for o in self._observation]
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
    def forecast(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return forecast."""
        forecast = self._filter_forecast(self._forecast)
        return self._convert_forecast(forecast)

    @property
    def forecast_metadata(self: SimpleNWS) -> Dict[str, str | None]:
        """Return forecast metadata."""
        return self._forecast_metadata

    @property
    def forecast_hourly(self: SimpleNWS) -> List[Dict[str, Any]]:
        """Return forecast hourly."""
        forecast = self._filter_forecast(self._forecast_hourly)
        return self._convert_forecast(forecast)

    @property
    def forecast_hourly_metadata(self: SimpleNWS) -> Dict[str, str | None]:
        """Return forecast hourly metadata."""
        return self._forecast_hourly_metadata

    @property
    def detailed_forecast(self: SimpleNWS) -> Optional[DetailedForecast]:
        """Return detailed forecast.

        Returns:
            Optional[DetailedForecast]: Returns None if update_detailed_forecast
            hasn't been called.
        """
        return self._detailed_forecast

    def _filter_forecast(
        self: SimpleNWS,
        input_forecast: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        if not input_forecast:
            return []
        if not self.filter_forecast:
            return input_forecast
        forecast: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)
        for forecast_entry in input_forecast:
            end_time = forecast_entry.get("endTime")
            if not end_time or now > datetime.fromisoformat(end_time):
                continue
            forecast.append(forecast_entry)
        return forecast

    @staticmethod
    def _convert_forecast(
        input_forecast: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Converts forecast to common dict."""
        forecast = []
        for forecast_entry in input_forecast:
            if (value := forecast_entry.get("temperature")) is not None:
                forecast_entry["temperature"] = int(value)

            temp_unit = forecast_entry.get("temperatureUnit")

            for key in ("probabilityOfPrecipitation", "dewpoint", "relativeHumidity"):
                extracted = SimpleNWS.extract_value(forecast_entry, key)
                if isinstance(extracted, tuple):
                    value, value_unit = extracted
                    if value_unit.endswith("degC") and temp_unit == "F":
                        value = round(float(value) * 1.8 + 32, 0)
                    elif value_unit.endswith("degF") and temp_unit == "C":
                        value = round((float(value) - 32) / 1.8, 0)
                    forecast_entry[key] = int(value)
                else:
                    forecast_entry[key] = extracted

            if forecast_entry["probabilityOfPrecipitation"] is None:
                forecast_entry["probabilityOfPrecipitation"] = 0

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
