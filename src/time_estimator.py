# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import sys
import random
import numpy as np
import pandas as pd
from scipy.stats import norm

from logger import logger
from cacher import cacher
from ml_template import ML_template

from pprint import pprint

class TimeEstimator(ML_template):

    def __init__(self, model_settings, read_settings, training_settings,  analyisis_settings, classification_settings):
        logger.info(f"Using model [{self.__class__.__name__}]")
        self.read_settings = read_settings
        self.training_settings = training_settings
        self.analyisis_settings = analyisis_settings
        self.classification_settings = classification_settings
        self.models = {}

    def needs_training(self):
        return True

    def _stack_data(self, values):
        return np.column_stack([v for k, v in values.items() if k not in ["time", "score"]])

    @cacher
    def _train(self, models, data):
        """This function has useless arguments for the cacher to identify different Calls"""
        for selector, hours in data.items():
            for hour, values in hours.items():
                if "value" not in values.keys():
                    logger.warning("Skipping the hour {} for the selector {}".format(hour, selector))
                    continue
                
                models.setdefault(selector, {})
                models[selector].setdefault(hour, 
                    {
                        "t_norm":np.nan,
                        "t_anom":np.nan
                    }
                )
                if len(values["time"]) > 0:
                    t_norm = np.nanquantile(values["value"], self.classification_settings["normal_percentage"])
                    t_anom = np.nanquantile(values["value"], self.classification_settings["anomaly_percentage"])
                    models[selector][hour] = {
                        "t_norm":t_norm,
                        "t_anom":t_anom,
                    }
                    logger.info(f'Normal  quantile [{self.classification_settings["normal_percentage"]}] is [{t_norm}]')
                    logger.info(f'Anomaly quantile [{self.classification_settings["anomaly_percentage"]}] is [{t_anom}]')
        return models

    def train(self, data):
        self._check_data(data, self.training_settings["min_n_of_data_points"])
        logger.info("Training the Models")
        self.models = self._train(self.models, data)
        logger.info(f"The final models are {self.models}")
        logger.info("Models Trained")

    
    def set_seed(self, seed):
        logger.info(f"Setting the seed to [{seed}]")
        random.seed(seed)
        np.random.seed(seed)

    def analyze(self, data):
        self._check_data(data, self.analyisis_settings["min_n_of_data_points"])
        logger.info("self.analyisis_settings the seed for reproducibility porpouses.")
        self.set_seed(self.analyisis_settings["seed"])
        return data

    
    def classify(self, data):
        logger.info("Classifying the scores")
        for selector, hours in data.items():
            for hour, values in hours.items():
                data[selector][hour].setdefault("class", [])
                if hour == "class":
                    continue
                if len(values["time"]) > 0:
                    
                    value = values["value"]

                    normals   = self.models[selector][hour]["t_norm"]
                    anomalies = self.models[selector][hour]["t_anom"]

                    # Compute the warnings
                    result = np.zeros_like(value)
                    if not np.isnan(normals):
                        result[np.logical_and(anomalies > value, value > normals)] = 1
                    data[selector][hour]["class_1"] = result
                                
                    # Compute the anomalies
                    result = np.zeros_like(value)
                    if not np.isnan(anomalies):
                        result[value >= anomalies] = 2
                    data[selector][hour]["class_2"] = result

        return data
