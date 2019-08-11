
import numpy as np

def data_merger(host, scores, classes):
    return [
        {
            "kpi":"all",
            "score":s,
            "class":c
        }
        for s, c in zip(scores, classes)
    ]

def data_converter(data):
    """Covnert the data from a list of dictionaries to a numpy array"""
    return np.array([v for k, v in data.items()])

