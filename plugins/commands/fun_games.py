"""More complex commands that allow users to play games within Discord."""
import random
import string

import asyncio
import discord
from akinator.async_aki import Akinator
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.enums import ButtonStyle

from photon_bot import PhotonBot
import utils

letter_games = {}


def register_commands(bot: PhotonBot):
    letter_game_group = bot.discord_bot.create_group("lettergame")

    @letter_game_group.command()
    async def start(ctx: ApplicationContext):
        """
        Do you know a lot of long words? This is the game to show off with!
        """
        consonants = [
            'b', 'b', 'c', 'c', 'c', 'd', 'd', 'd', 'd', 'd', 'd', 'f', 'f',
            'g', 'g', 'g', 'h', 'h', 'j', 'k', 'l', 'l', 'l', 'l', 'l', 'm',
            'm', 'm', 'm', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'p', 'p',
            'p', 'p', 'q', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r', 's',
            's', 's', 's', 's', 's', 's', 's', 's', 't', 't', 't', 't', 't',
            't', 't', 't', 't', 'v', 'w', 'x', 'y', 'z'
        ]
        vowels = [
            'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a',
            'a', 'a', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e',
            'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'i', 'i', 'i',
            'i', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'o', 'o', 'o',
            'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'u', 'u', 'u',
            'u', 'u'
        ]
        game_letters = []

        class LetterButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    return
                if self.custom_id == "c":
                    game_letters.append(consonants.pop(
                        random.randint(0, len(consonants) - 1)
                    ))
                elif self.custom_id == "v":
                    game_letters.append(vowels.pop(
                        random.randint(0, len(vowels) - 1)
                    ))
                letter_rack = ""
                for letter in game_letters:
                    letter_rack += f":regional_indicator_{letter}:  "
                if len(game_letters) != 9:
                    for _ in range(9 - len(game_letters)):
                        letter_rack += "⬜  "
                    embed = discord.Embed(
                        title="Selecting letters",
                        description=letter_game_desc + letter_rack,
                        color=ctx.author.color
                    )
                    await interaction.response.edit_message(
                        embed=embed, view=view
                    )
                else:
                    view.stop()
                    game_code = ''.join(
                        random.choice(string.ascii_lowercase + string.digits)
                        for _ in range(6)
                    )
                    while game_code in letter_games:
                        game_code = ''.join(
                            random.choice(
                                string.ascii_lowercase + string.digits
                            )
                            for _ in range(6)
                        )
                    letter_games[game_code] = ([], game_letters)
                    embed = discord.Embed(
                        title="You have 60 seconds to submit a word!",
                        description=f"{letter_rack}\n\n"
                        + f"Game Code: **{game_code}**\n\nAnyone can now send "
                        + "a word using only these letters (each letter can "
                        + "only be used once) to me, along with your game "
                        + "code (which is not case sensitive). "
                        + "Your message must be formatted like so: "
                        + "`/lettergame submit <game-code> <your-word>`. "
                        + "You may only submit a word once."
                    )
                    await interaction.response.edit_message(
                        embed=embed, view=None
                    )
                    await asyncio.sleep(60)
                    if len(letter_games[game_code][0]) == 0:
                        winners = "Nobody submitted a valid word!"
                    else:
                        winners = ""
                        result_counter = 1
                        for result in sorted(
                                letter_games[game_code][0],
                                key=lambda x: x[0], reverse=True)[:10]:
                            user = await bot.discord_bot.fetch_user(result[1])
                            winners += (
                                f"{result_counter}. **{user}** | "
                                + f"{result[0]} | {result[2].upper()}\n"
                            )
                            result_counter += 1
                    valid_words = []
                    for word in utils.get_all_words():
                        valid = True
                        game_letters_clone = game_letters.copy()
                        for letter in word:
                            if letter not in game_letters_clone:
                                valid = False
                            else:
                                game_letters_clone.remove(letter)
                        if valid:
                            valid_words += [word]
                    valid_text = "Best Words:\n"
                    for word in sorted(
                            valid_words,
                            key=len, reverse=True)[:10]:
                        valid_text += f"{len(word)} | {word.upper()}\n"
                    embed = discord.Embed(
                        title="Time is up! Let's see the results...",
                        description=f"{letter_rack}\n{winners}\n{valid_text}"
                        + "\nThanks for playing!"
                    )
                    del letter_games[game_code]
                    await response.edit_original_message(
                        embed=embed
                    )

        letter_game_desc = (
            "The rules are simple, select your letters then "
            + "make the longest word possible out of them. Multiple people "
            + "can participate! (Although you can still play alone)\n\n"
            + "Once the letters have been selected, you have 60 seconds to "
            + "send a word using only those letters (each letter can only be "
            + "used once) to me. You will also be given a game code so I "
            + "know which game you are playing. Your message must "
            + "be formatted like so: "
            + "`/lettergame submit <game-code> <your-word>`. "
            + "You may only submit a word once. Have fun!\n\n"
            + "Select either consonant or vowel 9 times with the two buttons "
            + "(only the person who started the game can do this)\n"
        )
        embed = discord.Embed(
            title="Welcome to the RoboSans Letter Game!",
            description=letter_game_desc + "⬜  " * 9,
            color=ctx.author.color
        )
        view = discord.ui.View(timeout=None)
        view.add_item(LetterButton(
            label="Consonant", style=ButtonStyle.primary, custom_id="c"
        ))
        view.add_item(LetterButton(
            label="Vowel", style=ButtonStyle.primary, custom_id="v"
        ))
        response = await ctx.respond(embed=embed, view=view)

    @letter_game_group.command()
    async def submit(ctx: ApplicationContext,
            code: Option(str, "Your game code"),
            word: Option(str, "Your word")):
        """Submit a word for an **active** letter game."""
        game_code = code.lower()
        if game_code not in letter_games:
            await ctx.respond("That game code is not valid", ephemeral=True)
            return
        player_scores, game_letters = letter_games[game_code]
        for submitted in player_scores:
            if submitted[1] == ctx.author.id:
                await ctx.respond(
                    "You have already submitted a word!",
                    ephemeral=True
                )
                return
        game_letters_clone = game_letters.copy()
        for letter in word.lower():
            if letter not in game_letters_clone:
                await ctx.respond("That is not a valid word!", ephemeral=True)
                letter_games[game_code][0].append((0, ctx.author.id, "X"))
                return
            game_letters_clone.remove(letter)
        if word.lower() not in utils.get_all_words():
            await ctx.respond("That is not a valid word!", ephemeral=True)
            letter_games[game_code][0].append((0, ctx.author.id, "X"))
            return
        await ctx.respond("That's a valid word, well done!", ephemeral=True)
        letter_games[game_code][0].append((len(word), ctx.author.id, word))
        return

    @bot.discord_bot.command()
    async def akinator(ctx: ApplicationContext,
            gamemode: Option(
                str, "What the Akinator will try to guess",
                choices=["people", "objects", "animals"])):
        """
        I can guess what you're thinking! ...After a few questions of course
        """
        language = "en"
        if gamemode != "people":
            language += f"_{gamemode}"
        aki = Akinator()
        embed = discord.Embed(
            title="Please wait whilst the Akinator loads",
            color=ctx.author.color,
            description="This may take some time"
        )
        response = await ctx.respond(embed=embed)

        class AkiButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    return
                # Akiantor can take over 3 seconds to respond so response
                # must be deferred
                await interaction.response.defer()
                if self.custom_id == "gb":
                    if aki.step == 0:
                        return
                    question = await aki.back()
                else:
                    question = await aki.answer(self.custom_id)
                    if aki.step == 79 or aki.progression >= 80:
                        await aki.win()
                        view.stop()
                        embed = discord.Embed(
                            title="You were thinking of: "
                            + aki.first_guess['name'],
                            color=ctx.author.color,
                            description=aki.first_guess['description']
                        )
                        embed.set_image(
                            url=aki.first_guess['absolute_picture_path']
                        )
                        await response.edit_original_message(
                            embed=embed, view=None
                        )
                        return
                embed = discord.Embed(
                    title=question, color=ctx.author.color
                )
                embed.set_footer(
                    text=f"Certainty: {aki.progression:.0f}% | "
                    + f"Question Number {aki.step + 1}"
                )
                await response.edit_original_message(embed=embed)

        first_question = await aki.start_game(language)
        first_embed = discord.Embed(
            title=first_question, color=ctx.author.color
        )
        first_embed.set_footer(text="Certainty: 0% | Question Number 1")
        view = discord.ui.View(timeout=None)
        view.add_item(AkiButton(
            label="Yes", style=ButtonStyle.primary, custom_id="y"
        ))
        view.add_item(AkiButton(
            label="No", style=ButtonStyle.primary, custom_id="n"
        ))
        view.add_item(AkiButton(
            label="I Don't Know", style=ButtonStyle.primary, custom_id="i"
        ))
        view.add_item(AkiButton(
            label="Probably", style=ButtonStyle.primary, custom_id="p"
        ))
        view.add_item(AkiButton(
            label="Probably Not", style=ButtonStyle.primary, custom_id="pn"
        ))
        view.add_item(AkiButton(
            label="Go Back", style=ButtonStyle.primary, custom_id="gb"
        ))
        await response.edit_original_message(embed=first_embed, view=view)

    @bot.discord_bot.command()
    async def tictactoe(ctx: ApplicationContext,
            opponent: Option(discord.User, "The user you want to play with")):
        """Play a game of Tic Tac Toe against another member of the server"""
        if not isinstance(opponent, discord.Member):
            await ctx.respond(
                "That user doesn't appear to be in this server",
                ephemeral=True
            )
            return
        current_player = 0
        grid = [[None] * 3 for _ in range(3)]

        def victory_check():
            # Check rows
            for y_coord in range(3):
                if grid[y_coord].count("X") == 3:
                    return 0  # Player 1 wins
                if grid[y_coord].count("O") == 3:
                    return 1  # Player 2 wins
            # Check columns
            for x_coord in range(3):
                if (grid[0][x_coord] == "X" and grid[1][x_coord] == "X"
                        and grid[2][x_coord] == "X"):
                    return 0  # Player 1 wins
                if (grid[0][x_coord] == "O" and grid[1][x_coord] == "O"
                        and grid[2][x_coord] == "O"):
                    return 1  # Player 2 wins
            # Check diagonals
            if grid[0][0] == "X" and grid[1][1] == "X" and grid[2][2] == "X":
                return 0  # Player 1 wins
            if grid[0][0] == "O" and grid[1][1] == "O" and grid[2][2] == "O":
                return 1  # Player 2 wins
            if grid[0][2] == "X" and grid[1][1] == "X" and grid[2][0] == "X":
                return 0  # Player 1 wins
            if grid[0][2] == "O" and grid[1][1] == "O" and grid[2][0] == "O":
                return 1  # Player 2 wins
            if all([x for y in grid for x in y]):
                # Game ended in draw
                return -1
            # Nobody has won yet
            return None

        class TicTacToeButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                nonlocal current_player
                if interaction.user != (
                        opponent if current_player else ctx.author):
                    return
                self.style = (
                    ButtonStyle.success
                    if current_player else
                    ButtonStyle.danger
                )
                grid[int(self.custom_id[1])][int(self.custom_id[0])] = (
                    "O" if current_player else "X"
                )
                self.disabled = True
                victory_state = victory_check()
                if victory_state is None:
                    current_player = 0 if current_player else 1
                    mention = (
                        opponent.mention
                        if current_player else
                        ctx.author.mention
                    )
                    await response.edit_original_message(
                        content=f"**{mention}:**", view=view
                    )
                    return
                if victory_state == -1:
                    await response.edit_original_message(
                        content="This game is a **draw**",
                        view=view
                    )
                elif victory_state == 0:
                    await response.edit_original_message(
                        content=f"**{ctx.author.mention}** wins!",
                        view=view
                    )
                elif victory_state == 1:
                    await response.edit_original_message(
                        content=f"**{opponent.mention}** wins!",
                        view=view
                    )
                view.stop()

        view = discord.ui.View(timeout=None)
        for i in range(3):
            for j in range(3):
                view.add_item(TicTacToeButton(
                    label="\u200b", row=i, style=ButtonStyle.secondary,
                    custom_id=f"{j}{i}"
                ))
        response = await ctx.respond(f"**{ctx.author.mention}:**", view=view)
