import sys
from unittest.mock import AsyncMock, patch

import aiohttp
from freezegun import freeze_time
import pytest

from pynws import NwsError, NwsNoDataError, SimpleNWS, call_with_retry
from tests.helpers import setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test_user"
ZONE = "test_zone"


async def test_nws_set_station(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    assert nws.station == STATION
    assert nws.stations == [STATION]


async def test_nws_set_station_none(aiohttp_client, mock_urls):
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
        "stations_observations_other_unitcode.json",
        "stations_observations_multiple_unsorted.json",
        "stations_observations_relative_icon.json",
    ],
)
async def test_nws_observation(aiohttp_client, mock_urls, observation_json):
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
    assert observation["windSpeed"] == 36  # converted to km_gr
    assert observation["iconTime"] == "day"
    assert observation["windGust"] == 36  # same
    assert observation["iconWeather"][0][0] == "A few clouds"
    assert observation["iconWeather"][0][1] is None


async def test_nws_observation_with_retry(aiohttp_client, mock_urls):
    # update fails without retry
    app = setup_app(
        stations_observations=[aiohttp.web.HTTPBadGateway, "stations_observations.json"]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)

    with pytest.raises(aiohttp.ClientResponseError):
        await nws.update_observation()

    # update succeeds with retry
    app = setup_app(
        stations_observations=[aiohttp.web.HTTPBadGateway, "stations_observations.json"]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)

    await call_with_retry(nws.update_observation, 0, 5)
    observation = nws.observation
    assert observation
    assert observation["temperature"] == 10

    # no retry for 4xx error
    app = setup_app(
        stations_observations=[aiohttp.web.HTTPBadRequest, "stations_observations.json"]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)

    await nws.set_station(STATION)
    with pytest.raises(aiohttp.ClientResponseError):
        await call_with_retry(nws.update_observation, 0, 5)


async def test_nws_observation_units(aiohttp_client, mock_urls):
    app = setup_app(stations_observations="stations_observations_alternate_units.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation
    assert observation
    assert round(observation["temperature"], 1) == -12.2
    assert observation["windSpeed"] == 10  # converted to km_gr
    assert observation["windGust"] == 10


async def test_nws_observation_metar(aiohttp_client, mock_urls):
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
    assert round(observation["windSpeed"], 2) == 9.26
    assert observation["windGust"] is None


async def test_nws_observation_metar_noparse(aiohttp_client, mock_urls):
    app = setup_app(stations_observations="stations_observations_metar_noparse.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation
    assert observation["temperature"] is None


async def test_nws_observation_empty(aiohttp_client, mock_urls):
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


async def test_nws_observation_noprop(aiohttp_client, mock_urls):
    app = setup_app(stations_observations="stations_observations_noprop.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation

    assert observation is None

    with pytest.raises(NwsNoDataError, match="Observation received with no data"):
        await nws.update_observation(raise_no_data=True)


async def test_nws_observation_noprop_w_retry(aiohttp_client, mock_urls):
    app = setup_app(
        stations_observations=[
            "stations_observations_noprop.json",
            "stations_observations.json",
        ]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)

    await call_with_retry(nws.update_observation, 0, 5, retry_no_data=True)
    assert nws.observation is not None


async def test_nws_observation_cache(aiohttp_client, mock_urls):
    app = setup_app(
        stations_observations=[
            "stations_observations.json",
            "stations_observations_noprop.json",
        ]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.set_station(STATION)
    await nws.update_observation()
    observation = nws.observation
    assert observation

    await nws.update_observation()
    assert observation


async def test_nws_observation_missing_value(aiohttp_client, mock_urls):
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


@pytest.mark.parametrize(
    "gridpoints_forecast",
    ["gridpoints_forecast.json", "gridpoints_forecast_relative_icon.json"],
)
@freeze_time("2019-10-13T14:30:00-04:00")
async def test_nws_forecast(aiohttp_client, mock_urls, gridpoints_forecast):
    app = setup_app(
        gridpoints_forecast=gridpoints_forecast,
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast

    assert forecast[0]["temperature"] == 41
    assert forecast[0]["probabilityOfPrecipitation"] == 20
    assert forecast[0]["dewpoint"] == 41
    assert forecast[0]["relativeHumidity"] == 63

    assert forecast[0]["iconWeather"][0][0] == "Thunderstorm (high cloud cover)"
    assert forecast[0]["iconWeather"][0][1] == 40
    assert forecast[0]["iconWeather"][1][0] == "Overcast"
    assert forecast[0]["iconWeather"][1][1] is None
    assert forecast[0]["windSpeedAvg"] == 10
    assert forecast[0]["windBearing"] == 180

    # tests null value in quatitative value
    assert forecast[1]["probabilityOfPrecipitation"] == 0

    # test metadata
    metadata = nws.forecast_metadata

    assert metadata["updateTime"] == "2019-10-13T18:16:20+00:00"
    assert metadata["generatedAt"] == "2019-10-13T18:42:44+00:00"
    assert metadata["validTimes"] == "2019-10-13T12:00:00+00:00/P6DT22H"


async def test_nws_forecast_discard_stale(aiohttp_client, mock_urls):
    with freeze_time("2019-10-14T21:30:00-04:00"):
        app = setup_app()
        client = await aiohttp_client(app)
        nws = SimpleNWS(*LATLON, USERID, client, filter_forecast=True)
        await nws.update_forecast_hourly()
        forecast = nws.forecast_hourly
        assert forecast[0]["temperature"] == 77

        nws = SimpleNWS(*LATLON, USERID, client, filter_forecast=False)
        await nws.update_forecast_hourly()
        forecast = nws.forecast_hourly

        assert forecast[0]["temperature"] == 78

    with freeze_time("2019-10-15T21:30:00-04:00"):
        nws = SimpleNWS(*LATLON, USERID, client, filter_forecast=True)
        await nws.update_forecast_hourly()
        forecast = nws.forecast_hourly
        assert forecast == []

        nws = SimpleNWS(*LATLON, USERID, client, filter_forecast=True)
        with pytest.raises(
            NwsNoDataError, match="Forecast hourly received with no data"
        ):
            await nws.update_forecast_hourly(raise_no_data=True)


@freeze_time("2019-10-14T20:30:00-04:00")
async def test_nws_forecast_hourly(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast_hourly()
    forecast = nws.forecast_hourly

    assert forecast[0]["temperature"] == 78
    assert forecast[0]["probabilityOfPrecipitation"] == 20
    assert forecast[0]["dewpoint"] == 41
    assert forecast[0]["relativeHumidity"] == 63

    # test metadata
    metadata = nws.forecast_hourly_metadata

    assert metadata["updateTime"] == "2019-10-14T23:16:24+00:00"
    assert metadata["generatedAt"] == "2019-10-15T00:12:54+00:00"
    assert metadata["validTimes"] == "2019-10-14T17:00:00+00:00/P7DT20H"


@freeze_time("2019-10-13T14:30:00-04:00")
async def test_nws_forecast_strings(aiohttp_client, mock_urls):
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


@freeze_time("2019-10-13T14:30:00-04:00")
async def test_nws_forecast_empty(aiohttp_client, mock_urls):
    app = setup_app(gridpoints_forecast="gridpoints_forecast_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast

    assert forecast == []
    assert nws.forecast_metadata == {}


@freeze_time("2019-10-13T14:30:00-04:00")
async def test_nws_forecast_empty_raise(aiohttp_client, mock_urls):
    app = setup_app(gridpoints_forecast="gridpoints_forecast_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    with pytest.raises(NwsNoDataError, match="Forecast received with no data"):
        await nws.update_forecast(raise_no_data=True)


@freeze_time("2019-10-13T14:30:00-04:00")
async def test_nws_forecast_cache(aiohttp_client, mock_urls):
    app = setup_app(
        gridpoints_forecast=[
            "gridpoints_forecast.json",
            "gridpoints_forecast_empty.json",
        ]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast()
    forecast = nws.forecast
    assert forecast

    await nws.update_forecast()
    assert forecast
    assert nws.forecast_metadata["updateTime"] == "2019-10-13T18:16:20+00:00"


@freeze_time("2019-10-14T20:30:00-04:00")
async def test_nws_forecast_hourly_empty(aiohttp_client, mock_urls):
    app = setup_app(gridpoints_forecast_hourly="gridpoints_forecast_hourly_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast_hourly()
    forecast_hourly = nws.forecast_hourly

    assert forecast_hourly == []
    assert nws.forecast_hourly_metadata == {}


@freeze_time("2019-10-14T20:30:00-04:00")
async def test_nws_forecast_hourly_empty_raise(aiohttp_client, mock_urls):
    app = setup_app(gridpoints_forecast_hourly="gridpoints_forecast_hourly_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    with pytest.raises(NwsNoDataError, match="Forecast hourly received with no data"):
        await nws.update_forecast_hourly(raise_no_data=True)


@freeze_time("2019-10-14T20:30:00-04:00")
async def test_nws_forecast_hourly_cache(aiohttp_client, mock_urls):
    app = setup_app(
        gridpoints_forecast_hourly=[
            "gridpoints_forecast_hourly.json",
            "gridpoints_forecast_hourly_empty.json",
        ]
    )
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_forecast_hourly()
    assert nws.forecast_hourly

    await nws.update_forecast_hourly()
    assert nws.forecast_hourly

    assert nws.forecast_hourly_metadata["updateTime"] == "2019-10-14T23:16:24+00:00"


async def test_nws_unimplemented_retry_no_data(aiohttp_client, mock_urls):
    app = setup_app(gridpoints_forecast="gridpoints_forecast_empty.json")
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    with pytest.raises(
        NotImplementedError,
        match="raise_no_data=True not implemented for update_detailed_forecast",
    ):
        await nws.update_detailed_forecast(raise_no_data=True)

    with pytest.raises(
        NotImplementedError,
        match="raise_no_data=True not implemented for update_alerts_forecast_zone",
    ):
        await nws.update_alerts_forecast_zone(raise_no_data=True)

    with pytest.raises(
        NotImplementedError,
        match="raise_no_data=True not implemented for update_alerts_county_zone",
    ):
        await nws.update_alerts_county_zone(raise_no_data=True)

    with pytest.raises(
        NotImplementedError,
        match="raise_no_data=True not implemented for update_alerts_fire_weather_zone",
    ):
        await nws.update_alerts_fire_weather_zone(raise_no_data=True)


async def test_nws_alerts_forecast_zone(aiohttp_client, mock_urls):
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


async def test_nws_alerts_county_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_alerts_county_zone()
    alerts = nws.alerts_county_zone
    assert alerts


async def test_nws_alerts_fire_weather_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_alerts_fire_weather_zone()
    alerts = nws.alerts_fire_weather_zone
    assert alerts


async def test_nws_alerts_all_zones(aiohttp_client, mock_urls):
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


async def test_nws_alerts_all_zones_after_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    nws = SimpleNWS(*LATLON, USERID, client)
    await nws.update_alerts_forecast_zone()
    new_alerts = await nws.update_alerts_all_zones()
    assert len(nws.all_zones) == 2
    assert new_alerts
    alerts = nws.alerts_all_zones
    assert alerts
    assert new_alerts == alerts
    assert len(alerts) == 1


async def test_nws_alerts_all_zones_second_alert(aiohttp_client, mock_urls):
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


async def test_retry(aiohttp_client, mock_urls):
    with patch("pynws.simple_nws._nws_retry_func") as err_mock:
        # retry all exceptions
        def _return_true(error):
            return True

        err_mock.return_value = _return_true

        app = setup_app()
        client = await aiohttp_client(app)
        nws = SimpleNWS(*LATLON, USERID, client)
        await nws.set_station(STATION)

        mock_update = AsyncMock()
        mock_update.side_effect = [ValueError, None]

        if sys.version_info >= (3, 10):
            mock_wrap = mock_update
        else:

            async def mock_wrap(*args, **kwargs):
                return await mock_update(*args, **kwargs)

        await call_with_retry(mock_wrap, 0, 5)

        assert mock_update.call_count == 2


async def test_retry_with_args():
    mock_update = AsyncMock()

    if sys.version_info >= (3, 10):
        mock_wrap = mock_update
    else:

        async def mock_wrap(*args, **kwargs):
            return await mock_update(*args, **kwargs)

    await call_with_retry(mock_wrap, 0, 5, "", test=None)
    # raise_no_data is always included when called with retry
    mock_update.assert_called_once_with("", raise_no_data=False, test=None)

    mock_update.reset_mock()
    await call_with_retry(mock_wrap, 0, 5, "", test=None, retry_no_data=True)
    # retry_no_data will change raise_no_data
    mock_update.assert_called_once_with("", raise_no_data=True, test=None)


async def test_retry_invalid_args():
    mock_update = AsyncMock()

    if sys.version_info >= (3, 10):
        mock_wrap = mock_update
    else:

        async def mock_wrap(*args, **kwargs):
            return await mock_update(*args, **kwargs)

    # positional only args
    with pytest.raises(TypeError):
        # 'interval' and 'stop' will be included in '**kwargs' since positional-only
        # parameters with these names already exist
        await call_with_retry(mock_wrap, interval=0, stop=5)

    assert mock_update.call_count == 0


async def test_retries_runtime_error():
    mock_update = AsyncMock()
    mock_update.side_effect = [RuntimeError, None]

    if sys.version_info >= (3, 10):
        mock_wrap = mock_update
    else:

        async def mock_wrap(*args, **kwargs):
            return await mock_update(*args, **kwargs)

    with pytest.raises(RuntimeError):
        await call_with_retry(mock_wrap, 0, 5)

    assert mock_update.call_count == 1
