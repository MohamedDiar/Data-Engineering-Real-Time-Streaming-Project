CREATE TRIGGER check_glucose_after_insert
AFTER INSERT ON glucose_reading
FOR EACH ROW
BEGIN
    -- Declaring variables
    DECLARE min_glucose FLOAT;
    DECLARE max_glucose FLOAT;
    DECLARE subscriber_ids JSON;  

    -- Getting the min and max glucose values for the user and storing them into the min_glucose and max_glucose variables
    SELECT mi.min_glucose, mi.max_glucose INTO min_glucose, max_glucose
    FROM medical_info mi
    WHERE mi.user_id = NEW.user_id;

    -- Checking if the new glucose reading is out of the normal range
    IF NEW.glucose_level < min_glucose OR NEW.glucose_level > max_glucose THEN
        -- Getting the list of subscriber IDs
        SELECT JSON_ARRAYAGG(subscriber_id) INTO subscriber_ids
        FROM user_subscriber
        WHERE user_id = NEW.user_id;

        -- Inserting an alert with the list of subscriber IDs
        INSERT INTO alert (reading_id, user_id, subscribers_informed, created_at, alert_type, status)
        VALUES (NEW.reading_id, NEW.user_id, subscriber_ids, NOW(), 'Abnormal Glucose Level', 'Active');
    END IF;
END;
