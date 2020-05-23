import json
import os

import aiohttp

def points_stations_data(request):
    with open(os.path.join("tests/fixtures/points_stations.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def points_data(request):
    with open(os.path.join("tests/fixtures/points.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def stations_observations_data(request):
    with open(os.path.join("tests/fixtures/stations_observations.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def gridpoints_forecast_data(request):
    with open(os.path.join("tests/fixtures/gridpoints_forecast.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def gridpoints_forecast_hourly_data(request):
    with open(os.path.join("tests/fixtures/gridpoints_forecast_hourly.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def alerts_active_zone_data(request):
    with open(os.path.join("tests/fixtures/alerts_active_zone.json"), "r") as f:
        return aiohttp.web.json_response(data=json.load(f))


def setup_app():
    app = aiohttp.web.Application()
    app.router.add_get("/points_stations", points_stations_data)
    app.router.add_get("/points", points_data)
    app.router.add_get("/stations_observations", stations_observations_data)
    app.router.add_get("/gridpoints_forecast", gridpoints_forecast_data)
    app.router.add_get("/gridpoints_forecast_hourly", gridpoints_forecast_hourly_data)
    app.router.add_get("/alerts_active_zone", alerts_active_zone_data)
    return app
