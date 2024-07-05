"""
This file is used for the connection setup to Redis and MySQL databases.
"""

import os
import redis
import mysql.connector
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

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
    def get_instance(user, password, host, database, port):
        """
        Returns the singleton instance of the SQL connection.

        Args:
            user: The username for the SQL connection.
            password: The password for the SQL connection.
            host: The host for the SQL connection.
            database: The database name for the SQL connection.
            port: The port number for the SQL connection.

        Returns:
            The singleton instance of the SQL connection.
        """
        if SQLConnection._instance is None:
            SQLConnection._instance = mysql.connector.connect(
                user=user,
                password=password,
                host=host,
                database=database,
                port=port
            )
        return SQLConnection._instance

def get_sql_connection():
    """
    Returns a SQL connection instance.
    """
    return SQLConnection.get_instance(
        os.getenv("user"),
        os.getenv("password"),
        os.getenv("host"),
        os.getenv("database"),
        int(os.getenv("port"))
    )


class RedisConnection:
    """
    A class representing a Redis connection.

    This class provides a static method to get a singleton instance of a Redis connection.

    Attributes:
        _instance: The singleton instance of the Redis connection.

    Methods:
        get_instance: Returns the singleton instance of the Redis connection.
    """
    
    _instance = None

    @staticmethod
    def get_instance(host, port, password):
        """
        Returns the singleton instance of the Redis connection.

        Args:
            host: The host for the Redis connection.
            port: The port for the Redis connection.
            password: The password for the Redis connection.

        Returns:
            The singleton instance of the Redis connection.
        """
        if RedisConnection._instance is None:
            RedisConnection._instance = redis.Redis(
                host=host,
                port=port,
                password=password,
                ssl=True,
                decode_responses=True
            )
        return RedisConnection._instance

def get_redis_connection():
    """
    Returns a Redis connection instance.
    """
    return RedisConnection.get_instance(
        os.getenv('REDIS_HOST_NAME'),
        int(os.getenv('REDIS_SSL_PORT')),
        os.getenv('REDIS_PRIMARY_ACCESS_KEY')
    )

