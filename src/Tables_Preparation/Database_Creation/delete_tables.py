"""
Delete all tables in the database
"""

import mysql.connector
from utils.db_config import get_sql_connection
import os


tables = [
    "device_feed",
    "patient_device",
    "device_settings",
    "alert",
    "glucose_reading",
    "device",
    "user_subscriber",
    "medical_info",
    "subscriber",
    "doctor",
    "manufacturer",
    "user",
]

cnx = get_sql_connection()

def delete_tables():
    """
    The function deletes all tables in the database.
    """    
    try:
        cursor = cnx.cursor()
        
        # Get the list of existing tables
        cursor.execute("SHOW TABLES")
        existing_tables = [item[0] for item in cursor.fetchall()]
        
        for table_name in tables:
            if table_name in existing_tables:
                # Construct SQL command with the table name
                sql_command = "DROP TABLE IF EXISTS `{}`".format(table_name)
                cursor.execute(sql_command)
                print("Table " + table_name + " deleted")
            else:
                print("Table " + table_name + " does not exist")
        
        cnx.commit()
    except Exception as e:
        print("An error occurred", e)
        cnx.rollback()
        return False
    finally:
        cursor.close()
        cnx.close()
        print("Connection closed")
    print("Function delete_tables() executed successfully")
    return True

if __name__ == "__main__":
    delete_tables()
