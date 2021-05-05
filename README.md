# AnomalyDetection
AnomalyDetection it's a plugin for Icinga to detect anomalies in datas.
It's under GPL2 license and it was developed for Würth Phoenix S.r.l.

Given the host and measurement it will detect if any anomlaies occurred in the detection time window set. If there is a plugin for the measurement it will be used, else the script will analyze the data from all the Numeric fields.
## Description

The script read the data from a measurement and write the analysis in a measurement with the same name of the one analyzed but with `_ml` appended.

The script try to infer the probability distribution of the data and classify them accordingly on how much they are "probable" (bayesian interpretation).

e.g.
![](https://github.com/zommiommy/AnomalyDetection/raw/master/doc/chi_quadro.png)

It expect the data to be in the form:
```
time         host            kpi                value
----         ----            ---                -----
1567005362   my.host.com     disk_utilization   0.9
```
and the result will be in the form:
```
time         host            kpi                class   score
----         ----            ---                -----   -----
1567005362   my.host.com     disk_utilization   1       1.5336
```

The data and it's classification will have the same ```time```. Each point in the time-frame will be analyzed and Classified.

So on Graphana it could be visualized as:
![](https://raw.githubusercontent.com/zommiommy/AnomalyDetection/master/doc/example.png)

The software specification and more informations (only in Italian for now) can be found [here](https://github.com/zommiommy/AnomalyDetection/raw/master/doc/WP_anomaly_detection_V1_1.pdf).

## Installation
In order to execute the script, there must be a python 3 environment with the followings modules installed:
```
Python 3.7.3
Package         Version 
--------------- --------
asn1crypto      0.24.0  
certifi         2019.3.9
cffi            1.12.2  
chardet         3.0.4   
conda           4.6.14  
cryptography    2.6.1   
idna            2.8     
influxdb        5.2.2   
joblib          0.13.2  
numpy           1.16.4  
pandas          0.24.2  
pip             19.0.3  
pycosat         0.6.3   
pycparser       2.19    
pyOpenSSL       19.0.0  
PySocks         1.6.8   
python-dateutil 2.8.0   
pytz            2019.1  
requests        2.21.0  
ruamel-yaml     0.15.46 
scikit-learn    0.21.2  
scipy           1.3.0   
setuptools      41.0.0  
six             1.12.0  
sklearn         0.0     
urllib3         1.24.1  
wheel           0.33.1  
```
This can be achieved in 3 ways:

- Have python 3 installed on the system and use pip to install all the needed modules if not already presents.
- Have python 3 installed and create a Virtual-Environment where the modules will be installed.
- Use the preconfigured python in ```check_time_env``` which is miniconda.

The last option allows the script to be installed without modifying anything in the system, this convinence is paid by the size of the folder which is ~500Mb.

## Update
Since the script do not have any dependancies beside his folder, in order to update the script a pull must be performed.
```
git pull
```

## Usage

To get more information about the script it can just be called with the ```-h / --help``` argument:
```$ ./anomalydetection -h       
usage: main.py [-h] [-v {0,1}] [--input-database INPUT_DATABASE]
               [--input-host INPUT_HOST] [--input-port INPUT_PORT]
               [--input-username INPUT_USERNAME]
               [--input-password INPUT_PASSWORD] [--input-ssl]
               [--input-verify-ssl] [--add-field ADD_FIELD]
               [--add-selector ADD_SELECTOR] [--exclude-field EXCLUDE_FIELD]
               [--timeframe TIMEFRAME]
               [--training-min-n-of-data-points TRAINING_MIN_N_OF_DATA_POINTS]
               [--training-timeframe TRAINING_TIMEFRAME]
               [--analysis-seed ANALYSIS_SEED]
               [--analysis-min-n-of-data-points ANALYSIS_MIN_N_OF_DATA_POINTS]
               [--model-file-format MODEL_FILE_FORMAT]
               [--model-contamination MODEL_CONTAMINATION]
               [--model-behaviour MODEL_BEHAVIOUR]
               [--model-n-of-jobs MODEL_N_OF_JOBS]
               [--model-n-of-estimators MODEL_N_OF_ESTIMATORS]
               [--classification-smoothing-windows-size CLASSIFICATION_SMOOTHING_WINDOWS_SIZE]
               [--classification-normal-percentage CLASSIFICATION_NORMAL_PERCENTAGE]
               [--classification-anomaly-percentage CLASSIFICATION_ANOMALY_PERCENTAGE]
               [--classification-ignore-lower-values]
               [--output-database OUTPUT_DATABASE] [--output-host OUTPUT_HOST]
               [--output-port OUTPUT_PORT] [--output-username OUTPUT_USERNAME]
               [--output-password OUTPUT_PASSWORD] [--output-ssl]
               [--output-verify-ssl] [--write-dry-run] [--write-to-file]
               [--output-file OUTPUT_FILE]
               [--write-measuremnt-name WRITE_MEASUREMNT_NAME]
               MEASUREMENT HOST

AnomalyDetector is a free software developed by Tommaso Fontana for Wurth
Phoenix S.r.l. under GPL-2 License. Given the host and measurement it will
detect if any anomlaies occurred in the detection time window set. If there is
a plugin for the measurement it will be used, else the script will analyze the
data from all the Numeric fields.

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1}, --verbosity {0,1}
                        set the logging verbosity, 0 == CRITICAL, 1 == INFO,
                        it defaults to ERROR.

input-db-settings:
  --input-database INPUT_DATABASE, -idb INPUT_DATABASE
                        The databse from where the data shall be read
  --input-host INPUT_HOST, -ih INPUT_HOST
                        The hostname / ip of the Influx DBMS
  --input-port INPUT_PORT, -ip INPUT_PORT
                        The port of the Influx DBMS
  --input-username INPUT_USERNAME, -iu INPUT_USERNAME
                        The username to use to login into the Influx DBMS
  --input-password INPUT_PASSWORD, -iP INPUT_PASSWORD
                        The password to use to login into the Influx DBMS
  --input-ssl, -issl    Whether to use ssl or else
  --input-verify-ssl, -ivs
                        Whether to use verify the ssl certificates or else

read-settings:
  MEASUREMENT           The measuremnt from where the data shall be read
  HOST                  The host from whom the data shall be filtered
  --add-field ADD_FIELD, -f ADD_FIELD
                        Add the field to the analysis. if this argument is not
                        setted then the script will use all the field of the
                        schema.
  --add-selector ADD_SELECTOR, -s ADD_SELECTOR
                        Add the selector to the analysis. This is the list of
                        fields that will be used to group the data for the
                        analysis
  --exclude-field EXCLUDE_FIELD, -e EXCLUDE_FIELD
                        Exclude the selected field from the analysis.
  --timeframe TIMEFRAME, -t TIMEFRAME
                        Select the timeframe relative to now of the analysis.
                        1d means that it will be used the data of the last
                        day.

training-settings:
  --training-min-n-of-data-points TRAINING_MIN_N_OF_DATA_POINTS, -tmdp TRAINING_MIN_N_OF_DATA_POINTS
                        The minimum number of points the training needs.
  --training-timeframe TRAINING_TIMEFRAME, -tt TRAINING_TIMEFRAME
                        Set the timeframe relative to now of the training. 1m
                        means that it will use the data of the last month.

analyisis-settings:
  --analysis-seed ANALYSIS_SEED, -as ANALYSIS_SEED
                        Set the seed for the analysis. This is done inorder to
                        have reproducible results.
  --analysis-min-n-of-data-points ANALYSIS_MIN_N_OF_DATA_POINTS, -amnodp ANALYSIS_MIN_N_OF_DATA_POINTS
                        The minimum number of points the analysis needs.

model-settings:
  --model-file-format MODEL_FILE_FORMAT, -mff MODEL_FILE_FORMAT
                        The path where to save the trained model, this is a
                        format string so it can be used {host} for the name of
                        the selected host and {measurement} for the
                        measurment, finally {date} for the date in which the
                        model was trained. If the path do not exist, the
                        folder will be created.
  --model-contamination MODEL_CONTAMINATION, -mc MODEL_CONTAMINATION
                        The percentage of outliers expected. By defaults is at
                        auto.
  --model-behaviour MODEL_BEHAVIOUR, -mb MODEL_BEHAVIOUR
                        Select which API the IsolationForest will use
  --model-n-of-jobs MODEL_N_OF_JOBS, -mnj MODEL_N_OF_JOBS
                        Number of core to be used for the analysis.
  --model-n-of-estimators MODEL_N_OF_ESTIMATORS, -mnf MODEL_N_OF_ESTIMATORS
                        The score is based on the mean path lenght, this
                        setting specify how many runs to use to extimate the
                        mean.

classification-settings:
  --classification-smoothing-windows-size CLASSIFICATION_SMOOTHING_WINDOWS_SIZE, -csws CLASSIFICATION_SMOOTHING_WINDOWS_SIZE
                        The size of the moving average used to smooth the data
  --classification-normal-percentage CLASSIFICATION_NORMAL_PERCENTAGE, -cnp CLASSIFICATION_NORMAL_PERCENTAGE
                        The probability that a random value (taken from an
                        uniform distribuiton) is classified as normal.
  --classification-anomaly-percentage CLASSIFICATION_ANOMALY_PERCENTAGE, -cap CLASSIFICATION_ANOMALY_PERCENTAGE
                        The probability that a random value (taken from an
                        uniform distribuiton) is classified as an anomaly.
  --classification-ignore-lower-values, -cilv
                        If this flag is setted the script will never detect
                        the values between the means as anomalous.

output-db-settings:
  --output-database OUTPUT_DATABASE, -odb OUTPUT_DATABASE
                        The databse from where the data shall be written
  --output-host OUTPUT_HOST, -oh OUTPUT_HOST
                        The hostname / ip of the Influx DBMS
  --output-port OUTPUT_PORT, -op OUTPUT_PORT
                        The port of the Influx DBMS
  --output-username OUTPUT_USERNAME, -ou OUTPUT_USERNAME
                        The username to use to login into the Influx DBMS
  --output-password OUTPUT_PASSWORD, -oP OUTPUT_PASSWORD
                        The password to use to login into the Influx DBMS
  --output-ssl, -ossl   Whether to use ssl or else
  --output-verify-ssl, -ovs
                        Whether to use verify the ssl certificates or else

write-settings:
  --write-dry-run, -dr  If this flag is setted the script will not write the
                        results on the output DB. It's mostly for testing.
  --write-to-file, -wtf
                        If this flag is setted the script will not write the
                        results on the output DB but on the JSON file setted
                        by the --output-file argument.
  --output-file OUTPUT_FILE, -of OUTPUT_FILE
                        The name of the output file that will be created if
                        the --write-to-fle flag is set.
  --write-measuremnt-name WRITE_MEASUREMNT_NAME, -wmn WRITE_MEASUREMNT_NAME
                        The name of the output measurement where the data will
                        be written, it's a format string where {measurement}
                        will be replaced with the name of the measurement from
                        which the data are read.

```

Except MEASUREMENT and HOST, all other arguments have defaults values, these defaults can be modified in the file ```src/arguments_settings.json```

### Executable
In order to execute the script it must follow the syntax:
```
python src/main.py 
```
And then adding the arguments after.

If the installation must be contained in the folder an useful trick is an executable bash script which find his current path (saved in the DIR variable) and then call the correct environment an script from there. 

e.g.
```Bash
#!/bin/bash
DIR=$(dirname "$(python -c "import os,sys; print(os.path.realpath(sys.argv[1]))" $0)")
$DIR/../env/bin/python $DIR/../src/main.py "$@"
```

## Future Improvements
The script is written with modularity in mind so the ```main.py``` is just a wrapper that take the arguments and pass them to the ```detect_anomalies``` function in the file ```src/detect_anomalies.py```.

So the same logic can be used as part of a bigger software.

Moreover the aforesaid function is ML-method angostic:

```python
def detect_anomalies(input_db_settings, read_settings, training_settings, analyisis_settings, model_settings, classification_settings, output_db_settings, write_settings):

    db_in = DB(input_db_settings)
    data = db_in.get_data(read_settings)

    ml = ML(model_settings, read_settings)

    if ml.needs_training():
        train_data = db_in.get_training_data(training_settings)
        ml.train(train_data, training_settings)

    scores  = ml.analyze(data, analyisis_settings)

    result = ml.classify(scores, classification_settings)

    db_out = DB(output_db_settings)
    db_out.write(result, write_settings, read_settings)
```

Therefore more detection methods can be implemented by creating classes that extends ```src/ml_template.py```

Other smaller improvements can be :

- Query Caching with expiring date
- Multiprocessing the analysis
- Adding the possibility to select different detection methods (Current one, Isolation Forest, ...)
- Model Caching

# Data flow

From Influx we get a list of dictionaries:
```
[
    {
        key:[]
    }
]
```

The data caster group the values by key (list of dict -> dict of dict of lists)
```
{
    selector:{
        key:[]
    }
}
```

Then it groups the lists by hour:
```
{
    selector:{
        ora:{
            chiave:np.array()
        }
    }
}
```

Analysis from the chosen ML method:
```
{
    selector:{
        ora:{
            "score" or "value":np.array()
            chiave:np.array()
        }
    }
}
```

Classification from the chosen ML method

```
{
    selector:{
        ora:{
            "class_1":np.array() # 1 if warning 0 if not
            "class_2":np.array() # 1 if anomaly 0 if not
            chiave:np.array()
        }
    }
}
```
