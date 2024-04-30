from datetime import datetime, timezone

import pytest

from pynws import raw_data
from tests.helpers import setup_app

LATLON = (0, 0)
STATION = "ABC"
USERID = "test"
WFO = "ABC"
X = 0
Y = 0
ZONE = "test"


async def test_gridpoints_stations(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints_stations(WFO, X, Y, client, USERID)


async def test_points(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_points(*LATLON, client, USERID)


async def test_stations_observations(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_stations_observations(STATION, client, USERID)
    await raw_data.raw_stations_observations(STATION, client, USERID, limit=2)
    await raw_data.raw_stations_observations(
        STATION, client, USERID, start=datetime.now(timezone.utc)
    )


async def test_stations_observations_start_datetime(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    with pytest.raises(
        ValueError, match="start parameter needs to be datetime, but got"
    ):
        await raw_data.raw_stations_observations(STATION, client, USERID, start="1PM")
    with pytest.raises(ValueError, match="start parameter must be timezone aware"):
        await raw_data.raw_stations_observations(
            STATION,
            client,
            USERID,
            start=datetime.now(),
        )


async def test_detailed_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_detailed_forecast(WFO, X, Y, client, USERID)


async def test_gridpoints_forecast(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints_forecast(WFO, X, Y, client, USERID)


async def test_gridpoints_forecast_hourly(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_gridpoints_forecast_hourly(WFO, X, Y, client, USERID)


async def test_alerts_active_zone(aiohttp_client, mock_urls):
    app = setup_app()
    client = await aiohttp_client(app)
    await raw_data.raw_alerts_active_zone(ZONE, client, USERID)
