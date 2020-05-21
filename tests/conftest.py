import os
import aiohttp
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_urls():
    with patch("pynws.nws.obs_url") as mock_obs_url, patch("pynws.nws.points_url") as mock_points_url, patch("pynws.urls.grid_forecast_url") as mock_forecast_url, patch("pynws.urls.grid_forecast_hourly_url") as mock_forecast_hourly_url, patch("pynws.urls.stn_url") as mock_station_url:
        mock_obs_url.return_value = "/observation"
        mock_points_url.return_value = "/points"
        mock_forecast_url.return_value = "/gridpoints_forecast"
        mock_forecast_hourly_url.return_value = "/gridpoints_forecast_hourly"
        mock_station_url.return_value = "/stations"
        yield mock_obs_url, mock_points_url, mock_forecast_url, mock_forecast_hourly, mock_station_url


def stations_data(request):
    with open(os.path.join("fixtures/stations.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def points_data(request):
    with open(os.path.join("fixtures/points.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def observation_data(request):
    with open(os.path.join("fixtures/observation.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def gridpoints_forecast_data(request):
    with open(os.path.join("fixtures/sgridpoints_forecast.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def gridpoints_forecast_hourly_data(request):
    with open(os.path.join("fixtures/gridpoints_forecast_hourly.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def setup_app():
    app = aiohttp.web.Application()
    app.router.add_get("/stations", stations_data)
    app.router.add_get("/points", points_data)
    app.router.add_get("/observation", observation_data)
    app.router.add_get("/gridpoints_forecast", gridpoints_forecast_data)
    app.router.add_get("/gridpoints_forecast_hourly", gridpoints_forecast_hourly_data)
    return app
