import os
from unittest.mock import patch

import aiohttp
import pytest


@pytest.fixture
def mock_urls():
    with patch(
        "pynws.urls.stations_observations_url"
    ) as mock_stations_observations_url, patch(
        "pynws.urls.stations_observations_latest_url"
    ) as mock_stations_observations_latest_url, patch(
        "pynws.urls.points_url"
    ) as mock_points_url, patch(
        "pynws.urls.forecast_all_url"
    ) as mock_forecast_all_url, patch(
        "pynws.urls.gridpoints_forecast_url"
    ) as mock_gridpoints_forecast_url, patch(
        "pynws.urls.gridpoints_forecast_hourly_url"
    ) as mock_gridpoints_forecast_hourly_url, patch(
        "pynws.urls.points_stations_url"
    ) as mock_points_stations_url, patch(
        "pynws.urls.alerts_active_zone_url"
    ) as mock_alerts_active_zone_url:
        mock_stations_observations_url.return_value = "/stations_observations"
        mock_stations_observations_latest_url.return_value = "/stations_observations_latest"
        mock_points_url.return_value = "/points"
        mock_forecast_all_url.return_value = "/gridpoints"
        mock_gridpoints_forecast_url.return_value = "/gridpoints_forecast"
        mock_gridpoints_forecast_hourly_url.return_value = "/gridpoints_forecast_hourly"
        mock_points_stations_url.return_value = "/points_stations"
        mock_alerts_active_zone_url.return_value = "/alerts_active_zone"

        yield mock_stations_observations_url, mock_stations_observations_latest_url, mock_points_url, mock_forecast_all_url, mock_gridpoints_forecast_url, mock_gridpoints_forecast_hourly_url, mock_points_stations_url, mock_alerts_active_zone_url
