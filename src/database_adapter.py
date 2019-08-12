
import sys
import time
from pprint import pprint
from influxdb import InfluxDBClient

from logger import logger
from data_caster import data_caster, epoch_to_iso

class DBAdapter:
    fields_query   = """SHOW FIELD KEYS ON "{database}" FROM "{measurement}" """
    data_query     = """SELECT {fields} FROM (SELECT * FROM "{measurement}" WHERE hostname = '{host}' AND time > (now() - {time}))"""

    def __init__(self, db_settings):
        self.settings = db_settings

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
        logger.info("Querying the DB to get the types of each fields in order to convert the data to the right type.")
        results = self.exec_query(self.fields_query.format(**{**self.settings,**self.read_settings}))
        self.fields = {x["fieldKey"] : x["fieldType"] for x in results}

    def get_fields_to_parse(self):
        logger.info("Since no field was passed, the script will now get all the fields of the measurement")
        return [
            x
            for x in self.fields.keys()
            if x not in [
                "hostname"
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
        logger.info("The fields rendered are [{results}]".format(**locals()))
        return results

    def get_data(self, read_settings):
        self.read_settings = self.validate_settings(read_settings)
        logger.info("Gathering the data to be analyzed")

        fields = self.render_fields()
        logger.info("The fields that will be analyzed are [{fields}]".format(**locals()))

        results = self.exec_query(self.data_query.format(**read_settings, fields=", ".join(fields)))
        casted_results = data_caster(results)
        return casted_results.pop("time"), casted_results

    def get_training_data(self, training_settings):
        settings = self.read_settings.copy()
        settings["time"] = training_settings["time"]

        # Get the data
        _, results = self.get_data(settings)

        return results

    def write(self, results, write_settings, read_settings):
        # I expect result to be a list of dictionaries
        # If the dry-run flag is set then do not write
        if write_settings["dry_run"]:
            logger.info("Dry-run flag set, then the results will not be written to the DB.")
            return

        # Compose the name of the measurement
        name = write_settings["measurement_name"].format(**read_settings)
        host = read_settings["host"]

        t = epoch_to_iso(time.time())
        # port the data to the influx standard
        results = [
                {
                    "measurement":name, 
                    "time": epoch_to_iso(x.pop("time")),
                    "tags":{
                        "host":host,
                        "kpi":x.pop("kpi")
                    },
                    "fields": {
                        **x
                    }
                } for x in results
            ]

        logger.info("Writing results to the DB [{host}:{port}] on the measurement [{name}]".format(**self.settings, name=name))
        self.client.write_points(results)



    def __del__(self):
        """On exit / delation close the client connetion"""
        if "client" in dir(self):
            self.client.close()