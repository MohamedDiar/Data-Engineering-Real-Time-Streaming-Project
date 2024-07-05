INSTALL mysql;

LOAD mysql;

ATTACH 'host={host} user={user} password={password} port={port} database={database}' AS mysqldb (TYPE mysql);

COPY (
    SELECT 
        user_id,
        device_id, 
        YEAR(timestamp) AS year,
        LPAD(CAST(MONTH(timestamp) AS VARCHAR), 2, '0') AS month,
        LPAD(CAST(DAY(timestamp) AS VARCHAR), 2, '0') AS day,
        AVG(glucose_level) AS avg_glucose,
        MIN(glucose_level) AS min_glucose,
        MAX(glucose_level) AS max_glucose
    FROM 
        mysqldb.glucose_reading
    WHERE
        CAST(timestamp AS DATE) = CURRENT_DATE - INTERVAL '1' DAY
    GROUP BY 
        user_id, 
        device_id,
        YEAR(timestamp),
        LPAD(CAST(MONTH(timestamp) AS VARCHAR), 2, '0'),
        LPAD(CAST(DAY(timestamp) AS VARCHAR), 2, '0')
    ORDER BY 
        user_id, 
        year,
        month,
        day
) TO 'abfs://glucosefeeds/aggregates' (FORMAT PARQUET, PARTITION_BY ('year', 'month', 'day'), OVERWRITE_OR_IGNORE);

