# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import sys
import random
import numpy as np
import pandas as pd
from scipy.stats import norm

from logger import logger
from ml_template import ML_template

from pprint import pprint

class DistributionEstimator(ML_template):

    def __init__(self, model_settings, read_settings):
        logger.info(f"Using model [{self.__class__.__name__}]")
        self.path  = model_settings.pop("model_file_format").format(**read_settings)
        logger.info("The model path is [{path}]".format(path=self.path))
        self.model_settings = model_settings
        self.models = {}

    def needs_training(self):
        return True

    def _stack_data(self, values):
        return np.column_stack([v for k, v in values.items() if k not in ["time", "score"]])

    def train(self, data, settings):
        self._check_data(data, settings["min_n_of_data_points"])
        logger.info("Training the Models")
        for selector, hours in data.items():
            for hour, values in hours.items():
                self.models.setdefault(selector, {})
                self.models[selector][hour] = {
                    "loc":np.mean(self._stack_data(values), axis=0),
                    "scale":np.std(self._stack_data(values), axis=0)
                }
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
            for hour, values in hours.items():
                # Calculate the - log probability of the values assuming that they are independent (Usually just 1 feature so reasonable)
                output[selector]["score"] = -np.sum(norm.logpdf(self._stack_data(values), **self.models[selector][hour]), axis=1)

        return output

    
    def classify(self, data, classification_settings):
        logger.info("Classifying the scores")
        for selector, points in data.items():
            values = points["score"]
            # Calc the two thresholds for normals and anomalies
            normals   = np.nanquantile(values, classification_settings["normal_percentage"])
            logger.info("The normal quantile for the selector [{selector}] is [{normals}]".format(**locals()))
            anomalies = np.nanquantile(values, classification_settings["anomaly_percentage"])
            logger.info("The anomaly quantile for the selector [{selector}] is [{anomalies}]".format(**locals()))
            # By default values are possible anomalies
            result = np.ones_like(values)
            result[values < normals] = 0
            result[values > anomalies] = 2
 
            if classification_settings["ignore_lower_values"]:
                logger.info("The analysis will defaults to normal points under the mean")
                # If the flag is set then the value below the mean are normal by defaults
                means = [self.models[selector][hour]["loc"] for hour in range(24)]
                mean_of_mean = np.mean(means)
                result[np.all(self._stack_data(points) < mean_of_mean, axis=1)] = 0

            data[selector]["class"] = result
        return data