# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import sys
import logging


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s') # %(asctime)s:
handler.setFormatter(formatter)
logger.addHandler(handler)

def setLevel(level):
    global handler
    global logger
    handler.setLevel(level=level)
    logger.setLevel(level=level)