"""
This is a module for querying weather data from the NWS/NOAA
asynchronously and organizing the data in an easier to use manner
"""

from .const import version
from .nws import *
from .simple_nws import SimpleNWS
