import json
import numpy
from pathlib import Path


class BridgePointsHandler:
    def __init__(self, points_path):
        points_list = []
        for path in Path(points_path).iterdir():
            with open(path, "r") as f:
                points_list.extend(json.load(f))
        self.points_list = numpy.array(points_list)

    def get_valid_points_mask(self, shape):
        mask = numpy.ones(shape, dtype=bool)
        mask[self.points_list[:, 0], self.points_list[:, 1]] = False
        return mask
