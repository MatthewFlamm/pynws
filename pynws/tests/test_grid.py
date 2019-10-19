"""Test observations"""

import pynws

LATLON = (0, 0)

WFO = 'TEST'
X = 1
Y = 1

async def test_point_url():
    """Observation url is correct"""
    assert (pynws.urls.point_url(*LATLON) == pynws.const.API_URL
            + pynws.const.API_POINT.format(*LATLON))


async def test_grid_forecast():
    """Observation url is correct"""
    assert (pynws.urls.grid_forecast_url(WFO, X, Y) == pynws.const.API_URL
            + pynws.const.API_GRID_FORECAST.format(WFO, X, Y))

async def test_grid_forecast_hourly():
    """Observation url is correct"""
    assert (pynws.urls.grid_forecast_hourly_url(WFO, X, Y) == pynws.const.API_URL
            + pynws.const.API_GRID_FORECAST_HOURLY.format(WFO, X, Y))
