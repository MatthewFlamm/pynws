from datetime import datetime
from types import GeneratorType

import pytest

from pynws import DetailedForecast, Nws, NwsError
from pynws.const import Detail
from pynws.forecast import ONE_HOUR
from tests.helpers import setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test_user"
ZONE = "test_zone"


async def test_nws_gridpoints_stations(aiohttp_client, mock_urls):
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
        await nws.get_stations_observations()
    nws.station = STATION
    observations = await nws.get_stations_observations()
    assert observations
    assert isinstance(observations, list)


async def test_nws_stations_observations_latest(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    with pytest.raises(NwsError):
        await nws.get_stations_observations_latest()
    nws.station = STATION
    observation = await nws.get_stations_observations_latest()
    assert observation
    assert isinstance(observation, dict)


async def test_nws_detailed_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast = await nws.get_detailed_forecast()
    assert nws.wfo
    assert forecast
    assert isinstance(forecast, DetailedForecast)

    when = datetime.fromisoformat("2022-02-04T03:15:00+00:00")

    # get_details_for_time tests
    details = forecast.get_details_for_time(when)
    assert isinstance(details, dict)
    assert details[Detail.TEMPERATURE] == 18.88888888888889  # celsius implied
    assert details[Detail.RELATIVE_HUMIDITY] == 97.0  # percent implied
    assert details[Detail.WIND_SPEED] == 12.964  # km/h implied

    # get_details_for_times tests
    hourly_details = forecast.get_details_for_times([when, when + ONE_HOUR])
    assert isinstance(hourly_details, GeneratorType)
    hourly_details = list(hourly_details)
    assert len(hourly_details) == 2
    for details in hourly_details:
        assert isinstance(details, dict)

    # get_detail_for_time tests
    value = forecast.get_detail_for_time(Detail.TEMPERATURE, when)
    assert value == 18.88888888888889  # celsius implied

    # get_details_by_hour tests
    hourly_details = forecast.get_details_by_hour(when, 15)
    assert isinstance(hourly_details, GeneratorType)
    hourly_details = list(hourly_details)
    assert len(hourly_details) == 15
    for details in hourly_details:
        assert isinstance(details, dict)
        assert Detail.TEMPERATURE in details


async def test_nws_gridpoints_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = Nws(client, USERID, LATLON)
    assert nws
    forecast_with_metadata = await nws.get_gridpoints_forecast()
    assert nws.wfo
    assert forecast_with_metadata
    assert isinstance(forecast_with_metadata, dict)
    forecast = forecast_with_metadata["periods"]
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
    forecast_with_metadata = await nws.get_gridpoints_forecast_hourly()
    assert nws.wfo
    assert forecast_with_metadata
    assert isinstance(forecast_with_metadata, dict)
    forecast = forecast_with_metadata["periods"]
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
