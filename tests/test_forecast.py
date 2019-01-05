import asyncio
import aiohttp
import pynws
import pytest

from tests.forecast_response import FORECAST_RESPONSE

LATLON = (0, 0)

@pytest.fixture()
def fore_url(monkeypatch):
    def mock_url(a,b):
        return '/fore'
    monkeypatch.setattr('pynws.urls.forc_url', mock_url)

async def fore(request):
    return aiohttp.web.json_response(data=FORECAST_RESPONSE)

async def test_fore_url(aiohttp_client, loop):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    assert pynws.urls.forc_url(*LATLON) == pynws.const.API_URL + pynws.const.API_FORECAST.format(*LATLON)

async def test_fore_response(aiohttp_client, loop, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get('/fore', fore)
    client = await aiohttp_client(app)
    await pynws.forecast(*LATLON, client)

async def test_fore_fail(aiohttp_client, loop, fore_url):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    forecast = await pynws.forecast(*LATLON, client)
    assert forecast == None
