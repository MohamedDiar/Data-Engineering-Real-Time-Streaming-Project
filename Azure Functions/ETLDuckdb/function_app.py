"""

This script is a timer-triggered Azure Function App. 
It is used to create two functions that will be used to run the ETL process and insert data into the fact table.

The first function, etl_work, is responsible for running the ETL process. It is scheduled to run every day at 16:47 UTC. 
The function reads the SQL commands from the glucose_aggregate.sql file and executes them using the DuckDB cursor.

The second function, fact_table_insert, is responsible for inserting data into the fact table.
 It is scheduled to run every day some time after the ETL process has completed.
"""

import logging
import azure.functions as func
import duckdb
import fsspec
import os

app = func.FunctionApp()

#Getting Schedule Timer
schedule_info_etl = os.getenv("SCHEDULE_ETL")
schedule_info_fact = os.getenv("SCHEDULE_FACT_INSERT")

#Storage account details
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")

#MySQL database details
db_host = os.getenv("host")
db_user = os.getenv("user")
db_password = os.getenv("password")
db_port = 3306
db_name = os.getenv("database")


fs = fsspec.filesystem("abfs", account_name=account_name, account_key=account_key)

cursor = duckdb.connect()
cursor.register_filesystem(fs)


@app.function_name(name="etl_work")
@app.schedule(
    schedule=schedule_info_etl, arg_name="myTimer", run_on_startup=False, use_monitor=True
)
def etl_work(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function executed.")
    
    with open("glucose_aggregate.sql", "r") as file:
            sql_commands = file.read()
            sql_commands = sql_commands.format(
                host=db_host,
                user=db_user,
                password=db_password,
                port=db_port,
                database=db_name
            )
    try:        
        cursor.execute(sql_commands) 
    except Exception as e:
        logging.info("An error occurred: %s", e)


@app.function_name(name="fact_table_insert")
@app.schedule(
    schedule=schedule_info_fact, arg_name="myTimer", run_on_startup=False, use_monitor=True
)
def fact_table_insert(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function executed.")

    try:
        with open("inserting_fact_table.sql", "r") as file:
            sql_commands = file.read()
        cursor.execute(sql_commands)
    
    except Exception as e:
        logging.info("An error occurred: %s", e)