import asyncio

import aiohttp
import pynws

PHILLY = (39.95, -75.16)
USERID = 'testing@address.xyz'

async def defaults():
    async with aiohttp.ClientSession() as session:
        nws = pynws.Nws(session, latlon=PHILLY, userid=USERID)
        stations = await nws.stations()
        nws.station = stations[0]
        observations = await nws.observations()
        forecast = await nws.forecast()

loop = asyncio.get_event_loop()
loop.run_until_complete(defaults())
