from pynws import raw_data
from tests.helpers import setup_app
LATLON = (0, 0)
STATION = "ABC"
USERID ="test"


async def test_raw_points_stations(aiohttp_client, loop, mock_urls):
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
