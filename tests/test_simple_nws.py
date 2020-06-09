from pynws import NwsError, SimpleNWS
import pytest

from tests.helpers import data_return_function, setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test_user"
ZONE = "test_zone"


async def test_nws_set_station(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    assert nws.station == STATION
    assert nws.stations == [STATION]


async def test_nws_set_station_none(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station()
    assert nws.station == "KCMH"
    assert isinstance(nws.stations, list)


@pytest.mark.parametrize(
    "observation_json",
    [
        "stations_observations.json",
        "stations_observations_multiple.json",
        "stations_observations_strings.json",
    ],
)
async def test_nws_observation(aiohttp_client, loop, mock_urls, observation_json):
    app = setup_app(stations_observations=observation_json)
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    with pytest.raises(NwsError):
        await nws.update_observation()
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation
    assert observation
    assert observation["temperature"] == 10
    assert observation["dewpoint"] == 10
    assert observation["relativeHumidity"] == 10
    assert observation["windDirection"] == 10
    assert observation["visibility"] == 10000
    assert observation["seaLevelPressure"] == 100000
    assert observation["windSpeed"] == 10
    assert observation["iconTime"] == "day"
    assert observation["windGust"] == 10
    assert observation["iconWeather"][0][0] == "A few clouds"
    assert observation["iconWeather"][0][1] is None


async def test_nws_observation_metar(aiohttp_client, loop, mock_urls):
    app = setup_app(stations_observations="stations_observations_metar.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation

    assert observation["temperature"] == 25.6
    assert observation["dewpoint"] is None
    assert observation["relativeHumidity"] is None
    assert observation["windDirection"] == 350.0
    assert observation["visibility"] == 16093.44
    assert round(observation["seaLevelPressure"]) == 101761
    assert round(observation["windSpeed"], 2) == 2.57
    assert observation["windGust"] is None


async def test_nws_observation_metar_noparse(aiohttp_client, loop, mock_urls):
    app = setup_app(stations_observations="stations_observations_metar_noparse.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation
    assert observation["temperature"] is None


async def test_nws_observation_empty(aiohttp_client, loop, mock_urls):
    app = setup_app(stations_observations="stations_observations_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation

    assert observation["temperature"] is None
    assert observation["dewpoint"] is None
    assert observation["relativeHumidity"] is None
    assert observation["windDirection"] is None
    assert observation["visibility"] is None
    assert observation["seaLevelPressure"] is None
    assert observation["windSpeed"] is None
    assert observation["windGust"] is None
    assert observation["iconTime"] is None
    assert observation["iconWeather"] is None


async def test_nws_observation_noprop(aiohttp_client, loop, mock_urls):
    app = setup_app(stations_observations="stations_observations_noprop.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation

    assert observation is None


async def test_nws_observation_missing_value(aiohttp_client, loop, mock_urls):
    app = setup_app(stations_observations="stations_observations_missing_value.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation

    assert observation["temperature"] is None
    assert observation["dewpoint"] is None
    assert observation["relativeHumidity"] is None
    assert observation["windDirection"] is None
    assert observation["visibility"] is None
    assert observation["seaLevelPressure"] is None
    assert observation["windSpeed"] is None
    assert observation["windGust"] is None
    assert observation["iconTime"] is None
    assert observation["iconWeather"] is None


async def test_nws_forecast(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast

    assert forecast[0]["iconWeather"][0][0] == "Thunderstorm (high cloud cover)"
    assert forecast[0]["iconWeather"][0][1] == 40
    assert forecast[0]["iconWeather"][1][0] == "Overcast"
    assert forecast[0]["iconWeather"][1][1] is None
    assert forecast[0]["windSpeedAvg"] == 10
    assert forecast[0]["windBearing"] == 180


async def test_nws_forecast_hourly(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast_hourly()
    forecast = nws.forecast_hourly

    assert forecast


async def test_nws_forecast_strings(aiohttp_client, loop, mock_urls):
    app = setup_app(gridpoints_forecast="gridpoints_forecast_strings.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast

    assert forecast[0]["iconWeather"][0][0] == "Thunderstorm (high cloud cover)"
    assert forecast[0]["iconWeather"][0][1] == 40
    assert forecast[0]["iconWeather"][1][0] == "Overcast"
    assert forecast[0]["iconWeather"][1][1] is None
    assert forecast[0]["windSpeedAvg"] == 10
    assert forecast[0]["windBearing"] == 180


async def test_nws_forecast_empty(aiohttp_client, loop, mock_urls):
    app = setup_app(gridpoints_forecast="gridpoints_forecast_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast

    assert forecast


async def test_nws_alerts_forecast_zone(aiohttp_client, loop, mock_urls):
    app = setup_app(
        alerts_active_zone=["alerts_active_zone.json", "alerts_active_zone_second.json"]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    new_alerts = await nws.update_alerts_forecast_zone()
    assert new_alerts
    alerts = nws.alerts_forecast_zone
    assert alerts
    assert new_alerts == alerts
    assert len(alerts) == 1

    new_alerts = await nws.update_alerts_forecast_zone()
    assert new_alerts != alerts
    alerts = nws.alerts_forecast_zone
    assert new_alerts != alerts
    assert len(new_alerts) == 1
    assert len(alerts) == 2


async def test_nws_alerts_county_zone(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_alerts_county_zone()
    alerts = nws.alerts_county_zone
    assert alerts


async def test_nws_alerts_fire_weather_zone(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_alerts_fire_weather_zone()
    alerts = nws.alerts_fire_weather_zone
    assert alerts


async def test_nws_alerts_all_zones(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    new_alerts = await nws.update_alerts_all_zones()
    assert len(nws.all_zones) == 2
    assert new_alerts
    alerts = nws.alerts_all_zones
    assert alerts
    assert new_alerts == alerts
    assert len(alerts) == 1


async def test_nws_alerts_all_zones_second_alert(aiohttp_client, loop, mock_urls):
    app = setup_app(
        alerts_active_zone=["alerts_active_zone.json", "alerts_active_zone_second.json"]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    new_alerts = await nws.update_alerts_all_zones()
    assert len(nws.all_zones) == 2
    assert new_alerts
    alerts = nws.alerts_all_zones
    assert alerts
    assert new_alerts == alerts
    assert len(alerts) == 2
