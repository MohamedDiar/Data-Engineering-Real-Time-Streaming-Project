"""
This script prepares the Redis cache with the data from the SQL database.
"""

import logging
from conn_config import get_sql_connection, get_redis_connection

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.debug("Started.")

# Get connections
r = get_redis_connection()
conn = get_sql_connection()

# Clear Redis database
r.flushall()

# SQL Queries and Redis Updates
cursor = conn.cursor()

# Query to fetch user and medical info
cursor.execute("""
    SELECT u.user_id, u.full_name, u.age, u.gender, p.min_glucose, p.max_glucose, p.medical_condition
    FROM user u
    JOIN medical_info p ON u.user_id = p.user_id
""")
rows = cursor.fetchall()

# Update Redis with patient data
for row in rows:
    user_id, full_name, age, gender, min_glucose, max_glucose, medical_condition = row
    patient_data = {
        "patient_name": full_name,
        "patient_age": age,
        "gender": gender,
        "max_glucose": max_glucose,
        "min_glucose": min_glucose,
        "medical_condition": medical_condition,
    }
    r.hmset(f"user:{user_id}", patient_data)

def expected_transmissions_per_given_minutes(interval, num_minutes):
    """
    Returns the expected number of transmissions expected in a given number of minutes
    """
    return round(num_minutes / interval)

# Query to fetch device information
cursor.execute("""
    SELECT pd.device_id, u.full_name, d.model, ds.data_transmission_interval, m.Name
    FROM patient_device pd
    JOIN user u ON pd.user_id = u.user_id
    JOIN device d ON pd.device_id = d.device_id
    JOIN device_settings ds ON pd.device_id = ds.device_id
    JOIN manufacturer m ON d.manufacturer_id = m.manufacturer_id
""")
rows = cursor.fetchall()

# Update Redis with device data
for row in rows:
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

# Close the SQL connection
conn.close()

logging.debug("Done.")



