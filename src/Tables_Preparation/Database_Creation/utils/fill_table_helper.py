"""
Helper script that reads the configuration file and returns the values
that are to be used for the generation of data to be inserted into the tables.
"""

import os
import sys
from pathlib import Path
import json

# Get the root directory of the project and the path to the configuration file
root_dir = Path(__file__).resolve().parents[4]
config_file_path = root_dir / "config.json"


# Reading configuration file
with open(config_file_path) as json_file:
    config_file = json.load(json_file)

#Extracting the values from the configuration file

# The age range of the users to be generated
range_age = config_file["user_generation"]["age_range"]

# The rnage of glucose values to be generated for different users
range_glucose = config_file["medical_info_generation"]["glucose_range"]

# Total number of users to be generated
num_users = config_file["user_generation"]["total_users"]

# Total number of doctors to be generated
num_doctors = config_file["doctor_generation"]["total_doctors"]

# Total number of devices to be generated
num_devices = config_file["device_generation"]["total_devices"]

# Total number of subscribers to be generated
num_subscribers = config_file["subscriber_generation"]["total_subscribers"]

# The maximum number of additional doctors that can be assigned to a patient as patient can have multiple doctors subscribed to their glucose data
max_additional_doctors_per_user = config_file["subscriber_generation"]["max_additional_doctors_per_user"]

# Total number of manufacturers to be generated
num_manufacturers = config_file["manufacturer_generation"]["total_manufacturers"]

# Range between which thee transmission interval of the devices can be generated
transmission_interval = config_file["device_settings_generation"]["data_transmission_interval"]
