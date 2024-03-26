from setuptools import setup

setup(
    name="satellite-image-handler",
    version="0.4.0",
    description="Package to handle satellite image",
    url="https://github.com/philbl/satellite-image-handler",
    author="Philippe Blouin-Leclerc",
    author_email="phil.19013@gmail.com",
    install_requires=[
        "geopandas==0.12.2",
        "netCDF4==1.6.5",
        "numpy==1.26.0",
        "pandas==2.1.0",
        "rasterio==1.3.6",
        "scikit-image==0.20.0",
    ],
)
