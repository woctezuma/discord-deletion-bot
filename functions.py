import csv
import logging
import re
import time
from http import HTTPStatus
from pathlib import Path

import requests

TIMEOUT_IN_SECONDS = 5

# start the logging module
logger = logging.getLogger(__name__)


def discordapi_check_channel_access(channel, header) -> bool:
    request = requests.get(
        "https://discordapp.com/api/channels/" + channel["id"] + "/messages?limit=1",
        headers=header,
        timeout=TIMEOUT_IN_SECONDS,
    )
    is_a_success = request.ok

    if not is_a_success:
        message = f"{request.status_code} for {channel['id']} (#{channel['name']})"
        logger.error(message)

    return is_a_success


def discordapi_get_messages_batch(channel, before, header):
    request = requests.get(
        "https://discordapp.com/api/channels/"
        + channel
        + "/messages?limit=100&before="
        + before,
        headers=header,
        timeout=TIMEOUT_IN_SECONDS,
    )
    if request.ok:
        response = request.json()
    elif request.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        json = request.json()
        wait_timer = get_cooldown_future(json)
        message = f"DISCORD API RATE LIMIT! [getmsgs] - Backing off and retrying in {wait_timer} seconds"
        logger.warning(message)
        time.sleep(wait_timer)
        response = None
    else:
        message = f"DISCORD API PROBLEM! - Got status code {request.status_code}. Waiting 10 seconds"
        logger.warning(message)
        time.sleep(10)
        response = False

    return response


def discordapi_delete_message(channel, message, header) -> bool:
    request = requests.delete(
        "https://discordapp.com/api/channels/" + channel + "/messages/" + message,
        headers=header,
        timeout=TIMEOUT_IN_SECONDS,
    )
    is_a_success = bool(request.status_code == HTTPStatus.NO_CONTENT)

    if not is_a_success:
        if request.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            json = request.json()
            wait_timer = get_cooldown_future(json)
            message = f"DISCORD API RATE LIMIT! [delete] - Backing off and retrying in {wait_timer} seconds"
            logger.warning(message)
            time.sleep(wait_timer)
        else:
            message = f"DISCORD API UNKNOWN ERROR! Status code {request.status_code}"
            logger.error(message)

    return is_a_success


def get_cooldown_future(rsp):
    return round(float(rsp["retry_after"] / 1000) + 1, 2)


# return True if we should delete the message
def message_parser_user(message, users):
    if message["author"]["id"] in users:
        return message["author"]["id"]
    return False


# return True if we should delete the message
def message_parser_regex(message, regex):
    regex_found = re.findall(regex, message["content"].lower())
    if len(regex_found) == 0:
        return False
    return regex_found


def message_parser_regexuser(message, users, regex):
    if message["author"]["id"] in users:
        regex_found = re.findall(regex, message["content"].lower())
        if len(regex_found) == 0:
            return False
        return regex_found
    return False


def archive_message_csv(channel, message, file) -> bool:
    with Path(file).open("a", encoding="utf-8", newline="") as f:
        f_writer = csv.writer(f)
        f_writer.writerow(
            [
                message["timestamp"],
                channel["id"],
                channel["name"],
                message["id"],
                message["author"]["id"],
                message["author"]["username"],
                message["content"],
            ],
        )
    return True
