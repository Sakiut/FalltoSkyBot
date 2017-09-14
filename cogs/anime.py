# -*- coding: utf-8 -*-

import  asyncio
import  discord
from    discord.ext         import commands
from    libraries.library   import *
from    libraries           import anilist
from    libraries           import mal

emotes = [
    u"\u0031\N{COMBINING ENCLOSING KEYCAP}", #1
    u"\u0032\N{COMBINING ENCLOSING KEYCAP}", #2
    u"\u0033\N{COMBINING ENCLOSING KEYCAP}", #3
    u"\u0034\N{COMBINING ENCLOSING KEYCAP}", #4
    u"\u0035\N{COMBINING ENCLOSING KEYCAP}", #5
    u"\u0036\N{COMBINING ENCLOSING KEYCAP}", #6
    u"\u0037\N{COMBINING ENCLOSING KEYCAP}", #7
    u"\u0038\N{COMBINING ENCLOSING KEYCAP}", #8
    u"\u0039\N{COMBINING ENCLOSING KEYCAP}"  #9
]

class Anime:

    def __init__(self,bot):
        self.bot = bot
        self.token = None
        self.params = {
            "grant_type":"client_credentials",
            "client_id": getAniClientID(),
            "client_secret": getAniClientSecret()
        }

    @commands.group(pass_context=True)
    async def anilist(self, ctx):
        """Commandes de requêtes d'informations sur des animes et mangas
        de la base de données d'Anilist.
        Langue de la base de données : EN

        Utilisation :
            .anilist anime <anime à rechercher>
            .anilist manga <manga à rechercher>"""

        if ctx.invoked_subcommand is None:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("```md\nSyntaxe invalide. Voir .help anilist pour plus d'informations sur comment utiliser cette commande.\n```")

    @anilist.command(pass_context=True, no_pm=False)
    async def anime(self, ctx, *, anime : str):
        """Récupère les informations concernant un anime
        Base de données utilisée : AniList.co
        Langue de la base de données : EN"""

        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say('Processing request')

        self.token = anilist.auth(self.params)

        try:
            results = anilist.getAnimes(anime, self.token)
            results = results[:9]
        except KeyError as e:
            await self.bot.delete_message(tmp)
            fmt = '```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            return

        ResultsEmbed = discord.Embed()
        ResultsEmbed.title = "Choisissez parmi ces résultats :"
        ResultsEmbed.colour = 0x3498db
        ResultsEmbed.description = ""
        ResultsEmbed.set_footer(text = anime)

        i = 0
        for x in results:
            i += 1
            j = str(i)
            if i > 9:
                break
            else:
                ResultsEmbed.description += "[{}]() - {} - {}\n".format(j, x[0], x[1])

        await self.bot.delete_message(tmp)
        resultsMessage = await self.bot.say(embed=ResultsEmbed)

        listing = []
        for emote, title in zip(emotes, results):
            dc = {emote:title}
            listing.append(dc)

        for x in range(0, len(results)):
            await self.bot.add_reaction(resultsMessage, emotes[x])

        await asyncio.sleep(1)
        res = await self.bot.wait_for_reaction(emotes, message=resultsMessage)
        react = res.reaction.emoji
        await self.bot.clear_reactions(resultsMessage)
        await self.bot.delete_message(resultsMessage)

        for l in listing:
            try:
                title = l[react]
            except KeyError:
                continue

        index = results.index(title)

        tmp = await self.bot.say("Processing request for {}".format(title))

        data = anilist.getAnimeInfo(anime, self.token, int(index))

        AnimeEmbed = discord.Embed()
        AnimeEmbed.title = str(data['title_english']) + " | " + str(data['title_japanese']) + " (" + str(data['id']) + ")"
        AnimeEmbed.colour = 0x3498db
        AnimeEmbed.set_thumbnail(url=data["image_url_lge"])
        AnimeEmbed.add_field(name = "Type", value = data["type"])
        AnimeEmbed.add_field(name = "Episodes", value = data['total_episodes'])
        AnimeEmbed.add_field(name = "Source", value = data['source'])
        AnimeEmbed.add_field(name = "Status", value = data['airing_status'].capitalize())
        AnimeEmbed.add_field(name = "Genre(s)", value = anilist.getAnimeGenres(data), inline = False)
        AnimeEmbed.add_field(name = "Episode Length", value = str(data['duration']) + " mins/ep")
        AnimeEmbed.add_field(name = "Score", value = str(data['average_score']) + " / 100")
        AnimeEmbed.add_field(name = "Synopsis", value = anilist.formatAnimeDescription(data), inline = False)
        AnimeEmbed.set_footer(text = anilist.formatAnimeDate(data))

        await self.bot.delete_message(tmp)
        await self.bot.say(embed=AnimeEmbed)

    @anilist.command(pass_context=True, no_pm=False)
    async def manga(self, ctx, *, anime : str):
        """Récupère les informations concernant un manga
        Base de données utilisée : AniList.co
        Langue de la base de données : EN"""

        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say('Processing request')

        self.token = anilist.auth(self.params)

        try:
            results = anilist.getMangas(anime, self.token)
            results = results[:9]
        except KeyError as e:
            await self.bot.delete_message(tmp)
            fmt = '```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            return

        ResultsEmbed = discord.Embed()
        ResultsEmbed.title = "Choisissez parmi ces résultats :"
        ResultsEmbed.colour = 0x3498db
        ResultsEmbed.description = ""
        ResultsEmbed.set_footer(text = anime)

        i = 0
        for x in results:
            i += 1
            j = str(i)
            if i > 9:
                break
            else:
                ResultsEmbed.description += "[{}]() - {} - {}\n".format(j, x[0], x[1])

        await self.bot.delete_message(tmp)
        resultsMessage = await self.bot.say(embed=ResultsEmbed)

        listing = []
        for emote, title in zip(emotes, results):
            dc = {emote:title}
            listing.append(dc)

        for x in range(0, len(results)):
            await self.bot.add_reaction(resultsMessage, emotes[x])

        await asyncio.sleep(1)
        res = await self.bot.wait_for_reaction(emotes, message=resultsMessage)
        react = res.reaction.emoji
        await self.bot.clear_reactions(resultsMessage)
        await self.bot.delete_message(resultsMessage)

        for l in listing:
            try:
                title = l[react]
            except KeyError:
                continue

        index = results.index(title)

        tmp = await self.bot.say("Processing request for {}".format(title))

        data = anilist.getMangaInfo(anime, self.token, int(index))

        if data['total_volumes'] == 0:
            data['total_volumes'] = '-'

        if data['total_chapters'] == 0:
            data['total_chapters'] = '-'

        MangaEmbed = discord.Embed()
        MangaEmbed.title = str(data['title_english']) + " | " + str(data['title_japanese']) + "\n(" + str(data['id']) + ")"
        MangaEmbed.colour = 0x3498db
        MangaEmbed.set_thumbnail(url=data['image_url_lge'])
        MangaEmbed.add_field(name = 'Type', value = data['type'])
        MangaEmbed.add_field(name = 'Volumes', value = str(data['total_volumes']))
        MangaEmbed.add_field(name = 'Chapters', value = str(data['total_chapters']))
        MangaEmbed.add_field(name = 'Status', value = data["publishing_status"].capitalize())
        MangaEmbed.add_field(name = 'Genre(s)', value = anilist.getAnimeGenres(data), inline = False)
        MangaEmbed.add_field(name = 'Score', value = str(data['average_score']) + " / 100")
        MangaEmbed.add_field(name = "Synopsis", value = anilist.formatAnimeDescription(data), inline = False)
        MangaEmbed.set_footer(text = anilist.formatAnimeDate(data))

        await self.bot.delete_message(tmp)
        await self.bot.say(embed=MangaEmbed)

    # CURRENT PROJECT

    # @commands.group(pass_context=True)
    # async def mal(self, ctx):
    #     """Commandes de requêtes d'informations sur des animes et mangas
    #     de la base de données d'Anilist.
    #     Langue de la base de données : EN

    #     Utilisation :
    #         .mal anime <anime à rechercher>
    #         .mal manga <manga à rechercher>"""

    #     if ctx.invoked_subcommand is None:
    #         await self.bot.delete_message(ctx.message)
    #         await self.bot.say("```md\nSyntaxe invalide. Voir .help mal pour plus d'informations sur comment utiliser cette commande.\n```")

    # @mal.command(pass_context=True, no_pm=False)
    # async def anime(self, ctx, *, anime):

    #     await self.bot.delete_message(ctx.message)
    #     tmp = await self.bot.say('Processing request')

    #     data = mal.getMalAnime(anime)
    #     results = mal.extractTitles(data)

    #     ResultsEmbed = discord.Embed()
    #     ResultsEmbed.title = "Choisissez parmi ces résultats :"
    #     ResultsEmbed.colour = 0x3498db
    #     ResultsEmbed.description = ""
    #     ResultsEmbed.set_footer(text = anime)

    #     i = 0
    #     for x in results:
    #         i += 1
    #         j = str(i)
    #         if i > 9:
    #             break
    #         else:
    #             ResultsEmbed.description += "[{}]() - {} - {}\n".format(j, x[0], x[1])

    #     await self.bot.delete_message(tmp)
    #     resultsMessage = await self.bot.say(embed=ResultsEmbed)

    #     emotes = [
    #         u"\u0031\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0032\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0033\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0034\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0035\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0036\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0037\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0038\N{COMBINING ENCLOSING KEYCAP}",
    #         u"\u0039\N{COMBINING ENCLOSING KEYCAP}"
    #     ]

    #     listing = []
    #     for emote, title in zip(emotes, results):
    #         dc = {emote:title}
    #         listing.append(dc)

    #     for x in range(0, len(results)):
    #         await self.bot.add_reaction(resultsMessage, emotes[x])

    #     await asyncio.sleep(1)
    #     res = await self.bot.wait_for_reaction(emotes, message=resultsMessage)
    #     react = res.reaction.emoji
    #     await self.bot.clear_reactions(resultsMessage)
    #     await self.bot.delete_message(resultsMessage)

    #     for l in listing:
    #         try:
    #             title = l[react]
    #         except KeyError:
    #             continue

    #     index = results.index(title)

    #     tmp = await self.bot.say("Processing request for {}".format(title))

    #     data = anilist.getAnimeInfo(anime, self.token, int(index))

    #     AnimeEmbed = discord.Embed()
    #     AnimeEmbed.title = str(data['title']) + " | " + str(data['english']) + " (" + str(data['id']) + ")"
    #     AnimeEmbed.colour = 0x3498db
    #     AnimeEmbed.set_thumbnail(url=data["image"])
    #     AnimeEmbed.add_field(name = "Type", value = data["type"])
    #     AnimeEmbed.add_field(name = "Episodes", value = data['episodes'])
    #     AnimeEmbed.add_field(name = "Status", value = data['status'])
    #     AnimeEmbed.add_field(name = "Score", value = str(data['score']))
    #     AnimeEmbed.add_field(name = "Synopsis", value = html.unescape(html.unescape(data['synopsis'])), inline = False)
    #     AnimeEmbed.set_footer(text = "Start date : {} | End date : {}".format(data['start_date'], data['end_date']))

    #     await self.bot.delete_message(tmp)
    #     await self.bot.say(embed=AnimeEmbed)