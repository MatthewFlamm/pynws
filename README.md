# pynws

A python library to asynchronously retrieve weather observation from NWS/NOAA.

## Example

```python
import asyncio
import aiohttp
import pynws

PHILLY = (39.95, -75.16)
USERID = 'testing@address.xyz'

async def defaults():
    async with aiohttp.ClientSession() as session:
        stn = await pynws.stations(*PHILLY,
                                   session,
                                   userid=USERID)
        print(stn)
        observation = await pynws.observations(stn[0],
                                               session,
                                               limit=1,
                                               userid=USERID)
        print(observation)
        forecast = await pynws.forecast(*PHILLY,
                                        session,
                                        userid=USERID)
        print(forecast)

loop = asyncio.get_event_loop()
nws = loop.run_until_complete(defaults())
```

