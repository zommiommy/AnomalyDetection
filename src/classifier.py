# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import numpy as np
import pandas as pd

from logger import logger

class Classifier:
    def __init__(self, settings):
        self.settings = settings


    def _classify(self, data):
        logger.info("Classifying the scores")
        for selector, points in data.items():
            values = points["score"]
            # Calc the two thresholds for normals and anomalies
            normals   = np.nanquantile(values, self.settings["normal_percentage"])
            logger.info(f"The normal quantile for the selector [{selector}] is [{normals}]")
            anomalies = np.nanquantile(values, self.settings["anomaly_percentage"])
            logger.info(f"The anomaly quantile for the selector [{selector}] is [{anomalies}]")
            # By default values are possible anomalies
            result = np.ones_like(values)
            result[result < normals] = 0
            result[result > anomalies] = 2
            data[selector]["class"] = result
        
        return data

    def classify(self, data):
        classes = self._classify(data)
        return classes
