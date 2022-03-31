import os

from setuptools import find_packages, setup

exec(open("pynws/version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pynws",
    version=__version__,
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MatthewFlamm/pynws",
    author="Matthew Flamm",
    author_email="matthewflamm0@gmail.com",
    description="Python library to retrieve observations and forecasts from NWS/NOAA",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "aiohttp",
        "metar",
    ],
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
