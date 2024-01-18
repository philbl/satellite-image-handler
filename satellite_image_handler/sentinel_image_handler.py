from satellite_image_handler.abstract_satellite_image_handler.abstract_sentinel_image_handler import (
    AbstractSentinelImageHandler,
)

from satellite_image_handler.config.polygon_dict import POLYGON_DICT
from satellite_image_handler.utils.image_transformation import (
    RotateImage,
    PolygoneBoundariesImage,
    IdentityPolygoneBoundariesImage,
)


class GeneralSentinelImageHandler(AbstractSentinelImageHandler):
    @property
    def estuary_name(self):
        return "general"

    def _image_transformation_list(self):
        transform_list = []
        return transform_list

    def _image_wkt_polygone_subset(self):
        return IdentityPolygoneBoundariesImage()


class BouctoucheSentinelImageHandler(AbstractSentinelImageHandler):
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


class CocagneSentinelImageHandler(AbstractSentinelImageHandler):
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


class WestSentinelImageHandler(AbstractSentinelImageHandler):
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


class MorellSentinelImageHandler(AbstractSentinelImageHandler):
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


class DunkSentinelImageHandler(AbstractSentinelImageHandler):
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
