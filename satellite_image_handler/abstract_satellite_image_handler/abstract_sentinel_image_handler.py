from abc import ABC, abstractmethod
import rasterio
import numpy
import pickle
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from scipy import ndimage
from skimage.transform import rescale

from satellite_image_handler.utils.projections import (
    project_epsg4326_to_epsg_32620,
    project_epsg_32620_to_epsg4326,
)
from satellite_image_handler.utils.bridge_points_handler import BridgePointsHandler


class AbstractSentinelImageHandler(ABC):
    """
    Abstract base class for handling Sentinel satellite images.

    Attributes:
        BAND_NAME_MAPPING (dict): Mapping of band names to band codes.

    Methods:
        estuary_name (property): Name of the estuary.
        blue_band (property): Blue band data 10m.
        green_band (property): Green band data 10m.
        red_band (property): Red band data 10m.
        nir_band (property): NIR band data 10m.
        true_color_image (property): True Color Image 10m.
        scene_clf (property): Scene Classification. Resolution of 20m, rescale to 10m.
        water_mask (property): Water mask according to scene_clf.
        cloud_prob (property): Cloud probability data.
        cloud_coverage (property): Cloud coverage percentage.
        calculated_cloud_coverage (property): Calculated cloud coverage based on cloud probability.
        date (property): Date of the image.
        crs (property): Coordinate reference system (CRS) of the image.
        affine_matrix (property): Affine transformation matrix of the image.
        image_shape (property): Shape of the image.
        index_function: Index function for transforming coordinates.
        get_smoothed_water_mask: Smooth the water mask according to gaussian filter.
        get_row_col_index_from_longitude_latitude: Get row and column indices from longitude and latitude coordinates.
        get_rgb_float_true_color_image: Get RGB float true color image.
        _image_transformation_list: List of image transformations to apply.
        _image_wkt_polygon_subset: WKT representation of the polygon subset.
        _apply_image_transformation_list: Apply image transformations to the loaded data.
        _get_row_col_index_after_transformation_from_longitude_latitude:
            Get row and column indices after transformations.
        _apply_image_wkt_polygon_subset: Apply polygon subset transformation to the transformed data.
        _get_data_from_zip_file: Get image data from a zip file.
        save: Save the image handler object.
        load: Load an image handler object from a file.
    """

    BAND_NAME_MAPPING = {
        "blue_band": "B02",
        "green_band": "B03",
        "red_band": "B04",
        "nir_band": "B08",
        "true_color_image": "TCI",
        "cloud_prob": "MSK_CLDPRB_20m",
        "scene_clf": "SCL_20m",
    }

    def __init__(self, zip_path, bridge_points_handler=None):
        """
        Initialize the AbstractImageHandler object.

        Args:
            zip_path (str): Path to the zip file containing the image data.
            bridge_points_handler (BridgePointsHandler): Bridge points handler class or None
        """
        self.zip_path = zip_path
        self.bridge_points_handler = bridge_points_handler
        loaded_data_dict = self._get_data_from_zip_file(self.zip_path)
        self._before_transform_image_shape = loaded_data_dict[
            "blue_band"
        ].shape  # TODO Clean that
        self._date = loaded_data_dict["date"]
        self._cloud_coverage = loaded_data_dict["cloud_coverage"]
        self._crs = loaded_data_dict["crs"]
        self._affine_matrix = loaded_data_dict["affine_matrix"]
        transformed_data_dict = self._apply_image_transformation_list(loaded_data_dict)
        self._subset_transformed_data_dict = self._apply_image_wkt_polygone_subset(
            transformed_data_dict
        )

    @property
    def atmoshperic_correction(self):
        """
        Name of the Atmoshperic Correction.

        Returns:
            str: Atmoshperic Correction
        """
        return "Sen2Cor"

    @property
    @abstractmethod
    def estuary_name(self):
        """
        Name of the estuary.

        Returns:
            str: Estuary name.
        """

    @property
    def blue_band(self):
        """
        Blue band data.

        Returns:
            numpy.ndarray: Blue band data.
        """
        return self._subset_transformed_data_dict["blue_band"]

    @property
    def green_band(self):
        """
        Green band data.

        Returns:
            numpy.ndarray: Green band data.
        """
        return self._subset_transformed_data_dict["green_band"]

    @property
    def red_band(self):
        """
        Red band data.

        Returns:
            numpy.ndarray: Red band data.
        """
        return self._subset_transformed_data_dict["red_band"]

    @property
    def nir_band(self):
        """
        NIR band data.

        Returns:
            numpy.ndarray: NIR band data.
        """
        return self._subset_transformed_data_dict["nir_band"]

    @property
    def true_color_image(self):
        """
        True Color Image.

        Returns:
            numpy.ndarry: True Color Image.
        """
        return self._subset_transformed_data_dict["true_color_image"]

    @property
    def cloud_prob(self):
        """
        Cloud probability data.

        Returns:
            numpy.ndarray: Cloud probability data.
        """
        return self._subset_transformed_data_dict["cloud_prob"]

    @property
    def scene_clf(self):
        """
        Scene Classification.
        mapping is:
            0: No Data
            1: Saturated or Defective
            2: Dark area pixels
            3: Cloud Shadows
            4: Vegetation
            5: non-Vegetated
            6: Water
            7: Unclassified
            8: Cloud medium Probability
            9: Cloud high Probability
            10: Thin cirrus
            11: Snow

        Returns:
            numpy.ndarray: Cloud probability data.
        """
        return self._subset_transformed_data_dict["scene_clf"]

    @property
    def water_mask(self):
        """
        Mask of water pixel according to the scene clf
        """
        return self.scene_clf == 6

    @property
    def cloud_coverage(self):
        """
        Cloud coverage percentage.

        Returns:
            float: Cloud coverage percentage.
        """
        return self._cloud_coverage

    @property
    def calculated_cloud_coverage(self):
        """
        Calculated cloud coverage based on cloud probability.

        Returns:
            float: Calculated cloud coverage percentage.
        """
        return (self._subset_transformed_data_dict["cloud_prob"] > 10).mean()

    @property
    def date(self):
        """
        Date of the image.

        Returns:
            str: Date of the image.
        """
        return self._date

    @property
    def crs(self):
        """
        Coordinate reference system (CRS) of the image.

        Returns:
            str: Coordinate reference system (CRS) of the image.
        """
        return self._crs

    @property
    def affine_matrix(self):
        """
        Affine transformation matrix of the image.

        Returns:
            numpy.ndarray: Affine transformation matrix of the image.
        """
        return self._affine_matrix

    @property
    def before_transform_image_shape(self):
        """
        Shape of the image before transformation.

        Returns:
            tuple: Shape of the image.
        """
        return self._before_transform_image_shape

    @property
    def image_shape(self):
        """
        Shape of the image.

        Returns:
            tuple: Shape of the image.
        """
        return self.blue_band.shape  # TODO Clean that

    def get_mask_from_bridge_points_handler(self):
        if isinstance(self.bridge_points_handler, BridgePointsHandler):
            return self.bridge_points_handler.get_valid_points_mask(self.image_shape)
        else:
            return None

    def get_smoothed_water_mask(self, sigma=2, threshold=0.75):
        return (
            ndimage.gaussian_filter(self.water_mask.astype(float), sigma=sigma)
            > threshold
        )

    @abstractmethod
    def _image_transformation_list(self):
        """
        List of image transformations to apply.

        Returns:
            list: List of image transformations to apply.
        """

    @abstractmethod
    def _image_wkt_polygone_subset(self):
        """
        WKT representation of the polygon subset.

        Returns:
            str: WKT representation of the polygon subset.
        """

    def index_function(self, longitude, latitude):
        """
        Transforms the given longitude and latitude coordinates to row and column indices
        based on the affine transformation matrix.

        Parameters:
            longitude (float): The longitude coordinate.
            latitude (float): The latitude coordinate.

        Returns:
            tuple: A tuple containing the transformed row and column indices as integers.

        Notes:
            This function applies an inverse affine transformation to convert the given
            longitude and latitude coordinates into row and column indices. The transformation
            is based on the affine transformation matrix stored in the instance variable
            `affine_matrix`. The transformed indices are rounded to the nearest integer values.

        Example:
            >>> handler = AbstractImageHandler(zip_path)
            >>> row, col = handler.index_function(-64.12345, 46.98765)
            >>> print(row, col)
            4321, 1234
        """
        # Invert the affine transformation
        inv_affine = ~self.affine_matrix

        # Transform the x, y input coordinates
        transformed_coords = inv_affine * (longitude, latitude)

        # Round the transformed coordinates to the nearest integer indices
        row_index = int(transformed_coords[1])
        col_index = int(transformed_coords[0])

        # Return the transformed indices
        return row_index, col_index

    def inverse_index_function(self, row_index, col_index):
        """
        Transforms the given row and column indices to longitude and latitude coordinates
        based on the affine transformation matrix.

        Parameters:
            row_index (int): The row indice.
            col_index (int): The column indice.

        Returns:
            tuple: A tuple containing the longitude and latitude coordinates.

        Notes:
            This function applies an affine transformation to convert the given
            row and column indice into longitude and latitude coordinates. The transformation
            is based on the affine transformation matrix stored in the instance variable
            `affine_matrix`.

        Example:
            >>> handler = AbstractImageHandler(zip_path)
            >>> row, col = handler.index_function(-64.12345, 46.98765)
            >>> print(row, col)
            4321, 1234
        """
        longitude, latitude = (col_index, row_index) * self.affine_matrix

        return longitude, latitude

    def _apply_image_transformation_list(self, loaded_data_dict):
        """
        Apply image transformations to the loaded data.

        Args:
            data_dict (dict): Dictionary containing the loaded image data.

        Returns:
            dict: Dictionary containing the transformed image data.
        """
        transformed_data_dict = {}
        for band_name in self.BAND_NAME_MAPPING.keys():
            band = loaded_data_dict.pop(band_name)
            for transformation in self._image_transformation_list():
                band = transformation.apply_transformation_to_band(band)
            transformed_data_dict[band_name] = band
            del band
        return transformed_data_dict

    def _get_row_col_index_after_transformation_from_longitide_latitude(
        self, longitude, latitude
    ):
        """
        Get row and column indices after transformations.

        Args:
            lon (float): Longitude coordinate.
            lat (float): Latitude coordinate.

        Returns:
            tuple: Row and column indices.
        """
        projected_longitude, projected_latitute = project_epsg4326_to_epsg_32620(
            longitude, latitude
        )
        row_index, col_index = self.index_function(
            projected_longitude, projected_latitute
        )
        for transformation in self._image_transformation_list():
            (
                row_index,
                col_index,
            ) = transformation.apply_transformation_to_geocoordinates(
                row_index, col_index
            )
        return row_index, col_index

    def _apply_image_wkt_polygone_subset(self, transformed_data_dict):
        """
        Apply polygon subset transformation to the transformed data.

        Args:
            transformed_data_dict (dict): Dictionary containing the transformed image data.

        Returns:
            dict: Dictionary containing the subset transformed image data.
        """
        polygone_subset_data_dict = {}
        for band_name in self.BAND_NAME_MAPPING.keys():
            band = transformed_data_dict.pop(band_name)
            band = self._image_wkt_polygone_subset().apply_transformation_to_band(band)
            polygone_subset_data_dict[band_name] = band
            del band
        return polygone_subset_data_dict

    def get_row_col_index_from_longitide_latitude(self, longitude, latitude):
        """
        Get row and column indices from longitude and latitude coordinates.

        Args:
            lon (float): Longitude coordinate.
            lat (float): Latitude coordinate.

        Returns:
            tuple: Row and column indices.
        """
        (
            row_index,
            col_index,
        ) = self._get_row_col_index_after_transformation_from_longitide_latitude(
            longitude, latitude
        )
        (
            row_index,
            col_index,
        ) = self._image_wkt_polygone_subset().apply_transformation_to_geocoordinates(
            row_index, col_index
        )
        return row_index, col_index

    def get_longitude_latitude_from_row_col_index(self, row_index, col_index):
        (
            row_index,
            col_index,
        ) = self._image_wkt_polygone_subset().apply_inverse_transformation_to_geocoordinate(
            row_index, col_index
        )
        for transformation in self._image_transformation_list():
            (
                row_index,
                col_index,
            ) = transformation.apply_inverse_transformation_to_geocoordinate(
                row_index, col_index
            )
        projected_longitude, projected_latitute = self.inverse_index_function(
            row_index, col_index
        )
        longitude, latitude = project_epsg_32620_to_epsg4326(
            projected_longitude, projected_latitute
        )
        return longitude, latitude

    def get_rgb_float_true_color_image(self, beta=3000):
        """
        Get RGB float true color image.

        Returns:
            numpy.ndarray: RGB float true color image.
        """
        blue_float = numpy.clip(self.blue_band / beta, 0, 1)
        green_float = numpy.clip(self.green_band / beta, 0, 1)
        red_float = numpy.clip(self.red_band / beta, 0, 1)

        rgb = numpy.dstack((red_float, green_float, blue_float))
        return rgb

    def _get_data_from_zip_file(self, zip_path):
        """
        Get image data from a zip file.

        Args:
            zip_path (str): Path to the zip file.

        Returns:
            dict: Dictionary containing the image data.
        """
        zip_path = str(Path(zip_path))
        zip_format_path = f"zip+file:{zip_path}!"
        meta_data_path = str(
            Path(zip_path.split("\\")[-1].replace("zip", "SAFE"), "MTD_MSIL2A.xml")
        ).replace("\\", "/")
        with zipfile.ZipFile(Path(zip_path), "r") as f:
            meta_data = ET.fromstring(str(f.read(meta_data_path), "UTF-8"))
            all_file_name = f.filelist
        general_info = meta_data.find(
            "{https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd}General_Info"
        )
        product_info = general_info.find("Product_Info")
        date = product_info.find("PRODUCT_START_TIME").text

        quality_ind = meta_data.find(
            "{https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd}Quality_Indicators_Info"
        )
        cloud_coverage = float(quality_ind.find("Cloud_Coverage_Assessment").text)

        data_dict = {"date": date, "cloud_coverage": cloud_coverage}

        granule_file = list(
            filter(lambda file: "GRANULE" in file.filename, all_file_name)
        )
        R10m_file = list(filter(lambda file: "R10m" in file.filename, granule_file))
        for band_name, band_code in self.BAND_NAME_MAPPING.items():
            file_list = (
                granule_file if band_name in ["cloud_prob", "scene_clf"] else R10m_file
            )
            path = list(filter(lambda file: band_code in file.filename, file_list))[
                0
            ].filename
            if band_name == "true_color_image":
                with rasterio.open(
                    Path(zip_format_path, path), driver="JP2OpenJPEG"
                ) as src:
                    band = src.read()
                band = numpy.moveaxis(band, 0, -1)
            else:
                with rasterio.open(
                    Path(zip_format_path, path), driver="JP2OpenJPEG"
                ) as src:
                    band = src.read(1)
            data_dict[band_name] = band
            if band_name == "blue_band":
                with rasterio.open(
                    Path(zip_format_path, path), driver="JP2OpenJPEG"
                ) as src:
                    crs = src.crs
                    affine_matrix = src.transform
        data_dict["crs"] = str(crs)
        data_dict["affine_matrix"] = affine_matrix

        data_dict["cloud_prob"] = rescale(
            data_dict["cloud_prob"], 2, preserve_range=True, order=0
        )
        data_dict["scene_clf"] = rescale(
            data_dict["scene_clf"], 2, preserve_range=True, order=0
        )

        return data_dict

    def save(self, saving_folder):
        """
        Save the image handler object to a file.

        Args:
            saving_folder (str): Path to the output folder.
        """
        saving_name = f"{self.estuary_name}_{self.date.split('T')[0]}.pkl"
        with open(Path(saving_folder, saving_name), "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, file_path):
        """
        Load an image handler object from a file.

        Args:
            file_path (str): Path to the input file.

        Returns:
            AbstractImageHandler: Loaded image handler object.
        """
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
        return obj
