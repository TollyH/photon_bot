# Photon Discord Bot Framework

An easily expandable Discord Bot written in Python 3 using the [pycord](https://github.com/Pycord-Development/pycord) library.

## Table of Contents
- [Photon Discord Bot Framework](#photon-discord-bot-framework)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Running the Bot](#running-the-bot)
  - [Configuration Files](#configuration-files)
    - [Required Sections](#required-sections)
  - [Plugins](#plugins)
    - [Default Plugins](#default-plugins)
      - [Commands](#commands)
      - [Events](#events)
      - [Tasks](#tasks)
    - [Examples](#examples)
      - [Example Command Plugin](#example-command-plugin)
      - [Example Event Plugin](#example-event-plugin)
      - [Example Task Plugin](#example-task-plugin)
  - [Third-Party APIs](#third-party-apis)
  - [Utils](#utils)
  - [Resources](#resources)
    - [Fonts](#fonts)
    - [Images](#images)
    - [Text](#text)

## Installation

**Python 3.8 or greater and a MySQL/MariaDB server are required.**

- Clone this repository with `git clone https://github.com/TollyH/photon_bot.git`, or by using the download button above
- Enter the new directory (`cd photon_bot`)
- Install required packages using `python3 -m pip install -r requirements.txt`
- Create a new database in your MySQL/MariaDB server and execute the contents of `database_template.sql` in it.
- Create a new configuration file based off of `configs/config-blank.ini` and fill in the `Personalisation`, `DatabaseConnection`, and `DiscordAuth` sections at minimum (more information on config files can be found below)
- If you want the `web` commands to work (these pull data from third-party APIs such as Reddit), you will need to register for all the required information in the config file through the relevant websites (each one has a free plan). Links for each one can be found below. **If you do not wish to do this, remove `web` from the `Plugins -> Commands` field of the config file.**

## Running the Bot

To run the bot, simply use `python3 . /path/to/config/file.ini` from within the repository root directory.

## Configuration Files

The bot loads all required authentication information, as well as the status it should give itself, from INI files. A blank template can be found in `configs/config-blank.ini`.

### Required Sections

| Section / Key          | Description                                                    |
|------------------------|----------------------------------------------------------------|
| **Personalisation**    | Contains information about the status the bot will give itself |
| — StatusText           | The text of the bot's custom status                            |
| — StatusType           | `0` = Playing `1` = Listening `2` = Watching `3` = Competing   |
| **Plugins**            | Stores comma separated lists of plugin names to load           |
| — Commands             | Commands to load from `plugins/commands/`                      |
| — Events               | Events to load from `plugins/events/`                          |
| — Tasks                | Tasks to load from `plugins/tasks/`                            |
| **DatabaseConnection** | Login and connection information for the bot database          |
| — Host                 | The hostname to connect to                                     |
| — Username             | The username of the MySQL user to use                          |
| — Password             | The password of the MySQL user to use                          |
| — DatabaseName         | The name of the database which you created during installation |
| **DiscordAuth**        | Login information for Discord                                  |
| — Token                | The token of the Discord bot account to connect to             |

## Plugins

This framework has three types of plugin: `commands`, `events`, and `tasks`, however each are defined in a very similar way, and it is ultimately up to you which one you decide to place new features under, as each type does not limit what can be placed under it. Plugins define the functionality of the bot, with commands usually taking the form of an application command, such as slash commands, events taking the form of event listeners, such as a message sent event, and tasks being functions that repeat in the background whilst the bot is online. When loading a plugin, the framework simply imports the `<plugin_name>.py` file from the relevant directory within the `plugins` directory and invokes the `register_commands`, `register_events`, or `register_tasks` method respectively. These functions have a single positional argument: the instance of `PhotonBot` that is loading the plugin.

### Default Plugins

#### Commands

- `admin` - Commands that can only be run by Administrators.
- `discord_info` - Commands that get information about Discord objects.
- `fun_basic` - Simple commands designed for entertainment.
- `fun_games` - More complex commands that allow users to play games within Discord.
- `ranking` - Commands used to check information about member EXP.
- `utilities` - Commands that provide useful functionality to discord chats.
- `web` - Commands that pull data from online third-party APIs. *Requires all third-party authentication information to be present in the config file.*

#### Events

- `connection` - Events directly relating to the bot's connection to Discord.
- `messages` - Events relating to actions revolving around messages.

#### Tasks

- `reminders` - The task that pushes reminders out to users.

### Examples

#### Example Command Plugin

```py
from discord.commands.context import ApplicationContext

from photon_bot import PhotonBot


def register_commands(bot: PhotonBot):
    @bot.discord_bot.command()
    async def hello(ctx: ApplicationContext):
        await ctx.respond(f"Hello {ctx.author.mention}!")
```

#### Example Event Plugin

```py
import discord

from photon_bot import PhotonBot


def register_events(bot: PhotonBot):
    @bot.discord_bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.discord_bot.user:
            print("Message was sent by me!")
```

#### Example Task Plugin

```py
import discord.ext.tasks

from photon_bot import PhotonBot


def register_tasks(bot: PhotonBot):
    @discord.ext.tasks.loop(seconds=60)
    async def send_advert():
        channel = bot.discord_bot.get_channel(1234567890)
        await channel.send("My very cool advertisement :)")

    @send_advert.before_loop
    async def wait_for_ready():
        # Do not start task until bot is logged in
        await bot.discord_bot.wait_until_ready()
```

## Third-Party APIs

- [Reddit](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps)
- [OMDb](https://www.omdbapi.com/apikey.aspx)
- [Wolfram|Alpha](https://developer.wolframalpha.com/portal/myapps/)
- [Oxford Dictionary](https://developer.oxforddictionaries.com/)
- [OpenWeatherMap](https://home.openweathermap.org/users/sign_up)
- [HERE](https://developer.here.com/projects)
- [Google Custom Search](https://programmablesearchengine.google.com/cse/all) *(must have image search enabled)*

## Utils

Some utility functions have been provided in order to make repeated actions easier. They can all be found within `utils.py` along with docstrings for each.

## Resources

### Fonts

- `DejaVuSans.ttf` - Used for putting text onto images in the ranking commands.

### Images

- `AvatarMask.png` - A mask used to make Discord avatars circular when pasting them on to images.
- `LeaderboardTemplate.png` - The base image for the guild EXP leaderboards.
- `RankCardMask.png` - Defines the shape of the colored part of the rank card.
- `RankCardTemplate.png` - The base image for user rank cards.

### Text
- `words_alpha.txt` - A list of almost every word in the English language, used by some commands.

---

**Copyright © 2022  Ptolemy Hill. More info in `COPYRIGHT` file.**
