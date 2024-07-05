CREATE TABLE IF NOT EXISTS user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255),
    age INT,
    gender VARCHAR(255),
    date_of_birth DATE,
    address VARCHAR(255),
    contact_number VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS doctor (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255),
    occupation VARCHAR(255),
    contact_number VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS manufacturer (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS device (
    device_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_id INT,
    model VARCHAR(255),
    purchase_date DATE,
    warranty_expiry DATE,
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer (manufacturer_id) ON DELETE SET NULL
);



CREATE TABLE IF NOT EXISTS patient_device (
    patient_device_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    device_id INT,
    start_date DATE,
    end_date DATE,
    active_status BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES device (device_id) ON DELETE SET NULL
);



CREATE TABLE IF NOT EXISTS device_settings (
    device_id INT PRIMARY KEY,
    data_transmission_interval INT,
    FOREIGN KEY (device_id) REFERENCES device (device_id) ON DELETE CASCADE
    );



CREATE TABLE IF NOT EXISTS subscriber (
    subscriber_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255),
    relation_to_user VARCHAR(255),
    contact_number VARCHAR(255),
    email VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS medical_info(
    user_id INT,
    doctor_id INT,
    min_glucose FLOAT,
    max_glucose FLOAT,
    medical_condition VARCHAR(255),
    medication VARCHAR(255),
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
);



CREATE TABLE IF NOT EXISTS user_subscriber (
    user_id INT,
    subscriber_id INT,
    PRIMARY KEY (user_id, subscriber_id),
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (subscriber_id) REFERENCES subscriber (subscriber_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS glucose_reading (
    reading_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    device_id INT,
    glucose_level FLOAT,
    timestamp DATETIME,
    latitude FLOAT,
    longitude FLOAT,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES device (device_id) ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS alert (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    reading_id INT,
    user_id INT,
    subscribers_informed JSON,
    created_at DATETIME,
    alert_type VARCHAR(255),
    status VARCHAR(255),
    FOREIGN KEY (reading_id) REFERENCES glucose_reading (reading_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS device_feed (
    feed_id INT PRIMARY KEY AUTO_INCREMENT,
    device_id INT,
    battery_level INT,
    firmware_name VARCHAR(255),           
    firmware_version VARCHAR(255),
    connectivity_status VARCHAR(255),
    error_codes VARCHAR(255),
    timestamp DATETIME,
    FOREIGN KEY (device_id) REFERENCES device (device_id) ON DELETE SET NULL);
    
