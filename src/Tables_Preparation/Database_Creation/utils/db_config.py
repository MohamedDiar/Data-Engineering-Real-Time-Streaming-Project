"""
This file is used to create a connection to the SQL Server database.
"""
#%%
import os
import sys

import mysql.connector
from dotenv import find_dotenv, load_dotenv

# Load the environment variables
load_dotenv(find_dotenv())


sql_db = {}
sql_db["host"] = os.getenv("host")
sql_db["port"] = os.getenv("port")
sql_db["user"] = os.getenv("user")
sql_db["password"] = os.getenv("password")
sql_db["database"] = os.getenv("database")


class SQLConnection:
    """
    A class representing a SQL connection.

    This class provides a static method to get a singleton instance of a SQL connection.

    Attributes:
        _instance: The singleton instance of the SQL connection.

    Methods:
        get_instance: Returns the singleton instance of the SQL connection.

    """

    _instance = None

    @staticmethod
    def get_instance(username, password, host, database, port):
        """
        Returns the singleton instance of the SQL connection.

        Args:
            username: The username for the SQL connection.
            password: The password for the SQL connection.
            host: The host for the SQL connection.
            database: The database name for the SQL connection.
            port: The port number for the SQL connection.

        Returns:
            The singleton instance of the SQL connection.

        """
        if SQLConnection._instance is None:
            SQLConnection._instance = mysql.connector.connect(
                user=username,
                password=password,
                host=host,
                database=database,
                port=port,
            )
        return SQLConnection._instance



def get_sql_connection():
    """
    Returns a SQL connection instance.
    """
    global sql_db

    return SQLConnection.get_instance(
        sql_db["user"],
        sql_db["password"],
        sql_db["host"],
        sql_db["database"],
        int(sql_db["port"]),
    )
