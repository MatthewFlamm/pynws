"""Support for NWS weather service."""
from statistics import mean

from metar.Metar import Metar

from .nws import Nws
from .const import API_WEATHER_CODE

WIND_DIRECTIONS = ['N', 'NNE', 'NE', 'ENE',
                   'E', 'ESE', 'SE', 'SSE',
                   'S', 'SSW', 'SW', 'WSW',
                   'W', 'WNW', 'NW', 'NNW']

WIND = {name: idx * 360 / 16 for idx, name in enumerate(WIND_DIRECTIONS)}


def convert_weather(weather):
    """Convert short code to readable name."""
    return [(API_WEATHER_CODE.get(w[0], w[0]), w[1]) for w in weather]


def parse_icon(icon):
    """
    Parse icon url to NWS weather codes.

    Example:
    https://api.weather.gov/icons/land/day/skc/tsra,40?size=medium

    Example return:
    ('day', (('skc', 0), ('tsra', 40),))
    """
    icon_list = icon.split('/')
    time = icon_list[5]
    weather = [i.split('?')[0] for i in icon_list[6:]]
    code = [w.split(',')[0] for w in weather]
    chance = [int(w.split(',')[1]) if len(w.split(',')) == 2 else 0
              for w in weather]
    return time, tuple(zip(code, chance))


class SimpleNWS:
    """
    NWS simplified data.

    Uses normal api first.  If value is None, use metar info.
    """
    def __init__(self, lat, lon, api_key, mode, session):
        """Set up simplified NWS class."""
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.session = session
        self.nws = Nws(session, latlon=(float(lat), float(lon)),
                       userid=api_key)
        self.mode = mode

        self.observation = None
        self.metar_obs = None
        self.station = None
        self.stations = None
        self._forecast = None

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

    async def update_observation(self):
        """Update observation."""

        obs = await self.nws.observations(limit=1)
        if obs is None:
            return None
        self.observation = obs[0]
        metar_msg = self.observation.get('rawMessage')
        if metar_msg:
            self.metar_obs = Metar(metar_msg)
        else:
            self.metar_obs = None

    async def update_forecast(self):
        """Update forecast."""
        if self.mode == 'daynight':
            forecast = await self.nws.forecast()
        elif self.mode == 'hourly':
            forecast = await self.nws.forecast_hourly()
        self._forecast = forecast

    @property
    def temperature(self):
        """Return the current temperature in F."""
        temp_c = None
        if self.observation:
            temp_c = self.observation.get('temperature', {}).get('value')
        if temp_c is None and self.metar_obs and self.metar_obs.temp:
            temp_c = self.metar_obs.temp.value(units='C')
        return temp_c

    @property
    def pressure(self):
        """Return the current pressure in inHg."""
        pressure_pa = None
        if self.observation:
            pressure_pa = self.observation.get('seaLevelPressure',
                                               {}).get('value')

        if pressure_pa is None and self.metar_obs and self.metar_obs.press:
            pressure_hpa = self.metar_obs.press.value(units='HPA')
            if pressure_hpa:
                pressure_pa = pressure_hpa * 100
        return pressure_pa

    @property
    def humidity(self):
        """Return the humidity in %."""
        humidity = None
        if self.observation:
            humidity = self.observation.get('relativeHumidity',
                                            {}).get('value')
        return humidity

    @property
    def wind_speed(self):
        """Return the current windspeed in mph."""
        wind_m_s = None
        if self.observation:
            wind_m_s = self.observation.get('windSpeed', {}).get('value')
        if wind_m_s is None and self.metar_obs and self.metar_obs.wind_speed:
            wind_m_s = self.metar_obs.wind_speed.value(units='MPS')
        return wind_m_s

    @property
    def wind_bearing(self):
        """Return the current wind bearing (degrees)."""
        wind_bearing = None
        if self.observation:
            wind_bearing = self.observation.get('windDirection',
                                                {}).get('value')
        if wind_bearing is None and (self.metar_obs
                                     and self.metar_obs.wind_dir):
            wind_bearing = self.metar_obs.wind_dir.value()
        return wind_bearing

    @property
    def icon_condition(self):
        """Return current condition."""
        icon = None
        if self.observation:
            icon = self.observation.get('icon')
        if icon:
            time, weather = parse_icon(self.observation['icon'])
            weather = convert_weather(weather)
            return time, weather
        return None

    @property
    def visibility(self):
        """Return visibility in mi."""
        vis_m = None
        if self.observation:
            vis_m = self.observation.get('visibility', {}).get('value')
        if vis_m is None and self.metar_obs and self.metar_obs.vis:
            vis_m = self.metar_obs.vis.value(units='M')
        return vis_m

    @property
    def forecast(self):
        """Return forecast."""
        forecast = []
        for forecast_entry in self._forecast:
            # get weather
            time, weather = parse_icon(forecast_entry['icon'])
            weather = convert_weather(weather)
            forecast_entry['iconCondition'] = (time, weather)
            forecast_entry['windBearing'] = \
                WIND[forecast_entry['windDirection']]

            # wind speed reported as '7 mph' or '7 to 10 mph'
            # if range, take average
            wind_speed = forecast_entry['windSpeed'].split(' ')[0::2]
            wind_speed_avg = mean(int(w) for w in wind_speed)
            forecast_entry['windSpeedAvg'] = wind_speed_avg

            forecast.append(forecast_entry)
        return forecast
