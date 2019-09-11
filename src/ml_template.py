# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.
import sys
import numpy as np

from logger import logger

class ML_template:
    def __init__(self, model_settings : dict):
        raise NotImplementedError()

    def needs_training() -> bool:
        raise NotImplementedError()
    
    def _check_data(self, data, minimum):
        for selector, hours in data.items():
            for hour, points in hours.items():
                for name, values in points.items():
                    if values.size < minimum:
                        logger.error(f"The number of points of [{selector} : {hour} : {name}] is [{values.size}] which is less than the min required [{minimum}]")
                        sys.exit(1)

    def train(self, data : np.array, settings : dict) -> None:
        raise NotImplementedError()

    def set_seed(self, seed : int) -> None:
        raise NotImplementedError()

    def analyze(self, data : np.array, settings : dict) -> np.array:
        raise NotImplementedError()

    def classify(self, data, classification_settings):
        raise NotImplementedError()