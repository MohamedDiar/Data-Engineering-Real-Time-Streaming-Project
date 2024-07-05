import asyncio
import logging
import os
import random
import re

import nest_asyncio
from dotenv import find_dotenv, load_dotenv
from telethon import TelegramClient, events

from writing_to_env import update_env_file

# Allow nested asyncio.run() calls
nest_asyncio.apply()

load_dotenv(find_dotenv())

# Load environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

logging.basicConfig(level=logging.DEBUG)

# Create a TelegramClient instance
client = TelegramClient("session", api_id, api_hash)

async def create_device_alert_bot():
    """
    Creates the DeviceAlerts bot using the Telegram Bot API.
    """
    await create_bot("DeviceAlerts", "DEVICE_ALERTS_BOT")

async def create_glucose_alert_bot():
    """
    Creates the GlucoseAlerts bot using the Telegram Bot API.
    """
    await create_bot("GlucoseAlerts", "GLUCOSE_ALERTS_BOT")

async def create_bot(bot_name, env_var_name):
    """
    Creates a bot with the given name using the Telegram Bot API.

    Args:
        bot_name (str): The name of the bot.
        env_var_name (str): The environment variable name to update with the bot token.
    """
    bot_token = None
    bot_username = None

    @client.on(events.NewMessage(from_users="botfather"))
    async def message_handler(event):
        nonlocal bot_token, bot_username
        
        logging.info(f"Received a message: {event.raw_text}")

        if "Please choose a name for your bot" in event.raw_text:
            await event.reply(bot_name)

        elif "choose a username for your bot" in event.raw_text:
            username_accepted = False
            while not username_accepted:
                bot_username = f"{bot_name}{random.randint(1, 1000)}Bot"
                await event.reply(bot_username)
                logging.info(f"Trying bot username: {bot_username}")
                await asyncio.sleep(5)
                response = await client.get_messages("botfather", limit=1)
                if "Sorry, this username is" not in response[0].message:
                    username_accepted = True

        elif "Done! Congratulations on your new bot" in event.raw_text:
            logging.info(f"Bot '{bot_name}' created with username '{bot_username}'!")
            update_env_file(f"{bot_name}_BotUsername", bot_username)
            bot_token_match = re.findall(r"\d+:[\w-]+", event.raw_text)

            if bot_token_match:
                bot_token = bot_token_match[0]
                update_env_file(env_var_name, bot_token)
                logging.info(f"Updated .env with {env_var_name}={bot_token}")
            await client.disconnect()

    async with client:
        await client.send_message("botfather", "/newbot")
        await client.run_until_disconnected()

async def main():
    """
    Main function that creates the DeviceAlerts and GlucoseAlerts bots.
    """
    await create_device_alert_bot()

    # Reset variables and reconnect for the next bot
    global client
    client = TelegramClient("session", api_id, api_hash)

    await asyncio.sleep(10)
    await create_glucose_alert_bot()

if __name__ == "__main__":
    client.start()
    client.loop.run_until_complete(main())