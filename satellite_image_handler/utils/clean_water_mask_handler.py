import pickle


class CleanWaterMaskHandler:
    def __init__(self, water_mask_path):
        with open(water_mask_path, "rb") as f:
            water_mask = pickle.load(f)
        self.water_mask = water_mask

    def get_valid_points_mask(self):
        return ~self.water_mask
