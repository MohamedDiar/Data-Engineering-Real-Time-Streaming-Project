"""
The script is used to quickly generate glucose readings data for testing the ETL pipeline and trend analysis.
"""
import argparse
import datetime
import json
import os
import random
from calendar import monthrange
from pathlib import Path

import mysql.connector
from dotenv import find_dotenv, load_dotenv
from faker import Faker

root_dir = Path(__file__).resolve().parents[2]
config_file_path = root_dir / "config.json"

with open(config_file_path) as f:
    config = json.load(f) 

# Load environment variables from .env file
load_dotenv(find_dotenv())

host = os.getenv("host")
user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")
port = os.getenv("port")


def get_date_range(mode):
    """
    Determine the start date and number of days based on the specified mode.

    Args:
        mode (str): The mode of operation, either 'daily_etl' or 'trend_analysis'.

    Returns:
        tuple: A tuple containing:
            - start_date (datetime.date): The start date for data generation.
            - num_days (int): The number of days to generate data for.

    Raises:
        ValueError: If an invalid mode is provided.
    """
    today = datetime.date.today()

    if mode == "daily_etl":
        start_date = today - datetime.timedelta(days=1)
        num_days = 1
    elif mode == "trend_analysis":
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(
            days=1
        )
        start_date = last_day_of_previous_month.replace(day=1)
        _, num_days = monthrange(start_date.year, start_date.month)
    else:
        raise ValueError("Invalid mode. Choose 'daily_etl' or 'trend_analysis'.")

    return start_date, num_days


def create_mysql_connection(host, user, password, database, port):
    """
    Create a connection to a MySQL database.

    Args:
        host (str): The hostname of the MySQL server.
        user (str): The username for the MySQL database.
        password (str): The password for the MySQL database.
        database (str): The name of the MySQL database.
        port (str): The port number for the MySQL server.

    Returns:
        mysql.connector.connection.MySQLConnection or None: A connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database, port=port
        )
        return connection
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL database: {error}")
        return None


def simulate_glucose_readings(
    start_date, num_days, interval_minutes, min_glucose, max_glucose, user_id, device_id
):
    """
    Simulate glucose readings for a user over a specified period.

    Args:
        start_date (datetime.date): The start date for the simulation.
        num_days (int): The number of days to simulate data for.
        interval_minutes (int): The interval between readings in minutes.
        min_glucose (float): The minimum glucose level to simulate.
        max_glucose (float): The maximum glucose level to simulate.
        user_id (int): The ID of the user.
        device_id (int): The ID of the device.

    Returns:
        list: A list of dictionaries, each representing a glucose reading.
    """
    fake = Faker()
    readings = []
    current_time = datetime.datetime.combine(start_date, datetime.time())

    start_offset = datetime.timedelta(seconds=random.randint(0, interval_minutes * 60))
    current_time += start_offset

    for day in range(num_days):
        while current_time.date() == (start_date + datetime.timedelta(days=day)):
            glucose_reading = random.uniform(min_glucose, max_glucose)
            latitude = float(fake.latitude())
            longitude = float(fake.longitude())
            readings.append(
                {
                    "user_id": user_id,
                    "device_id": device_id,
                    "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "glucose_reading": glucose_reading,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

            seconds_increment = random.randint(5, 59)
            current_time += datetime.timedelta(
                minutes=interval_minutes, seconds=seconds_increment
            )

    return readings


def insert_many(data, mysql_hermes, mysql_connection):
    """
    Insert multiple glucose readings into the MySQL database.

    Args:
        data (list): A list of dictionaries, each representing a glucose reading.
        mysql_hermes (mysql.connector.cursor.MySQLCursor): A MySQL cursor object.
        mysql_connection (mysql.connector.connection.MySQLConnection): A MySQL connection object.

    Raises:
        mysql.connector.Error: If there's an error while inserting data.
    """
    CHUNK_SIZE = config["quick_generation_conf"]["chunk_size"]
    index = 0
    try:
        mysql_connection.start_transaction()
        while True:
            chunk = data[index : index + CHUNK_SIZE]
            if not chunk:
                break

            values_str = ", ".join(
                "({}, {}, '{}', {}, {}, {})".format(
                    row["user_id"],
                    row["device_id"],
                    row["timestamp"],
                    row["glucose_reading"],
                    row["latitude"],
                    row["longitude"],
                )
                for row in chunk
            )

            sql = "INSERT INTO `glucose_reading` (user_id, device_id, timestamp, glucose_level, latitude, longitude) VALUES {}".format(
                values_str
            )

            mysql_hermes.execute(sql)
            mysql_connection.commit()

            index += CHUNK_SIZE

        mysql_connection.commit()

    except mysql.connector.Error as error:
        print(f"Error while inserting data: {error}")
        mysql_connection.rollback()


def main(mode):
    """
    Main function to generate and insert glucose readings data.

    Args:
        mode (str): The mode of operation, either 'daily_etl' or 'trend_analysis'.
    """
    start_date, num_days = get_date_range(mode)

    interval_minutes = config["quick_generation_conf"]["interval_minutes"]
    min_glucose = config["quick_generation_conf"]["min_glucose"]
    max_glucose = config["quick_generation_conf"]["max_glucose"]
    user_count = config["user_generation"]["total_users"]

    all_readings = []
    for user_id in range(1, user_count + 1):
        device_id = user_id
        user_readings = simulate_glucose_readings(
            start_date,
            num_days,
            interval_minutes,
            min_glucose,
            max_glucose,
            user_id,
            device_id,
        )
        all_readings.extend(user_readings)

    random.shuffle(all_readings)
    all_readings.sort(key=lambda reading: reading["timestamp"])

    mysql_connection = create_mysql_connection(host, user, password, database, port)
    mysql_hermes = mysql_connection.cursor() if mysql_connection else None

    insert_many(all_readings, mysql_hermes, mysql_connection)
    print(f"Inserted data into MySQL database for {mode}")

    mysql_hermes.close()
    mysql_connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate glucose readings data.")
    parser.add_argument(
        "mode", choices=["daily_etl", "trend_analysis"], help="Mode of operation"
    )
    args = parser.parse_args()

    main(args.mode)