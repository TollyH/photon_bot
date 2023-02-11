"""Commands that can only be run by Administrators."""
import discord
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mariadb import IntegrityError

import utils
from photon_bot import PhotonBot


def register_commands(bot: PhotonBot):
    level_up_channel_group = bot.discord_bot.create_group("levelupchannel")

    @level_up_channel_group.command()
    async def reset(ctx: ApplicationContext):
        """
        (ADMIN ONLY) Reset level up alerts to be sent in the message's channel
        """
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        with utils.Database(bot.config['DatabaseConnection']) as database:
            database.modify(
                "UPDATE guild_config SET exp_levelup_channel=NULL "
                + "WHERE guild_id = %s;", (ctx.guild.id,)
            )
        await ctx.respond(
            "Level up alerts have been reset", ephemeral=True
        )

    @level_up_channel_group.command()
    async def sethere(ctx: ApplicationContext):
        """
        (ADMIN ONLY) Set level up alerts to be sent in the current channel
        """
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        with utils.Database(bot.config['DatabaseConnection']) as database:
            if not database.modify(
                    "UPDATE guild_config SET exp_levelup_channel = %s "
                    + "WHERE guild_id = %s;", (ctx.channel.id, ctx.guild.id)):
                try:
                    database.modify(
                        "INSERT INTO guild_config "
                        + "(guild_id, exp_levelup_channel) VALUES (%s, %s);",
                        (ctx.guild.id, ctx.channel.id)
                    )
                except IntegrityError:
                    await ctx.respond(
                        "Level up alerts are already sent here", ephemeral=True
                    )
                    return
        await ctx.respond(
            "Level up alerts will now be sent here", ephemeral=True
        )

    @level_up_channel_group.command()
    async def disable(ctx: ApplicationContext):
        """(ADMIN ONLY) Completely disable level up alerts"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        with utils.Database(bot.config['DatabaseConnection']) as database:
            if not database.modify(
                    "UPDATE guild_config SET exp_levelup_channel=0 "
                    + "WHERE guild_id = %s;", (ctx.guild.id,)):
                try:
                    database.modify(
                        "INSERT INTO guild_config "
                        + "(guild_id, exp_levelup_channel) VALUES (%s, 0);",
                        (ctx.guild.id,)
                    )
                except IntegrityError:
                    await ctx.respond(
                        "Level up alerts are already disabled", ephemeral=True
                    )
                    return
        await ctx.respond(
            "Level up alerts are now disabled", ephemeral=True
        )

    @bot.discord_bot.command()
    async def toggleexp(ctx: ApplicationContext):
        """
        (ADMIN ONLY) Toggle whether users should gain EXP for sending messages
        """
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        guild_config = utils.get_guild_config(
            bot.config['DatabaseConnection'], ctx.guild.id
        )
        current_exp_state = (
            guild_config.exp_active or guild_config.exp_active is None
        )
        with utils.Database(bot.config['DatabaseConnection']) as database:
            if not database.modify(
                    "UPDATE guild_config SET exp_active = %s "
                    + "WHERE guild_id = %s;",
                    (int(not current_exp_state), ctx.guild.id)):
                database.modify(
                    "INSERT INTO guild_config "
                    + "(guild_id, exp_active) VALUES (%s, %s);",
                    (ctx.guild.id, int(not current_exp_state))
                )
        await ctx.respond(
            f"EXP has been {'disabled' if current_exp_state else 'enabled'}",
            ephemeral=True
        )

    @bot.discord_bot.command()
    async def expedit(ctx: ApplicationContext,
            user: Option(discord.User, "The user to edit EXP for"),
            exp: Option(int, "The new value for the user's EXP")):
        """(ADMIN ONLY) Edit the amount of EXP a user has"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        if exp > 999999999:
            await ctx.respond(
                "That amount of EXP is too high",
                ephemeral=True
            )
            return
        if isinstance(user, int):
            user_id = user
        else:
            user_id = user.id
        with utils.Database(bot.config['DatabaseConnection']) as database:
            if not database.modify(
                    "UPDATE user_exp SET exp = %s "
                    + "WHERE guild_id = %s AND user_id = %s;",
                    (exp, ctx.guild.id, user_id)):
                database.modify(
                    "INSERT INTO user_exp (guild_id, user_id, exp) "
                    + "VALUES (%s, %s, %s);",
                    (ctx.guild.id, user_id, exp)
                )
        await ctx.respond("EXP successfully updated", ephemeral=True)

    @bot.discord_bot.command()
    async def purge(ctx: ApplicationContext,
            limit: Option(int, "Maximum number of messages to delete")):
        """(ADMIN ONLY) Bulk delete messages from this channel"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You must be an administrator to run this command",
                ephemeral=True
            )
            return
        # Purging can take a long time (>3 seconds) so must be deferred
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=limit)
        await ctx.respond(
            f"I have deleted `{len(deleted)}` messages", ephemeral=True
        )
