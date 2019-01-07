import asyncio
import aiohttp
import pynws
import pytest

from tests.observation_response import OBSERVATION_RESPONSE
from tests.station_response import STATION_RESPONSE
from tests.forecast_response import FORECAST_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'

@pytest.fixture()
def obs_url(monkeypatch):
    def mock_url(a):
        return '/obs'
    monkeypatch.setattr('pynws.urls.obs_url', mock_url)

async def obs(request):
    return aiohttp.web.json_response(data=OBSERVATION_RESPONSE)

@pytest.fixture()
def station_url(monkeypatch):
    def mock_url(a, b):
        return '/stations'
    monkeypatch.setattr('pynws.urls.stn_url', mock_url)

async def stn(request):
    return aiohttp.web.json_response(data=STATION_RESPONSE)

@pytest.fixture()
def fore_url(monkeypatch):
    def mock_url(a,b):
        return '/fore'
    monkeypatch.setattr('pynws.urls.forc_url', mock_url)

async def fore(request):
    return aiohttp.web.json_response(data=FORECAST_RESPONSE)

async def test_nws_response(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/fore', fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=LATLON)
    stations = await nws.stations()
    nws.station = stations[0]
    observations = await nws.observations()
    forecast = await nws.forecast()
    
    nws2 = pynws.Nws(client, station='STNA')
    observations2 = await nws2.observations()
    
async def test_nws_fail_stn(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/fore', fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.stations()

async def test_nws_fail_obs(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/fore', fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.observations()

async def test_nws_fail_fore(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    app.router.add_get('/stations', stn)
    app.router.add_get('/fore', fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.forecast()
