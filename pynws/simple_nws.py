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
    def __init__(self, lat, lon, api_key, mode, session):
        """Set up simplified NWS class."""
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.session = session
        self.nws = Nws(session, latlon=(float(lat), float(lon)),
                       userid=api_key)
        self.mode = mode

        self._observation = None
        self._metar_obs = None
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
        self._observation = obs[0]
        metar_msg = self._observation.get('rawMessage')
        if metar_msg:
            self._metar_obs = Metar(metar_msg)
        else:
            self._metar_obs = None

    async def update_forecast(self):
        """Update forecast."""
        if self.mode == 'daynight':
            forecast = await self.nws.forecast()
        elif self.mode == 'hourly':
            forecast = await self.nws.forecast_hourly()
        self._forecast = forecast

    @property
    def observation(self):
        """Observation dict"""

        if self._observation is None:
            return None

        data = {}
        for obs, met in OBSERVATIONS.items():
            data[obs] = self._observation[obs]
            if isinstance(data[obs], dict):
                data[obs] = data[obs].get('value')
            if data[obs] is None and (met is not None
                                      and self._metar_obs is not None):
                met_prop = getattr(self._metar_obs, met[0])
                if met_prop:
                    if met[1]:
                        data[obs] = met_prop.value(units=met[1])
                    else:
                        data[obs] = met_prop.value()
                    if met[2] is not None:
                        data[obs] = data[obs] * met[2]

        time, weather = parse_icon(data['icon'])
        data['iconTime'] = time
        data['iconWeather'] = convert_weather(weather)
        return data

    @property
    def forecast(self):
        """Return forecast."""
        forecast = []
        for forecast_entry in self._forecast:
            # get weather
            time, weather = parse_icon(forecast_entry['icon'])
            weather = convert_weather(weather)
            forecast_entry['iconTime'] = time
            forecast_entry['iconWeather'] = weather
            forecast_entry['windBearing'] = \
                WIND[forecast_entry['windDirection']]

            # wind speed reported as '7 mph' or '7 to 10 mph'
            # if range, take average
            wind_speed = forecast_entry['windSpeed'].split(' ')[0::2]
            wind_speed_avg = mean(int(w) for w in wind_speed)
            forecast_entry['windSpeedAvg'] = wind_speed_avg

            forecast.append(forecast_entry)
        return forecast
