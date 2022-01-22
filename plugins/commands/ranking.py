"""Commands used to check information about member EXP."""
import random
from io import BytesIO

import discord
import requests
from discord.commands import Option
from discord.commands.context import ApplicationContext
from PIL import Image, ImageDraw, ImageFont

from photon_bot import PhotonBot
import utils


def register_commands(bot: PhotonBot):
    rank_calculator_group = bot.discord_bot.create_group("rankcalculator")

    @rank_calculator_group.command()
    async def level(ctx: ApplicationContext,
            exp: Option(int, "The input EXP amount")):
        """Calculate the level you would be at with a given amount of EXP"""
        if exp > 999999999:
            await ctx.respond(
                "The given EXP value is too high", ephemeral=True
            )
            return
        level, remainder = utils.calculate_level(exp)
        await ctx.respond(
            f"With {exp} EXP you would be at level "
            + f"`{level}` with `{remainder}` EXP towards the next level"
        )

    @rank_calculator_group.command()
    async def exp(ctx: ApplicationContext,
            level: Option(int, "The input level value")):
        """Calculate the minimum amount of EXP needed for a particular level"""
        if level > 1000:
            await ctx.respond(
                "The given level value is too high", ephemeral=True
            )
            return
        await ctx.respond(
            f"To be at level {level} you would need at least "
            + f"`{utils.total_exp_for_level(level)}` EXP"
        )

    @bot.discord_bot.command()
    async def rank(ctx: ApplicationContext, member: Option(
            discord.User, "Optional user to get rank for",
            required=False)):
        """Check your current level, rank, and distance from the next level"""
        if isinstance(member, int):
            member = await bot.discord_bot.fetch_user(member)
        user = member or ctx.author
        exp_info = utils.get_exp_info(
            bot.config['DatabaseConnection'], ctx.guild.id, user.id
        )
        user_avatar = Image.open(BytesIO(
            requests.get(user.display_avatar.url).content))
        customised = True
        if None in exp_info.color:
            customised = False
            color = user_avatar.convert(mode="RGB").resize(
                (1, 1)).getpixel((0, 0))
        else:
            color = exp_info.color
        rank_card = Image.new("RGBA", (512, 630), color)
        rank_card.paste(
            Image.open("resources/images/RankCardTemplate.png"),
            mask=Image.open(
                "resources/images/RankCardMask.png").convert(mode="1")
        )
        resized_avatar = user_avatar.resize((192, 192), Image.LANCZOS)
        avatar_mask = Image.open(
                "resources/images/AvatarMask.png")
        avatar_mask.paste(resized_avatar, mask=avatar_mask)
        rank_card.paste(
            resized_avatar,
            box=(24, 45, 216, 237),
            mask=avatar_mask
        )
        card_draw = ImageDraw.Draw(rank_card)
        rank_font = "resources/fonts/DejaVuSans.ttf"
        card_draw.text(
            (250, 143), str(exp_info.level), fill=color,
            font=ImageFont.truetype(rank_font, 72)
        )
        card_draw.text(
            (24, 270), user.name, fill=color,
            font=ImageFont.truetype(rank_font, 60)
        )
        card_draw.text(
            (24, 353), str(exp_info.exp), fill=color,
            font=ImageFont.truetype(rank_font, 48)
        )
        card_draw.text(
            (24, 429), str(exp_info.rank), fill=color,
            font=ImageFont.truetype(rank_font, 48)
        )
        card_draw.text(
            (24, 566), str(exp_info.remaining), fill=color,
            font=ImageFont.truetype(rank_font, 30)
        )
        card_draw.text(
            (372, 566), str(exp_info.next_level), fill=color,
            font=ImageFont.truetype(rank_font, 30)
        )
        card_draw.rectangle(
            (
                (23, 509),
                (23 + round(463 * (exp_info.remaining / exp_info.next_level)),
                 549)
            ),
            fill=color
        )

        rank_card.save(f"/tmp/rank-card-{user.id}.png", "PNG")
        content = None
        if not customised and user == ctx.author:
            content = random.choice([
                "**Tip:** If the text is hard to read, you can change the "
                + "color with /changerank",
                "**Tip:** If you don't like the color of your rank card, "
                + f"you can change it with /changerank"
            ])
        await ctx.respond(
            content,
            file=discord.File(f"/tmp/rank-card-{user.id}.png")
        )

    @bot.discord_bot.command()
    async def textrank(ctx: ApplicationContext, member: Option(
            discord.User, "Optional user to get rank for",
            required=False)):
        """A version of /rank that uses text instead of an image"""
        if isinstance(member, int):
            member = await bot.discord_bot.fetch_user(member)
        user = member or ctx.author
        exp_info = utils.get_exp_info(
            bot.config['DatabaseConnection'], ctx.guild.id, user.id
        )
        progress_bar = "█" * round(
            20 * (exp_info.remaining / exp_info.next_level)
        )
        progress_bar += " " * (20 - len(progress_bar))
        await ctx.respond(
            f"**{user}**: `{exp_info.exp}` **EXP** | `{exp_info.level}` **LV**"
            + f" | `{exp_info.rank}` **RANK**\n`[{progress_bar}]`"
            + f"**{exp_info.remaining} / {exp_info.next_level}**"
        )

    @bot.discord_bot.command()
    async def leaderboard(ctx: ApplicationContext):
        """View the members with the most EXP across the whole server"""
        # Command takes a long time (>3 seconds) so must be deferred
        await ctx.defer()
        with utils.Database(bot.config['DatabaseConnection']) as database:
            guild_response = database.fetch(
                "SELECT user_id, exp FROM user_exp WHERE guild_id = %s "
                + "ORDER BY exp DESC LIMIT 15;",
                (ctx.guild.id,)
            )
        board = Image.open("resources/images/LeaderboardTemplate.png")
        top_lineup = guild_response[:5]
        bottom_lineup = guild_response[5:]
        if len(top_lineup) == 0:
            await ctx.respond("Nobody has any EXP in this server!")
            return
        if len(bottom_lineup) == 0:
            board = board.crop((0, 0, 960, 540))
        if len(top_lineup) < 5:
            board = board.crop(
                (0, 0, 960, 540 - (108 * (5 - len(top_lineup))))
            )
        avatar_mask_base = Image.open(
                "resources/images/AvatarMask.png").resize(
                    (95, 95), Image.LANCZOS)
        board_draw = ImageDraw.Draw(board)
        board_font = "resources/fonts/DejaVuSans.ttf"
        for index, (user_id, exp) in enumerate(top_lineup):
            user = await bot.discord_bot.fetch_user(user_id)
            level = utils.calculate_level(exp)[0]
            user_avatar = Image.open(BytesIO(
                requests.get(user.display_avatar.url).content)).resize(
                    (95, 95), Image.LANCZOS)
            avatar_mask = avatar_mask_base.copy()
            avatar_mask.paste(user_avatar, mask=avatar_mask)
            board.paste(
                user_avatar,
                box=(17, 7 + (index * 108), 112, 102 + (index * 108)),
                mask=avatar_mask
            )
            board_draw.text(
                (140, 33 + (index * 108)), str(user), fill=(0, 0, 0),
                font=ImageFont.truetype(board_font, 35)
            )
            board_draw.text(
                (900, 2 + (index * 108)), str(exp), fill=(0, 0, 0),
                font=ImageFont.truetype(board_font, 40)
            )
            board_draw.text(
                (900, 55 + (index * 108)), str(level), fill=(0, 0, 0),
                font=ImageFont.truetype(board_font, 40)
            )
        for index, (user_id, _) in enumerate(bottom_lineup):
            user = await bot.discord_bot.fetch_user(user_id)
            user_avatar = Image.open(BytesIO(
                requests.get(user.display_avatar.url).content)).resize(
                    (95, 95), Image.LANCZOS)
            avatar_mask = avatar_mask_base.copy()
            avatar_mask.paste(user_avatar, mask=avatar_mask)
            board.paste(
                user_avatar,
                box=(90 + (index * 108), 546, 185 + (index * 108), 641),
                mask=avatar_mask
            )

        board.save(f"/tmp/leaderboard-{ctx.guild.id}.png", "PNG")
        await ctx.respond(
            file=discord.File(f"/tmp/leaderboard-{ctx.guild.id}.png")
        )

    @bot.discord_bot.command()
    async def changerank(ctx: ApplicationContext,
            red: Option(int, "Must be between 0 and 255"),
            green: Option(int, "Must be between 0 and 255"),
            blue: Option(int, "Must be between 0 and 255")):
        """
        Set the color of your rank card. It should be given as RGB values.
        """
        if max(red, green, blue) > 255 or min(red, green, blue) < 0:
            await ctx.respond(
                "One or more of the color values you provided was invalid",
                ephemeral=True
            )
            return
        with utils.Database(bot.config['DatabaseConnection']) as database:
            if not database.modify(
                    "UPDATE user_exp_card SET red = %s, green = %s, "
                    + "blue = %s WHERE user_id = %s;",
                    (red, green, blue, ctx.author.id)):
                database.modify(
                    "INSERT INTO user_exp_card (user_id, red, green, blue) "
                    + "VALUES (%s, %s, %s, %s);",
                    (ctx.author.id, red, green, blue)
                )
        await ctx.respond("Rank card updated", ephemeral=True)

    @bot.discord_bot.command()
    async def resetrank(ctx: ApplicationContext):
        """
        Reset the color of your rank card to be based on your profile picture.
        """
        with utils.Database(bot.config['DatabaseConnection']) as database:
            database.modify(
                "DELETE FROM user_exp_card WHERE user_id = %s;",
                (ctx.author.id,)
            )
        await ctx.respond("Rank card reset", ephemeral=True)
