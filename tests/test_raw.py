from pynws import raw_data

LATLON = (0, 0)
USERID ="test"


async def test_raw_stations(aiohttp_client, loop):
    app = setup(app)
    client = await aiohttp_client(app)
    await raw_data.stations(*LATLON, client, USERID)
