# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

def data_merger(time, scores, classes):
    return [   {
            "kpi":kpi,
            "score":s,
            "class":c,
            "time":t
        }
        for kpi in classes.keys()
            for s, c, t in zip(scores[kpi], classes[kpi], time) 
    ]