"""
With this script, we use duckdb to create a dimensional model for the glucose data. It is created using the star schema,
with a fact table and dimension tables.

The script creates tables in a database, fills them with data, and exports them to ADLS.
"""

import duckdb
import os
import sys
from setup_storage_account import fs, db_host, db_user, db_password, db_port, db_name,container_name


# We Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Path to the database be loaded with duckdb and used to create the dimensional model
gdm_path = os.path.join(script_dir, "glucose_dimensional_model.db")

# SQL script that contains the commands to create tables in glucose_dimensional_model.db
table_creation_path = os.path.join(script_dir, "tables_creation.sql")

# SQL script that contains the commands to fill tables in glucose_dimensional_model.db
table_filling_path = os.path.join(script_dir, "tables_filling.sql")

# SQL script that contains the commands to export tables to ADLS
export_adls_path = os.path.join(script_dir, "export_adls.sql")

# Remove the database file if it already exists
if os.path.exists(gdm_path):
    os.remove(gdm_path)

# If the database file does not exist, it will be created and connected to
cursor = duckdb.connect(gdm_path)

# register_filesystem() method is used to register the filesystem object with the duckdb connection
cursor.register_filesystem(fs)



#----------------Functions to create and export the dimensional model -----------------------------#

def remove_container_contents(fs, container_name):
    """
    Remove all files and folders in the specified Azure container.
   
    args:
        :param fs: The filesystem object with Azure Storage Account credentials
        :param container_name: The name of the container to clean
    """
    try:
        # List all items in the container
        items = fs.ls(container_name)
        print(items)
        
        if not items:
            print(f"The container '{container_name}' is already empty.")
            return
       
        # Remove each item
        for item in items:
            # Check if the item is a directory
            if fs.isdir(item):
                fs.rm(item, recursive=True)
            # If the item is a file, remove it
            else:
                fs.rm(item)
       
        print(f"All contents of container '{container_name}' have been removed.")
    except Exception as e:
        print(f"An error occurred while cleaning the container: {str(e)}")

def create_and_fill_tables():
    """
    This Function creates tables in the database and fills them with data.
    """

    try:
        # Read and execute SQL commands for table creation
        with open(table_creation_path, "r") as file:
            sql_commands = file.read()
        cursor.execute(sql_commands)
        print("All Data Warehouse Tables Created Successfully")

        # Read and execute SQL commands for filling tables
        with open(table_filling_path, "r") as file:
            sql_commands = file.read()
            sql_commands = sql_commands.format(
                host=db_host,
                user=db_user,
                password=db_password,
                port=db_port,
                database=db_name,
            )
        cursor.execute(sql_commands)
        print("Dimension Tables Of Data warehouse filled successfully")

    except FileNotFoundError as fnf_error:
        print(f"Error: File not found - {fnf_error}")

    except IOError as io_error:
        print(f"Error: IO error - {io_error}")

    except Exception as e:
        print(f"An error occurred: {e}")


def export_to_adls():
    """
    Once the tables are created and filled, the .sql file used in this function will be executed to export the tables to ADLS.
    """
    try:
        with open(export_adls_path, "r") as file:
            sql_commands = file.read()
        cursor.execute(sql_commands)
        print("Operation of exporting to ADLS completed successfully")
    except Exception as e:
        print("Error while exporting to ADLS:", str(e))
    finally:
        cursor.close()


if __name__ == "__main__":
    remove_container_contents(fs, container_name)
    create_and_fill_tables()
    export_to_adls()