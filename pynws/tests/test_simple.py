# pylint: disable=redefined-outer-name
"""Test observations"""
import json
import os

import aiohttp
import pytest

import pynws
from pynws.tests.observation_response import OBSERVATION_RESPONSE
from pynws.tests.station_response import STATION_RESPONSE
from pynws.tests.metar_observation_response import METAR_OBSERVATION_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'

DIR = os.path.dirname(os.path.realpath(__file__))


async def stn(request):
    """Return station response"""
    return aiohttp.web.json_response(data=STATION_RESPONSE)


async def point(request):
    with open(os.path.join(DIR, 'points.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def grid_forecast(request):
    with open(os.path.join(DIR, 'grid_forecast.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def grid_forecast_hourly(request):
    with open(os.path.join(DIR, 'grid_forecast_hourly.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def alerts_zone(request):
    with open(os.path.join(DIR, 'alerts.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


@pytest.fixture()
def urls(monkeypatch):
    """Monkeypatch observation url to /obs"""
    def obs_url(a):
        return '/obs'
    monkeypatch.setattr('pynws.urls.obs_url', obs_url)
    def stn_url(a, b):
        return '/stations'
    monkeypatch.setattr('pynws.urls.stn_url', stn_url)
    def grid_forecast_url(a, b, c):
        return '/forecast'
    monkeypatch.setattr('pynws.urls.grid_forecast_url', grid_forecast_url)
    def point_url(a, b):
        return '/point'
    monkeypatch.setattr('pynws.urls.point_url', point_url)
    def grid_forecast_hourly_url(a, b, c):
        return '/forecast_hourly'
    monkeypatch.setattr('pynws.urls.grid_forecast_hourly_url', grid_forecast_hourly_url)
    def alerts_zone_url(a):
        return '/alerts_zone'
    monkeypatch.setattr('pynws.urls.alerts_zone_url', alerts_zone_url)
    

async def obs(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'obs.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))

async def obs_multiple(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'obs_multiple.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))
    

async def test_set_station(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    assert snws.station == 'STN'
    assert snws.stations == ['STN']
    assert snws.nws.station == 'STN'
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station()
    assert snws.station == 'STNA'
    assert snws.stations == ['STNA', 'STNB', 'STNC', 'STND']
    assert snws.nws.station == 'STNA'

@pytest.mark.parametrize("obs_json", [obs, obs_multiple])
async def test_obs(aiohttp_client, loop, urls, obs_json):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs_json)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)
    app.router.add_get('/forecast', grid_forecast)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    assert observation['temperature'] == 10
    assert observation['dewpoint'] == 10
    assert observation['relativeHumidity'] == 10
    assert observation['windDirection'] == 10
    assert observation['visibility'] == 10000
    assert observation['seaLevelPressure'] == 100000
    assert observation['windSpeed'] == 10
    assert observation['iconTime'] == "day"
    assert observation['windGust'] == 10
    assert observation['iconWeather'][0][0] == "A few clouds"
    assert observation['iconWeather'][0][1] is None

    await snws.update_forecast()
    forecast = snws.forecast[0]
    assert forecast['iconWeather'][0][0] == "Thunderstorm (high cloud cover)" 
    assert forecast['iconWeather'][0][1] == 40
    assert forecast['iconWeather'][1][0] == "Overcast"
    assert forecast['iconWeather'][1][1] is None
    assert forecast['windSpeedAvg'] == 10
    assert forecast['windBearing'] == 180


async def test_hourly_forecast(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)
    app.router.add_get('/forecast_hourly', grid_forecast_hourly)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_forecast_hourly()
    assert snws.forecast_hourly

async def metar_obs(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'obs_metar.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_metar_obs(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', metar_obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)

    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    assert observation['temperature'] == 25.6
    assert observation['dewpoint'] is None
    assert observation['relativeHumidity'] is None
    assert observation['windDirection'] == 350.
    assert observation['visibility'] == 16093.44
    assert round(observation['seaLevelPressure']) == 101761
    assert round(observation['windSpeed'], 2) == 2.57
    assert observation['windGust'] is None


async def noparse_metar_obs(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'obs_noparse_metar.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_noparse_metar_obs(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', noparse_metar_obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)

    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    assert observation['temperature'] is None


async def empty_obs(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'obs_empty.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_empty_obs(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', empty_obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)

    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    
    assert observation['temperature'] is None
    assert observation['dewpoint'] is None
    assert observation['relativeHumidity'] is None
    assert observation['windDirection'] is None
    assert observation['visibility'] is None
    assert observation['seaLevelPressure'] is None
    assert observation['windSpeed'] is None
    assert observation['windGust'] is None
    assert observation['iconTime'] is None
    assert observation['iconWeather'] is None


async def obs_no_prop(request):
    """Return no observation"""
    with open(os.path.join(DIR, 'obs_empty.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_obs_no_prop(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs_no_prop)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)

    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    
    assert observation['temperature'] is None
    assert observation['dewpoint'] is None
    assert observation['relativeHumidity'] is None
    assert observation['windDirection'] is None
    assert observation['visibility'] is None
    assert observation['seaLevelPressure'] is None
    assert observation['windSpeed'] is None
    assert observation['windGust'] is None
    assert observation['iconTime'] is None
    assert observation['iconWeather'] is None


async def obs_miss_value(request):
    """Return no observation"""
    with open(os.path.join(DIR, 'obs_miss_value.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))
    
    
async def test_obs_missing_value(aiohttp_client, loop, urls):
    """No error when missing value."""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs_miss_value)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)

    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_observation()

    observation = snws.observation
    
    assert observation['temperature'] is None
    assert observation['dewpoint'] is None
    assert observation['relativeHumidity'] is None
    assert observation['windDirection'] is None
    assert observation['visibility'] is None
    assert observation['seaLevelPressure'] is None
    assert observation['windSpeed'] is None
    assert observation['windGust'] is None
    assert observation['iconTime'] is None
    assert observation['iconWeather'] is None


async def empty_fore(request):
    """Return observation response"""
    with open(os.path.join(DIR, 'fore_empty.json'), 'r') as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_empty_fore(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/point', point)
    app.router.add_get('/forecast', empty_fore)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.set_station('STN')
    await snws.update_forecast()
    assert snws.forecast


async def test_alerts_zone(aiohttp_client, loop, urls):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/point', point)
    app.router.add_get('/alerts_zone', alerts_zone)
    client = await aiohttp_client(app)
    snws = pynws.SimpleNWS(*LATLON, USERID, client) 
    await snws.update_alerts_zone()
    assert snws.alerts_zone
