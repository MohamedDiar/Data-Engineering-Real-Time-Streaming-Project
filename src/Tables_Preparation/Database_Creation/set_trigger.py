"""
Create a trigger in the database
"""
#%%
import os
import sys
import mysql.connector
from utils.db_config import get_sql_connection

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, "alert_table_trigger.sql")

cnx = get_sql_connection()

def create_trigger():
    """
    Creates a trigger in the database using an SQL script file.

    This function reads the alert_table_trigger script file, splits it into individual commands,
    and executes each command to create a trigger in the database.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(script_dir, "alert_table_trigger.sql")

    cnx = get_sql_connection()

    try:
        cursor = cnx.cursor()
        with open(sql_file_path, "r") as file:
            sql_script = file.read()

            # Remove DELIMITER statements and split commands by 'END$$'
            sql_script = sql_script.replace("DELIMITER $$", "").replace("$$", "")
            sql_commands = sql_script.split("END;")

            for command in sql_commands:
                command = command.strip()
                if command:
                    cursor.execute(command + " END;")
                    
        print("Trigger created successfully")
        cnx.commit()

        cursor.execute("SHOW TRIGGERS;")
        triggers = cursor.fetchall()
        for trigger in triggers:
            print(trigger)

    except Exception as e:
        print("An error occurred", e)
        cnx.rollback()

    finally:
        cursor.close()
        cnx.close()
        print("Connection closed")

    print("Function create_trigger() executed successfully")


if __name__ == "__main__":
    create_trigger()

