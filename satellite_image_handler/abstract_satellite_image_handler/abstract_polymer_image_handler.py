from abc import ABC, abstractmethod
from netCDF4 import Dataset
import numpy
from skimage.util import img_as_ubyte

from satellite_image_handler.utils.bridge_points_handler import BridgePointsHandler
from satellite_image_handler.utils.clean_water_mask_handler import CleanWaterMaskHandler


class AbstractPolymerImageHandler(ABC):
    BAND_NAME_MAPPING = {
        "blue_band": ["Rw490"],
        "green_band": ["Rw560"],
        "red_band": ["Rw665"],
        "nir_band": ["Rw842"],
        "swir_band": ["Rnir"],
        # "swir2_band": ["rhos_2186", "rhos_2202"],
        "lon": ["longitude"],
        "lat": ["latitude"],
    }

    def __init__(self, path, bridge_points_handler=None, clean_water_mask_handler=None):
        self.path = path
        self.bridge_points_handler = bridge_points_handler
        self.clean_water_mask_handler = clean_water_mask_handler
        loaded_data_dict = self._load_nc_data_dict(self.path)
        self._before_transform_image_shape = loaded_data_dict[
            "blue_band"
        ].shape  # TODO Clean that
        self._date = loaded_data_dict["date"]
        transformed_data_dict = self._apply_image_transformation_list(loaded_data_dict)
        self._transformed_lon = transformed_data_dict["lon"]
        self._transformed_lat = transformed_data_dict["lat"]
        self._subset_transformed_data_dict = self._apply_image_wkt_polygone_subset(
            transformed_data_dict
        )
        del self._transformed_lon
        del self._transformed_lat
        self._subset_transformed_data_dict[
            "true_color_image"
        ] = self._get_true_color_image()
        # self._subset_transformed_data_dict.pop("blue_band")
        # self._subset_transformed_data_dict.pop("green_band")
        # self._subset_transformed_data_dict.pop("red_band")

    @property
    def atmoshperic_correction(self):
        """
        Name of the Atmoshperic Correction.
        Returns:
            str: Atmoshperic Correction
        """
        return "Polymer"

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
    def swir_band(self):
        """
        SWIR band data.

        Returns:
            numpy.ndarray: SWIR band data.
        """
        return self._subset_transformed_data_dict["swir_band"]

    # @property
    # def swir2_band(self):
    #     """
    #     SWIR band data.

    #     Returns:
    #         numpy.ndarray: SWIR band data.
    #     """
    #     return self._subset_transformed_data_dict["swir2_band"]

    @property
    def true_color_image(self):
        """
        True Color Image.

        Returns:
            numpy.ndarry: True Color Image.
        """
        return self._subset_transformed_data_dict["true_color_image"]

    @property
    def lon(self):
        """
        Longitude band data.

        Returns:
            numpy.ndarray: Lon band data.
        """
        return self._subset_transformed_data_dict["lon"]

    @property
    def lat(self):
        """
        Latitude band data.

        Returns:
            numpy.ndarray: Lat band data.
        """
        return self._subset_transformed_data_dict["lat"]

    @property
    def date(self):
        """
        Date of the image.

        Returns:
            str: Date of the image.
        """
        return self._date.replace(" ", "T")

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
        return self.nir_band.shape  # TODO Clean that

    def get_mask_from_bridge_points_handler(self):
        if isinstance(self.bridge_points_handler, BridgePointsHandler):
            return self.bridge_points_handler.get_valid_points_mask(self.image_shape)
        else:
            return None

    def get_mask_from_clean_water_mask_handler(self):
        if isinstance(self.clean_water_mask_handler, CleanWaterMaskHandler):
            return self.clean_water_mask_handler.get_valid_points_mask()
        else:
            return None

    def get_water_mask_from_bridge_and_clean_water_mask_handler(self):
        water_mask = []
        if isinstance(self.bridge_points_handler, BridgePointsHandler) and isinstance(
            self.clean_water_mask_handler, CleanWaterMaskHandler
        ):
            water_mask.append(
                self.bridge_points_handler.get_valid_points_mask(self.image_shape)
            )
            water_mask.append(~self.clean_water_mask_handler.get_valid_points_mask())
            return numpy.all(water_mask, axis=0)
        else:
            return None

    def _get_true_color_image(self):
        scale_in = 0, 0.15
        scale_cur = [scale_in[0], scale_in[1]]
        bsc = numpy.asarray(scale_cur)
        r_tmp = numpy.interp(self.red_band, bsc, [0, 1])
        g_tmp = numpy.interp(self.green_band, bsc, [0, 1])
        b_tmp = numpy.interp(self.blue_band, bsc, [0, 1])
        tci = numpy.concatenate([[r_tmp], [g_tmp], [b_tmp]]).transpose(1, 2, 0)
        return img_as_ubyte(tci)

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
        nc_lon = self.lon
        nc_lat = self.lat
        londiff = (longitude - nc_lon) ** 2
        latdiff = (latitude - nc_lat) ** 2
        diff = londiff + latdiff
        x, y = numpy.where(diff == diff.min())
        x = x[0]
        y = y[0]
        return x, y

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
        nc_lon = self._transformed_lon
        nc_lat = self._transformed_lat
        londiff = (longitude - nc_lon) ** 2
        latdiff = (latitude - nc_lat) ** 2
        diff = londiff + latdiff
        x, y = numpy.where(diff == diff.min())
        x = x[0]
        y = y[0]
        return x, y

    def get_longitude_latitude_from_row_col_index(self, row_index, col_index):
        lon = self.lon[row_index, col_index]
        lat = self.lat[row_index, col_index]
        return lon, lat

    def _load_nc_data_dict(self, path):
        nc_data = Dataset(path)
        data_dict = {"date": nc_data.sensing_time}
        for band_name, band_code_list in self.BAND_NAME_MAPPING.items():
            data_dict[band_name] = self.get_items_with_list_fallback(
                nc_data.variables, band_code_list
            )[:].data
        nc_data.close()
        return data_dict

    @staticmethod
    def get_items_with_list_fallback(d, get_list):
        for elem in get_list:
            value = d.get(elem)
            if value is not None:
                return value
        raise ValueError
