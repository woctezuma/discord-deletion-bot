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
  "guild": "GUILD_ID_ONLY_NUMBERS",
  "token": "YOUR_BOT_TOKEN",
  "mode": "regex",
  "match_regex": "http(s?):\\/\\/.*tenor\\.com\\/.*",
  "match_users": [
    "ONE_USER_ID_ONLY_NUMBERS",
    "ANOTHER_USER_ID_ONLY_NUMBERS"
  ],
  "ignore_channels": [
    "ONE_CHANNEL_ID_ONLY_NUMBERS",
    "ANOTHER_CHANNEL_ID_ONLY_NUMBERS"
  ],
  "archival_enabled": "true",
  "archival_file": "deleted_this.csv"
}

```

| Setting          | Accepted Value                                                                   |
|------------------|----------------------------------------------------------------------------------|
| guild            | Discord Server Snowflake.                                                        |
| token            | Discord Bot Token.                                                               |
| mode             | `"regex"`, `"users"`, or `"regexuser"`.                                          |
| match_regex      | regex to compare messages against, if the mode is set to `regex` or `regexuser`. |
| match_users      | list of Discord User Snowflakes, if the mode is set to `users` or `regexuser`.   |
| ignore_channels  | list of Discord Channel Snowflakes to bypass. It can be an empty list.           |
| archival_enabled | `"true"` or `"false"`. It toggles the saving of deleted messages.                |
| archival_file    | CSV filename to save deleted messages to, if `archival_enabled` is true.         |

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
