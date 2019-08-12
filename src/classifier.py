
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
        return {
            kpi : np.convolve(values, kernel)
            for kpi, values in data.items()
        }

    def filter_data(self, data):
        logger.info("Filtering the scores")
        return data

    def _classify(self, data):
        logger.info("Classifying the scores")
        output = {}
        for kpi, values in data.items():
            # Calc the two thresholds for normals and anomalies
            normals   = np.nanquantile(values, self.settings["normal_percentage"])
            logger.info("The normal quantile for the kpi [{kpi}] is [{normals}]".format(**locals()))
            anomalies = np.nanquantile(values, self.settings["anomaly_percentage"])
            logger.info("The anomaly quantile for the kpi [{kpi}] is [{anomalies}]".format(**locals()))
            # By default values are possible anomalies
            result = np.ones_like(values)
            result[result < normals] = 0
            result[result > anomalies] = 2
            output[kpi] = result
        
        return output

    def classify(self, data):
        data = self.smooth_data(data)
        data = self.filter_data(data)
        classes = self._classify(data)
        return classes
