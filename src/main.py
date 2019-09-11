# AnomalyDetection is a free software developed by Tommaso Fontana for Würth Phoenix S.r.l. under GPL-2 License.

import json
import logging
import argparse


from logger import setLevel
from detect_anomalies import detect_anomalies

# Table of type conversion
cast_type = {
    "bool":bool,
    "int":int,
    "float":float,
    "str":str
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""AnomalyDetector is a free software developed by Tommaso Fontana for Wurth Phoenix S.r.l. under GPL-2 License.
Given the host and measurement it will detect if any anomlaies occurred in the detection time window set.
If there is a plugin for the measurement it will be used, else the script will analyze the data from all the Numeric fields.""")
    parser.add_argument("-v", "--verbosity", help="set the logging verbosity, 0 == CRITICAL, 1 == INFO, it defaults to ERROR.",  type=int, choices=[0,1], default=0)

    
    # Load the defaults
    current_script_dir = "/".join(__file__.split("/")[:-1])
    with open(current_script_dir + "/arguments_settings.json") as f:
        args_settings = json.load(f)
   
    # Create the groups
    for group, arguments in args_settings.items():
        groups_settings = parser.add_argument_group(group)

        # add the fields to the group
        for argument_name, description in arguments.items():
            # Convert the type from string to the real class type
            if "type" in description.keys():
                description["type"] = cast_type[description["type"]]

            settings = description.copy()

            # Render the positional argumentsAnd delete them from the key ones
            positional = []
            if "long" in settings.keys():
                positional.append(settings.pop("long"))
            if "short" in settings.keys():
                positional.append(settings.pop("short"))

            
            # Add the field with the settings
            groups_settings.add_argument(*positional, **settings)
   
   # Parse the Inputs
    args = parser.parse_args()

    # TODO set it to the right value
    if args.verbosity == 1:
        setLevel(logging.INFO)
    else:
        setLevel(logging.ERROR)

    # Replace the description of the argument with the value
    settings = {
        group.replace("-","_") : {
            name.replace("-", "_") : args.__getattribute__(description["long"].lstrip("-").replace("-","_"))
            for name, description in arguments.items()
        }
        for group, arguments in args_settings.items()
    }

    # Call the anomaly detection
    detect_anomalies(**settings)

