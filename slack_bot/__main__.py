"""
Checks calculates this month's rent
"""

import sys
import string
from pathlib import Path
import time
from os import environ
import json

from slack_sdk import WebClient

from . import calc_rent
from .calc_rent import ConfigData, calculate_rent_due

RATE_LIMIT = 0.5  # seconds
CONFIG_FILE = Path().home() / ".local/share/slack_bot/rent.json"


if not CONFIG_FILE.exists():
    sys.stderr.write(f"Failed to open {CONFIG_FILE}")
    sys.exit(4)


def get_user_dict():
    client = WebClient(environ["SLACK_API_KEY"])
    time.sleep(RATE_LIMIT)
    users = client.users_list()
    user_dict = {member["name"]: member["id"] for member in users.data["members"]}
    print(json.dumps(user_dict, indent=4))


def get_sum_from_message(message: str) -> int:
    """
    gets all of the numbers, assumes they are in dollars
    returns the number of cents of the sum
    """
    numbers = []
    for word in message.split():
        no_money = word.strip("$")
        try:
            numbers.append(float(no_money) * 100)
        except ValueError:
            pass
    return int(sum(numbers))


def run_bot(config_data: ConfigData):
    client = WebClient(environ["SLACK_API_KEY"])
    time.sleep(RATE_LIMIT)
    history = client.conversations_history(channel=config_data.channel_id)
    input_message: str = history.data["messages"][0]["text"]
    if not input_message.startswith("!rent"):
        sys.stderr.write("Last message was not invoking rent command")
        sys.exit(3)
    utilities_owed = get_sum_from_message(input_message)
    output_messages, _ = calculate_rent_due(config_data, set(), utilities_owed)
    for message in output_messages:
        time.sleep(RATE_LIMIT)
        client.chat_postMessage(channel=config_data.channel_id, text=message)


run_bot(ConfigData.fromDict(json.loads(CONFIG_FILE.read_text("utf-8"))))
