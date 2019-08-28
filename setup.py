import os
from setuptools import setup

exec(open('pynws/version.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pynws',
    version=__version__,
    license='MIT License',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MatthewFlamm/pynws',
    author='Matthew Flamm',
    author_email='matthewflamm0@gmail.com',
    description='Python library to retrieve observations and forecasts from NWS/NOAA',
    packages=['pynws'],
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'metar',
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"]
)
