IMPORT DATABASE 'abfs://glucosefeeds/glucose_dimensional_model';

INSERT INTO fact_glucose_reading
SELECT
   nextval('seq_fact_glucose_reading'),
   g.user_id,
   g.device_id,
   CONCAT(g.year, LPAD(CAST(g.month AS VARCHAR), 2, '0'), LPAD(CAST(g.day AS VARCHAR), 2, '0')) AS date_key,
   g.avg_glucose,
   g.min_glucose,
   g.max_glucose
FROM
   read_parquet('abfs://glucosefeeds/aggregates/year=' || EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 day') || '/month=' || LPAD(CAST(EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 day') AS VARCHAR), 2, '0') || '/day=' || LPAD(CAST(EXTRACT(DAY FROM CURRENT_DATE - INTERVAL '1 day') AS VARCHAR), 2, '0') || '/*.parquet', hive_partitioning = 1) as g;

EXPORT DATABASE 'abfs://glucosefeeds/glucose_dimensional_model' (FORMAT PARQUET);
