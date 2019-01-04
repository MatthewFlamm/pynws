# pynws

A python library to asynchronously retrieve weather observation from NWS/NOAA.

## Example

```python
import asyncio
import aiohttp
import pynws

PHILLY = (39.95, -75.16)

async def defaults():
    async with aiohttp.ClientSession() as session:
        stn = await pynws.stations(*PHILLY, session)
        print(stn)
        obs = await pynws.observations(stn[0], session, limit=1)
        print(obs)
        fore = await pynws.forecast(*PHILLY, session)
        print(fore)

loop = asyncio.get_event_loop()
nws = loop.run_until_complete(defaults())
```

