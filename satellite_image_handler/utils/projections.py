import pyproj


def project_epsg4326_to_epsg_32620(longitude, latitude):
    """
    Projects geographic coordinates from EPSG:4326 (WGS84) to EPSG:32620 (UTM Zone 20N).

    Args:
        longitude (float): The longitude coordinate in decimal degrees.
        latitude (float): The latitude coordinate in decimal degrees.

    Returns:
        tuple: A tuple containing the projected UTM coordinates in EPSG:32620 (easting, northing).

    Raises:
        pyproj.exceptions.CRSError: If the coordinate transformation fails due to
        CRS (Coordinate Reference System) errors.

    Note:
        This function uses the pyproj library for coordinate transformations. Make sure to have pyproj installed.
    """
    wgs84 = pyproj.CRS("EPSG:4326")
    utm32620 = pyproj.CRS("EPSG:32620")
    transformer = pyproj.Transformer.from_crs(wgs84, utm32620, always_xy=True)
    return transformer.transform(longitude, latitude)


def project_epsg_32620_to_epsg4326(longitude, latitude):
    """
    Projects geographic coordinates from EPSG:32620 (UTM Zone 20N) to EPSG:4326 (WGS84).

    Args:
        longitude (float): The longitude coordinate in EPSG:32620.
        latitude (float): The latitude coordinate in EPSG:32620.

    Returns:
        tuple: A tuple containing the projected WGS84 coordinates in EPSG:4326 (easting, northing).

    Raises:
        pyproj.exceptions.CRSError: If the coordinate transformation fails due to
        CRS (Coordinate Reference System) errors.

    Note:
        This function uses the pyproj library for coordinate transformations. Make sure to have pyproj installed.
    """
    wgs84 = pyproj.CRS("EPSG:4326")
    utm32620 = pyproj.CRS("EPSG:32620")
    transformer = pyproj.Transformer.from_crs(utm32620, wgs84, always_xy=True)
    return transformer.transform(longitude, latitude)
