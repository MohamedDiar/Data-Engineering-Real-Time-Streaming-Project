"""
Create tables in the database
"""
#%%
import mysql.connector
import sys
from utils.db_config import get_sql_connection
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, 'sql_tables_creation.sql')

cnx = get_sql_connection()

def create_tables():
    """
    Creates tables in the database using SQL commands from a file.

    The function reads SQL commands from a file, splits them into individual commands,
    and executes each command to create tables in the database.
    """
    try:
        cursor = cnx.cursor()
        with open(sql_file_path, "r") as file:
            sql_script = file.read()

            sql_commands = sql_script.split(";")

            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        print("Tables created successfully")
        cnx.commit()

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            print(table)

    except Exception as e:
        print("An error occurred", e)
        cnx.rollback()

    finally:
        cursor.close()
        cnx.close()
        print("Connection closed")

    print("Function create_tables() executed successfully")

#%%
if __name__ == "__main__":
    create_tables()