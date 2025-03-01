import logging
import time
from http import HTTPStatus

import requests

TIMEOUT_IN_SECONDS = 5

# Reference: https://discord.com/developers/docs/resources/channel#channel-object-channel-types
GUILD_TEXT_CHANNEL_TYPE = 0
PUBLIC_THREAD_CHANNEL_TYPE = 11
PRIVATE_THREAD_CHANNEL_TYPE = 12
GUILD_FORUM_CHANNEL_TYPE = 15

# start the logging module
logger = logging.getLogger(__name__)


def discordapi_get_channel_batch(guild, header) -> dict | None:
    request = requests.get(
        "https://discordapp.com/api/guilds/" + guild + "/channels",
        headers=header,
        timeout=TIMEOUT_IN_SECONDS,
    )

    return request.json() if request.ok else None


def discordapi_get_thread_batch(guild, header) -> dict | None:
    # Reference: https://discord.com/developers/docs/topics/threads#enumerating-threads

    request = requests.get(
        "https://discordapp.com/api/guilds/" + guild + "/threads/active",
        headers=header,
        timeout=TIMEOUT_IN_SECONDS,
    )

    return request.json() if request.ok else None


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
