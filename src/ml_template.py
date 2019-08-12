
import numpy as np

from logger import logger

class ML_template:
    def __init__(self, model_settings : dict):
        raise NotImplementedError()

    def needs_training() -> bool:
        raise NotImplementedError()
    
    def _check_data(self, data, minimum):
        for selector, points in data.items():
            for name, values in points.items():
                if values.size < minimum:
                    logger.error("The number of points is [{length}] which is less than the min required [{minimum}]".format(length=values.size, minimum=minimum))
                    sys.exit(1)

    def train(self, data : np.array, settings : dict) -> None:
        raise NotImplementedError()

    def set_seed(self, seed : int) -> None:
        raise NotImplementedError()

    def analyze(self, data : np.array, settings : dict) -> np.array:
        raise NotImplementedError()