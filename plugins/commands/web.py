"""
Commands that pull data from online third-party APIs.
Requires all third-party authentication information to be present in the config
file.
"""
import datetime

import asyncpraw
import discord
import discord.ext.pages
import requests
import srcomapi
import wikipedia
import wolframalpha
from discord.commands import Option
from discord.commands.context import ApplicationContext

from photon_bot import PhotonBot

URLS = {
    "OpenWeatherMap":
    "https://api.openweathermap.org/data/2.5/weather?appid={0}&units=metric&q={1}",

    "WeatherIcons":
    "https://openweathermap.org/img/w/{0}.png",

    "HereMap":
    "https://image.maps.api.here.com/mia/1.6/mapview?app_id={0}&app_code={1}&z=7&c={2}",

    "OxfordDictionary":
    "https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/{0}",

    "OxfordLemmas":
    "https://od-api.oxforddictionaries.com/api/v2/lemmas/en-gb/{0}",

    "OMDb":
    "http://www.omdbapi.com/?apikey={0}&plot=full&t={1}",

    "UrbanDictionary":
    "http://api.urbandictionary.com/v0/define?term={0}",

    "GoogleCustomSearch":
    "https://www.googleapis.com/customsearch/v1?cx={0}&safe={1}&searchType=image&key={2}&q={3}"
}


def register_commands(bot: PhotonBot):
    @bot.discord_bot.command()
    async def wiki(ctx: ApplicationContext,
                   search: Option(str, "Wikipedia search query")):
        """Display a summary of a page on Wikipedia"""
        results = wikipedia.search(search)
        if len(results) < 1:
            await ctx.respond(
                "No pages were found with that search term", ephemeral=True
            )
            return
        page = wikipedia.page(results[0], auto_suggest=False)
        summary = page.summary
        if len(summary) > 1000:
            summary = summary[:1000]
            summary += "... **Read more on Wikipedia by clicking the title**"
        embed = discord.Embed(
            title=page.title, description=summary, url=page.url,
            color=ctx.author.color
        )
        if len(page.images) > 0:
            embed.set_thumbnail(url=page.images[0])
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def speedrun(ctx: ApplicationContext,
            game: Option(str, "Name of the game to search for")):
        """Find speedrun record information for a game from speedrun.com"""
        # Speedrun API can be slow (>3 seconds) so must be deferred
        await ctx.defer()
        srcom = srcomapi.SpeedrunCom()
        results = srcom.search(srcomapi.datatypes.Game, {"name": game})
        if len(results) == 0:
            await ctx.respond("No games could be found")
            return
        game = results[0]
        if len(game.categories) == 0:
            await ctx.respond("This game currently has no categories")
            return
        selected_category = None
        for category in game.categories:
            if category.type == 'per-game':
                selected_category = category
                break
        if selected_category is None:
            await ctx.respond("This game has no full-game categories")
            return
        if len(selected_category.records) == 0:
            await ctx.respond("This game has no records")
            return
        if len(selected_category.records[0].runs) == 0:
            await ctx.respond("This game has no runs")
            return
        run = selected_category.records[0].runs[0]['run']
        embed = discord.Embed(
            title=f"World Record for {game.name}",
            description=f"Release Date: `{game.released}`",
            color=ctx.author.color, url=run.weblink
        )
        embed.add_field(name="Record Holder", value=run.players[0].name)
        embed.add_field(
            name="Category Name",
            value=selected_category.name
        )
        record_time = run.times['primary_t']
        embed.add_field(
            name="Record Time",
            value=f"{datetime.timedelta(seconds=round(record_time))}"
        )
        submitted_timestamp = datetime.datetime.fromisoformat(
            run.submitted.replace("Z", "")
        ).timestamp()
        embed.add_field(
            name="Record Uploaded On",
            value=f"<t:{round(submitted_timestamp)}:F>"
        )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def dictionary(ctx: ApplicationContext,
            word: Option(str, "Word to find definition for")):
        """Find a list of definitions for a word"""
        request_headers = {
            "app_id": bot.config['OxfordDictionaryAuth']['ID'],
            "app_key": bot.config['OxfordDictionaryAuth']['Key']
        }
        try:
            lemmas_response = requests.get(
                URLS["OxfordLemmas"].format(word), headers=request_headers
            ).json()
            resolved_word = (
                lemmas_response['results'][0]['lexicalEntries'][0]
                ['inflectionOf'][0]['text']
            )
        except IndexError:
            await ctx.respond("I couldn't find that word", ephemeral=True)
            return
        dictionary_response = requests.get(
            URLS["OxfordDictionary"].format(resolved_word),
            headers=request_headers
        ).json()
        if 'error' in dictionary_response:
            await ctx.respond("I couldn't find that word", ephemeral=True)
            return
        definitions = []
        for entry in dictionary_response['results'][0]['lexicalEntries']:
            for sense in entry['entries'][0]['senses']:
                new_definition = ""
                if 'regions' in sense:
                    new_definition += "**["
                    new_definition += " • ".join(
                        [
                            x['text'].replace("_", " ")
                            for x in sense['regions']
                        ]
                    )
                    new_definition += "]**\n"
                if 'registers' in sense:
                    new_definition += "**("
                    new_definition += " • ".join(
                        [
                            x['text'].replace("_", " ")
                            for x in sense['registers']
                        ]
                    )
                    new_definition += ")**\n"
                if 'definitions' in sense:
                    new_definition += (
                        f"**{len(definitions) + 1}** "
                        + f"*{entry['lexicalCategory']['text'].strip()}*\n"
                    )
                    new_definition += "\n".join(
                        [
                            f"**-** `{x.strip()}`"
                            for x in sense['definitions']
                        ]
                    )
                if 'examples' in sense:
                    new_definition += "\n" + "\n".join(
                        [
                            f"    **-** *{x['text'].strip()}*"
                            for x in sense['examples']
                        ]
                    )
                if new_definition != "":
                    definitions.append(new_definition)
        if len(definitions) == 0:
            await ctx.respond(
                "This word has no information to display", ephemeral=True
            )
            return
        if 'etymologies' in (dictionary_response['results'][0]
                ['lexicalEntries'][0]['entries'][0]):
            definitions.append(
                "**Etymology:**\n"
                + "\n".join(
                    [
                        f"`{x.strip()}`"
                        for x in (
                            dictionary_response['results'][0]
                            ['lexicalEntries'][0]['entries'][0]['etymologies']
                        )
                    ]
                )
            )
        dictionary_message = f"**{resolved_word.capitalize()}**\n"
        dictionary_message += '\n\n'.join(definitions)
        if len(dictionary_message) < 2000:
            await ctx.respond(dictionary_message)
        else:
            await ctx.respond(f"**{resolved_word.capitalize()}**\n")
            yet_to_send = definitions.copy()
            while len(yet_to_send) > 0:
                message = ""
                try:
                    while len(message) + len(yet_to_send[0]) + 2 < 2000:
                        message += yet_to_send.pop(0) + "\n\n"
                except IndexError:
                    break
                finally:
                    await ctx.channel.send(message.strip())

    @bot.discord_bot.command()
    async def thesaurus(ctx: ApplicationContext,
            word: Option(str, "Word to find synonyms for")):
        """Find a list of synonyms for a word"""
        request_headers = {
            "app_id": bot.config['OxfordDictionaryAuth']['ID'],
            "app_key": bot.config['OxfordDictionaryAuth']['Key']
        }
        try:
            lemmas_response = requests.get(
                URLS["OxfordLemmas"].format(word), headers=request_headers
            ).json()
            resolved_word = (
                lemmas_response['results'][0]['lexicalEntries'][0]
                ['inflectionOf'][0]['text']
            )
        except IndexError:
            await ctx.respond("I couldn't find that word", ephemeral=True)
            return
        dictionary_response = requests.get(
            URLS["OxfordDictionary"].format(resolved_word),
            headers=request_headers
        ).json()
        if 'error' in dictionary_response:
            await ctx.respond("I couldn't find that word", ephemeral=True)
            return
        synonyns = []
        for entry in dictionary_response['results'][0]['lexicalEntries']:
            for sense in entry['entries'][0]['senses']:
                if 'synonyms' in sense:
                    synonyns += [x['text'] for x in sense['synonyms']]
        if len(synonyns) == 0:
            await ctx.respond("This word has no synonyms", ephemeral=True)
            return
        thesaurus_message = f"**Synonyms for {resolved_word.capitalize()}:** "
        for index, word in enumerate(synonyns):
            thesaurus_message += f"`{word}`"
            if index != len(synonyns) - 1:
                thesaurus_message += ", "
        await ctx.respond(thesaurus_message)

    @bot.discord_bot.command()
    async def weather(ctx: ApplicationContext,
            city: Option(str, "Name of the city to get weather for")):
        """
        Get the current weather conditions for cities anywhere in the world
        """
        city_data = requests.get(
            URLS['OpenWeatherMap'].format(
                bot.config['OpenWeatherMapAuth']['ID'], city
            )
        ).json()
        if city_data["cod"] == '404':
            await ctx.respond("That city could not be found", ephemeral=True)
            return
        if city_data["cod"] != 200:
            await ctx.respond("An unknown error occured", ephemeral=True)
            return
        embed = discord.Embed(
            title=f":flag_{city_data['sys']['country'].lower()}: "
            + city_data['weather'][0]['description'].capitalize(),
            color=ctx.author.color
        )
        embed.set_image(
            url=URLS['HereMap'].format(
                bot.config['HereMapAuth']['ID'],
                bot.config['HereMapAuth']['Code'],
                f"{city_data['coord']['lat']},{city_data['coord']['lon']}"
            )
        )
        embed.set_author(
            name=f"Weather for {city_data['name']}",
            icon_url=URLS['WeatherIcons'].format(
                city_data['weather'][0]['icon']
            )
        )
        embed.add_field(
            name="Temperature",
            value="**Current:** "
            + f"`{city_data['main']['temp']:.2f}°C`\n"
            + "**Minimum:** "
            + f"`{city_data['main']['temp_min']:.2f}°C`\n"
            + "**Maximum:** "
            + f"`{city_data['main']['temp_max']:.2f}°C`",
            inline=True
        )
        embed.add_field(
            name="Atmosphere",
            value="**Pressure:** "
            + f"`{city_data['main']['pressure']} mbar`\n"
            + "**Humidity:** "
            + f"`{city_data['main']['humidity']}%`\n"
            + "**Cloud Cover:** "
            + f"`{city_data['clouds']['all']}%`",
            inline=True
        )
        directions = [
            "North", "North-East", "East", "South-East",
            "South", "South-West", "West", "North-West"
        ]
        embed.add_field(
            name="Wind",
            value="**Speed:** "
            + f"`{city_data['wind']['speed'] * 2.237:.2f} mph`\n"
            + "**Direction**: "
            + f"`{directions[city_data['wind']['deg'] // 45]}`",
            inline=True
        )
        embed.add_field(
            name="Sun",
            value=f"**Rise**: <t:{city_data['sys']['sunrise']}:f>\n"
            + f"**Set:** <t:{city_data['sys']['sunset']}:f>",
            inline=True
        )
        embed.add_field(
            name="Map",
            value="Did I get the wrong country? Try again but after the "
            + "city name type a comma and your country code. E.g. `London,CA`",
            inline=False
        )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def filmlookup(ctx: ApplicationContext,
            film: Option(str, "The name of the film")):
        """Get information about a particular film or TV show"""
        film_response = requests.get(
            URLS["OMDb"].format(bot.config['OMDbAuth']['Key'], film)
        ).json()
        if film_response['Response'] == 'False':
            await ctx.respond(film_response['Error'], ephemeral=True)
            return
        embed = discord.Embed(color=ctx.author.color)
        if 'Title' in film_response:
            embed.title = film_response['Title']
        else:
            embed.title = "Title Unknown"
        if 'Plot' in film_response:
            embed.description = film_response['Plot']
        else:
            embed.description = "Plot Unknown"
        if ('Website' in film_response
                and film_response['Website'].startswith("http")):
            embed.url = film_response['Website']
        if ('Poster' in film_response
                and film_response['Poster'].startswith("http")):
            embed.set_thumbnail(url=film_response['Poster'])
        if 'Released' in film_response:
            embed.add_field(
                name="Release Date", value=film_response['Released'],
                inline=True
            )
        else:
            embed.add_field(name="Release Date", value="Unknown", inline=True)
        if 'Rated' in film_response:
            embed.add_field(
                name="Age Rating", value=film_response['Rated'], inline=True
            )
        else:
            embed.add_field(name="Age Rating", value="Unknown", inline=True)
        if 'Runtime' in film_response:
            embed.add_field(
                name="Runtime", value=film_response['Runtime'], inline=True
            )
        else:
            embed.add_field(name="Runtime", value="Unknown", inline=True)
        if 'Language' in film_response:
            embed.add_field(
                name="Language", value=film_response['Language'], inline=True
            )
        else:
            embed.add_field(name="Language", value="Unknown", inline=True)
        if 'Country' in film_response:
            embed.add_field(
                name="Country", value=film_response['Country'], inline=True
            )
        else:
            embed.add_field(name="Country", value="Unknown", inline=True)
        if 'Awards' in film_response:
            embed.add_field(
                name="Awards", value=film_response['Awards'], inline=True
            )
        else:
            embed.add_field(name="Awards", value="Unknown", inline=True)
        if 'BoxOffice' in film_response:
            embed.add_field(
                name="Money Made", value=film_response['BoxOffice'],
                inline=True
            )
        else:
            embed.add_field(name="Money Made", value="Unknown", inline=True)
        if 'Director' in film_response:
            embed.add_field(
                name="Director", value=film_response['Director'], inline=True
            )
        else:
            embed.add_field(name="Director", value="Unknown", inline=True)
        if 'Genre' in film_response:
            embed.add_field(
                name="Genre", value=film_response['Genre'], inline=True
            )
        else:
            embed.add_field(name="Genre", value="Unknown", inline=True)
        if 'Actors' in film_response:
            embed.add_field(
                name="Starring Actors", value=film_response['Actors'],
                inline=True
            )
        else:
            embed.add_field(
                name="Starring Actors", value="Unknown", inline=True
            )
        await ctx.respond(embed=embed)

    @bot.discord_bot.command()
    async def urban(ctx: ApplicationContext,
            word: Option(str, "The word to search for")):
        """Search for definitions on the Urban dictionary"""
        urban_response = requests.get(
            URLS["UrbanDictionary"].format(word)
        ).json()
        if len(urban_response['list']) == 0:
            await ctx.respond("No results found", ephemeral=True)
            return
        pages = []
        for result in sorted(urban_response['list'],
                key=lambda x: x['thumbs_up'] - x['thumbs_down'], reverse=True):
            embed = discord.Embed(
                title=f"Definitions for {word.capitalize()}",
                description="These definitions are not guaranteed to be "
                + "accurate. For reliable definitions, use `/dictionary`.",
                color=ctx.author.color
            )
            definition = result['definition'].replace("[", "").replace("]", "")
            if len(definition) > 1000:
                definition = definition[:997] + "..."
            embed.add_field(name="Definition", value=definition, inline=False)
            if result['example'] != "":
                example = result['example'].replace("[", "").replace("]", "")
                if len(example) > 1000:
                    example = example[:997] + "..."
                embed.add_field(
                    name="Example Sentence", value=example, inline=False
                )
            embed.set_footer(
                text=f"{result['thumbs_up']} likes • "
                + f"{result['thumbs_down']} dislikes • "
                + f"Submitted by {result['author']}"
            )
            pages.append(embed)
        await discord.ext.pages.Paginator(pages).respond(ctx.interaction)

    @bot.discord_bot.command()
    async def reddit(ctx: ApplicationContext,
            subreddit: Option(str, "The name of the subreddit")):
        """Get the hot posts from a specified subreddit"""
        reddit_client = asyncpraw.Reddit(
            client_id=bot.config["RedditAuth"]["ClientID"],
            client_secret=bot.config["RedditAuth"]["ClientSecret"],
            user_agent=bot.config["RedditAuth"]["UserAgent"],
            username=bot.config["RedditAuth"]["Username"],
            password=bot.config["RedditAuth"]["Password"]
        )
        if subreddit.startswith("r/"):
            subreddit = subreddit[2:]
        try:
            subreddit_instance = await reddit_client.subreddit(subreddit, True)
        except Exception:
            await ctx.respond(
                "That subreddit could not be found", ephemeral=True
            )
            return
        pages = []
        async for post in subreddit_instance.hot(limit=50):
            if (post.selftext != "" or 'i.redd.it' not in post.url
                    or post.stickied):
                continue
            if post.over_18 and not ctx.channel.is_nsfw():
                continue
            embed = discord.Embed(
                title=f"Reddit Posts from r/{subreddit}",
                description=f"**Title:** {post.title}",
                color=ctx.author.color
            )
            if not ctx.channel.is_nsfw():
                embed.description += (
                    "\n\nYou are not in an NSFW channel. "
                    + "NSFW posts will not be displayed."
                )
            embed.set_image(url=post.url)
            embed.set_footer(
                text=f"{post.score} upvotes • "
                + f"Posted by u/{post.author.name}"
            )
            pages.append(embed)
        if len(pages) == 0:
            await ctx.respond(
                "No images could be found on that subreddit",
                ephemeral=True
            )
            return
        await discord.ext.pages.Paginator(pages).respond(ctx.interaction)

    @bot.discord_bot.command()
    async def imagelookup(ctx: ApplicationContext,
            search: Option(str, "The image search term")):
        """Search google images and display the of results"""
        search_response = requests.get(
            URLS["GoogleCustomSearch"].format(
                bot.config['GoogleCustomSearchAuth']['SearchID'],
                'off' if ctx.channel.is_nsfw() else 'active',
                bot.config['GoogleCustomSearchAuth']['Key'],
                search
            )
        ).json()
        pages = []
        for item in search_response['items']:
            if 'image' in item:
                embed = discord.Embed(
                    title=f"Image Results for {search}",
                    color=ctx.author.color
                )
                if not ctx.channel.is_nsfw():
                    embed.description = (
                        "SafeSearch has been enabled as you "
                        + "are not in a NSFW channel"
                    )
                embed.set_image(url=item['link'])
                pages.append(embed)
        if len(pages) == 0:
            await ctx.respond("No images could be found", ephemeral=True)
            return
        await discord.ext.pages.Paginator(pages).respond(ctx.interaction)

    @bot.discord_bot.command()
    async def wolfram(ctx: ApplicationContext,
            expression: Option(str, "Expression to send to Wolfram|Alpha")):
        """Get results for an expression from Wolfram|Alpha"""
        # Wolfram processing takes a long time (>3 seconds) so must be deferred
        await ctx.defer()
        wolfram_client = wolframalpha.Client(
            bot.config['WolframAlphaAuth']['Key']
        )
        wolfram_result = wolfram_client.query(
            expression, params=(
                ("scantimeout", "60"), ("podtimeout", "60"),
                ("formattimeout", "60"), ("parsetimeout", "60"),
                ("totaltimeout", "240")
            )
        )
        if wolfram_result.success == "false":
            await ctx.respond(
                "Wolfram|Alpha could not understand your request"
            )
            return
        if not hasattr(wolfram_result, "pods"):
            await ctx.respond("Your expression returned no results")
            return
        page_groups = []
        for pod in wolfram_result.pods:
            pages = []
            for subpod in pod.subpods:
                embed = discord.Embed(
                    title=f"**{pod.title}**", color=ctx.author.color
                )
                embed.set_image(url=subpod.img.src)
                pages.append(embed)
            page_groups.append(discord.ext.pages.PageGroup(
                pages, label=pod.title, description=f"{len(pages)} item(s)"
            ))
        await discord.ext.pages.Paginator(
            page_groups, show_menu=True
        ).respond(ctx.interaction)
