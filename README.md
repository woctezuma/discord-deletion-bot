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
- `Read Messages/View Channels`,
- `Manage Messages`,
- `Read Message History`.

## Filters

Filters include:
1. regex search in messages, with `"mode": "regex"`,
2. userIDs, with `"mode": "users"`,
3. a combination of both, with `"mode": "regexuser"`.

## Example config.json

The `token` of your bot can be found at `https://discord.com/developers/applications/[APPLICATION_ID]/bot`,
where `[APPLICATION_ID]` should be replaced by **your** application ID.

The `guild`, `match_users` and `ignore_channels` IDs can be found by right-clicking on the server, users, and channels
respectively, after you have enabled the developer tools in the advanced section of the settings of your Discord client.

You can check your `match_regex` with online tools such as [this one][regex-online-tool].

```Json
{
  "guild": "265256381437706240",
  "token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "mode": "regex",
  "match_regex": "\\bretard(?:ed)?\\b",
  "match_users": [
    "252869311545212928",
    "265255911012958208"
  ],
  "ignore_channels": [
    "270579644372090880",
    "356781927836942339",
    "270578632026488851",
    "270695480873189376",
    "419976078321385473",
    "273164941857652737"
  ],
  "archival_enabled": "true",
  "archival_file": "deleted_this.csv"
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

These are optional parameters, to resume from where the script stopped in case of crashes, disconnections, or to debug.

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
[regex-online-tool]: <https://regex101.com/>
