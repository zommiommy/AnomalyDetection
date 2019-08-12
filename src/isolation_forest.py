
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
        self.model_settings = model_settings
        self.models = {}

    def needs_training(self):
        return True

    def train(self, data, settings):
        self._check_data(data, settings["min_n_of_data_points"])
        logger.info("Training the Models")

        self.models["all"] = IF(**self.model_settings)
        stacked_data = np.column_stack(list(data.values()))
        self.models["all"].fit(stacked_data)

        for kpi, values in data.items():
            self.models[kpi] = IF(**self.model_settings)
            self.models[kpi].fit(values)

        logger.info("Models Trained")

    
    def set_seed(self, seed):
        logger.info("Setting the seed to [{seed}]".format(**locals()))
        random.seed(seed)
        np.random.seed(seed)

    def analyze(self, data, settings):
        self._check_data(data, settings["min_n_of_data_points"])
        logger.info("Setting the seed for reproducibility porpouses.")
        self.set_seed(settings["seed"])
        logger.info("Predicting the average anomalies scores for the data")

        results = {
            kpi : self.models[kpi].decision_function(values)
            for kpi, values in data.items()
        }

        stacked_data = np.column_stack(list(data.values()))
        results["all"] = self.models["all"].decision_function(stacked_data)

        return results