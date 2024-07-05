"""
This script generates fake data and fills the tables in the database with the generated data.
"""

import os
import random
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker
from utils.db_config import get_sql_connection
from utils.fill_table_helper import (
    max_additional_doctors_per_user,
    num_devices,
    num_doctors,
    num_manufacturers,
    num_subscribers,
    num_users,
    range_age,
    range_glucose,
    transmission_interval,
)
from utils.medical_provider import MedicalProvider

# Establish a connection to the database
conn = get_sql_connection()
cursor = conn.cursor()

# Initialize Faker library with Spanish locale
fake = Faker("es_ES")
fake.add_provider(MedicalProvider)


# For the generation of manufacturer names and device models
model_names = [
    "GlucoTrack Pro",
    "SugarScan Elite",
    "GlycoGuardian X",
    "BloodSugar Navigator",
    "GlucoWave Plus",
    "SugarSense Ultra",
    "GlucoJourney 360",
    "DiabeCheck Precision",
    "HealthGluco Smart",
    "GlucoVista XE",
    "SweetLife Monitor",
    "AlphaGluco Pro",
    "GlucoMaster Elite",
    "ZenGluco Check",
    "LifeStream GlucoMonitor",
    "GlucoBalance Optima",
    "BioSugar Tracker",
    "GlucoTrend Advanced",
    "SugarCare Connect",
    "GlucoActive Explorer",
    "GlucoTech ProMax",
    "SugarSmart Prime",
    "GlucoPilot Elite",
    "HealthCheck GlucoPro",
    "GlucoVision Quantum",
    "SugarTrack Navigator",
    "GlucoAce 1000",
    "DiabeSense UltraX",
    "GlucoHarmony Elite",
    "SugarEase Expert",
    "GlucoWave RX",
    "SweetMonitor Precision",
    "GlucoLink Premier",
    "LifeGluco Tracker",
    "SugarControl Max",
    "GlucoSync Advance",
    "BioBalance SugarCheck",
    "GlucoMonitor Xpert",
    "SugarWatch Plus",
    "GlucoCare Elite",
]


# --------Functions to generate fake data and fill the tables in the database--------#
def generate_user(gender, age_range):
    """
    Generate a fake user with the specified gender and age range.

    Args:
        gender (str): The gender of the user, either "male" or "female".
        age_range (tuple): A tuple specifying the minimum and maximum age of the user.

    Returns:
        tuple: A tuple containing the user's full name, age, gender, date of birth, address, and contact number.
    """
    full_name = fake.name_male() if gender == "male" else fake.name_female()
    age = fake.random_int(min=age_range[0], max=age_range[1])
    date_of_birth = (datetime.today() -
                     timedelta(days=age * 365)).strftime("%Y-%m-%d")
    address = fake.address().replace("\n", ", ")
    contact_number = fake.phone_number()
    return full_name, age, gender, date_of_birth, address, contact_number


def create_fake_users():
    """
    Create and insert fake users into the user table in the database.
    """
    age_range = range_age
    users = [
        generate_user(random.choice(["male", "female"]), age_range)
        for _ in range(num_users)
    ]
    cursor.executemany(
        "INSERT INTO user (full_name, age, gender, date_of_birth, address, contact_number) VALUES (%s, %s, %s, %s, %s, %s)",
        users,
    )
    conn.commit()


def create_doctors():
    """
    Create and insert fake doctors into the doctor table in the database.
    """
    doctors = [
        (fake.name(), fake.doctor_occupation(), fake.phone_number())
        for _ in range(num_doctors)
    ]
    cursor.executemany(
        "INSERT INTO doctor (full_name, occupation, contact_number) VALUES (%s, %s, %s)",
        doctors,
    )
    conn.commit()


def generate_medical_info(user_id, glucose_range):
    """
    Generate fake medical information for a given user.

    Args:
        user_id (int): The ID of the user.
        glucose_range (dict): A dictionary with 'min' and 'max' keys specifying the range for glucose levels.

    Returns:
        tuple: A tuple containing the user ID, minimum and maximum glucose levels, medical condition, medication, and doctor ID.
    """
    min_glucose = round(random.uniform(*glucose_range["min"]), 2)
    max_glucose = round(random.uniform(*glucose_range["max"]), 2)
    condition = fake.medical_condition()
    medication = fake.medication()
    doctor_id = random.randint(1, num_doctors)
    return user_id, min_glucose, max_glucose, condition, medication, doctor_id


def create_medical_info():
    """
    Create and insert fake medical information into the medical_info table in the database.

    Returns:
        dict: A mapping of user IDs to their assigned doctor IDs.
    """
    glucose_range = range_glucose
    medical_info = [
        generate_medical_info(user_id, glucose_range)
        for user_id in range(1, num_users + 1)
    ]

    user_doctor_map = {info[0]: info[-1] for info in medical_info}
    cursor.executemany(
        "INSERT INTO medical_info (user_id, min_glucose, max_glucose, medical_condition, medication, doctor_id) VALUES (%s, %s, %s, %s, %s, %s)",
        medical_info,
    )
    conn.commit()

    return user_doctor_map


def create_subscribers():
    """
    Create and insert fake subscribers into the subscriber table in the database.
    """
    subscribers = []

    # Fetching doctors from the database
    cursor.execute("SELECT full_name, contact_number FROM doctor")
    doctors = cursor.fetchall()

    # Add all doctors as subscribers
    for doctor in doctors:
        full_name, contact_number = doctor
        relation = "Doctor"
        email = fake.email()
        subscribers.append((full_name, relation, contact_number, email))

    # Adding additional subscribers until we reach a total of 120 (or value specified in num_subscribers/config.json)
    while len(subscribers) < num_subscribers:
        full_name = fake.name()
        relation = fake.relation_to_user()
        while relation == "Doctor":
            relation = fake.relation_to_user()
        contact_number = fake.phone_number()
        email = fake.email()
        subscribers.append((full_name, relation, contact_number, email))

    # Insert subscribers into the database
    cursor.executemany(
        "INSERT INTO subscriber (full_name, relation_to_user, contact_number, email) VALUES (%s, %s, %s, %s)",
        subscribers,
    )


def create_fake_user_subscribers(user_doctor_map):
    """
    Create and insert fake user-subscriber relationships into the user_subscriber table in the database.

    Args:
        user_doctor_map (dict): A mapping of user IDs to their assigned doctor IDs.
    """
    user_subscribers = []

    doctor_ids = list(range(1, num_doctors + 1))
    all_subscriber_ids = list(range(1, num_subscribers + 1))

    for user_id in range(1, num_users + 1):
        assigned_doctor = user_doctor_map[user_id]

        # This Ensures the assigned doctor is one of the subscribers
        selected_subscribers = [assigned_doctor]

        # Selecting additional doctor subscribers, excluding the assigned doctor
        num_additional_doctors = random.randint(
            0, max_additional_doctors_per_user)
        additional_doctors = random.sample(
            [d for d in doctor_ids if d != assigned_doctor], num_additional_doctors
        )
        selected_subscribers.extend(additional_doctors)

        # Filling the remaining slots with random subscribers
        remaining_slots = 3 - len(
            selected_subscribers
        )  # Assuming each user can have up to 3 subscribers
        other_subscribers = random.sample(
            [sid for sid in all_subscriber_ids if sid not in selected_subscribers],
            remaining_slots,
        )
        selected_subscribers.extend(other_subscribers)

        # Now I am adding the subscribers for this user
        for subscriber_id in selected_subscribers:
            user_subscribers.append((user_id, subscriber_id))

    cursor.executemany(
        "INSERT INTO user_subscriber (user_id, subscriber_id) VALUES (%s, %s)",
        user_subscribers,
    )
    conn.commit()


def create_fake_manufacturer():
    """
    Create and insert fake manufacturers and their associated models into the manufacturer table in the database.
    """
    global manufacturer_models
    manufacturers = []
    manufacturer_models = {}
    shuffled_model_names = random.sample(model_names, len(model_names))

    # Initially assigning one model to each manufacturer.
    for i in range(num_manufacturers):
        name = fake.company()
        manufacturers.append((name,))
        # Assigning one model to each manufacturer initially
        manufacturer_models[i + 1] = [shuffled_model_names.pop()]

    # Assigning additional models to manufacturers randomly
    while shuffled_model_names:
        model = shuffled_model_names.pop()
        manufacturer_id = random.randint(1, num_manufacturers)
        manufacturer_models[manufacturer_id].append(model)
    cursor.executemany(
        "INSERT INTO manufacturer (name) VALUES (%s)", manufacturers)
    conn.commit()


def create_fake_devices():
    """
    Create and insert fake devices into the device table in the database.
    """
    devices = []

    for _ in range(num_devices):
        manufacturer_id = random.choice(list(manufacturer_models.keys())) # Defined in the create_fake_manufacturer function
        model = random.choice(manufacturer_models[manufacturer_id])
        purchase_date = fake.date_this_decade().strftime("%Y-%m-%d")
        warranty_expiry = fake.future_date().strftime("%Y-%m-%d")
        devices.append(
            (manufacturer_id, model, purchase_date, warranty_expiry))
    cursor.executemany(
        "INSERT INTO device (manufacturer_id, model, purchase_date, warranty_expiry) VALUES (%s, %s, %s, %s)",
        devices,
    )
    conn.commit()


def create_fake_patient_devices():
    """
    Create and insert fake patient-device relationships into the patient_device table in the database.
    """
    patient_devices = []
    device_ids = list(range(1, num_devices + 1))
    random.shuffle(device_ids)

    for user_id in range(1, num_users + 1):
        device_id = device_ids.pop()
        start_date = fake.date_between(start_date="-1y", end_date="today")
        end_date = fake.date_between(start_date=start_date, end_date="+2y")
        active_status = True
        patient_devices.append(
            (user_id, device_id, start_date, end_date, active_status)
        )

    cursor.executemany(
        "INSERT INTO patient_device (user_id, device_id, start_date, end_date, active_status) VALUES (%s, %s, %s, %s, %s)",
        patient_devices,
    )
    conn.commit()


def create_fake_device_settings():
    """
    Create and insert fake device settings into the device_settings table in the database.
    """
    device_settings = []

    for device_id in range(1, num_devices + 1):
        data_transmission_interval = random.randint(*transmission_interval)
        device_settings.append((device_id, data_transmission_interval))

    cursor.executemany(
        "INSERT INTO device_settings (device_id, data_transmission_interval) VALUES (%s, %s)",
        device_settings,
    )
    conn.commit()


def main():
    create_fake_users()
    create_doctors()
    user_doctor_map = create_medical_info()
    create_fake_manufacturer()
    create_fake_devices()
    create_subscribers()
    create_fake_user_subscribers(user_doctor_map)
    create_fake_patient_devices()
    create_fake_device_settings()
    print("Tables Were Fillled Successfully.")
    cursor.close()
    conn.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
