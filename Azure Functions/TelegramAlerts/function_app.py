"""
This script is designed to send alerts to a Telegram bot when certain events occur.

It is triggered by events from an Azure Event Hub, and sends messages to a Telegram bot using the bot's API.

The bot then sends the message to the appropriate chat based on the chat ID.
"""

import azure.functions as func
import logging
import requests
import os

app = func.FunctionApp()

# Bot Tokens
glucose_alerts_bot_token = os.getenv("GLUCOSE_ALERTS_BOT")
device_alerts_bot_token = os.getenv("DEVICE_ALERTS_BOT")

# Channel IDs
high_glucose_chat_id = os.getenv("HIGH_GLUCOSE_CHAT_ID")
low_glucose_chat_id = os.getenv("LOW_GLUCOSE_CHAT_ID")
disconnected_error_chat_id = os.getenv("DISCONNECTED_ERROR_CHAT_ID")
transmission_quality_chat_id = os.getenv("TRANSMISSION_QUALITY_CHAT_ID")
glucose_increasing_trend_chat_id = os.getenv("GLUCOSE_INCREASING_TREND")


def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send message to Telegram: {response.text}")


def escape_markdown(text):
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


@app.function_name(name="high_glucose_trigger")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="above_max_glucose_threshold",
    connection="EventHubConnectionString",
    consumer_group="telegrambot",
)
def high_glucose_trigger(azeventhub: func.EventHubEvent):
    event_data = azeventhub.get_body().decode("utf-8")
    logging.info("High glucose event: %s", event_data)

    message = f"High glucose level detected: {escape_markdown(event_data)}"

    bot_token = glucose_alerts_bot_token
    chat_id = high_glucose_chat_id

    send_telegram_message(bot_token, chat_id, message)


@app.function_name(name="low_glucose_trigger")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="below_min_glucose_threshold",
    connection="EventHubConnectionString",
    consumer_group="below_min",
)
def low_glucose_trigger(azeventhub: func.EventHubEvent):
    event_data = azeventhub.get_body().decode("utf-8")
    logging.info("Low glucose event: %s", event_data)

    message = f"Low glucose level detected: {escape_markdown(event_data)}"

    bot_token = glucose_alerts_bot_token
    chat_id = low_glucose_chat_id

    send_telegram_message(bot_token, chat_id, message)


@app.function_name(name="missed_readings_trigger")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="missed_readings",
    connection="EventHubConnectionString",
    consumer_group="transmission_quality",
)
def missed_readings_trigger(azeventhub: func.EventHubEvent):
    event_data = azeventhub.get_body().decode("utf-8")
    logging.info("Missed readings event: %s", event_data)

    message = f"Missed iinterval Alert: {escape_markdown(event_data)}"

    bot_token = device_alerts_bot_token
    chat_id = transmission_quality_chat_id

    send_telegram_message(bot_token, chat_id, message)


@app.function_name(name="disconnected_error_trigger")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="device_error",
    connection="EventHubConnectionString",
    consumer_group="lost_connection",
)
def disconnected_error_trigger(azeventhub: func.EventHubEvent):
    event_data = azeventhub.get_body().decode("utf-8")
    logging.info("Disconnected error event: %s", event_data)

    message = f"Device disconnected Alert: {escape_markdown(event_data)}"

    bot_token = device_alerts_bot_token
    chat_id = disconnected_error_chat_id

    send_telegram_message(bot_token, chat_id, message)


@app.function_name(name="glucose_increasing_trend_trigger")
@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="increasing_trend_alert",
    connection="EventHubConnectionString",
    consumer_group="sparksql",
)
def glucose_increasing_trend_trigger(azeventhub: func.EventHubEvent):
    event_data = azeventhub.get_body().decode("utf-8")
    logging.info("Glucose increasing trend event: %s", event_data)

    message = f"Glucose increasing trend Alert: {escape_markdown(event_data)}"

    bot_token = glucose_alerts_bot_token
    chat_id = glucose_increasing_trend_chat_id

    send_telegram_message(bot_token, chat_id, message)
