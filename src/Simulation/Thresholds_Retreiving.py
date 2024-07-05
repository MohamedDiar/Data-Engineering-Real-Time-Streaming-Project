"""
This script is used to retreive the thresholds, user_id_age, user_id_condition, user_id_medication, 
user_device_id, and user_device_interval from the database.

They will help in creating the user behavior and factors that might affect glucose levels for the simulation.
"""

import logging
import os
import mysql.connector
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(filename='Thresholds_Retreiving.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


# Loading the environment variables
host = os.getenv("host")
port = os.getenv("port")
username = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")




def fetch_data(cursor, query):
    """
    Fetches data from the database using the provided cursor and query
    :param cursor: The cursor to use for the query
    :param query: The query to execute
    :return: The result of the query
    """

    cursor.execute(query)
    return list(cursor)


# Retreives user_id, min_glucose, and max_glucose, user_id_age, 
# user_id_condition, user_id_medication, user_device_id, and user_device_interval from the database.
with mysql.connector.connect(user=username, password=password, host=host, database=database) as cnx:
    
    try:
        with cnx.cursor() as cursor:
            thresholds = fetch_data(cursor, 'SELECT user_id, min_glucose, max_glucose FROM medical_info')
            user_id_age = fetch_data(cursor, 'SELECT user_id, age FROM user')
            user_id_condition = fetch_data(cursor, 'SELECT user_id, medical_condition FROM medical_info')
            user_id_medication = fetch_data(cursor, 'SELECT user_id, medication FROM medical_info')
            user_device_id = fetch_data(cursor, 'SELECT user_id, device_id FROM patient_device')
            user_device_interval = fetch_data(cursor, '''
                SELECT user.user_id, device_settings.data_transmission_interval
                FROM patient_device pd
                JOIN user ON pd.user_id = user.user_id
                JOIN device_settings ON pd.device_id = device_settings.device_id
            ''')
    except Exception as e:
        logging.error(e)
        raise e

logging.info('Finished retrieving thresholds, user_device_id, and user_device_interval, user_id_age, user_id_condition, user_id_medication')