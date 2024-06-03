from satellite_image_handler.config.polygon_dict import POLYGON_DICT
from satellite_image_handler.utils.image_transformation import (
    RotateImage,
    PolygoneBoundariesImage,
)

from satellite_image_handler.abstract_satellite_image_handler.abstract_polymer_image_handler import (
    AbstractPolymerImageHandler,
)


class BouctouchePolymerImageHandler(AbstractPolymerImageHandler):
    @property
    def estuary_name(self):
        return "bouctouche"

    def _image_transformation_list(self):
        transform_list = [RotateImage(-45, self.before_transform_image_shape)]
        return transform_list

    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            POLYGON_DICT["bouctouche"],
            self._get_row_col_index_after_transformation_from_longitide_latitude,
        )


class CocagnePolymerImageHandler(AbstractPolymerImageHandler):
    @property
    def estuary_name(self):
        return "cocagne"

    def _image_transformation_list(self):
        transform_list = []
        return transform_list

    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            POLYGON_DICT["cocagne"],
            self._get_row_col_index_after_transformation_from_longitide_latitude,
        )


class WestPolymerImageHandler(AbstractPolymerImageHandler):
    @property
    def estuary_name(self):
        return "west"

    def _image_transformation_list(self):
        transform_list = []
        return transform_list

    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            POLYGON_DICT["west"],
            self._get_row_col_index_after_transformation_from_longitide_latitude,
        )


class DunkPolymerImageHandler(AbstractPolymerImageHandler):
    @property
    def estuary_name(self):
        return "dunk"

    def _image_transformation_list(self):
        transform_list = []
        return transform_list

    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            POLYGON_DICT["dunk"],
            self._get_row_col_index_after_transformation_from_longitide_latitude,
        )


class MorellPolymerImageHandler(AbstractPolymerImageHandler):
    @property
    def estuary_name(self):
        return "morell"

    def _image_transformation_list(self):
        transform_list = [RotateImage(-90, self.before_transform_image_shape)]
        return transform_list

    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            POLYGON_DICT["morell"],
            self._get_row_col_index_after_transformation_from_longitide_latitude,
        )
