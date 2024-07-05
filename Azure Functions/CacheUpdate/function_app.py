import azure.functions as func
import logging
from conn_config import get_sql_connection, get_redis_connection
import json
from datetime import datetime
import time

app = func.FunctionApp()

# Getting connections


def update_cache(user_id):
    """
    Updates the cache using new user data captured
    """

    # Get SQL connection

    try:
        conn = get_sql_connection()
    except Exception as e:
        logging.error(f"Error connecting to SQL: {e}")
        return
    # Get Redis connection
    try:
        r = get_redis_connection()
    except Exception as e:
        logging.error(f"Error connecting to Redis: {e}")
        return

    # This ensures that the commit transaction is reflected in the MYSQL tables before fetching the data
    time.sleep(3)

    try:
        cursor = conn.cursor()
    except Exception as e:
        logging.error(f"Error creating cursor: {e}")
        return

    try:
        # Fetch user and medical info
        cursor.execute(
            """
            SELECT u.user_id, u.full_name, u.age, u.gender, p.min_glucose, p.max_glucose, p.medical_condition
            FROM user u
            JOIN medical_info p ON u.user_id = p.user_id
            WHERE u.user_id = %s
        """,
            (user_id,),
        )
        user_info = cursor.fetchone()
        logging.info(f"User info: {user_info}")

        if user_info:
            (
                user_id,
                full_name,
                age,
                gender,
                min_glucose,
                max_glucose,
                medical_condition,
            ) = user_info
            patient_data = {
                "patient_name": full_name,
                "patient_age": age,
                "gender": gender,
                "max_glucose": max_glucose,
                "min_glucose": min_glucose,
                "medical_condition": medical_condition,
            }
            r.hmset(f"user:{user_id}", patient_data)
    except Exception as e:
        logging.error(f"Error fetching user info: {e}")
        
    try:
        # Fetching device information
        cursor.execute(
            """
            SELECT pd.device_id, u.full_name, d.model, ds.data_transmission_interval, m.Name
            FROM patient_device pd
            JOIN user u ON pd.user_id = u.user_id
            JOIN device d ON pd.device_id = d.device_id
            JOIN device_settings ds ON pd.device_id = ds.device_id
            JOIN manufacturer m ON d.manufacturer_id = m.manufacturer_id
            WHERE u.user_id = %s
        """,
            (user_id,),
        )
        device_info = cursor.fetchall()
        logging.info(f"Device info: {device_info}")

        for row in device_info:
            device_id, full_name, model, data_transmission_interval, manufacturer = row
            expected_transmissions = expected_transmissions_per_given_minutes(
                data_transmission_interval, 15
            )
            device_data = {
                "owner_name": full_name,
                "device_model": model,
                "data_transmission_interval": data_transmission_interval,
                "expected_transmissions": expected_transmissions,
                "manufacturer_name": manufacturer,
            }
            r.hmset(f"device:{device_id}", device_data)
    except Exception as e:
        logging.error(f"Error fetching device info: {e}")
    finally:
        cursor.close()


def expected_transmissions_per_given_minutes(interval, num_minutes):
    """
    Returns the expected number of transmissions expected in a given number of minutes
    """
    return round(num_minutes / interval)


@app.function_name(name="update_redis_cache")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="cache_update",
    connection="EventHubConnectionString",
    consumer_group="redis_cache",
)
def update_redis_cache(azeventhub: func.EventHubEvent):
    logging.info(
        f"Function triggered to process a message: {azeventhub.get_body().decode()}"
    )

    try:
        event_data = json.loads(azeventhub.get_body().decode())
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return

    if event_data["op"] == "c":  # Check if the operation that happened in the database is a create operation
        user_id = event_data["after"]["user_id"]
        try:
            update_cache(user_id)
        except Exception as e:
            logging.error(f"Error updating cache for user_id {user_id}: {e}")
