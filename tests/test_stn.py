import asyncio
import aiohttp
import pynws
import pytest

from tests.station_response import STATION_RESPONSE

LATLON = (0, 0)
USERID = 'testing@test'

@pytest.fixture()
def station_url(monkeypatch):
    def mock_url(a, b):
        return '/stations'
    monkeypatch.setattr('pynws.urls.stn_url', mock_url)

async def stn(request):
    return aiohttp.web.json_response(data=STATION_RESPONSE)

async def test_stn_url(aiohttp_client, loop):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    assert pynws.urls.stn_url(*LATLON) == pynws.const.API_URL + pynws.const.API_STATIONS.format(*LATLON)

async def test_stn_response(aiohttp_client, loop, station_url):
    app = aiohttp.web.Application()
    app.router.add_get('/stations', stn)
    client = await aiohttp_client(app)
    await pynws.stations(*LATLON, client, USERID)

async def test_stn_fail(aiohttp_client, loop, station_url):
    app = aiohttp.web.Application()
    client = await aiohttp_client(app)
    with pytest.raises(aiohttp.ClientResponseError):
        stations = await pynws.stations(*LATLON, client, USERID)
