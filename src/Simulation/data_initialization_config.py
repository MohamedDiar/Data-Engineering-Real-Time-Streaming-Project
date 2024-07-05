"""
This script is used for preliminary data setup initialization for the simulation.
"""

import random
from faker import Faker
from .Thresholds_Retreiving import user_device_id

# Initialize Faker
fake = Faker()

# Define the number of patients 
patient_count = len(user_device_id)

# Define the number of devices
device_count = patient_count


# Firmware data that will be assigned to devices for simulation
firmware_data = [
    {"name": "FirmwareA", "version": "1.0.0"},
    {"name": "FirmwareB", "version": "2.1.0"},
    {"name": "FirmwareC", "version": "3.0.1"},
    {"name": "FirmwareD", "version": "4.0.2"},
    {"name": "FirmwareE", "version": "5.1.1"},
]

# Defining error codes and connection statuses to be used in the simulation
error_codes = ["Battery Low", "404 Connection Lost", "None"]
connection_statuses = ["Connected", "Disconnected"]

# Generating device data
devices = [
    {"device_id": i + 1, "firmware_info": firmware_data[i % 5]}
    for i in range(device_count)
]

# Create a shuffled list of device IDs
device_ids = [i + 1 for i in range(device_count)]

# Shuffle the device IDs to simulate different devices being used by patients
random.shuffle(device_ids)

# Create a list of patients with user IDs and device IDs
patients = []

# Here I am using the predefined user_device_id list to assign device IDs to patients.
# This ensures that each patient is assigned the device ID that is already present in the database.
for i in range(patient_count):

    user_id = i + 1
    device_id = None

    # Check if the user_id is in the predefined list
    for ud_pair in user_device_id:
        if ud_pair[0] == user_id:
            device_id = ud_pair[1]
            break

    # If not in predefined list, assign a random device ID
    if device_id is None:
        device_id = random.randint(1, device_count)

    patients.append({"user_id": user_id, "device_id": device_id})


# The duration of the simulation in minutes (24 hours)(1440 minutes)
simulation_duration = 60 * 24