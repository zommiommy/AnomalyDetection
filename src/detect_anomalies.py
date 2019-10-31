# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

from data_caster import transpose
from classifier import Classifier as CL
from database_adapter import DBAdapter as DB

# from isolation_forest import IsolationForest as ML
from time_estimator import TimeEstimator as ML


def detect_anomalies(input_db_settings, read_settings, training_settings, analyisis_settings, model_settings, classification_settings, output_db_settings, write_settings):

    db_in = DB(input_db_settings)
    data = db_in.get_data(read_settings)

    ml = ML(model_settings, read_settings, training_settings,  analyisis_settings, classification_settings)

    if ml.needs_training():
        train_data = db_in.get_training_data(training_settings)
        ml.train(train_data)

    scores  = ml.analyze(data)

    result = ml.classify(scores)

    db_out = DB(output_db_settings)
    db_out.write(result, write_settings, read_settings)


