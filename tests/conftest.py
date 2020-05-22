import os
import aiohttp
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_urls():
    with patch("pynws.urls.stations_observations_url") as mock_stations_observations_url, patch("pynws.urls.points_url") as mock_points_url, patch("pynws.urls.gridpoints_forecast_url") as mock_gridpoints_forecast_url, patch("pynws.urls.gridpoints_forecast_hourly_url") as mock_gridpoints_forecast_hourly_url, patch("pynws.urls.points_stations_url") as mock_points_stations_url:
        mock_stations_observations_url.return_value = "/stations_observations"
        mock_points_url.return_value = "/points"
        mock_gridpoints_forecast_url.return_value = "/gridpoints_forecast"
        mock_gridpoints_forecast_hourly_url.return_value = "/gridpoints_forecast_hourly"
        mock_points_stations_url.return_value = "/points_stations"
        yield mock_stations_observations_url, mock_points_url, mock_gridpoints_forecast_url, mock_gridpoints_forecast_hourly_url, mock_points_stations_url
