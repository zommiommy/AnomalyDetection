# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import sys
import time
import json
import numpy as np
from pprint import pprint
from influxdb import InfluxDBClient

from logger import logger
from data_caster import data_caster, epoch_to_iso
from cacher import cacher

def get_unique_combinations(list_of_dictionaries, selectors): 
    unique = [] 
    for item in [[(k, x[k]) for k in selectors] for x in list_of_dictionaries]: 
        if item not in unique: 
            unique.append(item) 
    return unique 

def transpose(lista):
    """Transpose a list of dictionaries to a dictionary of lists. 
       It assumes all the dictionaries have the sames keys."""
    _dict = {}
    for x in lista:
        for k, v in x.items():
            _dict.setdefault(k,[])
            _dict[k] += [v]
    return _dict


class DBAdapter:
    fields_query   = """SHOW FIELD KEYS ON "{database}" FROM "{measurement}" """
    tags_query     = """SHOW TAG KEYS ON "{database}" FROM "{measurement}" """
    data_query     = """SELECT {fields} FROM (SELECT * FROM "{measurement}" WHERE {host_field} = '{host}' AND time > (now() - {time}))"""

    def __init__(self, db_settings):
        self.settings = db_settings

    def _connect_to_db(self):
        if "client" not in dir(self):
            logger.info("Conneting to the DB on [{host}:{port}] for the database [{database}]".format(**self.settings))
            self.client = InfluxDBClient(**self.settings)

    def validate_settings(self, settings : dict):
        if any(any(c in value for c in """'#"%""") for value in settings.values()):
            logger.error("Bad character in a query field. Possibile SQL Injection test.")
            sys.exit(-1)
        return settings

    def exec_query(self, query : str):
        # Construct the query to workaround the tags distinct constraint
        logger.info("Executing query [%s]"%query)
        results = list(self.client.query(query).get_points())
        logger.info("The query results has %d rows"%len(results))
        return results

    def get_fields_types(self):
        logger.info("Querying the DB to get the types of each FIELDS in order to convert the data to the right type.")
        results = self.exec_query(self.fields_query.format(**{**self.settings,**self.read_settings}))
        self.fields = {x["fieldKey"] : x["fieldType"] for x in results}
        logger.info("Querying the DB to get the types of each TAGS in order to convert the data to the right type.")
        results = self.exec_query(self.tags_query.format(**{**self.settings,**self.read_settings}))
        self.tags = {x["tagKey"] : str for x in results}

        if "host" in self.fields.keys() or "host" in self.tags.keys():
            self.host_field = "host"
        else:
            self.host_field = "hostname"
        logger.info("Detected that the host value is called [{}]".format(self.host_field))

    def get_fields_to_parse(self):
        logger.info("Since no field was passed, the script will now get all the fields of the measurement")
        return [
            x
            for l in [self.fields.keys(), self.tags.keys()]
            for x in l
            if x not in [
                self.host_field
            ]
        ]

    def render_fields(self):
        self.get_fields_types()
        fields = self.read_settings["field"]
        if fields == []:
            fields = self.get_fields_to_parse()
        if "time" not in fields:
            fields.append("time")
        results = [x for x in fields if x not in self.read_settings["exclude"]]
        results.extend(self.read_settings["selectors"])
        logger.info(f"The fields rendered are [{results}]")
        return results


    def _group_data(self, results, read_settings):
        return  {
                    combination : [
                        x for x in results
                        if all (
                            x[selector] == value
                            for selector, value in zip(read_settings["selectors"], combination)
                        )
                    ]
                    for combination in {
                        tuple([
                            x[selector]
                            for selector in read_settings["selectors"]
                        ])
                        for x in results
                    }
                }
        
    
    def get_data(self, read_settings):
        self._connect_to_db()
        self.read_settings = self.validate_settings(read_settings)
        logger.info("Gathering the data to be analyzed")

        fields = self.render_fields()
        logger.info(f"The fields that will be analyzed are [{fields}]")

        results = self.exec_query(self.data_query.format(**read_settings, fields=", ".join(fields), host_field=self.host_field))
        results = self._group_data(results, read_settings)
        casted_results = data_caster(results)
        return casted_results
        
    @cacher
    def _get_training_data(self, training_settings, read_settings):
        """Dummy function with useless arguments for the cacher to be able to differentiate calls"""
        self._connect_to_db()
        settings = self.read_settings.copy()
        settings["time"] = training_settings["time"]

        # Get the data
        results = self.get_data(settings)

        return results

    def get_training_data(self, training_settings):
        return self._get_training_data(training_settings, self.read_settings)

    def write(self, results, write_settings, read_settings):
        self.read_settings = read_settings
        # I expect result to be a list of dictionaries
        # If the dry-run flag is set then do not write
        if write_settings["dry_run"]:
            logger.info("Dry-run flag set, then the results will not be written to the DB.")
            logger.info(f"The results are: {results}")
            return

        self._connect_to_db()
        self.get_fields_types()

        # Compose the name of the measurement
        name = write_settings["measurement_name"].format(**read_settings)
        host = read_settings["host"]

        # port the data to the influx standard
        results = [
                {
                    "measurement":name, 
                    "time": epoch_to_iso(values[0]),
                    "tags":{
                        self.host_field:host,
                        **dict(zip(read_settings["selectors"], combination))
                        
                    },
                    "fields": {
                        "score":float(),
                        "class":int(values[1]),
                        **{
                            field: values[i]
                            for field, i in zip(fields_to_parse, range(1, len(data.keys())))
                        }
                    }
                } 
                for combination, hours in results.items()
                for hour, data in hours.items()
                for values in zip(data["time"], data["class"], *[data[x] for x in data.keys() if x not in ["time", "class"]])
                if not np.isnan(s)
            ]
            
        if write_settings["write_to_file"]:
            filepath = write_settings["output_file"].format(**read_settings)
            logger.info("write-to-file flag set, then the results will not be written to the DB but on {}".format(filepath))
            with open(filepath, "w") as f:
                json.dump(results, f, indent=4)
            return

        logger.info("Writing results to the DB [{host}:{port}] on the measurement [{name}]".format(**self.settings, name=name))
        self.client.write_points(results)



    def __del__(self):
        """On exit / delation close the client connetion"""
        if "client" in dir(self):
            self.client.close()
