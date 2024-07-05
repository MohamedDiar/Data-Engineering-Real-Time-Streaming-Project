
import os
import sys
import random
from datetime import datetime, timedelta
from faker import Faker

# Finding the absolute path to needed directory and adding the directory to sys.path
current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, '..', 'Tables_Preparation', 'Database_Creation'))
sys.path.insert(0, target_dir)

from utils.db_config import get_sql_connection
from utils.fill_table_helper import (
    num_devices,
    num_doctors,
    num_manufacturers,
    range_age,
    range_glucose,
    transmission_interval,
)
from utils.medical_provider import MedicalProvider
from filling_tables import model_names,generate_user,generate_medical_info



# Establish a connection to the database
conn = get_sql_connection()
cursor = conn.cursor()

# Initialize Faker library with Spanish locale
fake = Faker("es_ES")
fake.add_provider(MedicalProvider)


def insert_new_user(user_data):
    cursor.execute(
        "INSERT INTO user (full_name, age, gender, date_of_birth, address, contact_number) VALUES (%s, %s, %s, %s, %s, %s)",
        user_data,
    )
    conn.commit()
    return cursor.lastrowid


def insert_medical_info(medical_info_data):
    cursor.execute(
        "INSERT INTO medical_info (user_id, min_glucose, max_glucose, medical_condition, medication, doctor_id) VALUES (%s, %s, %s, %s, %s, %s)",
        medical_info_data,
    )
    conn.commit()

def generate_device(manufacturer_id, model):
    purchase_date = fake.date_this_decade().strftime("%Y-%m-%d")
    warranty_expiry = fake.future_date().strftime("%Y-%m-%d")
    return manufacturer_id, model, purchase_date, warranty_expiry

def insert_device(device_data):
    cursor.execute(
        "INSERT INTO device (manufacturer_id, model, purchase_date, warranty_expiry) VALUES (%s, %s, %s, %s)",
        device_data,
    )
    conn.commit()
    return cursor.lastrowid

def insert_patient_device(patient_device_data):
    cursor.execute(
        "INSERT INTO patient_device (user_id, device_id, start_date, end_date, active_status) VALUES (%s, %s, %s, %s, %s)",
        patient_device_data,
    )
    conn.commit()

def insert_device_settings(device_settings_data):
    cursor.execute(
        "INSERT INTO device_settings (device_id, data_transmission_interval) VALUES (%s, %s)",
        device_settings_data,
    )
    conn.commit()

# Main function to simulate the addition of a new patient
def add_new_patient():
    # Generate and insert a new user
    gender = random.choice(["male", "female"])
    user_data = generate_user(gender, range_age)
    user_id = insert_new_user(user_data)
    
    # Generate and insert medical info for the new user
    medical_info_data = generate_medical_info(user_id, range_glucose)
    insert_medical_info(medical_info_data)
    
    # Generate and insert a new device for the user
    manufacturer_id = random.randint(1, num_manufacturers)
    model = random.choice(model_names)
    device_data = generate_device(manufacturer_id, model)
    device_id = insert_device(device_data)
    
    # Link the new device to the user
    start_date = datetime.today().strftime("%Y-%m-%d")
    end_date = (datetime.today() + timedelta(days=365 * 2)).strftime("%Y-%m-%d")
    patient_device_data = (user_id, device_id, start_date, end_date, True)
    insert_patient_device(patient_device_data)
    
    # Insert device settings
    interval = random.randint(*transmission_interval)
    device_settings_data = (device_id, interval)
    insert_device_settings(device_settings_data)
    
    print("New patient added successfully.")

if __name__ == "__main__":
    add_new_patient()
    cursor.close()
    conn.close()
    print("Connection closed.")


