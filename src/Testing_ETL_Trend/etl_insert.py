import duckdb
from fsspec import filesystem
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

cursor = duckdb.connect()
cursor.register_filesystem(filesystem('abfs', account_name=os.getenv('account_name'), account_key=os.getenv('account_key')))

cursor.execute('INSTALL mysql;')
cursor.execute('LOAD mysql;')
cursor.execute(f"ATTACH 'host={os.getenv('host')} database={os.getenv('database')} user={os.getenv('user')} password={os.getenv('password')} port={os.getenv('port')}' AS mysqldb (TYPE mysql);")

print('Started loading the data into the staging table')
cursor.execute('''
COPY (
    SELECT 
        user_id,
        device_id, 
        YEAR(timestamp) AS year,
        MONTH(timestamp) AS month,
        DAY(timestamp) AS day,
        AVG(glucose_level) AS avg_glucose,
        MIN(glucose_level) AS min_glucose,
        MAX(glucose_level) AS max_glucose
    FROM 
        mysqldb.glucose_reading
    GROUP BY 
        user_id, 
        device_id,
        YEAR(timestamp),
        MONTH(timestamp),
        DAY(timestamp)
    ORDER BY 
        user_id, 
        year,
        month,
        day
) TO 'abfs://glucosefeeds/aggregates' (FORMAT PARQUET, PARTITION_BY ('year', 'month', 'day'), OVERWRITE_OR_IGNORE);
   ''')

print('The partitioned parquet files are saved in the following path: abfs://glucosefeeds/aggregates')


print('Started loading the data into the dimensional model')
cursor.execute('''
Import database 'abfs://glucosefeeds/glucose_dimensional_model';

INSERT INTO fact_glucose_reading
SELECT
   nextval('seq_fact_glucose_reading'),
   g.user_id,
   g.device_id,
   CONCAT(CAST(g.year AS VARCHAR), LPAD(CAST(g.month AS VARCHAR), 2, '0'), LPAD(CAST(g.day AS VARCHAR), 2, '0')) AS date_key,
   g.avg_glucose,
   g.min_glucose,
   g.max_glucose
FROM
    read_parquet('abfs://glucosefeeds/aggregates/*/*/*/*.parquet', hive_partitioning = 1) as g;

EXPORT DATABASE 'abfs://glucosefeeds/glucose_dimensional_model' (FORMAT PARQUET);
''')

print('The dimensional model is saved in the storage account at abfs://glucosefeeds/glucose_dimensional_model')