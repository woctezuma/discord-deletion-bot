import argparse
import json
import logging
import sys

import requests

from functions import *

# start the logging module
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# load the configuration file
try:
    with open("config.json") as cfgFile:
        cfg = json.load(cfgFile)
except Exception as e:
    logger.critical(
        f"Unable to start script (something with config.json is wrong?). Error:{e}",
    )
    sys.exit()

# load in optional arguements to resume, to prevent re-iteration over millions of messages
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
channels_req = requests.get(
    "https://discordapp.com/api/guilds/" + cfg["guild"] + "/channels",
    headers=discord_headers,
)
if channels_req.status_code != 200:
    logger.critical("Invalid Discord Guild! (check your token and bot permissions?)")
    sys.exit()
else:
    channels_raw = channels_req.json()

# if the --resumechannel flag is set, lets skip to that channel
if args["resumechannel"]:
    i = 0
    for channel in channels_raw:
        if channel["id"] != str(args["resumechannel"]):
            logger.info(
                f"RESUME: Skipping '{channel['id']}' (#{channel['name']}) on loop '{i}'",
            )
        else:
            logger.info(
                f"RESUME: Resuming on '{channel['id']}' (#{channel['name']}) on loop '{i}'",
            )
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
            logger.info(
                f"SKIPPING CHANNEL FROM CFG: {channel['id']} (#{channel['name']})",
            )
            continue

        if discordapi_check_channel_access(channel["id"], discord_headers):
            logger.info(f"ALLOWED CHANNEL READ: {channel['id']} (#{channel['name']})")

            if args["resumefrom"] and args["resumechannel"] == channel["id"]:
                BEFORE = args["resumefrom"]
            else:
                BEFORE = channel["last_message_id"]

            history = 0

            while True:
                logger.info(
                    "GETTING BATCH OF 100 MESSAGES: LAST ID {} in {}".format(
                        BEFORE,
                        channel["name"],
                    ),
                )
                msgs = discordapi_get_messages_batch(
                    channel["id"],
                    BEFORE,
                    discord_headers,
                )

                # reloop if we dont get the right api data
                if msgs is False:
                    continue

                if msgs is None:
                    logger.warning(
                        "DISCORD API ERROR: Recieved None for messages batch, trying again.",
                    )
                    continue

                history = history + len(msgs)

                for msg in msgs:
                    LASTID = msg["id"]

                    if cfg["mode"].lower() == "users":
                        message_result = message_parser_user(msg, cfg["match_users"])
                    elif cfg["mode"].lower() == "regex":
                        message_result = message_parser_regex(msg, cfg["match_regex"])
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
                        logger.info(
                            "MSG FOUND: Reason: {} Message: {}".format(
                                message_result,
                                msg["content"].lower(),
                            ),
                        )

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
                if args["lookback"] != 0:
                    if history >= int(args["lookback"]):
                        logger.info(
                            f"LOOKBACK ENABLED, LOOPED THROUGH {history} MESSAGES IN {LASTID}",
                        )
                        break

                # if the LASTID is not changing, we hit the end of the channel
                if BEFORE == LASTID:
                    logger.info(f"END OF CHANNEL: LAST ID {LASTID}")
                    break
                else:
                    BEFORE = LASTID
