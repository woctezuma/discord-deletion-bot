# Discord Deletion Bot

This repository contains Python code to delete in bulk Discord messages based on a regex filter.

## Requirements

- Install the latest version of [Python 3.X][python-download].
- Install the required packages:

```bash
pip install -r requirements.txt
```

- You should run the script with [a Discord bot][discordpy-doc], not a user account!

Permissions of the bot should include:
- `VIEW_CHANNEL`,
- `MANAGE_CHANNELS`,
- `READ_MESSAGE_HISTORY`.

## Filters

Filters include:
1. regex search in messages,
2. userIDs,
3. a combination of both.

## Example config.json

```Json
{
    "guild":"265256381437706240",
    "token":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "mode":"regex",
    "match_regex":"\\bretard(?:ed)?\\b",
    "match_users":["252869311545212928","265255911012958208"],
    "ignore_channels":["270579644372090880","356781927836942339","270578632026488851","270695480873189376","419976078321385473","273164941857652737"],
    "archival_enabled":"true",
    "archival_file":"deleted_this.csv"
}

```

| Setting          | Accepted Value                                                    |
| ---------------- | ----------------------------------------------------------------- |
| guild            | Discord Server Snowflake                                          |
| token            | Discord Bot Token                                                 |
| mode             | "regex", "users", or "regexuser"                                  |
| match_regex      | regex to compare messages against if mode is set to regex         |
| match_users      | list of Discord User Snowflakes if mode is set to users           |
| ignore_channels  | list of Discord Channel Snowflakes to bypass, can be empty list   |
| archival_enabled | true or false, toggles saving of deleted messages                 |
| archival_file    | location to save deleted messages csv if archival_enabled is true |

## Command Line Parameters

These are optional. Best used to pick off where the script stopped on a crash or disconnect or debugging.

```
--resumefrom <Discord Message Snowflake>
--resumechannel <Discord Channel Snowflake>
--dryrun <bool, disables sending delete commands to API>
--lookback <int>, only go back x messages per channel.
```

## Running delet.py

```
python .\delet.py
python .\delet.py --resumechannel 265256381437706240
python .\delet.py --resumechannel 265256381437706240 --resumefrom 469620983704190999 --dryrun
```

<!-- Definitions -->

[python-download]: <https://www.python.org/downloads/>
[discordpy-doc]: <https://discordpy.readthedocs.io/en/latest/discord.html>
