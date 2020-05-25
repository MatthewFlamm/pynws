# pynws

A python library to asynchronously retrieve weather observation from NWS/NOAA.

## Example
See [example.py](example.py) for a runnable example.
```python
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
```

## Functionality
pynws exposes the ability to retrieve raw data using `raw_data` module. `Nws` class offers ability to retrieve minimally processed data for a single location.  `SimpleNWS` class offers data caching and several other helpers for interpreting output.
