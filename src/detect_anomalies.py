
from data_caster import transpose
from classifier import Classifier as CL
from database_adapter import DBAdapter as DB
from isolation_forest import IsolationForest as ML


def detect_anomalies(input_db_settings, read_settings, training_settings, analyisis_settings, model_settings, classification_settings, output_db_settings, write_settings):

    db_in = DB(input_db_settings)
    data = db_in.get_data(read_settings)
    
    print(data)

    ml = ML(model_settings, read_settings)

    if ml.needs_training():
        train_data = db_in.get_training_data(training_settings)
        ml.train(train_data, training_settings)

    scores  = ml.analyze(data, analyisis_settings)

    result = CL(classification_settings).classify(scores)

    db_out = DB(output_db_settings)
    db_out.write(result, write_settings, read_settings)


