
import sys
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest as IF

from logger import logger
from ml_template import ML_template

class IsolationForest(ML_template):

    def __init__(self, model_settings, read_settings):
        self.path  = model_settings.pop("model_file_format").format(**read_settings)
        logger.info("The model path is [{path}]".format(path=self.path))
        self.model = IF(**model_settings)

    def _check_data(self, data, minimum):
        if data.shape[1] < minimum:
            logger.error("The number of points is [{length}] which is less than the min required [{minimum}]".format(length=data.shape[1], minimum=minimum))
            sys.exit(1)

    def needs_training(self):
        return True

    def train(self, data, settings):
        self._check_data(data, settings["min_n_of_data_points"])
        logger.info("Training the Model")
        self.model.fit(data)
        logger.info("Model Trained")
    
    def set_seed(self, seed):
        logger.info("Setting the seed to [{seed}]".format(**locals()))
        random.seed(seed)
        np.random.seed(seed)

    def analyze(self, data, settings):
        self._check_data(data, settings["min_n_of_data_points"])
        logger.info("Setting the seed for reproducibility porpouses.")
        self.set_seed(settings["seed"])
        logger.info("Predicting the average anomalies scores for the data")
        return self.model.decision_function(data)