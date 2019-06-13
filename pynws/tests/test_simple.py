"""Test observations"""
import asyncio
import aiohttp
import pynws
import pytest

from pynws.tests.forecast_hourly_response import FORECAST_HOURLY_RESPONSE
from pynws.tests.forecast_response import FORECAST_RESPONSE
from pynws.tests.observation_response import OBSERVATION_RESPONSE
from pynws.tests.station_response import STATION_RESPONSE
from pynws.tests.metar_observation_response import METAR_OBSERVATION_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'
MODE = 'daynight'
USERID = 'testing@test'


async def stn(request):
    """Return station response"""
    return aiohttp.web.json_response(data=STATION_RESPONSE)


@pytest.fixture()
def urls(monkeypatch):
    """Monkeypatch observation url to /obs"""
    def obs_url(a):
        return '/obs'
    monkeypatch.setattr('pynws.urls.obs_url', obs_url)
    def stn_url(a, b):
        return '/stations'
    monkeypatch.setattr('pynws.urls.stn_url', stn_url)
    def forc_url(a, b):
        return '/forecast'
    monkeypatch.setattr('pynws.urls.forc_url', forc_url)
    def forc_hourly_url(a, b):
        return '/forecast_hourly'
    monkeypatch.setattr('pynws.urls.hour_forc_url', forc_hourly_url)


async def obs(request):
    """Return observation response"""
    return aiohttp.web.json_response(data=OBSERVATION_RESPONSE)


async def forc(request):
    """Return observation response"""
    return aiohttp.web.json_response(data=FORECAST_RESPONSE)


async def forc_hourly(request):
    """Return observation response"""
    return aiohttp.web.json_response(data=FORECAST_HOURLY_RESPONSE)


async def test_set_station(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, MODE, client) 
    await snws.set_station('STN')
    assert snws.station == 'STN'
    assert snws.stations == ['STN']
    assert snws.nws.station == 'STN'
    snws = pynws.SimpleNWS(*LATLON, USERID, MODE, client) 
    await snws.set_station()
    assert snws.station == 'STNA'
    assert snws.stations == ['STNA', 'STNB', 'STNC', 'STND']
    assert snws.nws.station == 'STNA'

async def test_obs(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/forecast', forc)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, MODE, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    assert snws.temperature == 10
    assert snws.humidity == 10
    assert snws.wind_bearing == 10
    assert snws.visibility == 10
    assert snws.pressure == 10
    assert snws.wind_speed == 10
    assert snws.icon_condition[0] == "night"
    assert snws.icon_condition[1][0][0] == "Overcast"
    assert snws.icon_condition[1][0][1] == 0

    await snws.update_forecast()
    forecast = snws.forecast[0]
    forecast['iconCondition'][0][0] == "Thunderstorm (high cloud cover)" 
    forecast['iconCondition'][0][1] == 40
    forecast['iconCondition'][0][0] == "Overcast"
    forecast['iconCondition'][0][1] == 0
    forecast['windSpeed'] == 10
    forecast['windBearing'] == 180


async def test_hourly_forecast(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/forecast_hourly', forc_hourly)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, 'hourly', client) 
    await snws.set_station('STN')
    await snws.update_forecast()
    assert snws.forecast

async def metar_obs(request):
    """Return observation response"""
    return aiohttp.web.json_response(data=METAR_OBSERVATION_RESPONSE)


async def test_metar_obs(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', metar_obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/forecast', forc)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, MODE, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    assert snws.temperature == 25.6
    assert snws.humidity is None
    assert snws.wind_bearing == 80
    assert snws.visibility == 16090
    assert snws.pressure == 101625.80398
    assert snws.wind_speed == 3.601108
    assert snws.icon_condition[0] == "night"
    assert snws.icon_condition[1][0][0] == "A few clouds"
    assert snws.icon_condition[1][0][1] == 0
