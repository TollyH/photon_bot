"""Simple commands designed for entertainment."""
import random
import string

import asyncio
import discord
import nekos
import requests
from discord.commands import Option
from discord.commands.context import ApplicationContext

from photon_bot import PhotonBot


def register_commands(bot: PhotonBot):
    num_fact_group = bot.discord_bot.create_group("numfact")

    @num_fact_group.command()
    async def trivia(ctx: ApplicationContext,
            number: Option(int, "Number to get trivia for")):
        """Get a general trivia fact about a particular number"""
        fact = requests.get(f"http://numbersapi.com/{number}").text
        await ctx.respond(
            f"**A random fact about {number} is:** `{fact}`"
        )

    @num_fact_group.command()
    async def math(ctx: ApplicationContext,
            number: Option(int, "Number to get a math fact for")):
        """Get a mathematical fact about a particular number"""
        fact = requests.get(f"http://numbersapi.com/{number}/math").text
        await ctx.respond(
            f"**A mathematical fact about {number} is:** `{fact}`"
        )

    @num_fact_group.command()
    async def date(ctx: ApplicationContext,
            date: Option(int, "Date to get a fact for"),
            month: Option(int, "Month to get a fact for")):
        """Get a fact about a particular date"""
        fact = requests.get(f"http://numbersapi.com/{month}/{date}/date").text
        await ctx.respond(
            f"**A mathematical fact about {date}/{month} is:** `{fact}`"
        )

    @bot.discord_bot.command()
    async def pp(ctx: ApplicationContext,
            member: Option(
                discord.User, "Optional user to get size for",
                required=False)):
        """
        A totally accurate, not at all rigged measurement of your penis size
        """
        if isinstance(member, int):
            member = await bot.discord_bot.fetch_user(member)
        user = member or ctx.author
        await ctx.respond(
            f"**Size of {user}'s PP:**\n"
            + f"`8{'=' * random.randint(0, 12)}D`"
        )

    @bot.discord_bot.command()
    async def homometer(ctx: ApplicationContext,
            member: Option(
                discord.User, "Optional user to get percentage for",
                required=False)):
        """Struggling to figure out how gay you are? Worry no more!"""
        if isinstance(member, int):
            member = await bot.discord_bot.fetch_user(member)
        user = member or ctx.author
        await ctx.respond(f"{user} is {random.randint(0, 100)}% gay")

    @bot.discord_bot.command()
    async def emojify(ctx: ApplicationContext,
            text: Option(str, "Enter text to convert")):
        """Convert every letter in a message into large block characters"""
        formatted = ""
        for char in text.lower():
            if char in string.ascii_lowercase:
                formatted += f":regional_indicator_{char}:"
            elif char == " ":
                formatted += "   "
        await ctx.respond(formatted)

    @bot.discord_bot.command()
    async def catpic(ctx: ApplicationContext):
        """Gets a random picture of a cat. How cute!"""
        embed = discord.Embed(
            title="Here's a Cat Picture",
            color=ctx.author.color
        )
        embed.set_image(url=nekos.cat())
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def toiletpaper(ctx: ApplicationContext,
            rolls: Option(int, "How many rolls of toilet paper do you have?"),
            sheets: Option(int, "How many sheets are on each roll?"),
            visits: Option(int, "How many times does each person go?"),
            wipes: Option(int, "How many times does each person wipe?"),
            people: Option(int, "How many people are in the household?")):
        """See how long your remaining toilet paper supply will last"""
        remaining_days = (rolls * sheets) // (visits * wipes * people)
        await ctx.respond(
            "**Your stock of Toilet Paper will last:** "
            + f"`{remaining_days}` day{'s' if remaining_days != 1 else ''}"
        )

    @bot.discord_bot.command()
    async def randomcaps(ctx: ApplicationContext,
            text: Option(str, "Enter text to process")):
        """Randomise the capitalisation of each letter in a message"""
        await ctx.respond(
            ''.join(map(
                lambda x: x.lower() if random.randint(0, 1) else x.upper(),
                text
            ))
        )

    @bot.discord_bot.command()
    async def thicc(ctx: ApplicationContext,
            text: Option(str, "Enter text to process")):
        """Make a message T  H  I  C  C"""
        await ctx.respond(
            f"**{''.join(map(lambda x: x.upper() + '   ', text))}**"
        )

    @bot.discord_bot.command()
    async def owoify(ctx: ApplicationContext,
            text: Option(str, "Enter text to process")):
        """Release your inner anime girl (=｀ω´=)"""
        await ctx.respond(nekos.owoify(text) + "  " + nekos.textcat())

    @bot.discord_bot.command()
    async def eightball(ctx: ApplicationContext):
        """Think of a question then ask this eight ball for reliable™ advice"""
        eightball_response = nekos.eightball()._dict
        embed = discord.Embed(
            title=eightball_response['text'],
            color=ctx.author.color
        )
        embed.set_image(url=eightball_response['image'])
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def fact(ctx: ApplicationContext):
        """Get a random piece of trivia"""
        await ctx.respond(f"**Your Random Fact:** `{nekos.fact()}`")

    @bot.discord_bot.command()
    async def hack(ctx: ApplicationContext,
            target: Option(str, "The target of the hack")):
        """Take down someone's system. 100% real and working confirmed!"""
        response = await ctx.respond(f"Starting hack on {target}")
        await asyncio.sleep(1)
        for i in range(11):
            await response.edit_original_message(
                content=f"[{i * 10}%] Activating RAT on {target}"
            )
            await asyncio.sleep(0.5)
        await response.edit_original_message(
            content=f"RAT Active and Broadcasting on {target}"
        )
        await asyncio.sleep(1)
        await response.edit_original_message(
            content="IP Address Located. "
            + f"{random.randint(1, 255)}.{random.randint(1, 255)}."
            + f"{random.randint(1, 255)}.{random.randint(1, 255)}"
        )
        await asyncio.sleep(2)
        system_hack_text = (
            f"Planting Trojan in svhost.exe on {target.upper()}-PC/SYSTEM"
        )
        for i in range(3):
            await response.edit_original_message(
                content="[|] " + system_hack_text
            )
            await asyncio.sleep(1)
            await response.edit_original_message(
                content="[/] " + system_hack_text
            )
            await asyncio.sleep(1)
            await response.edit_original_message(
                content="[-] " + system_hack_text
            )
            await asyncio.sleep(1)
            await response.edit_original_message(
                content="[\\\\] " + system_hack_text
            )
            await asyncio.sleep(1)
        await response.edit_original_message(
            content=f"{target} has been hacked and had their system destroyed."
        )

    @bot.discord_bot.command()
    async def cowsay(ctx: ApplicationContext,
            message: Option(str, "What should the cow say?")):
        """Put your message in the speech bubble of a cow"""
        if len(message) > 40:
            await ctx.respond(
                "Your message is too long! "
                + "Please keep messages under 40 characters"
            )
            return
        cow = r"""
   \   ^__^
    \  (oo)\_______
       (__)\       )\/\
           ||----w |
           ||     ||"""
        await ctx.respond(
            f"``` _{'_' * len(message)}_\n"
            + f"< {message} >\n"
            + f" ¯{'¯' * len(message)}¯" +
            cow + "```"
        )
