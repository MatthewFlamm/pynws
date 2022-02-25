from pynws import Nws, NwsError, Forecast
from pynws.layer import Layer
from datetime import datetime
import pytest

from tests.helpers import setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test_user"
ZONE = "test_zone"


async def test_nws_points_stations(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    stations = await nws.get_points_stations()
    assert stations
    assert isinstance(stations, list)


async def test_nws_points(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    points = await nws.get_points()
    assert points
    assert nws.wfo
    assert nws.x
    assert nws.y
    assert nws.forecast_zone
    assert nws.county_zone
    assert nws.fire_weather_zone


async def test_nws_stations_observations(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    with pytest.raises(NwsError):
        stations = await nws.get_stations_observations()
    nws.station = STATION
    observations = await nws.get_stations_observations()
    assert observations
    assert isinstance(observations, list)


async def test_nws_forecast_all(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_forecast_all()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, Forecast)

    when = datetime.fromisoformat("2022-02-04T03:15:00+00:00")

    values = forecast.get_forecast_for_time(when)
    assert isinstance(values, dict)
    assert values[Layer.TEMPERATURE] == (18.88888888888889, "wmoUnit:degC")
    assert values[Layer.RELATIVE_HUMIDITY] == (97.0, "wmoUnit:percent")
    assert values[Layer.WIND_SPEED] == (12.964, "wmoUnit:km_h-1")


async def test_nws_gridpoints_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_gridpoints_forecast()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, list)

    values = forecast[0]
    assert isinstance(values, dict)
    assert values["startTime"] == "2019-10-13T14:00:00-04:00"
    assert values["temperature"] == 41
    assert values["temperatureUnit"] == "F"
    assert values["windSpeed"] == "10 mph"


async def test_nws_gridpoints_forecast_hourly(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_gridpoints_forecast_hourly()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, list)

    values = forecast[0]
    assert isinstance(values, dict)
    assert values["startTime"] == "2019-10-14T20:00:00-04:00"
    assert values["temperature"] == 78
    assert values["temperatureUnit"] == "F"
    assert values["windSpeed"] == "0 mph"


async def test_nws_alerts_active_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    alerts = await nws.get_alerts_active_zone(ZONE)
    assert alerts
    assert isinstance(alerts, list)


async def test_nws_alerts_forecast_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    alerts = await nws.get_alerts_forecast_zone()
    assert alerts
    assert isinstance(alerts, list)


async def test_nws_alerts_county_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    alerts = await nws.get_alerts_county_zone()
    assert alerts
    assert isinstance(alerts, list)


async def test_nws_alerts_fire_weather_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    alerts = await nws.get_alerts_fire_weather_zone()
    assert alerts
    assert isinstance(alerts, list)
