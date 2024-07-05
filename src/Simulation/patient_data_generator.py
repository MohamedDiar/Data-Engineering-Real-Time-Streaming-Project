"""
This script simulates glucose monitoring data for patients over a 24-hour period. 
It initializes patient data, including initial coordinates within Spain, and sets up timestamps for data generation at user-specific intervals.
The script retrieves glucose thresholds and generates realistic glucose readings, accounting for user behaviors and device disconnection periods. 
It produces metric records with user ID, device ID, timestamp, glucose reading, and coordinates.
Finally, it collects, randomizes, and sorts these records by timestamp for realistic simulation output.
"""

import datetime
import random

from .data_initialization_config import patients, simulation_duration
from .device_data_generator import disconnection_periods
from .Thresholds_Retreiving import thresholds, user_device_interval
from .user_behaviour import get_glucose_effect, user_behaviors


def get_threshold_for_patient(user_id):
    """
    Get the glucose threshold values for a given user ID.

    Parameters:
    user_id (int): The ID of the user.

    Returns:
    tuple: A tuple containing the minimum and maximum glucose thresholds for the user.
           If the user ID is not found, the default threshold values of 50 and 240 are returned.
    """

    for uid, min_glucose, max_glucose in thresholds:
        if uid == user_id:
            return min_glucose, max_glucose

    return 50, 240


# For the simulation I decided that the patients will be moving within Spain.
def generate_random_coordinates_within_spain():
    """
    Generates random latitude and longitude coordinates within the bounding box of Spain.

    Returns:
        tuple: A tuple containing the latitude and longitude coordinates.
    """
    # Define the approximate bounding box for Spain

    spain_bounding_box = {
        "latitude_min": 36.0,  # Southernmost latitude of Spain
        "latitude_max": 43.79,  # Northernmost latitude of Spain
        "longitude_min": -9.3,  # Westernmost longitude of Spain
        "longitude_max": 3.3,  # Easternmost longitude of Spain
    }

    # Generate random latitude and longitude within the bounding box
    latitude = random.uniform(
        spain_bounding_box["latitude_min"], spain_bounding_box["latitude_max"]
    )
    longitude = random.uniform(
        spain_bounding_box["longitude_min"], spain_bounding_box["longitude_max"]
    )

    return latitude, longitude


# This makes the simulation more realistic by generating nearby coordinates based on the current location.
# So the patients will not jump to a completely different location in the next observation.
def generate_nearby_coordinates(lat, lon):
    """
    Generate nearby coordinates based on the given latitude and longitude.

    Args:
        lat (float): The latitude of the current location.
        lon (float): The longitude of the current location.

    Returns:
        tuple: A tuple containing the new latitude and longitude coordinates.
    """
    # Define a small range for generating nearby coordinates
    range_min, range_max = 0.01, 0.05
    range_lat = random.uniform(range_min, range_max)
    range_lon = random.uniform(range_min, range_max)
    new_lat = random.uniform(lat - range_lat, lat + range_lat)
    new_lon = random.uniform(lon - range_lon, lon + range_lon)
    return new_lat, new_lon


def generate_metric_record(patient, timestamp, disconnection_periods, user_behaviors):
    """
    Generate a metric record for a patient.

    Args:
        patient (dict): The patient information containing 'user_id' and 'device_id'.
        timestamp (str or datetime.datetime): The timestamp of the metric record.
            If it's a string, it should be in the format '%Y-%m-%dT%H:%M:%S'.
        disconnection_periods (dict): A dictionary containing disconnection periods for devices.
            The keys are device IDs and the values are dictionaries with 'start' and 'end' keys
            representing the start and end timestamps of the disconnection period.
        user_behaviors (dict): A dictionary containing user behaviors affecting glucose readings.

    Returns:
        dict or None: The generated metric record as a dictionary with the following keys:
            - 'user_id': The user ID of the patient.
            - 'device_id': The device ID of the patient.
            - 'timestamp': The timestamp of the metric record in the format '%Y-%m-%dT%H:%M:%S'.
            - 'glucose_reading': The generated glucose reading value.
            - 'latitude': The latitude coordinate of the patient's location.
            - 'longitude': The longitude coordinate of the patient's location.
            If the device is currently in a disconnection period, None is returned.

    """
    user_id = patient["user_id"]
    device_id = patient["device_id"]

    # Convert timestamp to datetime object if it's a string
    if isinstance(timestamp, str):
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    # Check if the device is currently in a disconnection period.
    # If it is, no metric record will be generated for the duration of the disconnection.
    if (
        device_id in disconnection_periods
        and disconnection_periods[device_id]["start"]
        <= timestamp
        <= disconnection_periods[device_id]["end"]
    ):
        return None

    min_glucose, max_glucose = get_threshold_for_patient(user_id)

    # Decide whether to generate a value within the threshold or outside it
    # I used a weighted random choice to generate values within the threshold with a higher probability.
    # So,95% of the time, within_threshold will be True, and 5% of the time, it will be False.
    within_threshold = random.choices([True, False], weights=[95, 5], k=1)[0]

    if within_threshold:
        glucose_reading = random.uniform(min_glucose, max_glucose)
    else:
        # Generate a value outside either below the minimum threshold or above the maximum threshold
        # 50% chance for both cases.
        if random.random() < 0.5:
            glucose_reading = random.uniform(50, min_glucose)  # Below threshold
        else:
            glucose_reading = random.uniform(max_glucose, 240)  # Above threshold

    # The initial glucose reading is affected by the user's behavior
    behavior_effect = get_glucose_effect(user_id, user_behaviors)
    glucose_reading += behavior_effect

    # Generate coordinates for the first time or nearby coordinates for subsequent observations
    if user_id not in initial_coordinates:
        # First time generating coordinates for the user
        latitude, longitude = generate_random_coordinates_within_spain()
        initial_coordinates[user_id] = (latitude, longitude)
    else:
        # Generate coordinates close to the initial ones
        initial_lat, initial_lon = initial_coordinates[user_id]
        latitude, longitude = generate_nearby_coordinates(initial_lat, initial_lon)

    return {
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
        "glucose_reading": glucose_reading,
        "latitude": latitude,
        "longitude": longitude,
    }


# Total duration of the simulation/data generation process in minutes (24 hours).
total_duration = simulation_duration

# A dictionary to store the initial coordinates (latitude, longitude) for each user.
# These coordinates are  used as a starting point for generating movement or location data.
initial_coordinates = {}

# This variable represents the time one minute before the current moment.
# It's used as a reference point for generating timestamps for the data.
# It facilitates ensuring that we only observe the record of a user at their specific interval.
last_observed_time = datetime.datetime.now() - datetime.timedelta(minutes=1)

# This dictionary is used to store the next expected timestamp for each user.
# It is calculated based on the last observed time and user-specific intervals(user_device_interval)
# For example, if a user has an interval of 5 minutes, the next expected timestamp will be 5 minutes after the last observed time.
next_expected_timestamps = {
    uid: last_observed_time + datetime.timedelta(minutes=interval) 
    for uid, interval in user_device_interval
}

# Records for users will be seen based on their interval
# For example, if a user has an interval of 5 minutes, they will have a record every 5 minutes.
# If a user has 1 minute, they will have a record every minute
# If a user has 2 minutes, the difference between last seen record and the next record will be 2 minutes
# This makes the simulation more realistic as the data is generated at user-specific intervals.
records = []
for minute in range(total_duration):
    for patient in patients:
        user_id = patient["user_id"]
        
        current_generation_time = last_observed_time + datetime.timedelta(
            minutes=minute
        )
        # Checks if the current time has reached the next expected timestamp for the user
        if current_generation_time >= next_expected_timestamps[user_id]:
            # Getting the user-specific interval for generating records
            interval = next(
                interval for uid, interval in user_device_interval if uid == user_id
            )
            # Generating a random timestamp within the interval for more realistic data
            random_seconds = random.randint(1, interval * 60 - 1)
            realistic_timestamp = current_generation_time + datetime.timedelta(
                seconds=random_seconds
            )
            # Checks if the realistic timestamp less than the next expected timestamp.
            # It might seem redundant, but it ensures that we don't generate records beyond the next expected timestamp.
            if realistic_timestamp < last_observed_time + datetime.timedelta(
                minutes=minute + interval
            ):  # Generate a metric record for the user
                record = generate_metric_record(
                    patient,
                    realistic_timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                    disconnection_periods,
                    user_behaviors,
                )
                if record is not None:  
                    records.append(record)
                # Updating the next expected timestamp for when the next record should be generated
                next_expected_timestamps[user_id] = (
                    last_observed_time + datetime.timedelta(minutes=minute + interval)
                )
random.shuffle(records)
records.sort(key=lambda x: x["timestamp"])
