"""Storage Account helper to access the Azure Storage Account"""

import os
import sys
from dotenv import load_dotenv, find_dotenv
import fsspec

load_dotenv(find_dotenv())

# Get the environment variables for storage account
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")
container_name = os.getenv("container_name")

# Getting the environment variables for the database
# Will be used to access the MYSQL database in glucose_dimensional_design.py
db_host = os.getenv("host")
db_user = os.getenv("user")
db_password = os.getenv("password")
db_port = os.getenv("port")
db_name = os.getenv("database")

# Define the path to the folder in the Azure Storage Account
folder_path = "glucose_dimensional_model"

# Define the full path to the folder in the Azure Storage Account
full_path = f"{container_name}/{folder_path}"

# Create a filesystem object with Azure Storage Account credentials
fs = fsspec.filesystem("abfs", account_name=account_name, account_key=account_key)
