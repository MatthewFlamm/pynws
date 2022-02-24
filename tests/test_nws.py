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


async def test_nws_all_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_all_forecast()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, Forecast)

    when = datetime.fromisoformat("2022-02-04T03:15:00+00:00")

    value = forecast.get_value_at_time(when, Layer.TEMPERATURE)
    assert value == (18.88888888888889, "wmoUnit:degC")

    values = forecast.get_values_at_time(when)
    assert isinstance(values, dict)
    assert Layer.TEMPERATURE in values
    assert Layer.RELATIVE_HUMIDITY in values
    assert Layer.PROBABILITY_OF_HURRICANE_WINDS not in values
    assert values[Layer.TEMPERATURE] == (18.88888888888889, "wmoUnit:degC")
    assert values[Layer.RELATIVE_HUMIDITY] == (97.0, "wmoUnit:percent")


async def test_nws_daily_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_daily_forecast()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, list)


async def test_nws_hourly_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_hourly_forecast()
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
