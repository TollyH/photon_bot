"""Commands that provide useful functionality to discord chats."""
import datetime
import random
import time

import discord
import qrcode
from discord.commands import Option
from discord.commands.context import ApplicationContext

import utils
from photon_bot import PhotonBot

SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]
VALUES = [
    "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Jack", "Queen", "King"
]


def register_commands(bot: PhotonBot):
    reminder_group = bot.discord_bot.create_group("reminder")

    @reminder_group.command()
    async def add(ctx: ApplicationContext,
            content: Option(str, "What should be sent in the reminder"),
            days: Option(int, "Number of days from now"),
            hours: Option(int, "Number of hours from now"),
            minutes: Option(int, "Number of minutes from now"),
            seconds: Option(int, "Number of seconds from now")):
        """
        Create a reminder that will be sent via DM after the specified duration
        """
        due_datetime = datetime.datetime.now() + datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
        with utils.Database(bot.config['DatabaseConnection']) as database:
            database.modify(
                "INSERT INTO reminders (due_datetime, user_id, content) "
                + "VALUES (%s, %s, %s);",
                (due_datetime, ctx.author.id, content)
            )
        await ctx.respond(
            "Reminder added successfully. Note that reminders are only "
            + "pushed once per minute, so reminders could be delayed by up "
            + "to a minute",
            ephemeral=True
        )

    @reminder_group.command()
    async def current(ctx: ApplicationContext):
        """List all of your currently set reminders"""
        with utils.Database(bot.config['DatabaseConnection']) as database:
            reminder_list = database.fetch(
                "SELECT due_datetime, content FROM reminders "
                + "WHERE user_id = %s ORDER BY due_datetime ASC;",
                (ctx.author.id,)
            )
        if len(reminder_list) == 0:
            await ctx.respond(
                "You currently have no reminders", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="Currently Set Reminders",
            description="Note that reminders are only pushed once per "
            + "minute, so times could be up to a minute out",
            color=ctx.author.color
        )
        for index, reminder in enumerate(reminder_list):
            embed.add_field(
                name=f"**{index + 1}.** "
                + f"<t:{round(reminder[0].timestamp())}:F> "
                + f"(<t:{round(reminder[0].timestamp())}:R>)",
                value=reminder[1], inline=True
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @reminder_group.command()
    async def delete(ctx: ApplicationContext,
            number: Option(
                int,
                "The number of the reminder, as shown in /reminder current")):
        """
        Delete a reminder. You will need its number found in /reminder current
        """
        if number < 1:
            await ctx.respond(
                "Reminder numbers must be 1 or greater", ephemeral=True
            )
            return
        with utils.Database(bot.config['DatabaseConnection']) as database:
            reminder_list = database.fetch(
                "SELECT due_datetime, content FROM reminders "
                + "WHERE user_id = %s ORDER BY due_datetime ASC;",
                (ctx.author.id,)
            )
            if len(reminder_list) == 0:
                await ctx.respond(
                    "You currently have no reminders", ephemeral=True
                )
                return
            if number > len(reminder_list):
                await ctx.respond(
                    "You do not have that many reminders", ephemeral=True
                )
                return
            reminder = reminder_list[number - 1]
            if database.modify(
                    "DELETE FROM reminders WHERE due_datetime = %s "
                    + "AND user_id = %s AND content = %s LIMIT 1;",
                    (reminder[0], ctx.author.id, reminder[1])):
                await ctx.respond(
                    "Reminder deleted successfully", ephemeral=True
                )
            else:
                await ctx.respond(
                    "Something went wrong deleting the reminder",
                    ephemeral=True
                )

    random_group = bot.discord_bot.create_group("random")

    @random_group.command()
    async def number(ctx: ApplicationContext,
            lowest: Option(int, "Lowest number possible"),
            highest: Option(int, "Highest number possible")):
        """Generate a random number between two other specified numbers"""
        if lowest > highest:
            await ctx.respond(
                "Your lower number is greater than your higher one",
                ephemeral=True
            )
            return
        await ctx.respond(
            f"**Your random number is:** `{random.randint(lowest, highest)}`"
        )

    @random_group.command()
    async def word(ctx: ApplicationContext):
        """Get a random word in the English language"""
        await ctx.respond(
            f"Your random word is: `{random.choice(utils.get_all_words())}`"
        )

    @random_group.command()
    async def card(ctx: ApplicationContext,
            jokers: Option(
                str, "Whether to include jokers in the draw",
                choices=["yes", "no"]
            )):
        """Get a random playing card, optionally including jokers"""
        if random.random() < 2 / 54:
            await ctx.respond("Your random card is: `Joker`")
        else:
            await ctx.respond(
                "Your random card is: "
                + f"`{random.choice(VALUES)} of {random.choice(SUITS)}`"
            )

    @bot.discord_bot.command()
    async def qr(ctx: ApplicationContext,
            text: Option(str, "The text to encode")):
        """Generate a QR Code from a piece of text"""
        qrcode.make(text).save(f"/tmp/qrcode-{ctx.author.id}.png", "PNG")
        await ctx.respond(
            file=discord.File(f"/tmp/qrcode-{ctx.author.id}.png")
        )

    @bot.discord_bot.command()
    async def timestamp(ctx: ApplicationContext,
            stamp: Option(
                int, "Timestamp to convert to date and time", required=False
            )):
        """Get the current UNIX timestamp or convert one to a date and time"""
        if stamp is not None:
            await ctx.respond(f"<t:{stamp}:F> (<t:{stamp}:R>)")
        else:
            await ctx.respond(
                f"The current UNIX timestamp is: `{round(time.time())}`"
            )
