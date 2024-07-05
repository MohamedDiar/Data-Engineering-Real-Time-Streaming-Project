
CREATE SEQUENCE seq_fact_glucose_reading;
CREATE SEQUENCE seq_dim_user;
CREATE SEQUENCE seq_dim_device;
CREATE SEQUENCE seq_dim_medical_information;


CREATE TABLE IF NOT EXISTS dim_user (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    age INT,
    gender VARCHAR(50),
    contact_number VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS dim_device (
    device_id INT PRIMARY KEY,
    model VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS dim_time (
date_key INT PRIMARY KEY, 
full_date DATE,           
day INT,
month INT,
year INT,
day_of_week VARCHAR(50),
month_name VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS fact_glucose_reading (
    fact_id INT PRIMARY KEY,
    user_id INT,
    device_id INT,
    date_key INT,
    avg_glucose FLOAT,
    min_glucose FLOAT,
    max_glucose FLOAT,
    FOREIGN KEY (user_id) REFERENCES dim_user (user_id),
    FOREIGN KEY (device_id) REFERENCES dim_device (device_id),
    FOREIGN KEY (date_key) REFERENCES dim_time (date_key)
);