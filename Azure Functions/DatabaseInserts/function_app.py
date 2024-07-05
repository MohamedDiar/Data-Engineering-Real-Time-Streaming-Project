"""
This file contains the code for the Azure Function App that is triggered events reaching the Event Hub.
The function app is responsible for inserting data into the MySQL database in the respective tables.
"""

import azure.functions as func
import logging
import mysql.connector
import json
import os
from datetime import datetime

app = func.FunctionApp()

# Will load the environment variables from the function app settings when deployed
host=os.getenv('host')
user=os.getenv('user')
password=os.getenv('password')
database=os.getenv('database')


# Function helper to connect to the database
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=3306  
        )
        logging.info("Successfully connected to the database")
        return connection
    except mysql.connector.Error as error:
        logging.error(f"Failed to connect to database: {error}")
        return None

@app.function_name(name="glucose_readings_table_insert")
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="raw_glucose_readings",
                               connection="EventHubConnectionString",
                               consumer_group="mysql_glucose_reading_table"
                               ) 
def glucose_readings_table_insert(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))

    # Connect to MySQL database
    connection = get_db_connection()
    if not connection:
        return

    cursor = connection.cursor()
  
    # Parse the message
    try:
        message = json.loads(azeventhub.get_body().decode('utf-8'))
    except json.JSONDecodeError as error:
        logging.error(f"Error decoding JSON: {error}")
        return

    # timestamp = datetime.utcfromtimestamp(message["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')


    insert_stmt = (
        "INSERT INTO glucose_reading (user_id, device_id, glucose_level, timestamp, latitude, longitude) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    data = (
        message["user_id"],
        message["device_id"],
        message["glucose_reading"],
        message["timestamp"],
        message["latitude"],
        message["longitude"]
    )

    # Inserting data into the database
    try:
        cursor.execute(insert_stmt, data)
        connection.commit()
        logging.info("1 row inserted successfully")
    except mysql.connector.Error as error:
        logging.error(f"Failed to insert row: {error}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")


@app.function_name(name="device_feed_table_insert")
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="raw_device_feeds",
                               connection="EventHubConnectionString",
                               consumer_group="mysql_device_feed_table") 
def device_feed_table_insert(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))

    # Connect to MySQL database
    connection = get_db_connection()
    if not connection:
        return

    cursor = connection.cursor()

    # Parse the message
    try:
        message = json.loads(azeventhub.get_body().decode('utf-8'))
        logging.info(f"Message parsed successfully: {message}")
    except json.JSONDecodeError as error:
        logging.error(f"Error decoding JSON: {error}")
        return

    # Verify and prepare data
    try:
        # timestamp = datetime.utcfromtimestamp(message["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        data = (
            message["device_id"],
            message["battery_level"],
            message["firmware_version"],
            message["connection_status"],
            message["error_code"],
            message["timestamp"]
        )
        logging.info(f"Data prepared for insertion: {data}")
    except KeyError as e:
        logging.error(f"Key error in message: {e}")
        return
    except Exception as e:
        logging.error(f"Error in data preparation: {e}")
        return

    # Insert statement
    insert_stmt = (
        "INSERT INTO device_feed (device_id, battery_level, firmware_version, connectivity_status, error_codes, timestamp)"
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )

    # Inserting data into the database
    try:
        cursor = connection.cursor()
        cursor.execute(insert_stmt, data)
        connection.commit()
        logging.info("1 row inserted successfully")
    except mysql.connector.Error as error:
        logging.error(f"Failed to insert row: {error}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logging.info("MySQL connection is closed")


