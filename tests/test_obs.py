import asyncio
import aiohttp
import pynws
import pytest

from tests.observation_response import OBSERVATION_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'

@pytest.fixture()
def obs_url(monkeypatch):
    def mock_url(a):
        return '/obs'
    monkeypatch.setattr('pynws.urls.obs_url', mock_url)

async def obs(request):
    return aiohttp.web.json_response(data=OBSERVATION_RESPONSE)

async def test_obs_url(aiohttp_client, loop):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    assert pynws.urls.obs_url('STNA') == pynws.const.API_URL + pynws.const.API_OBSERVATION.format('STNA')

async def test_obs_response(aiohttp_client, loop, obs_url):
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    client = await aiohttp_client(app)
    await pynws.observations('STNA', client, USERID)

async def test_obs_fail(aiohttp_client, loop, obs_url):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    with pytest.raises(aiohttp.ClientResponseError):
        observations = await pynws.observations('STNA', client, USERID)
    
