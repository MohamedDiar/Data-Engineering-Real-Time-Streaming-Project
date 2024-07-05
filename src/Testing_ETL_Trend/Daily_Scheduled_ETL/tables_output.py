"""
This script contains functions to execute SQL commands from .sql files and print the results in a table format.
"""
import logging
import os
import sys
from pathlib import Path

import duckdb
from dotenv import find_dotenv, load_dotenv
from tabulate import tabulate

# Load the environment variables
load_dotenv(find_dotenv())
connection_string = os.getenv('connection_string')
container_name = os.getenv('container_name')

# Connect to DuckDB
cursor = duckdb.connect()

def execute_sql_file(file_name):
    """
    This function executes the SQL commands in the specified file and prints the results in a table format

    Args:
        file_name (str): The name of the .sql file from which to load the SQL commands
    """
    try:
        # Getting the directory of the current script
        current_dir = Path(__file__).parent.absolute()
        
        # Full path to the SQL file
        sql_file_path = current_dir / file_name

        # Loading the SQL commands from the file
        with open(sql_file_path, 'r') as file:
            sql_commands = file.read()
        
        # Formatting the SQL commands with the connection string and container name
        sql_commands = sql_commands.format(
            connection_string=connection_string,
            container_name=container_name
        )
       
        cursor.execute(sql_commands)
        results = cursor.fetchall()
        
        # Using tabulate to print the results in a table format
        column_names = [description[0] for description in cursor.description]
        print(tabulate(results, headers=column_names, tablefmt='grid'))
    except Exception as e:
        logging.error(f'An error occurred while executing {file_name}: {e}')

def aggregates_output_table():
    """
    This function executes the SQL commands in the aggregates_output.sql file
    """
    execute_sql_file('aggregates_output.sql')

def fact_glucose_reading_table_output():
    """
    This function executes the SQL commands in the fact_glucose_reading_table_output.sql file
    """
    execute_sql_file('fact_glucose_reading_table_output.sql')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        if function_name in globals():
            globals()[function_name]()
        else:
            print(f"Function '{function_name}' not found.")
    else:
        print("Please provide a function name to execute.")

