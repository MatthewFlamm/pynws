from pynws import Nws, NwsError, Forecast
from pynws.const import LAYER_RELATIVE_HUMIDITY, LAYER_TEMPERATURE
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
    tC, unit = forecast.get_layer_value(LAYER_TEMPERATURE, when)
    assert tC == 18.88888888888889
    assert unit == "wmoUnit:degC"
    rh, unit = forecast.get_layer_value(LAYER_RELATIVE_HUMIDITY, when)
    assert rh == 97.0
    assert unit == "wmoUnit:percent"


async def test_nws_gridpoints_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_gridpoints_forecast()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, list)


async def test_nws_gridpoints_forecast_hourly(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_gridpoints_forecast_hourly()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, list)


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
