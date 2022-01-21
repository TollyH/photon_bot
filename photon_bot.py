"""
An easily expandable Discord Bot written in Python 3 using the pycord library.
"""
import configparser
import importlib
import os

import discord
from discord.flags import Intents


class plugin_types:
    """
    An enum representing the different types of plugin that the bot can load
    """
    COMMAND = 0
    EVENT = 1
    TASK = 2


class PhotonBot:
    """
    Represents a Discord bot being handled by the Photon Bot Framework.
    The `discord.Bot` instance itself can be found under `discord_bot`,
    the loaded config file under `config` and the bot's starting datetime under
    `start_time`. The bot will automatically load plugins specified in config
    file when an instance is created.
    """
    __version__ = "1.0.0"

    def __init__(self, config_path: str):
        """
        Create an instance of discord.Bot with all Intents and load plugins
        specified in the config file. Does not open a connection to Discord.
        """
        self.discord_bot = discord.Bot(intents=Intents.all())
        self.config = configparser.ConfigParser(
            interpolation=configparser.BasicInterpolation()
        )
        self.config.read(config_path)
        self.directory_location = os.path.dirname(__file__)
        self.variables = {}
        self.start_time = None
        # Load plugins specified in config file
        for cmd_plugin in self.config['Plugins']['Commands'].split(","):
            self.load_plugin(cmd_plugin.strip(), plugin_types.COMMAND)
        for event_plugin in self.config['Plugins']['Events'].split(","):
            self.load_plugin(event_plugin.strip(), plugin_types.EVENT)
        for task_plugin in self.config['Plugins']['Tasks'].split(","):
            self.load_plugin(task_plugin.strip(), plugin_types.TASK)

    def load_plugin(self, name: str, plugin_type: int):
        """
        Manually load a plugin. The plugin name should not include the
        directory as that will automatically be inferred based on the plugin
        type.
        """
        old_cwd = os.getcwd()
        os.chdir(self.directory_location)
        try:
            if plugin_type == 0:
                importlib.import_module(
                    f"plugins.commands.{name}"
                ).register_commands(self)
            elif plugin_type == 1:
                importlib.import_module(
                    f"plugins.events.{name}"
                ).register_events(self)
            elif plugin_type == 2:
                importlib.import_module(
                    f"plugins.tasks.{name}"
                ).register_tasks(self)
            else:
                raise ValueError(f"Invalid plugin type '{plugin_type}'")
        finally:
            os.chdir(old_cwd)

    def start(self, *args, **kwargs):
        """
        Login and open a connection to Discord
        """
        self.discord_bot.run(
            *args, **kwargs, token=self.config['DiscordAuth']['Token']
        )
