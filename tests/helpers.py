import json
import os

import aiohttp

DIR = "tests/fixtures"


def data_return_function(input):
    async def function(request):
        if isinstance(input, str):
            if "units" in request.query:
                input_name = "_".join((input, request.query["units"]))
            else:
                input_name = input
        elif isinstance(input, list):
            input0 = input.pop(0)
            if "units" in request.query:
                input_name = "_".join((input0, request.query["units"]))
            else:
                input_name = input0
            if isinstance(input0, str):
                pass
            elif issubclass(input0, Exception):
                raise input0
        else:
            raise TypeError("Unexpected input")
        with open(os.path.join(DIR, f"{input_name}.json")) as f:
            return aiohttp.web.json_response(data=json.load(f))

    return function


def setup_app(
    gridpoints_stations="gridpoints_stations",
    points="points",
    stations_observations="stations_observations",
    stations_observations_latest="stations_observations_latest",
    detailed_forecast="detailed_forecast",
    gridpoints_forecast="gridpoints_forecast",
    gridpoints_forecast_hourly="gridpoints_forecast_hourly",
    alerts_active_zone="alerts_active_zone",
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
