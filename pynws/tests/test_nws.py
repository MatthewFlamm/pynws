import asyncio
import json
import os

import aiohttp
import pynws
from pynws.tests.forecast_response import FORECAST_RESPONSE
from pynws.tests.observation_response import OBSERVATION_RESPONSE
from pynws.tests.station_response import STATION_RESPONSE
import pytest

LATLON = (0, 0)
USERID = "testing@test"


DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def obs_url(monkeypatch):
    def mock_url(a):
        return "/obs"

    monkeypatch.setattr("pynws.urls.obs_url", mock_url)


async def obs(request):
    return aiohttp.web.json_response(data=OBSERVATION_RESPONSE)


async def no_obs(request):
    with open(os.path.join(DIR, "obs_no_prop.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


@pytest.fixture()
def station_url(monkeypatch):
    def mock_url(a, b):
        return "/stations"

    monkeypatch.setattr("pynws.urls.stn_url", mock_url)


async def stn(request):
    return aiohttp.web.json_response(data=STATION_RESPONSE)


@pytest.fixture()
def fore_url(monkeypatch):
    def mock_url(a, b):
        return "/fore"

    monkeypatch.setattr("pynws.urls.forc_url", mock_url)


async def fore(request):
    return aiohttp.web.json_response(data=FORECAST_RESPONSE)


async def test_nws_response(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get("/obs", obs)
    app.router.add_get("/stations", stn)
    app.router.add_get("/fore", fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=LATLON)
    stations = await nws.stations()
    nws.station = stations[0]
    observations = await nws.observations()
    forecast = await nws.forecast()

    nws2 = pynws.Nws(client, station="STNA")
    observations2 = await nws2.observations()


async def test_nws_response_no_obs(
    aiohttp_client, loop, obs_url, station_url, fore_url
):
    app = aiohttp.web.Application()
    app.router.add_get("/obs", no_obs)
    app.router.add_get("/stations", stn)
    app.router.add_get("/fore", fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=LATLON)
    stations = await nws.stations()
    nws.station = stations[0]
    observations = await nws.observations()
    assert not observations


async def test_nws_fail_stn(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get("/obs", obs)
    app.router.add_get("/stations", stn)
    app.router.add_get("/fore", fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.stations()


async def test_nws_fail_obs(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get("/obs", obs)
    app.router.add_get("/stations", stn)
    app.router.add_get("/fore", fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.observations()


async def test_nws_fail_fore(aiohttp_client, loop, obs_url, station_url, fore_url):
    app = aiohttp.web.Application()
    app.router.add_get("/obs", obs)
    app.router.add_get("/stations", stn)
    app.router.add_get("/fore", fore)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client)
    with pytest.raises(pynws.NwsError):
        stations = await nws.forecast()


@pytest.fixture()
def point_url(monkeypatch):
    def mock_url(a, b):
        return "/point"

    monkeypatch.setattr("pynws.urls.point_url", mock_url)


async def point(request):
    with open(os.path.join(DIR, "points.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


@pytest.fixture()
def grid_forecast_url(monkeypatch):
    def mock_url(a, b, c):
        return "/grid_forecast"

    monkeypatch.setattr("pynws.urls.grid_forecast_url", mock_url)


async def grid_forecast(request):
    with open(os.path.join(DIR, "grid_forecast.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


@pytest.fixture()
def grid_forecast_hourly_url(monkeypatch):
    def mock_url(a, b, c):
        return "/grid_forecast_hourly"

    monkeypatch.setattr("pynws.urls.grid_forecast_hourly_url", mock_url)


async def grid_forecast_hourly(request):
    with open(os.path.join(DIR, "grid_forecast_hourly.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_nws_point_response(aiohttp_client, loop, point_url):
    app = aiohttp.web.Application()
    app.router.add_get("/point", point)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=(30, -85))

    await nws.get_pointdata()

    assert nws.wfo == "TAE"
    assert nws.x == 59
    assert nws.y == 64
    assert nws.zone == "FLZ015"


async def test_nws_grid_forecast(aiohttp_client, loop, point_url, grid_forecast_url):
    app = aiohttp.web.Application()
    app.router.add_get("/grid_forecast", grid_forecast)
    app.router.add_get("/point", point)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=(30, -85))

    assert await nws.grid_forecast()

    assert nws.wfo == "TAE"
    assert nws.x == 59
    assert nws.y == 64


async def test_nws_grid_forecast_hourly(
    aiohttp_client, loop, point_url, grid_forecast_hourly_url
):
    app = aiohttp.web.Application()
    app.router.add_get("/grid_forecast_hourly", grid_forecast_hourly)
    app.router.add_get("/point", point)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=(30, -85))

    assert await nws.grid_forecast_hourly()

    assert nws.wfo == "TAE"
    assert nws.x == 59
    assert nws.y == 64


@pytest.fixture()
def alerts_url(monkeypatch):
    def mock_url(a):
        return "/alerts"

    monkeypatch.setattr("pynws.urls.alerts_zone_url", mock_url)


async def alerts(request):
    with open(os.path.join(DIR, "alerts.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


async def test_alerts(aiohttp_client, loop, point_url, alerts_url):
    app = aiohttp.web.Application()
    app.router.add_get("/alerts", alerts)
    app.router.add_get("/point", point)
    client = await aiohttp_client(app)
    nws = pynws.Nws(client, latlon=(30, -85))

    assert await nws.alerts_zone()

    assert nws.zone == "FLZ015"
