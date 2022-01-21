"""Events relating to actions revolving around messages."""
import datetime
import random

import discord

import utils
from photon_bot import PhotonBot


def register_events(bot: PhotonBot):
    bot.variables["exp_grant_cooldowns"] = {}

    @bot.discord_bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.discord_bot.user or message.author.bot:
            return
        guild_config = utils.get_guild_config(
            bot.config['DatabaseConnection'], message.guild.id
        )
        if message.guild.id not in bot.variables["exp_grant_cooldowns"]:
            bot.variables["exp_grant_cooldowns"][message.guild.id] = {}
        cooldowns = bot.variables["exp_grant_cooldowns"][message.guild.id]
        if ((guild_config.exp_active or guild_config.exp_active is None)
                and (
                    message.author.id not in cooldowns
                    or cooldowns[message.author.id] < datetime.datetime.now()
                )):
            cooldowns[message.author.id] = (
                datetime.datetime.now() + datetime.timedelta(seconds=60)
            )
            old_exp_info = utils.get_exp_info(
                bot.config['DatabaseConnection'], message.guild.id,
                message.author.id
            )
            new_exp = old_exp_info.exp + random.randint(15, 25)
            with utils.Database(bot.config['DatabaseConnection']) as database:
                if not database.modify(
                        "UPDATE user_exp SET exp = %s "
                        + "WHERE guild_id = %s AND user_id = %s;",
                        (new_exp, message.guild.id, message.author.id)):
                    database.modify(
                        "INSERT INTO user_exp (guild_id, user_id, exp) "
                        + "VALUES (%s, %s, %s);",
                        (message.guild.id, message.author.id, new_exp)
                    )
            new_level = utils.calculate_level(new_exp)[0]
            if (new_level > old_exp_info.level
                    and guild_config.exp_levelup_channel != 0):
                if guild_config.exp_levelup_channel is None:
                    channel = message.channel
                else:
                    channel = bot.discord_bot.get_channel(
                        guild_config.exp_levelup_channel
                    )
                if channel is not None:
                    await channel.send(
                        message.author.mention
                        + f" Your level has raised to **{new_level}**!"
                    )
