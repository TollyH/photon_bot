"""Commands that get information about Discord objects."""
import os
import re

import discord
import pygount
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.enums import (
    ContentFilter,
    NotificationLevel,
    NSFWLevel,
    VerificationLevel,
)

from photon_bot import PhotonBot


def register_commands(bot: PhotonBot):
    @bot.discord_bot.command()
    async def getpfp(ctx: ApplicationContext,
            user: Option(discord.User, "User to get profile picture for")):
        """Get the profile picture of a user"""
        if isinstance(user, int):
            user = await bot.discord_bot.fetch_user(user)
        embed = discord.Embed(
            title=f"Profile Picture for {user}",
            color=ctx.author.color
        )
        embed.set_image(url=user.display_avatar.url)
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def defaultpfp(ctx: ApplicationContext,
            user: Option(discord.User, "User to get default picture for")):
        """Get the default profile picture of a user"""
        if isinstance(user, int):
            user = await bot.discord_bot.fetch_user(user)
        embed = discord.Embed(
            title=f"Default Profile Picture for {user}",
            color=ctx.author.color
        )
        embed.set_image(url=user.default_avatar.url)
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def getemoji(ctx: ApplicationContext,
            emoji: Option(str, "Custom emoji to display")):
        """Display a custom Discord emoji"""
        match = re.match(r"<(a?):(.*?):(\d+?)>", emoji)
        if not match:
            await ctx.respond(
                "You did not send a custom emoji", ephemeral=True
            )
            return
        extension = "gif" if match.group(1) else "webp"
        embed = discord.Embed(
            title=f"Emoji {match.group(2)}",
            color=ctx.author.color
        )
        embed.set_image(
            url="https://cdn.discordapp.com/emojis/"
            + f"{match.group(3)}.{extension}?size=1024&quality=lossless"
        )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def userinfo(ctx: ApplicationContext,
            user: Option(discord.User, "User to get information for")):
        """Get information about a Discord user"""
        is_in_guild = True
        if isinstance(user, int):
            user = await bot.discord_bot.fetch_user(user)
            is_in_guild = False
        embed = discord.Embed(
            title=f"User Info for {user}",
            color=ctx.author.color,
            description=f"**ID:** `{user.id}`"
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Account Created On",
            value=f"<t:{round(user.created_at.timestamp())}:F>",
            inline=True
        )
        embed.add_field(
            name="Account Created",
            value=f"<t:{round(user.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Bot User",
            value=str(user.bot),
            inline=False
        )
        if is_in_guild:
            embed.add_field(
                name="Member Joined On",
                value=f"<t:{round(user.joined_at.timestamp())}:F>",
                inline=True
            )
            embed.add_field(
                name="Joined",
                value=f"<t:{round(user.joined_at.timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="Administrator",
                value=str(user.guild_permissions.administrator),
                inline=False
            )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def mostroles(ctx: ApplicationContext):
        """Get a list of the top members in the server by number of roles"""
        role_board = "**Top Members by Number of Roles:**"
        for member in sorted(
                ctx.guild.members, key=lambda x: len(x.roles),
                reverse=True)[:25]:
            role_board += f"\n{member}: `{len(member.roles) - 1}`"
        await ctx.respond(role_board)

    @bot.discord_bot.command()
    async def oldestmembers(ctx: ApplicationContext):
        """
        Get a list of the top members in the server by length of membership
        """
        oldest_board = "**Top Members by Number of Roles:**"
        for member in sorted(
                ctx.guild.members, key=lambda x: x.joined_at)[:25]:
            oldest_board += (
                f"\n{member}: "
                + f"<t:{round(member.joined_at.timestamp())}:F> "
                + f"(<t:{round(member.joined_at.timestamp())}:R>)"
            )
        await ctx.respond(oldest_board)

    @bot.discord_bot.command()
    async def botinfo(ctx: ApplicationContext):
        """Get information about this bot"""
        embed = discord.Embed(
            title="Bot Info",
            description=f"Connected: **{bot.discord_bot.user}**\nBuilt on the "
            + "[Photon Bot Framework](https://github.com/TollyH/photon_bot)"
            + " written by Tolly Hill.",
            color=ctx.author.color
        )
        embed.set_thumbnail(url=bot.discord_bot.user.display_avatar.url)
        embed.add_field(
            name="Bot Reconnected On",
            value=f"<t:{round(bot.start_time.timestamp())}:F>",
            inline=True
        )
        embed.add_field(
            name="Bot Reconnected",
            value=f"<t:{round(bot.start_time.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Server Count",
            value=str(len(bot.discord_bot.guilds)),
            inline=True
        )
        command_count = 0
        for command in bot.discord_bot.commands:
            if isinstance(command, discord.commands.SlashCommandGroup):
                command_count += len(list(command.walk_commands()))
            else:
                command_count += 1
        embed.add_field(
            name="Command Count",
            value=str(command_count),
            inline=True
        )
        embed.add_field(
            name="Plugin Count",
            value="**Commands:** "
            + str(len(bot.config['Plugins']['Commands'].split(','))) + "\n"
            + "**Events:** "
            + str(len(bot.config['Plugins']['Events'].split(','))) + "\n"
            + f"**Tasks:** {len(bot.config['Plugins']['Tasks'].split(','))}\n",
            inline=True
        )
        sloc = 0
        for root, _, files in os.walk(bot.directory_location):
            for file_name in files:
                if file_name.endswith(".py"):
                    sloc += pygount.SourceAnalysis.from_file(
                        os.path.join(root, file_name), "photon_bot"
                    ).code_count
        embed.add_field(
            name="Source Lines of Code",
            value=str(sloc),
            inline=True
        )
        embed.add_field(
            name="Photon Bot Framework Version",
            value=bot.__version__,
            inline=True
        )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def serverinfo(ctx: ApplicationContext):
        """Get information about this server"""
        embed = discord.Embed(
            title=f"Server Info for {ctx.guild}",
            description=f"**ID:** `{ctx.guild.id}`",
            color=ctx.author.color
        )
        if ctx.guild.icon is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(
            name="Server Created On",
            value=f"<t:{round(ctx.guild.created_at.timestamp())}:F>",
            inline=True
        )
        embed.add_field(
            name="Server Created",
            value=f"<t:{round(ctx.guild.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(name="Owner", value=str(ctx.guild.owner), inline=True)
        embed.add_field(
            name="Emoji Count",
            value=str(len(ctx.guild.emojis)),
            inline=True
        )
        embed.add_field(
            name="Sticker Count",
            value=str(len(ctx.guild.stickers)),
            inline=True
        )
        embed.add_field(
            name="Moderators Require 2FA",
            value=str(bool(ctx.guild.mfa_level)),
            inline=True
        )
        if ctx.guild.verification_level == VerificationLevel.low:
            verification_str = "Email"
        elif ctx.guild.verification_level == VerificationLevel.medium:
            verification_str = "Email and 5 Minutes Old"
        elif ctx.guild.verification_level == VerificationLevel.high:
            verification_str = "Email, 5 Minutes Old and Member For 10 Minutes"
        elif ctx.guild.verification_level == VerificationLevel.highest:
            verification_str = "Phone Number"
        else:
            verification_str = "None"
        embed.add_field(
            name="Verification Requirements", value=verification_str,
            inline=True
        )
        if ctx.guild.explicit_content_filter == ContentFilter.no_role:
            filter_str = "Members Without a Role"
        elif ctx.guild.explicit_content_filter == ContentFilter.all_members:
            filter_str = "Everybody"
        else:
            filter_str = "Disabled"
        embed.add_field(
            name="Content Filter", value=filter_str,
            inline=True
        )
        if ctx.guild.default_notifications == NotificationLevel.all_messages:
            notification_str = "Every Message"
        else:
            notification_str = "Only @mentions"
        embed.add_field(
            name="Default Notifications", value=notification_str,
            inline=True
        )
        embed.add_field(
            name="Boost Status",
            value=f"{ctx.guild.premium_subscription_count} boosts "
            + f"(Tier {ctx.guild.premium_tier})",
            inline=True
        )
        if ctx.guild.verification_level == NSFWLevel.explicit:
            nsfw_str = "NSFW Centered (iOS Users Cannot Access)"
        elif ctx.guild.verification_level == NSFWLevel.safe:
            nsfw_str = "No NSFW Focus"
        elif ctx.guild.verification_level == NSFWLevel.age_restricted:
            nsfw_str = "Some NSFW Focus (iOS Users Cannot Access By Default)"
        else:
            nsfw_str = "Not Applicable"
        embed.add_field(
            name="NSFW Content Level", value=nsfw_str,
            inline=True
        )
        embed.add_field(
            name="Channel Count", value=str(len(ctx.guild.channels)),
            inline=True
        )
        embed.add_field(
            name="Member Count", value=str(ctx.guild.member_count), inline=True
        )
        embed.add_field(
            name="Role Count", value=str(len(ctx.guild.roles)), inline=True
        )
        embed.add_field(
            name="Special Features",
            value=", ".join(
                x.title().replace("_", " ") for x in ctx.guild.features
            ) or "None",
            inline=False
        )
        await ctx.respond(embed=embed)
