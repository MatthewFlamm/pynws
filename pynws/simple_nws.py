"""Support for NWS weather service."""
from statistics import mean

from metar import Metar

from .nws import Nws
from .const import API_WEATHER_CODE

WIND_DIRECTIONS = ['N', 'NNE', 'NE', 'ENE',
                   'E', 'ESE', 'SE', 'SSE',
                   'S', 'SSW', 'SW', 'WSW',
                   'W', 'WNW', 'NW', 'NNW']

WIND = {name: idx * 360 / 16 for idx, name in enumerate(WIND_DIRECTIONS)}

OBSERVATIONS = {
    'temperature': ['temp', 'C', None],
    'barometricPressure': None,
    'seaLevelPressure': ['press', 'HPA', 100],
    'relativeHumidity': None,
    'windSpeed': ['wind_speed', 'MPS', None],
    'windDirection': ['wind_dir', None, None],
    'visibility': ['vis', 'M', None],
    'elevation': None,
    'textDescription': None,
    'dewpoint': None,
    'windGust': None,
    'station': None,
    'timestamp': None,
    'icon': None,
    'maxTemperatureLast24Hours': None,
    'minTemperatureLast24Hours': None,
    'precipitationLastHour': None,
    'precipitationLast3Hours': None,
    'precipitationLast6Hours': None,
    'windChill': None,
    'heatIndex': None,
}

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
    icon_list = icon.split('/')
    time = icon_list[5]
    weather = [i.split('?')[0] for i in icon_list[6:]]
    code = [w.split(',')[0] for w in weather]
    chance = [int(w.split(',')[1]) if len(w.split(',')) == 2 else None
              for w in weather]
    return time, tuple(zip(code, chance))


class SimpleNWS:
    """
    NWS simplified data.

    Uses normal api first.  If value is None, use metar info.
    """
    def __init__(self, lat, lon, api_key, session):
        """Set up simplified NWS class."""
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.session = session
        self.nws = Nws(session, latlon=(float(lat), float(lon)),
                       userid=api_key)

        self._observation = None
        self._metar_obs = None
        self.station = None
        self.stations = None
        self._forecast = None
        self._forecast_hourly = None
        self._alerts_zone = None

    async def set_station(self, station=None):
        """
        Set station or retrieve station list.
        If no station is supplied, the first retrieved value is set.
        """
        if station:
            self.nws.station = station
            self.station = station
            self.stations = [self.station]
        else:
            self.stations = await self.nws.stations()
            self.nws.station = self.stations[0]
            self.station = self.stations[0]

    @staticmethod
    def extract_metar(obs):
        """Return parsed metar if available."""
        metar_msg = obs.get('rawMessage')
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
        obs = await self.nws.observations(limit, start_time=start_time)
        if obs is None:
            return None
        self._observation = obs
        self._metar_obs = [self.extract_metar(iobs) for iobs in self._observation]

    async def update_forecast(self):
        """Update forecast."""
        self._forecast = await self.nws.grid_forecast()

    async def update_forecast_hourly(self):
        """Update forecast."""
        self._forecast_hourly = await self.nws.grid_forecast_hourly()

    async def update_alerts_zone(self):
        """Update alerts zone."""
        self._alerts_zone = await self.nws.alerts_zone()

    @staticmethod
    def extract_observation_value(observation, value):
        """Returns observation or observation value."""
        obs_value = observation.get(value)
        if obs_value is None:
            return None
        if isinstance(observation[value], dict):
            return observation[value].get('value')
        return observation[value]

    @property
    def observation(self):
        """Observation dict"""

        if self._observation is None:
            return None

        data = {}
        for obs, met in OBSERVATIONS.items():
            obs_list = [self.extract_observation_value(o, obs) for o in self._observation]
            data[obs] = next(iter([o for o in obs_list if o]), None)
            if data[obs] is None and (met is not None
                                      and self._metar_obs[0] is not None):
                met_prop = getattr(self._metar_obs[0], met[0])
                if met_prop:
                    if met[1]:
                        data[obs] = met_prop.value(units=met[1])
                    else:
                        data[obs] = met_prop.value()
                    if met[2] is not None:
                        data[obs] = data[obs] * met[2]
        if data.get('icon'):
            time, weather = parse_icon(data['icon'])
            data['iconTime'] = time
            data['iconWeather'] = convert_weather(weather)
        else:
            data['iconTime'] = None
            data['iconWeather'] = None
        return data

    @property
    def forecast(self):
        """Return forecast."""
        return self._convert_forecast(self._forecast)

    @property
    def forecast_hourly(self):
        """Return forecast hourly."""
        return self._convert_forecast(self._forecast_hourly)

    @staticmethod
    def _convert_forecast(input_forecast):
        """Converts forecast to common dict."""
        if not input_forecast:
            return []
        forecast = []
        for forecast_entry in input_forecast:
            # get weather
            if forecast_entry.get('icon'):
                time, weather = parse_icon(forecast_entry['icon'])
                weather = convert_weather(weather)
            else:
                time, weather = (None, None)
            forecast_entry['iconTime'] = time
            forecast_entry['iconWeather'] = weather
            if forecast_entry.get('windDirection'):
                forecast_entry['windBearing'] = \
                    WIND[forecast_entry['windDirection']]
            else:
                forecast_entry['windBearing'] = None

            # wind speed reported as '7 mph' or '7 to 10 mph'
            # if range, take average
            if forecast_entry.get('windSpeed'):
                wind_speed = forecast_entry['windSpeed'].split(' ')[0::2]
                wind_speed_avg = mean(int(w) for w in wind_speed)
                forecast_entry['windSpeedAvg'] = wind_speed_avg
            else:
                forecast_entry['windSpeedAvg'] = None

            forecast.append(forecast_entry)
        return forecast

    @property
    def alerts_zone(self):
        """Return alerts as a list of dict."""
        return self._alerts_zone
