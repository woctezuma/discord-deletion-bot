import argparse
import json
import logging
import sys
from pathlib import Path

from src.disk_utils import archive_message_csv
from src.parsing_utils import (
    message_parser_regex,
    message_parser_regexuser,
    message_parser_user,
)
from src.request_utils import (
    discordapi_check_channel_access,
    discordapi_delete_message,
    discordapi_get_channel_batch,
    discordapi_get_messages_batch,
)


def main():
    # start the logging module
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)

    # load the configuration file
    try:
        with Path("config.json").open() as cfg_file:
            cfg = json.load(cfg_file)
    except FileNotFoundError as e:
        message = (
            f"Unable to start script (something with config.json is wrong?). Error:{e}"
        )
        logger.critical(message)
        sys.exit()

    # load in optional arguments to resume, to prevent re-iteration over millions of messages
    arg = argparse.ArgumentParser()
    arg.add_argument("-rf", "--resumefrom")
    arg.add_argument("-rc", "--resumechannel")
    arg.add_argument("-lb", "--lookback")
    arg.add_argument("-d", "--dryrun", action="store_true")
    args = vars(arg.parse_args())

    if args["dryrun"]:
        logger.warning(
            "DRY: Dry run mode enabled. Messages will not be deleted, but the bot will act like it is.",
        )

    # build the discord headers
    discord_headers = {"Authorization": "Bot " + cfg["token"]}

    # get all the server channels
    channels_raw = discordapi_get_channel_batch(cfg["guild"], discord_headers)

    if channels_raw is None:
        logger.critical(
            "Invalid Discord Guild! (check your token and bot permissions?)",
        )
        sys.exit()

    # if the --resumechannel flag is set, lets skip to that channel
    if args["resumechannel"]:
        i = 0
        for channel in channels_raw:
            if channel["id"] != str(args["resumechannel"]):
                message = f"RESUME: Skipping '{channel['id']}' (#{channel['name']}) on loop '{i}'"
                logger.info(message)

            else:
                message = f"RESUME: Resuming on '{channel['id']}' (#{channel['name']}) on loop '{i}'"
                logger.info(message)
                break
            i += 1
        channels = channels_raw[i:]
    else:
        channels = channels_raw

    # run through the channels, yes this is nested pretty badly don't @ me
    for channel in channels:
        if channel["type"] == 0:
            # if the channel is in the ignore list, skip
            if channel["id"] in cfg["ignore_channels"]:
                message = (
                    f"SKIPPING CHANNEL FROM CFG: {channel['id']} (#{channel['name']})"
                )
                logger.info(message)
                continue

            if discordapi_check_channel_access(channel, discord_headers):
                message = f"ALLOWED CHANNEL READ: {channel['id']} (#{channel['name']})"
                logger.info(message)

                if args["resumefrom"] and args["resumechannel"] == channel["id"]:
                    value_before = args["resumefrom"]
                else:
                    value_before = channel["last_message_id"]

                history = 0
                value_lastid = None

                while True:
                    message = "GETTING BATCH OF 100 MESSAGES: LAST ID {} in {}".format(
                        value_before,
                        channel["name"],
                    )
                    logger.info(message)
                    msgs = discordapi_get_messages_batch(
                        channel["id"],
                        value_before,
                        discord_headers,
                    )

                    # reloop if we dont get the right api data
                    if msgs is False:
                        continue

                    if msgs is None:
                        logger.warning(
                            "DISCORD API ERROR: Received None for messages batch, trying again.",
                        )
                        continue

                    history = history + len(msgs)

                    for msg in msgs:
                        value_lastid = msg["id"]

                        if cfg["mode"].lower() == "users":
                            message_result = message_parser_user(
                                msg,
                                cfg["match_users"],
                            )
                        elif cfg["mode"].lower() == "regex":
                            message_result = message_parser_regex(
                                msg,
                                cfg["match_regex"],
                            )
                        elif cfg["mode"].lower() == "regexuser":
                            message_result = message_parser_regexuser(
                                msg,
                                cfg["match_users"],
                                cfg["match_regex"],
                            )
                        else:
                            logger.critical(
                                "Unsupported mode! (should be set to either users or regex)",
                            )
                            sys.exit()

                        # if this is returned to be true from the parsers, we have to act on the message
                        if message_result:
                            message = "MSG FOUND: Reason: {} Message: {}".format(
                                message_result,
                                msg["content"].lower(),
                            )
                            logger.info(message)

                            if args["dryrun"]:
                                logger.debug(
                                    "DRY: Message not being deleted. --dryrun enabled!",
                                )
                            else:
                                delet = discordapi_delete_message(
                                    channel["id"],
                                    msg["id"],
                                    discord_headers,
                                )
                                while delet is not True:
                                    delet = discordapi_delete_message(
                                        channel["id"],
                                        msg["id"],
                                        discord_headers,
                                    )

                            if cfg["archival_enabled"]:
                                archive_message_csv(channel, msg, cfg["archival_file"])

                    # if we are in limited lookback mode, hit n and move to next channel
                    if (
                        args["lookback"]
                        and args["lookback"] != 0
                        and history >= int(args["lookback"])
                    ):
                        message = f"LOOKBACK ENABLED, LOOPED THROUGH {history} MESSAGES IN {value_lastid}"
                        logger.info(message)
                        break

                    # if the value_lastid is not changing, we hit the end of the channel
                    if value_before == value_lastid:
                        message = f"END OF CHANNEL: LAST ID {value_lastid}"
                        logger.info(message)
                        break

                    value_before = value_lastid


if __name__ == "__main__":
    main()
