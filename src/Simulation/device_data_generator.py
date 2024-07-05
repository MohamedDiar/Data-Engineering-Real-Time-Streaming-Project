"""
This script generates simulated device records over a specified duration. 
It creates records for each device at regular intervals, randomly assigns battery levels, and simulates disconnection periods. 
Each record includes information such as device ID, battery level, firmware details, connection status, and error codes.

"""
import datetime
import random
from .data_initialization_config import devices, fake, simulation_duration


def generate_device_record(device_id, timestamp, disconnection_periods):
    """
    Generate a device record with the given device ID, timestamp, and disconnection periods.

    Args:
        device_id (str): The ID of the device.
        timestamp (str or datetime.datetime): The timestamp of the device record. If it's a string, it should be in the format "%Y-%m-%dT%H:%M:%S".
        disconnection_periods (dict): A dictionary containing the disconnection periods for each device.

    Returns:
        dict: A dictionary representing the device record with the following keys:
            - "device_id" (str): The ID of the device.
            - "battery_level" (int): The battery level of the device.
            - "firmware_name" (str): The name of the firmware installed on the device.
            - "firmware_version" (str): The version of the firmware installed on the device.
            - "connection_status" (str): The connection status of the device ("Connected" or "Disconnected").
            - "error_code" (str): The error code of the device ("None", "Battery Low", or "404 Connection Lost").
            - "timestamp" (str): The timestamp of the device record in the format "%Y-%m-%dT%H:%M:%S".
    """

    device = next(device for device in devices if device["device_id"] == device_id)
    battery_level = fake.random_int(min=0, max=100)

    # Converts timestamp to datetime object if it's a string
    if isinstance(timestamp, str):
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    # We are Checking if the device is currently in a disconnection period
    # The device will remain disconnected for a random duration between 1 and 3 minutes
    if (
        device_id in disconnection_periods
        and disconnection_periods[device_id]["start"]<= timestamp <= disconnection_periods[device_id]["end"]
    ):
        connection_status = "Disconnected"
    else:
        if random.random() < 0.1:  # 10% chance to disconnect
            disconnection_duration = random.randint(
                1, 3
            )  # Random disconnection duration in minutes
            disconnection_periods[device_id] = {
                "start": timestamp,
                "end": timestamp + datetime.timedelta(minutes=disconnection_duration),
            }
            connection_status = "Disconnected"
        else:
            connection_status = "Connected"

    # Assign error code
    if connection_status == "Connected":
        error_code = "None"
    elif battery_level < 20:
        error_code = "Battery Low"
    else:
        error_code = "404 Connection Lost"

    return {
        "device_id": device_id,
        "battery_level": battery_level,
        "firmware_name": device["firmware_info"]["name"],
        "firmware_version": device["firmware_info"]["version"],
        "connection_status": connection_status,
        "error_code": error_code,
        "timestamp": timestamp.strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
    }

# Initialize the disconnection periods for each device
disconnection_periods = {}


# Define the interval for records in minutes.
record_interval = 1

# We start the simulation at the current time
current_time = datetime.datetime.now()


device_records = []

# Generate device records for each device at regular intervals
for minute in range(0, simulation_duration, record_interval):
    for device in devices:

        # Gnerate a random number of seconds to add to the timestamp
        seconds_to_add = random.randint(0, 59)

        #Add the random number of seconds to the timestamp
        timestamp = current_time + datetime.timedelta(
            minutes=minute, seconds=seconds_to_add
        )

        # Generate a record for this device
        record = generate_device_record(
            device["device_id"], timestamp, disconnection_periods
        )
        device_records.append(record)

random.shuffle(device_records)

device_records.sort(key=lambda x: x["timestamp"])
