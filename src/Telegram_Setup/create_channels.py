"""
This script creates the channels in the Telegram account and updates the .env file with the chat IDs.
"""

import os

from dotenv import find_dotenv, load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest

from writing_to_env import update_env_file

# Load environment variables
load_dotenv(find_dotenv())

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

channels_to_create = [
    "Low Glucose Alert",
    "High Glucose Alert",
    "Transmission Quality",
    "Device Disconnected Error",
    "Glucose Increasing Trend",
]

env_var_to_chat_id = {
    "LOW_GLUCOSE_CHAT_ID": "Low Glucose Alert",
    "HIGH_GLUCOSE_CHAT_ID": "High Glucose Alert",
    "TRANSMISSION_QUALITY_CHAT_ID": "Transmission Quality",
    "DISCONNECTED_ERROR_CHAT_ID": "Device Disconnected Error",
    "GLUCOSE_INCREASING_TREND": "Glucose Increasing Trend",
}

with TelegramClient("session", api_id, api_hash) as client: # A session file will be created in the root directory
    for channel_name in channels_to_create:
        try:
            result = client(
                CreateChannelRequest(
                    title=channel_name,
                    about=f"This is {channel_name}.",
                    megagroup=False,  # Set to False for regular groups
                )
            )
            chat_id = str(result.chats[0].id)
            modified_chat_id = f"-100{chat_id}"

            print(
                f"Created channel: {result.chats[0].title} with ID: {modified_chat_id}"
            )

            # Find the corresponding env var name and update the .env file
            for env_var, name in env_var_to_chat_id.items():
                if name == channel_name:
                    update_env_file(env_var, modified_chat_id)
                    break
        except Exception as e:
            print(f"Failed to create channel '{channel_name}': {e}")
