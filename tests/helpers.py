import json
import os

import aiohttp

DIR = "tests/fixtures"


def data_return_function(file_name):
    async def function(request):
        if isinstance(file_name, str):
            with open(os.path.join(DIR, file_name)) as f:
                return aiohttp.web.json_response(data=json.load(f))
        elif isinstance(file_name, list):
            with open(os.path.join(DIR, file_name.pop(0))) as f:
                return aiohttp.web.json_response(data=json.load(f))

    return function


def setup_app(
    gridpoints_stations="gridpoints_stations.json",
    points="points.json",
    stations_observations="stations_observations.json",
    stations_observations_latest="stations_observations_latest.json",
    detailed_forecast="detailed_forecast.json",
    gridpoints_forecast="gridpoints_forecast.json",
    gridpoints_forecast_hourly="gridpoints_forecast_hourly.json",
    alerts_active_zone="alerts_active_zone.json",
):
    app = aiohttp.web.Application()
    app.router.add_get(
        "/gridpoints_stations", data_return_function(gridpoints_stations)
    )
    app.router.add_get("/points", data_return_function(points))
    app.router.add_get(
        "/stations_observations", data_return_function(stations_observations)
    )
    app.router.add_get(
        "/stations_observations_latest",
        data_return_function(stations_observations_latest),
    )
    app.router.add_get("/gridpoints", data_return_function(detailed_forecast))
    app.router.add_get(
        "/gridpoints_forecast", data_return_function(gridpoints_forecast)
    )
    app.router.add_get(
        "/gridpoints_forecast_hourly", data_return_function(gridpoints_forecast_hourly)
    )
    app.router.add_get("/alerts_active_zone", data_return_function(alerts_active_zone))
    return app
