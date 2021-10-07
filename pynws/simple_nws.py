"""Support for NWS weather service."""
from datetime import datetime, timedelta, timezone
from statistics import mean

from metar import Metar

from .const import ALERT_ID, API_WEATHER_CODE
from .nws import Nws

WIND_DIRECTIONS = [
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


def unchanged(value):
    """Return same value."""
    return value


def f_to_c(fahrenheit):
    """Convert to Celsius."""
    return (fahrenheit - 32.0) / 1.8


def m_p_s_to_km_p_hr(m_p_s):
    """Convert to km/hr."""
    return m_p_s * 3.6


unit_conversion = {
    "degC": unchanged,
    "degF": f_to_c,
    "km_h-1": unchanged,
    "m_s-1": m_p_s_to_km_p_hr,
    "m": unchanged,
    "Pa": unchanged,
    "percent": unchanged,
    "degree_(angle)": unchanged,
}

WIND = {name: idx * 360 / 16 for idx, name in enumerate(WIND_DIRECTIONS)}

OBSERVATIONS = {
    "temperature": ["temp", "C", None],
    "barometricPressure": None,
    "seaLevelPressure": ["press", "HPA", 100],
    "relativeHumidity": None,
    "windSpeed": ["wind_speed", "MPS", 3.6],
    "windDirection": ["wind_dir", None, None],
    "visibility": ["vis", "M", None],
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


def convert_unit(unit_code, value):
    """Convert value with unit code to preferred unit."""
    for unit, converter in unit_conversion.items():
        if unit in unit_code:
            return converter(value)
    raise ValueError(f"unit code: '{unit_code}' not recognized.")


def convert_weather(weather):
    """Convert short code to readable name."""
    return [(API_WEATHER_CODE.get(w[0], w[0]), w[1]) for w in weather]


def parse_icon(icon):
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
    return time, tuple(zip(code, chance))


class SimpleNWS(Nws):
    """
    NWS simplified data.

    Uses normal api first.  If value is None, use metar info.

    By default, forecasts that end before now will be filtered out.
    """

    def __init__(self, lat, lon, api_key, session, filter_forecast=True):
        """Set up simplified NWS class."""
        super().__init__(session, api_key, (lat, lon))

        self.filter_forecast = filter_forecast
        self._observation = None
        self._metar_obs = None
        self.station = None
        self.stations = None
        self._forecast = None
        self._forecast_hourly = None
        self._alerts_forecast_zone = []
        self._alerts_county_zone = []
        self._alerts_fire_weather_zone = []
        self._alerts_all_zones = []
        self._all_zones = []

    async def set_station(self, station=None):
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
    def extract_metar(obs):
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

    async def update_observation(self, limit=0, start_time=None):
        """Update observation."""
        obs = await self.get_stations_observations(limit, start_time=start_time)
        if obs is None:
            return None
        self._observation = sorted(
            obs,
            key=lambda item: self.extract_observation_value(item, "timestamp"),
            reverse=True,
        )
        self._metar_obs = [self.extract_metar(iobs) for iobs in self._observation]

    async def update_forecast(self):
        """Update forecast."""
        self._forecast = await self.get_gridpoints_forecast()

    async def update_forecast_hourly(self):
        """Update forecast hourly."""
        self._forecast_hourly = await self.get_gridpoints_forecast_hourly()

    @staticmethod
    def _unique_alert_ids(alerts):
        """Return set of unique alert_ids."""
        return {alert[ALERT_ID] for alert in alerts}

    def _new_alerts(self, alerts, current_alerts):
        """Return new alerts."""
        current_alert_ids = self._unique_alert_ids(current_alerts)
        return [alert for alert in alerts if alert[ALERT_ID] not in current_alert_ids]

    async def update_alerts_forecast_zone(self):
        """Update alerts zone."""
        alerts = await self.get_alerts_forecast_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_forecast_zone)
        self._alerts_forecast_zone = alerts
        return new_alerts

    async def update_alerts_county_zone(self):
        """Update alerts zone."""
        alerts = await self.get_alerts_county_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_county_zone)
        self._alerts_county_zone = alerts
        return new_alerts

    async def update_alerts_fire_weather_zone(self):
        """Update alerts zone."""
        alerts = await self.get_alerts_fire_weather_zone()
        new_alerts = self._new_alerts(alerts, self._alerts_fire_weather_zone)
        self._alerts_fire_weather_zone = alerts
        return new_alerts

    async def update_alerts_all_zones(self):
        """Update all alerts zones."""
        if not self.forecast_zone or not self.county_zone:
            await self.get_points()
        if not self._all_zones:
            self._all_zones = {
                self.forecast_zone,
                self.county_zone,
                self.fire_weather_zone,
            }
        alerts_data = [
            await self.get_alerts_active_zone(zone) for zone in self._all_zones
        ]

        alerts = []
        for alert_list in alerts_data:
            for alert in alert_list:
                if alert["id"] not in self._unique_alert_ids(alerts):
                    alerts.append(alert)

        new_alerts = self._new_alerts(alerts, self._alerts_all_zones)
        self._alerts_all_zones = alerts
        return new_alerts

    @property
    def all_zones(self):
        """All alert zones."""
        return self._all_zones

    @staticmethod
    def extract_observation_value(observation, value):
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
    def observation(self):
        """Observation dict"""

        if self._observation is None or self._observation == []:
            return None

        data = {}
        for obs, met in OBSERVATIONS.items():
            obs_list = [
                self.extract_observation_value(o, obs) for o in self._observation
            ]
            obs_item = next(iter([o for o in obs_list if o]), None)
            if isinstance(obs_item, tuple):
                data[obs] = convert_unit(obs_item[1], obs_item[0])
            else:
                data[obs] = obs_item

            if data[obs] is None and (
                met is not None and self._metar_obs[0] is not None
            ):
                met_prop = getattr(self._metar_obs[0], met[0])
                if met_prop:
                    if met[1]:
                        data[obs] = met_prop.value(units=met[1])
                    else:
                        data[obs] = met_prop.value()
                    if met[2] is not None:
                        data[obs] = data[obs] * met[2]
        if data.get("icon"):
            time, weather = parse_icon(data["icon"])
            data["iconTime"] = time
            data["iconWeather"] = convert_weather(weather)
        else:
            data["iconTime"] = None
            data["iconWeather"] = None
        return data

    @property
    def forecast(self):
        """Return forecast."""
        return self._convert_forecast(self._forecast, self.filter_forecast)

    @property
    def forecast_hourly(self):
        """Return forecast hourly."""
        return self._convert_forecast(self._forecast_hourly, self.filter_forecast)

    @staticmethod
    def _convert_forecast(input_forecast, filter_forecast):
        """Converts forecast to common dict."""
        if not input_forecast:
            return []
        forecast = []
        for forecast_entry in input_forecast:
            # get weather
            if filter_forecast:
                end_time = forecast_entry.get("endTime")
                if not end_time:
                    continue
                # needed for python 3.6
                # https://stackoverflow.com/questions/30999230/how-to-parse-timezone-with-colon
                if end_time[-3] == ":":
                    end_time = end_time[:-3] + end_time[-2:]
                if datetime.now(timezone.utc) - datetime.strptime(
                    end_time, "%Y-%m-%dT%H:%M:%S%z"
                ) > timedelta(seconds=0):
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
    def alerts_forecast_zone(self):
        """Return alerts as a list of dict."""
        return self._alerts_forecast_zone

    @property
    def alerts_county_zone(self):
        """Return alerts as a list of dict."""
        return self._alerts_county_zone

    @property
    def alerts_fire_weather_zone(self):
        """Return alerts as a list of dict."""
        return self._alerts_fire_weather_zone

    @property
    def alerts_all_zones(self):
        """Return alerts as a list of dict."""
        return self._alerts_all_zones
