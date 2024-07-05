"""
This script adds a list of bots to a list of channels.
"""

from dotenv import load_dotenv, find_dotenv
import os
from telethon import TelegramClient, events, functions,types


load_dotenv(find_dotenv())

# Load environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# List of bot names to add to channels
device_alert_bot= os.getenv("DeviceAlerts_BotUsername")
glucose_alert_bot= os.getenv("GlucoseAlerts_BotUsername")

# List of channel IDs to add bots to
high_glucose_chat_id= int(os.getenv("HIGH_GLUCOSE_CHAT_ID"))
low_glucose_chat_id= int(os.getenv("LOW_GLUCOSE_CHAT_ID"))
transmission_quality_chat_id= int(os.getenv("TRANSMISSION_QUALITY_CHAT_ID"))
disconnected_error_chat_id= int(os.getenv("DISCONNECTED_ERROR_CHAT_ID"))
glucose_increasing_trend= int(os.getenv("GLUCOSE_INCREASING_TREND"))

# Bots to channels mapping
bot_to_channel = {
    device_alert_bot: [disconnected_error_chat_id, transmission_quality_chat_id],
    glucose_alert_bot: [high_glucose_chat_id, low_glucose_chat_id, glucose_increasing_trend],
}

# We are adding the bots to the channels and promoting them to admins
async def main():
    async with TelegramClient("session", api_id, api_hash) as client:
        for bot, channels in bot_to_channel.items():
            for channel_id in channels:
                
                # Promote bot to admin
                try:
                    await client(functions.channels.EditAdminRequest(
                        channel=channel_id,
                        user_id=bot,
                        admin_rights=types.ChatAdminRights(
                            change_info=True,
                            post_messages=True,
                            edit_messages=True,
                            delete_messages=True,
                            ban_users=True,
                            invite_users=True,
                            pin_messages=True,
                            add_admins=False,
                            anonymous=False,
                            manage_call=False,
                        ),
                        rank='bot'
                    ))
                    print(f"Promoted {bot} to admin in channel {channel_id}")
                except Exception as e:
                    print(f"Failed to promote {bot} in channel {channel_id}: {e}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

