"""Test observations"""
import asyncio
from datetime import timedelta

import aiohttp
import pynws
import pytest

from pynws.tests.observation_response import OBSERVATION_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'

@pytest.fixture()
def obs_url(monkeypatch):
    """Monkeypatch observation url to /obs"""
    def mock_url(a):
        return '/obs'
    monkeypatch.setattr('pynws.urls.obs_url', mock_url)

async def obs(request):
    """Return observation response"""
    return aiohttp.web.json_response(data=OBSERVATION_RESPONSE)

async def test_obs_url(aiohttp_client, loop):
    """Observation url is correct"""
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    assert pynws.urls.obs_url('STNA') == pynws.const.API_URL + \
        pynws.const.API_OBSERVATION.format('STNA')

async def test_obs_response(aiohttp_client, loop, obs_url):
    """Getting response succeeds"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    client = await aiohttp_client(app)
    await pynws.observations('STNA', client, USERID)
    await pynws.observations('STNA', client, USERID, limit=1)
    await pynws.observations('STNA', client, USERID, start_time=timedelta(hours=1))


async def test_obs_fail(aiohttp_client, loop, obs_url):
    """Response fails when url not correct"""
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    with pytest.raises(aiohttp.ClientResponseError):
        observations = await pynws.observations('STNA', client, USERID)
    

async def test_obs_fail_start(aiohttp_client, loop, obs_url):
    """Non timedelta fails"""
    app = aiohttp.web.Application()
    app.router.add_get('/obs', obs)
    client = await aiohttp_client(app)
    with pytest.raises(ValueError):
        await pynws.observations('STNA', client, USERID, start_time=1)
