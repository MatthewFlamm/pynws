import asyncio

import aiohttp

import pynws

PHILLY = (39.95, -75.16)
USERID = "testing@address.xyz"


async def example():
    async with aiohttp.ClientSession() as session:
        nws = pynws.SimpleNWS(*PHILLY, USERID, session)
        await nws.set_station()
        await nws.update_observation()
        await nws.update_forecast()
        await nws.update_alerts_forecast_zone()
        print(nws.observation)
        print(nws.forecast[0])
        print(nws.alerts_forecast_zone)


loop = asyncio.get_event_loop()
loop.run_until_complete(example())
