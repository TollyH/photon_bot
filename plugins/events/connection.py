"""Events directly relating to the bot's connection to Discord."""
import datetime

import discord
from discord.enums import ActivityType

from photon_bot import PhotonBot


def register_events(bot: PhotonBot):
    @bot.discord_bot.event
    async def on_ready():
        bot.start_time = datetime.datetime.now()
        activity_types = [
            ActivityType.playing, ActivityType.listening,
            ActivityType.watching, ActivityType.competing
        ]
        await bot.discord_bot.change_presence(activity=discord.Activity(
            name=bot.config['Personalisation']['StatusText'],
            type=activity_types[
                int(bot.config['Personalisation']['StatusType'])
            ]
        ))
        command_count = 0
        for command in bot.discord_bot.commands:
            if isinstance(command, discord.commands.SlashCommandGroup):
                command_count += len(list(command.walk_commands()))
            else:
                command_count += 1
        print(
            f"Connected to {bot.discord_bot.user} on "
            + f"{len(bot.discord_bot.guilds)} guilds. "
            + f"{command_count} global commands registered."
        )
