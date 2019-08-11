
import numpy as np
import pandas as pd

from logger import logger

class Classifier:
    def __init__(self, settings):
        self.settings = settings

    def smooth_data(self, data):
        logger.info("Smoothing the scores")
        n = self.settings["smoothing_window_size"]
        kernel = np.ones(n) / n
        return np.convolve(data, kernel)

    def filter_data(self, data):
        logger.info("Filtering the scores")
        return data

    def _classify(self, data):
        logger.info("Classifying the scores")
        # Calc the two thresholds for normals and anomalies
        normals   = np.nanquantile(data, self.settings["normal_percentage"])
        logger.info("The normal quantile is [{normals}]".format(**locals()))
        anomalies = np.nanquantile(data, self.settings["anomaly_percentage"])
        logger.info("The anomaly quantile is [{anomalies}]".format(**locals()))
        # By default data are possible anomalies
        result = np.ones_like(data)
        result[result < normals] = 0
        result[result > anomalies] = 2
        print(data)
        print(result)
        return result

    def classify(self, data):
        data = self.smooth_data(data)
        data = self.filter_data(data)
        classes = self._classify(data)
        return classes
