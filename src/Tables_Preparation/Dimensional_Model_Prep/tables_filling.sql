INSTALL mysql;

LOAD mysql;

ATTACH 'host={host} user={user} password={password} port={port} database={database}' AS mysqldb (TYPE mysql);

INSERT INTO dim_user SELECT user_id, full_name, age, gender, contact_number FROM mysqldb.user;


INSERT INTO dim_device SELECT device_id, model FROM mysqldb.device;


INSERT INTO dim_time (date_key, full_date, day, month, year, day_of_week, month_name)
SELECT
    YEAR(date) * 10000 + MONTH(date) * 100 + DAY(date) AS date_key,
    date AS full_date,
    DAY(date) AS day,
    MONTH(date) AS month,
    YEAR(date) AS year,
    DAYNAME(date) AS day_of_week,
    MONTHNAME(date) AS month_name
FROM
    generate_series(CAST('2023-01-01' AS TIMESTAMP), CAST('2025-12-31' AS TIMESTAMP), INTERVAL 1 DAY) AS t(date);


