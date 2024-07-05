
"""
This script counts the number of user and device keys in the Redis cache.
"""

import logging

import redis
from conn_config import get_redis_connection, get_sql_connection

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.debug("Started.")

# Get Redis connection
r = get_redis_connection()

# Initialize counters
device_key_count = 0
user_key_count = 0

# Count device keys
for key in r.scan_iter(match="device:*"):
    device_key_count += 1

# Count user keys
for key in r.scan_iter(match="user:*"):
    user_key_count += 1

# Output the counts
print(f"Number of device keys: {device_key_count}")
print(f"Number of user keys: {user_key_count}")

logging.debug("Done.")

