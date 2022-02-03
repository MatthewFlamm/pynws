from datetime import datetime, timezone

from pynws import raw_data
import pytest

from tests.helpers import setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test"
WFO = "ABC"
X = 0
Y = 0
ZONE = "test"


async def test_points_stations(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_points_stations(*LATLON, client, USERID)


async def test_points(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_points(*LATLON, client, USERID)


async def test_stations_observations(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_stations_observations(STATION, client, USERID)
    await raw_data.raw_stations_observations(STATION, client, USERID, limit=2)
    await raw_data.raw_stations_observations(
        STATION, client, USERID, start=datetime.now(timezone.utc)
    )


async def test_stations_observations_start_datetime(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    with pytest.raises(ValueError):
        await raw_data.raw_stations_observations(STATION, client, USERID, start="1PM")


async def test_gridpoints(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints(WFO, X, Y, client, USERID)


async def test_gridpoints_forecast(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints_forecast(WFO, X, Y, client, USERID)


async def test_gridpoints_forecast_hourly(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints_forecast_hourly(WFO, X, Y, client, USERID)


async def test_alerts_active_zone(aiohttp_client, loop, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_alerts_active_zone(ZONE, client, USERID)
