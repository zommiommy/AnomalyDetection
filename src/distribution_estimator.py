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

class DistributionEstimator(ML_template):

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
                models.setdefault(selector, {})
                models[selector][hour] = {
                    "loc":np.nanmean(self._stack_data(values), axis=0),
                    "scale":np.nanstd(self._stack_data(values), axis=0)
                }
        return models

    def train(self, data):
        self._check_data(data, self.training_settings["min_n_of_data_points"])
        logger.info("Training the Models")
        self.models = self._train(self.models, data)
        logger.info("Models Trained")

    
    def set_seed(self, seed):
        logger.info(f"Setting the seed to [{seed}]")
        random.seed(seed)
        np.random.seed(seed)

    def analyze(self, data):
        self._check_data(data, self.analyisis_settings["min_n_of_data_points"])
        logger.info("self.analyisis_settings the seed for reproducibility porpouses.")
        self.set_seed(self.analyisis_settings["seed"])
        logger.info("Predicting the average anomalies scores for the data")
        # Degroup by hour
        output = {
            selector : {
                kpi: [
                    x
                    for hour in hours.keys()
                    for x in hours[hour][kpi]
                ]
                for kpi in hours[0].keys()
            }
            for selector, hours in data.items()
        }
        for selector, hours in data.items():
            output[selector].setdefault("score", [])
            for hour, values in hours.items():
                # Calculate the - log probability of the values assuming that they are independent (Usually just 1 feature so reasonable)
                score = -np.sum(norm.logpdf(self._stack_data(values), **self.models[selector][hour]), axis=1)
                output[selector]["score"].extend(score)

        return output

    
    def classify(self, data):
        logger.info("Classifying the scores")
        for selector, points in data.items():
            values = points["score"]
            # Calc the two thresholds for normals and anomalies
            normals   = np.nanquantile(values, self.classification_settings["normal_percentage"])
            logger.info(f"The normal quantile for the selector [{selector}] is [{normals}]")
            anomalies = np.nanquantile(values, self.classification_settings["anomaly_percentage"])
            logger.info(f"The anomaly quantile for the selector [{selector}] is [{anomalies}]")
            logger.info(f"The max score for [{selector}] is [{max(values)}]")
            # By default values are possible anomalies
            result = np.ones_like(values)
            result[values < normals] = 0
            result[values > anomalies] = 2
 
            if self.classification_settings["ignore_lower_values"]:
                logger.info("The analysis will defaults to normal points under the mean")
                # If the flag is set then the value below the mean are normal by defaults
                means = [self.models[selector][hour]["loc"] for hour in range(24)]
                mean_of_mean = np.nanmean(means)
                result[np.all(self._stack_data(points) < mean_of_mean, axis=1)] = 0

            data[selector]["class"] = result
        return data