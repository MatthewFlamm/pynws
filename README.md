# pynws

A python library to asynchronously retrieve weather observation from NWS/NOAA.

![PyPI - Downloads](https://img.shields.io/pypi/dm/pynws?style=flat-square)

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


### Units for Observations in SimpleNWS
NWS API does not expose all possible units for observations.  Known units are converted to the following:

|unit type   | known NWS units| pynws unit |
|------------|----------------|------------|
|temperature | degF, degC     | Celsius    |
|pressure    | Pa             | Pascal     |
|speed       | m_s-1, km_h-1  | km_h-1     |
|percent     | percent        | percent    |
|angle       | degree_(angle) | degrees    |
|distance    | m              | meter      |
