# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands
from libraries.perms import *
from libraries.library import *
from libraries import anilist
from libraries import lol
from libraries import youtube
from libraries import moderation

from riotwatcher import RiotWatcher
from riotwatcher import EUROPE_WEST
from riotwatcher import LoLException, error_404, error_429

import random
import os
import math
import traceback
import pickle
import urllib

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

print('[FTS] Connecting...')

freshestMemes = [
    "mem/meme1.jpeg",
    "mem/meme2.jpeg",
    "mem/meme3.jpeg",
    "mem/meme6.jpeg",
    "mem/meme7.jpeg",
    "mem/meme8.jpeg",
    "mem/meme9.jpeg",
    "mem/meme10.jpeg",
    "mem/meme11.jpeg",
    "mem/meme12.jpeg",
    "mem/meme14.jpeg",
    "mem/meme15.jpeg"
]

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '`{0.title}` uploaded by *{0.uploader}* and requested by *{1.display_name}*'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: `{0[0]}m {0[1]}s`]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Anime:
    """Animes related Commands"""

    def __init__(self,bot):

        self.bot = bot
        self.voice_states = {}
        self.token = None
        self.params = {
            "grant_type":"client_credentials",
            "client_id": getAniClientID(),
            "client_secret": getAniClientSecret()
        }

    @commands.command(pass_context=True, no_pm=False)
    async def anime(self, ctx, *, anime:str):
        """Get anime informations"""

        try:
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say('Processing request')
            
            if self.token == None:
                self.token = anilist.auth(self.params)

            data = anilist.getAnimeInfo(anime, self.token)

            AnimeEmbed = discord.Embed()
            AnimeEmbed.title = str(data['title_english']) + " | " + str(data['title_japanese']) + " (" + str(data['id']) + ")"
            AnimeEmbed.colour = 0x3498db
            AnimeEmbed.set_thumbnail(url=data["image_url_lge"])
            AnimeEmbed.add_field(name = "Type", value = data["type"])
            AnimeEmbed.add_field(name = "Episodes", value = data['total_episodes'])
            AnimeEmbed.add_field(name = "Source", value = data['source'])
            AnimeEmbed.add_field(name = "Status", value = data['airing_status'])
            AnimeEmbed.add_field(name = "Genre(s)", value = anilist.getAnimeGenres(data), inline = False)
            AnimeEmbed.add_field(name = "Episode Length", value = str(data['duration']) + " mins/ep")
            AnimeEmbed.add_field(name = "Score", value = str(data['average_score']) + " / 100")
            AnimeEmbed.add_field(name = "Synopsis", value = anilist.formatAnimeDescription(data), inline = False)
            AnimeEmbed.set_footer(text = anilist.formatAnimeDate(data))

            await self.bot.delete_message(tmp)
            await self.bot.say(embed=AnimeEmbed)

        except AttributeError:
            await self.bot.delete_message(tmp)
            await self.bot.say("```py\nAnime not found\n```")
        except IndexError:
            await self.bot.delete_message(tmp)
            await self.bot.say("```py\nWe got a problem with this anime, please try another\n```")
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.delete_message(tmp)
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=False)
    async def manga(self, ctx, *, manga:str):
        """Get manga informations"""

        try:
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say('Processing request')

            if self.token == None:
                self.token = anilist.auth(self.params)

            data = anilist.getMangaInfo(manga, self.token)

            if data['total_volumes'] == 0:
                data['total_volumes'] = '-'

            if data['total_chapters'] == 0:
                data['total_chapters'] = '-'

            MangaEmbed = discord.Embed()
            MangaEmbed.title = str(data['title_english']) + " | " + str(data['title_japanese']) + "\n(" + str(data['id']) + ")"
            MangaEmbed.colour = 0x3498db
            MangaEmbed.set_thumbnail(url=data['image_url_lge'])
            MangaEmbed.add_field(name = 'Type', value = data['type'])
            MangaEmbed.add_field(name = 'Volumes', value = data['total_volumes'])
            MangaEmbed.add_field(name = 'Chapters', value = data['total_chapters'])
            MangaEmbed.add_field(name = 'Status', value = data["publishing_status"])
            MangaEmbed.add_field(name = 'Genre(s)', value = anilist.getAnimeGenres(data), inline = False)
            MangaEmbed.add_field(name = 'Score', value = str(data['average_score']) + " / 100")
            MangaEmbed.add_field(name = "Synopsis", value = anilist.formatAnimeDescription(data), inline = False)
            MangaEmbed.set_footer(text = anilist.formatAnimeDate(data))

            await self.bot.delete_message(tmp)
            await self.bot.say(embed=MangaEmbed)
        except AttributeError:
            await self.bot.delete_message(tmp)
            await self.bot.say("```py\nManga not found\n```")
        except IndexError:
            await self.bot.delete_message(tmp)
            await self.bot.say("```py\nWe got a problem with this manga, please try another\n```")
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.delete_message(tmp)
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

class LeagueOfLegends:
    """Commandes reliées à League of Legends"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=False)
    async def summoner(self, ctx, *, user:str):
        """Récupère les informations d'un invocateur"""

        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say("Processing request...")

        try:
            user = user.replace(" ", "")

            data = lol.getSummonerStats(user)

            name = str(data["name"])
            sum_id = str(data['id'])
            level = str(data['level'])
            icon = str(data['icon'])

            tier5c5 = str(data['tier5c5'])
            rank5c5 = str(data['rank5c5'])
            winr5c5 = str(data['winr5c5'])
            tierflex = str(data['tierflex'])
            rankflex = str(data['rankflex'])
            winrflex = str(data['winrflex'])
            tier33 = str(data['tier33'])
            rank33 = str(data['rank33'])
            winr33 = str(data['winr33'])

            best_champ = str(data['best_champ'])
            best_level = str(data['best_level'])
            best_point = str(data['best_point'])
            sec_champ = str(data['sec_champ'])
            sec_level = str(data['sec_level'])
            sec_point = str(data['sec_point'])
            tri_champ = str(data['tri_champ'])
            tri_level = str(data['tri_level'])
            tri_point = str(data['tri_point'])

            SummonerEmbed = discord.Embed()
            SummonerEmbed.colour = 0x3498db
            SummonerEmbed.title = "Summoner Information for {0} ({1})".format(name, sum_id)
            SummonerEmbed.set_thumbnail(url=icon)
            SummonerEmbed.add_field(name = "_ _", value = "_ _", inline = False)
            SummonerEmbed.add_field(name = "Nom", value = name)
            SummonerEmbed.add_field(name = "Niveau", value = level)
            SummonerEmbed.add_field(name = "_ _", value = "_ _", inline = False)
            SummonerEmbed.add_field(name = "Ranked Solo Duo", value = tier5c5 + " " + rank5c5)
            SummonerEmbed.add_field(name = "Winrate", value = winr5c5)
            SummonerEmbed.add_field(name = "Ranked Flex 5c5", value = tierflex + " " + rankflex)
            SummonerEmbed.add_field(name = "Winrate", value = winrflex)
            SummonerEmbed.add_field(name = "Ranked Flex 3c3", value = tier33 + " " + rank33)
            SummonerEmbed.add_field(name = "Winrate", value = winr33)
            SummonerEmbed.add_field(name = "_ _", value = "_ _", inline = False)
            SummonerEmbed.add_field(name = "Meilleur Champion", value = best_champ)
            SummonerEmbed.add_field(name = "XP", value = "**Maîtrise** : {0}, **Points** : {1}k".format(best_level, best_point))
            SummonerEmbed.add_field(name = "Deuxième Champion", value = sec_champ)
            SummonerEmbed.add_field(name = "XP", value = "**Maîtrise** : {0}, **Points** : {1}k".format(sec_level, sec_point))
            SummonerEmbed.add_field(name = "Troisième Champion", value = tri_champ)
            SummonerEmbed.add_field(name = "XP", value = "**Maîtrise** : {0}, **Points** : {1}k".format(tri_level, tri_point))
            SummonerEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            await self.bot.delete_message(tmp)
            await self.bot.say(embed = SummonerEmbed)

        except Exception as e:
            await self.bot.delete_message(tmp)
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=False)
    async def unranked(self, ctx, *, user:str):
        """Récupère les informations complètes des normal games d'un invocateur"""
        try:
            tmp = await self.bot.say("Processing request...")
            await self.bot.delete_message(ctx.message)

            try:
                summoner = lol.getSummonerInfo(user)
                SummonerWins = lol.getUnrankedWins(summoner['id'])
                SummonerStats = lol.getUnrankedStats(summoner['id'])

                SummonerEmbed = discord.Embed()
                SummonerEmbed.colour = 0x3498db
                SummonerEmbed.title = 'Unranked League of Legends stats for ' + summoner['name'] + ' (' + str(summoner['id']) + ')'
                SummonerEmbed.set_thumbnail(url=lol.getSummonerIconUrl(summoner['name']))
                SummonerEmbed.add_field(name = 'ID Icône', value = str(summoner['profileIconId']))
                SummonerEmbed.add_field(name = 'Niveau', value = str(summoner['summonerLevel']))
                SummonerEmbed.add_field(name = 'Wins', value = str(SummonerWins))
                SummonerEmbed.add_field(name = 'Total Champion Kills', value = str(SummonerStats['totalChampionKills']))
                SummonerEmbed.add_field(name = 'Total Turret Kills', value = str(SummonerStats['totalTurretsKilled']))
                SummonerEmbed.add_field(name = 'Total Minions Kills', value = str(SummonerStats['totalMinionKills']))
                SummonerEmbed.add_field(name = 'Total Neutral Minions Kills', value = str(SummonerStats['totalNeutralMinionsKilled']))
                SummonerEmbed.add_field(name = 'Total Assists', value = str(SummonerStats['totalAssists']))
                SummonerEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)
                await self.bot.delete_message(tmp)
                await self.bot.say(embed=SummonerEmbed)

            except KeyError:
                await self.bot.say("```py\nSummoner not found\n```")
                await self.bot.delete_message(tmp)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(tmp)

    @commands.command(pass_context=True, no_pm=False)
    async def champion(self, ctx, *, champion:str):
        """Récupère les informations d'un champion

        Source : https://champion.gg/
        """
        try:
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say("Processing request...")
            champion = champion.lower()
            name = champion.capitalize()

            if "'" in champion:
                champion = champion.replace("'", "")

            if " " in champion:
                champ = champion.split(" ")
                champion = "{}{}".format(champ[0].capitalize(), champ[1].capitalize())
                stats = lol.getChampion(champion)
                icon = lol.getChampionIconUrl(champion) #FIXME : Les noms composés n'ont pas d'icône.
            else:
                stats = lol.getChampion(champion)
                icon = lol.getChampionIconUrl(champion)

            id = stats[0]
            del stats[0]

            ChampionEmbed = discord.Embed()
            ChampionEmbed.title = "Stats for {0} ({1})".format(name, str(id))
            ChampionEmbed.colour = 0x3498db
            ChampionEmbed.set_thumbnail(url=icon)
            ChampionEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            for stat in stats:
                for key, value in stat.items():
                    value["winRate"] *= 100
                    value["playRate"] *= 100
                    value["banRate"] *= 100
                    ChampionEmbed.add_field(name = "_ _", value = "`{}`".format(key.upper()), inline = False)
                    ChampionEmbed.add_field(name = "Winrate", value = "{0:3.4f} %".format(value["winRate"]))
                    ChampionEmbed.add_field(name = "Playrate", value = "{0:3.4f} %".format(value["playRate"]))
                    ChampionEmbed.add_field(name = "Banrate", value = "{0:3.4f} %".format(value["banRate"]))
                    ChampionEmbed.add_field(name = "Average Ratio", value = "{0:2.1f}/{1:2.1f}/{2:2.1f}".format(value["kills"], value["deaths"], value["assists"]))

            await self.bot.delete_message(tmp)
            await self.bot.say(embed=ChampionEmbed)

        except Exception as e:
            await self.bot.delete_message(tmp)
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=False)
    async def freechamps(self, ctx):
        """Retourne la liste des champions gratuits"""

        try:
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say("Processing request...")

            ChampsIds = lol.getFreeChamps()
            ChampsNames = []
            Message = "```scheme"

            for x in ChampsIds:
                ChampsNames.append(lol.getChampionName(x))

            for x in ChampsNames:
                Message += "\n[>] " + x

            ChampionEmbed = discord.Embed()
            ChampionEmbed.colour = 0x3498db
            ChampionEmbed.set_author(name = "Free Champions", icon_url = 'https://static-cdn.jtvnw.net/jtv_user_pictures/milleniumtvlol-profile_image-ff2429286c8c534a-300x300.png')
            ChampionEmbed.description = Message + "\n```"
            ChampionEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            await self.bot.delete_message(tmp)
            await self.bot.say(embed=ChampionEmbed)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=False)
    async def game(self, ctx, *, user:str):
        """Montre les statistiques d'une game en cours"""

        try:
            try:
                tmp = await self.bot.say("Processing request...")
                await self.bot.delete_message(ctx.message)
                user = user.replace(" ", "")

                summoner = lol.getSummonerInfo(user)
                game = lol.getGameInfo(summoner['id'])

                if game['gameId'] == '404':

                    await self.bot.delete_message(tmp)
                    await self.bot.say("```\nAucune game n'est en cours pour ce joueur.\n```")

                else:

                    print("[FTS][GAME] Processing request...")

                    Participants = game['participants']

                    Team1 = []
                    Team2 = []

                    ranks1 = []
                    champs1 = []
                    summonersNames1 = []
                    WinRate1 = []
                    games1 = []

                    ranks2 = []
                    champs2 = []
                    summonersNames2 = []
                    WinRate2 = []
                    games2 = []

                    print("[FTS][GAME] Variables définies")

                    for x in game['participants']:
                        if x['teamId'] == 100:
                            Team1 += [x]
                        elif x['teamId'] == 200:
                            Team2 += [x]
                        else:
                            raise TypeError('Problème de teams')

                    i = 0
                    bar = ['........', '........', '........', '........', '........', '........', '........', '........', '........', '........']
                    chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'

                    for x in Team1:
                        i += 1
                        j = i - 1

                        SummonerName = x['summonerName']
                        SummonerID = x['summonerId']

                        bar[j] = '█.......'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Variables définies\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Variables définies")

                        Rank = lol.getRank(SummonerID)
                        ranks1 += [Rank]

                        bar[j] = '██......'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Rank collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Rank collected")

                        ChampID = x['championId']
                        Champ = lol.getChampionName(ChampID)
                        champs1 += [Champ]

                        bar[j] = '███.....'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Champion collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Champion collected")

                        summonersNames1 += [SummonerName]

                        bar[j] = '████....'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Summoner's name collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Summoner's name collected")

                        SummonerName2 = SummonerName.replace(" ", "")
                        Player = lol.getSummonerInfo(SummonerName2)

                        bar[j] = '█████...'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Summoner's ID collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Summoner's ID collected")

                        SummonerStats = lol.getRankedStats(Player['id'])

                        bar[j] = '██████..'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Summoner's Stats collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Summoner's Stats collected")

                        if SummonerStats['losses'] != 0:
                            WRate = SummonerStats['wins'] / SummonerStats['losses'] * 100
                        else:
                            WRate = SummonerStats['wins']

                        WRate = float(WRate)
                        WinRate1 += [WRate]

                        bar[j] = '███████.'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Summoner's WinRate collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Summoner's WinRate collected")

                        Games = SummonerStats['wins'] + SummonerStats['losses']
                        games1 += [Games]

                        bar[j] = '████████'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM I][J"+str(i)+"] Summoner's Games collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM I][J"+str(i)+"] Summoner's Games collected")

                        await asyncio.sleep(2)

                    TeamI = {'Rank':ranks1, 'Champ':champs1, 'Name':summonersNames1, 'WRate':WinRate1, 'Games':games1}

                    await self.bot.edit_message(tmp, "[GAME][TEAM I] Team I Complete" + chargingBar)
                    print("[FTS][GAME][TEAM I] Team I Complete")
                    print(TeamI)

                    MsgBase = "```css\n"
                    msg1 = MsgBase

                    for x in range(5):
                        MsgRank = TeamI['Rank']
                        MsgChamp = TeamI['Champ']
                        MsgName = TeamI['Name']
                        MsgWRate = TeamI['WRate']
                        MsgGames = TeamI['Games']

                        msg1 += "{0:13}{1:15}{2:17}W/L: {3:>5.1f} % {4:4} games\n".format(MsgRank[x], MsgChamp[x], MsgName[x], MsgWRate[x], MsgGames[x])

                        await asyncio.sleep(1)

                    MsgT1 = "Team 1 :\n" + msg1 + "```"

                    i = 0

                    for x in Team2:

                        i += 1
                        j = i + 4

                        SummonerName = x['summonerName']
                        SummonerID = x['summonerId']

                        bar[j] = '█.......'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Variables définies\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Variables définies")

                        Rank = lol.getRank(SummonerID)
                        ranks2 += [Rank]

                        bar[j] = '██......'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Rank collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Rank collected")

                        ChampID = x['championId']
                        Champ = lol.getChampionName(ChampID)
                        champs2 += [Champ]

                        bar[j] = '███.....'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Champion collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Champion collected")

                        summonersNames2 += [SummonerName]

                        bar[j] = '████....'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Summoner's name collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Summoner's name collected")

                        SummonerName2 = SummonerName.replace(" ", "")
                        player = lol.getSummonerInfo(SummonerName2)
                        playerID = player['id']

                        bar[j] = '█████...'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Summoner's ID collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Summoner's ID collected")

                        SummonerStatsII = lol.getRankedStats(playerID)

                        bar[j] = '██████..'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Summoner's Stats collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Summoner's Stats collected")

                        if SummonerStatsII['losses'] != 0:
                            WRate = SummonerStatsII['wins'] / SummonerStatsII['losses'] * 100
                        else:
                            WRate = SummonerStatsII['wins']

                        WRate = float(WRate)
                        WinRate2 += [WRate]

                        bar[j] = '███████.'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Summoner's WinRate collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Summoner's WinRate collected")

                        Games = SummonerStatsII['wins'] + SummonerStatsII['losses']
                        games2 += [Games]

                        bar[j] = '████████'
                        chargingBar = '```\n[' + bar[0] + bar[1] + bar[2] + bar[3] + bar[4] + bar[5] + bar[6] + bar[7] + bar[8] + bar[9] + ']\n```'
                        await self.bot.edit_message(tmp, "[GAME][TEAM II][J" + str(i) + "] Summoner's Games collected\n" + chargingBar)
                        print("[FTS][GAME][TEAM II][J" + str(i) + "] Summoner's Games collected")

                        await asyncio.sleep(2)

                    TeamII = {'Rank':ranks2, 'Champ':champs2, 'Name':summonersNames2, 'WRate':WinRate2, 'Games':games2}

                    msg2 = MsgBase

                    for x in range(5):
                        Msg2Rank = TeamII['Rank']
                        Msg2Champ = TeamII['Champ']
                        Msg2Name = TeamII['Name']
                        Msg2WRate = TeamII['WRate']
                        Msg2Games = TeamII['Games']

                        msg2 += "{0:13}{1:15}{2:17}W/L: {3:>5.1f} % {4:4} games\n".format(Msg2Rank[x], Msg2Champ[x], Msg2Name[x], Msg2WRate[x], Msg2Games[x])

                        await asyncio.sleep(1)

                    MsgT2 = "Team 2 :\n" + msg2 + "```"

                    MSG = MsgT1 + "\n" + MsgT2

                    await self.bot.delete_message(tmp)
                    await self.bot.say(MSG)
            except LoLException as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n\n{}\n```'
                await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e, type(e).__traceback__))
                traceback.print_tb(e.__traceback__)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            traceback.print_tb(e.__traceback__)

class Vote:
    """Commandes de Vote"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}
        self.VoteMess = None
        self.Requester = None
        self.VoteTitle = None
        self.Voters = None

    @commands.command(pass_context=True, no_pm=True)
    async def votestart(self, ctx, *, subject : str):
        """Démarrer un vote"""

        try:
            await self.bot.delete_message(ctx.message)

            VoteEmbed = discord.Embed()
            VoteEmbed.title = "Vote : " + subject
            VoteEmbed.colour = 0x3498db
            VoteEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            self.VoteTitle = subject
            self.Requester = ctx.message.author
            self.VoteMess = {'oui': 0,'non': 0}
            self.Voters = {}

            await self.bot.say(embed=VoteEmbed)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def vote(self, ctx, *, answer:str='oui'):
        """Répondre à un vote par oui ou non"""

        answer = str(answer)
        answer = answer.lower()

        try:
            if self.VoteMess != None:
                if answer == 'oui':

                    if ctx.message.author.name in self.Voters.keys():
                        await self.bot.delete_message(ctx.message)
                        tmp = await self.bot.say('```\nVous avez déjà voté\n```')
                        await asyncio.sleep(5)
                        await self.bot.delete_message(tmp)
                    else:
                        oui = self.VoteMess['oui']
                        oui = int(oui) + 1
                        self.VoteMess['oui'] = oui

                        filler = {ctx.message.author.name:"Oui"}
                        self.Voters.update(filler)

                        await self.bot.delete_message(ctx.message)
                        tmp = await self.bot.say("{0} Votre vote a bien été pris en compte".format(ctx.message.author.mention))
                        await asyncio.sleep(5)
                        await self.bot.delete_message(tmp)

                elif answer == 'non':

                    if ctx.message.author.name in self.Voters.keys():
                        await self.bot.delete_message(ctx.message)
                        tmp = await self.bot.say('```\nVous avez déjà voté\n```')
                        await asyncio.sleep(5)
                        await self.bot.delete_message(tmp)
                    else:
                        non = self.VoteMess['non']
                        non = int(non) + 1
                        self.VoteMess['non'] = non
                        
                        filler = {ctx.message.author.name:"Non"}
                        self.Voters.update(filler)

                        await self.bot.delete_message(ctx.message)
                        tmp = await self.bot.say("{0} Votre vote a bien été pris en compte".format(ctx.message.author.mention))
                        await asyncio.sleep(5)
                        await self.bot.delete_message(tmp)

                else:
                    raise TypeError("Seulement oui ou non attendus")
            else:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```\nAucun vote n'est en cours\n```")

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.delete_message(ctx.message)
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=True)
    async def votestatus(self, ctx):
        """Donne le statut du vote en cours"""
        try:
            if self.VoteMess != None:
                await self.bot.delete_message(ctx.message)
                VoteEmbed = discord.Embed()
                VoteEmbed.title = "Vote : " + self.VoteTitle
                VoteEmbed.colour = 0x3498db
                VoteEmbed.description = "{} personne(s) ont voté :".format(len(self.Voters))
                VoteEmbed.add_field(name = 'Oui', value = str(self.VoteMess['oui']))
                VoteEmbed.add_field(name = 'Non', value = str(self.VoteMess['non']))
                VoteEmbed.set_footer(text = "Requested by {0}".format(self.Requester.name), icon_url = self.Requester.avatar_url)
                await self.bot.say(embed=VoteEmbed)
            else:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```\nAucun vote n'est en cours\n```")

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def votestop(self, ctx):
        """Arrête le vote"""
        try:
            if self.VoteMess != None:
                if ctx.message.author == self.Requester:
                    await self.bot.delete_message(ctx.message)
                    VoteEmbed = discord.Embed()
                    VoteEmbed.title = "Résultats du Vote : " + self.VoteTitle
                    VoteEmbed.colour = 0x3498db
                    VoteEmbed.description = "{} personne(s) ont voté :".format(len(self.Voters))
                    VoteEmbed.add_field(name = 'Oui', value = str(self.VoteMess['oui']))
                    VoteEmbed.add_field(name = 'Non', value = str(self.VoteMess['non']))
                    VoteEmbed.set_footer(text = "Requested by {0}".format(self.Requester.name), icon_url = self.Requester.avatar_url)
                    await self.bot.say('```\nVOTE TERMINÉ !\n```', embed=VoteEmbed)
                    self.VoteMess = None
                    self.VoteTitle = None
                    self.Requester = None
                else:
                    await self.bot.delete_message(ctx.message)
                    await self.bot.say("```\nVous n'êtes pas le requêteur du vote\n```")
            else:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```\nAucun vote n'est en cours\n```")

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def voters(self, ctx):
        """Liste des votants et leur vote

        Admins uniquement"""
        
        member = ctx.message.author
        await self.bot.delete_message(ctx.message)
        
        fmt = "```\n+-------------------------+----------+" + "\n|{0:25}|{1:10}|".format("Voter", "Vote") + "\n+-------------------------+----------+"
        
        if self.Voters != None:
            if member.server_permissions.administrator == True:
                for voter, vote in self.Voters.items():
                    fmt += "\n|{0:25}|{1:10}|".format(voter, vote)
                fmt += "\n+-------------------------+----------+\n```"
                await self.bot.say(fmt)
            else:
                await self.bot.say("```\nVous n'êtes pas administrateur-e\n```")
        else:
            await self.bot.say("```\nAucun vote n'a eu lieu\n```")

class Jeux:
    """Jeux proposés par le bot FtS"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=False)
    async def ZCasino(self, ctx, mise, nb):
        """Bienvenue au ZCasino !

        Misez une somme sur un nombre, si c'est le bon nombre vous récupérez
        trois fois votre mise, si le nombre est de la même couleur vous
        récupérez la moitié de votre mise ! Bonne chance !"""

        await self.bot.delete_message(ctx.message)

        try:
            mise = int(mise)
            nb = int(nb)
        except TypeError:
            await self.bot.say("Seuls des chiffres sont attendus")

        await self.bot.say("Bienvenue au ZCasino {2.message.author.mention} ! Vous avez misé {0}$ sur le {1} !".format(mise, nb, ctx))
        print('[FTS] - ZCASINO - Welcome to the ZCasino, @{2.message.author.name} ! You have mised {0}$ on the {1} !'.format(mise, nb, ctx))

        result = random.randrange(50)
        result = str(result)
        await self.bot.say("Le résultat est... " + result)
        print('[FTS] - ZCASINO - And the result is... ' + result)
        result = int(result)

        #Pair
        if nb % 2 == 0:
            nbpair = 1
        else:
            nbpair = 0

        if result % 2 == 0:
            pair = 1
        else:
            pair = 0

        #Comparer les résultats
        if result == nb: #On compare les chiffres
            win = mise * 3
            await self.bot.say("Vous avez gagné ! Vous récupérez " + str(win) + "$.")
            print('[FTS] - ZCASINO - You won !')
        elif nbpair == pair: #On compare les "couleurs"
            win2 = mise / 2
            win2 = math.ceil(win2)
            await self.bot.say("La couleur des nombres correspond, vous récupérez " + str(win2) + "$.")
            print('[FTS] - ZCASINO - The colors responds !')
        else: #On perd
            await self.bot.say("Vous avez perdu, vous pouvez recommencer ! ;)")
            print('[FTS] - ZCASINO - You have loose !')

class Admin:
    """Commandes d'administration et de gestion"""

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=True)
    async def setgame(self, ctx, *, game : str):
        """Définit le jeu du bot"""

        member = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if member.server_permissions.administrator == True:
            await self.bot.change_presence(game=discord.Game(name=game))
            print('[FTS] Game changed to', game)
        else:
            await self.bot.say("Vous n'êtes pas administrateur")
            print('[FTS] SetGame : Command aborted : User is not an administrator')

    @commands.command(pass_context=True, no_pm=True)
    async def perms(self, ctx, *, user=None):
        """Donne les permissions du joueur choisi"""

        if user == None:
            member = ctx.message.author
        else:
            user = str(user)
            member = ctx.message.server.get_member_named(user)

        if member == None:
            await self.bot.say("{1} L'utilisateur {0} est inconnu".format(user, ctx.message.author.mention))
        else:
            tmp = await self.bot.say("Récupération des permissions...")

            perms = [
                get_perm_admin(member),
                get_perm_create_instant_invite(member),
                get_perm_kick_members(member),
                get_perm_ban_members(member),
                get_perm_manage_channels(member),
                get_perm_manage_server(member),
                get_perm_add_reactions(member),
                get_perm_send_tts_messages(member),
                get_perm_manage_messages(member),
                get_perm_mute(member),
                get_perm_deafen(member),
                get_perm_send_embed_links(member),
                get_perm_attach_files(member),
                get_perm_mention_everyone(member),
                get_perm_external_emojis(member),
                get_perm_change_nickname(member),
                get_perm_manage_nicknames(member),
                get_perm_manage_roles(member),
                get_perm_manage_webhooks(member),
                get_perm_manage_emojis(member),
                get_perm_view_audit_logs(member)
            ]

            titles = [
                "Permissions administrateur",
                "Créer invitations",
                "Éjecter les membres",
                "Bannir les membres",
                "Gérer les channels",
                "Gérer le serveur",
                "Ajouter des réactions",
                "Envoyer des messages tts",
                "Gérer les messages",
                "Rendre muet",
                "Rendre sourd",
                "Envoyer des messages Embed",
                "Envoyer des pièces jointes",
                "Mentionner @everyone",
                "Utiliser des emojis externes au serveur",
                "Changer son pseudo",
                "Gérer les pseudos",
                "Gérer les roles",
                "Gérer les WebHooks",
                "Gérer les Emojis",
                "Voir les logs"
            ]

            MsgBase = ctx.message.author.mention + " Voici les permissions de " + member.mention + " : ```scheme\n"
            Msg = MsgBase

            for perm, title in zip(perms, titles):
                fmt = "[>] {0:45} {1:12}\n".format(title, perm)
                Msg += fmt

            Msg += "```"

            await self.bot.delete_message(ctx.message)
            await self.bot.delete_message(tmp)
            await self.bot.say(Msg)

            print('[FTS] Permissions message sent')

    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, *, user=None):
        """Donne les informations concernant le joueur cité"""

        if user == None:
            member = ctx.message.author
        else:
            user = str(user)
            member = ctx.message.server.get_member_named(user)

        if member == None:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("{1} L'utilisateur {0} est inconnu".format(user, ctx.message.author.mention))
        else:
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say("Chargement des informations...")

            try:
                RolesList = get_user_roles(member)
                createdAt = dateConverter(member.created_at)
                joinedAt = dateConverter(member.joined_at)
                Statut = str(member.status)
                StatutFinal = Statut.capitalize()

                UserEmbed = discord.Embed()
                UserEmbed.title = "Userinfo for {0}#{1} [{2}]:".format(member.name, member.discriminator, member.top_role)
                UserEmbed.colour = 0x3498db
                UserEmbed.set_thumbnail(url=member.avatar_url)
                UserEmbed.add_field(name = "Surnom", value = member.nick)
                UserEmbed.add_field(name = "ID", value = member.id)
                UserEmbed.add_field(name = "Discriminateur", value = member.discriminator)
                UserEmbed.add_field(name = 'Statut', value = StatutFinal)
                UserEmbed.add_field(name = 'Joue à', value = member.game)
                UserEmbed.add_field(name = 'Compte créé le', value = createdAt)
                UserEmbed.add_field(name = 'A rejoint le serveur le', value = joinedAt)
                UserEmbed.add_field(name = "Roles", value = RolesList)
                UserEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

                await self.bot.delete_message(tmp)
                await self.bot.say(embed=UserEmbed)

            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=True)
    async def serverinfo(self, ctx):
        """Donne les informations du serveur"""

        server = ctx.message.server
        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say('Processing request...')
        VerifLevel = str(server.verification_level)

        ServerEmbed = discord.Embed()
        ServerEmbed.colour = 0x3498db
        ServerEmbed.set_thumbnail(url=server.icon_url)
        ServerEmbed.add_field(name = "Server Name", value = server.name)
        ServerEmbed.add_field(name = "Server ID", value = server.id)
        ServerEmbed.add_field(name = "Owner's Name", value = server.owner.name)
        ServerEmbed.add_field(name = "Owner's ID", value = server.owner.id)
        ServerEmbed.add_field(name = "Text Channels", value = str(len(getTextChannels(server))))
        ServerEmbed.add_field(name = "Voice Channels", value = str(len(getVoiceChannels(server))))
        ServerEmbed.add_field(name = "Users", value = server.member_count)
        ServerEmbed.add_field(name = "Verification level", value = VerifLevel.upper())
        ServerEmbed.add_field(name = "Roles Count", value = str(len(server.role_hierarchy)))
        ServerEmbed.add_field(name = "Region", value = formatServerRegion(server.region))
        ServerEmbed.add_field(name = "Creation Date", value = dateConverter(server.created_at))
        ServerEmbed.add_field(name = "Emotes Count", value = str(len(server.emojis)))
        ServerEmbed.add_field(name = "Roles", value = formatServerRoles(server.role_hierarchy), inline=False)
        ServerEmbed.add_field(name = "Emojis", value = formatEmojis(server.emojis), inline = False)
        ServerEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

        await self.bot.delete_message(tmp)
        await self.bot.say(embed=ServerEmbed)

    @commands.command(pass_context=True, no_pm=True)
    async def convoque(self, ctx, user=None, *, reason):
        """Envoie une convocation au joueur cité

        Nécessite le droit de ban"""

        author = ctx.message.author
        if author.server_permissions.ban_members == True:
            if user == None:
                member = ctx.message.author
            else:
                user = str(user)
                member = ctx.message.server.get_member_named(user)

            if member == None:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("{1} L'utilisateur {0} est inconnu".format(user, ctx.message.author.mention))
            else:
                await self.bot.delete_message(ctx.message)
                tmp = await self.bot.say("Processing...")

                ConvocEmbed = discord.Embed()
                ConvocEmbed.title = "Convocation"
                ConvocEmbed.colour = 0x3498db
                ConvocEmbed.set_thumbnail(url=member.avatar_url)
                ConvocEmbed.description = "Vous avez été convoqué par l'administration du serveur **{0}** pour la raison qui suit.\n\
Vous êtes prié de vous rendre sur le serveur dans les plus brefs délais et de vous mettre en contact avec un des administrateurs ou des modérateurs".format(ctx.message.server.name)
                ConvocEmbed.add_field(name = 'Raison', value = reason)
                ConvocEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

                server = ctx.message.server
                Channels = server.channels
                End = []

                Return = False

                for chan in list(Channels):
                    Name = str(chan.name)
                    Type = str(chan.type)
                    if "moderation" in str(chan.name):
                        if Type is "text":
                            ModChan = chan
                            Return = True

                if Return is not True:
                    ModChan = await self.bot.create_channel(server, 'moderation', type=discord.ChannelType.text)

                await self.bot.delete_message(tmp)
                await self.bot.send_message(member, embed=ConvocEmbed)
                await self.bot.send_message(ModChan, "@here Une convocation a été envoyée à {0} par {1}, raison : {2}".format(member.mention, ctx.message.author.mention, reason))

        else:
            await self.bot.say("```\nVous n'avez pas la permission de convoquer un utilisateur\n```")

    @commands.command(pass_context=True, no_pm=False)
    async def rules(self, ctx, line="all", *, user:discord.Member=None):
        """Envoie le règlement du serveur à un joueur
        Si aucun joueur n'est spécifié, le règlement est envoyé dans le chat. 
        On peut spécifier une ligne précise du règlement."""
        try:
            rules = getServerRules()
            rulesLines = getSplittedRules()
            line = line.lower()

            await self.bot.delete_message(ctx.message)

            try:
                line = int(line)
                line -= 1
            except ValueError as e:
                if line == "all":
                    pass
                else:
                    raise ValueError("Seuls soit un entier soit la mention all (insensible à la casse) est attendue.")

            if user == None:
                user = ctx.message.channel

            if ctx.message.author.server_permissions.manage_messages == True:
                if line == "all":
                    await self.bot.send_message(user, rules)
                else:
                    try:
                        base = "*Extrait du règlement :*"
                        if line >= 6:
                            base += "\nCe qui est interdit :"
                        msg = base + "\n```css\n" + rulesLines[line] + "\n```"
                    except IndexError as e:
                        raise IndexError("Cette règle n'existe pas")
                    await self.bot.send_message(user, msg)

                if type(user) != discord.Channel:
                    tmp = await self.bot.say("Message sent")
                    await asyncio.sleep(10)
                    await self.bot.delete_message(tmp)

        except Exception as e:
            print(e)
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=False)
    async def disconnect(self, ctx):
        """Déconnecte le bot - Bot Master uniquement"""
        requester = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if requester.id == '187565415512276993':
            await self.bot.send_message(bot.get_channel('283397577552953344'), "```Déconnection du bot```")
            print('[FTS] Déconnexion...')
            self.bot.logout()
            print('[FTS] Logged out')
            self.bot.close()
            print('[FTS] Connexions closed')
            os.system('pause')
            exit()
        else:
            await self.bot.say("Vous n'êtes pas le Bot Master")

    @commands.command(pass_context=True, no_pm=False)
    async def test(self, ctx):
        """Teste le bot [10 secondes]"""
        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say("Test en cours :\n```\n|..........|\n```")
        i = 0
        bar = ""
        pt = ".........."
        while i < 10:
            i += 1
            bar += "█"
            pt = pt[:-1]
            await self.bot.edit_message(tmp, "Test en cours :\n```\n|"+ bar + pt +"|\n```")
            await asyncio.sleep(1)
        await self.bot.edit_message(tmp, "```Test terminé```")
        await asyncio.sleep(5)
        await self.bot.delete_message(tmp)

    @commands.command(pass_context=True, no_pm=True)
    async def randomplayer(self, ctx):
        """Retourne un membre du serveur au hasard"""
        await self.bot.delete_message(ctx.message)
        server = ctx.message.server
        members = getServerMembers(server)

        length = len(members) - 1
        rand = random.randint(0, length)

        member = members[rand]

        MbrEmbed = discord.Embed()
        MbrEmbed.colour = 0x3498db
        MbrEmbed.title = "Random Player :"
        MbrEmbed.description = member
        MbrEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)
        await self.bot.say(embed=MbrEmbed)

class Messages:
    """Commandes Textuelles"""

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=False)
    async def hi(self, ctx):
        """Fall to Sky vous salue"""
        await self.bot.say("Salut {0.message.author.mention} !".format(ctx))
        print('[FTS] Hello Message sent')

    @commands.command(pass_context=True, no_pm=False)
    async def ip(self, ctx):
        """Envoie l'IP du serveur Minecraft"""
        await self.bot.say("{0.message.author.mention} IP du serveur Minecraft : {1}".format(ctx, getServerIP()))
        print('[FTS] IP sent')

    @commands.command(pass_context=True, no_pm=False)
    async def website(self, ctx):
        """Affiche le site web du serveur"""
        await self.bot.say("{0.message.author.mention} Site web du serveur : {1}".format(ctx, getWebSite()))
        print("[FTS] Website's URL sent")

    @commands.command(pass_context=True, no_pm=False)
    async def meme(self, ctx):
        """Affiche une meme random parmi la bibliothèque"""
        print('[FTS] Sending Meme...')
        mem = random.choice(freshestMemes)
        await self.bot.send_file(ctx.message.channel, mem)
        print('[FTS] Meme Sent')

    @commands.command(pass_context=True, no_pm=False)
    async def echo(self, ctx, *, mess : str):
        """Répète le message de l'utilisateur"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say(mess)
        print('[FTS] Message sent :', mess)

    @commands.command(pass_context=True, no_pm=True)
    async def mpecho(self, ctx, user:discord.Member, *, mess : str):
        """Envoie un MP via le bot"""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(user, mess)
        print('[FTS] Message sent to {0.name} : {1}'.format(user, mess))

    @commands.command(pass_context=True, no_pm=True)
    async def report(self, ctx, user: discord.Member, *, reason: str):
        """Reporte un utilisateur au staff"""
        
        await self.bot.delete_message(ctx.message)

        server = ctx.message.server
        Channels = server.channels
        End = []

        Return = False

        for chan in list(Channels):
            Name = str(chan.name)
            Type = str(chan.type)
            if "moderation" in str(chan.name):
                if Type is "text":
                    ModChan = chan
                    Return = True

        if Return is not True:
            ModChan = await self.bot.create_channel(server, 'moderation', type=discord.ChannelType.text)

        await self.bot.send_message(ModChan, "{0} a été report par {1}, raison : {2}, @here".format(user.mention, ctx.message.author.mention, reason))
        print('[FTS] {0} has been reported by {1}'.format(user, ctx.message.author))

    @commands.command(pass_context=True, no_pm=False)
    async def bug(self, ctx, *, subject:str):
        """Rapporte un bug du bot à l'équipe de dev"""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(bot.get_channel('307799958965190656'), "Un bug a été report par {0}, sujet : {1}, @here".format(ctx.message.author.mention, subject))

    @commands.command(pass_context=True, no_pm=False)
    async def roll(self, ctx, start: int=0, end: int=10):
        """Donne un nombre aléatoire entre [start] et [end]"""
        rand = random.randint(start, end)

        try:

            RollEmbed = discord.Embed()
            RollEmbed.title = 'Roll'
            RollEmbed.colour = 0x3498db
            RollEmbed.description = str(rand)

            await self.bot.say(embed=RollEmbed)

        except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))


    @commands.command(pass_context=True, no_pm=True)
    async def purge(self, ctx, limit=10):
        """Supprime le nombre de messages spécifié

        10 Messages seront supprimés par défaut

        Cette commande ne peut être utilisée que par les utilisateurs ayant la permission de gérer les messages
        """

        member = ctx.message.author
        if member.server_permissions.manage_messages == True:
            print('[FTS] Proceding purge...')

            await self.bot.purge_from(ctx.message.channel, limit = limit)

            print('[FTS] Purge done')
            print('[FTS] Deleted {0} messages'.format(limit))
        else:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("Vous n'avez pas l'autorisation de gérer les messages")
            print('[FTS] Purge : Command aborted : User do not have manage_messages permission')

    @commands.command(pass_context=True, no_pm=True)
    async def purgeuser(self, ctx, limit=10, *, user:discord.Member):
        """Supprime le nombre de messages spécifié du membre choisi

        10 Messages seront scannés par défaut

        Cette commande ne peut être utilisée que par les utilisateurs ayant la permission de gérer les messages
        """
        await self.bot.delete_message(ctx.message)

        member = ctx.message.author
        if member.server_permissions.manage_messages == True:

            def compare(m):
                return m.author == user 

            print('[FTS] Proceding purge...')

            deleted = await self.bot.purge_from(ctx.message.channel, limit = limit, check = compare)

            FeedBack = await self.bot.say("```{2} messages de {0} parmi les {1} derniers messages supprimés```".format(user.name, limit, len(deleted)))
            await asyncio.sleep(10)
            await self.bot.delete_message(FeedBack)

            print('[FTS] Purge done')
            print('[FTS] Deleted {0} messages'.format(limit))
        else:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("Vous n'avez pas l'autorisation de gérer les messages")
            print('[FTS] Purge : Command aborted : User do not have manage_messages permission')

    @commands.command(pass_context=True, no_pm=False)
    async def addme(self, ctx):
        """Envoie le lien d'ajout du bot"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say("{0.message.author.mention} Pour m'ajouter, utiliser ce lien : https://discordapp.com/oauth2/authorize?client_id=283379732538720256&scope=bot&permissions=8".format(ctx))
        print('[FTS] Add message sent')

    @commands.command(pass_context=True, no_pm=False)
    async def messcount(self, ctx, limit=1000):
        """Donne le nombre de messages envoyés dans le channel"""
        await self.bot.delete_message(ctx.message)
        counter = 0
        tmp = await self.bot.say('Calculating messages...')
        print('[FTS] Calculating...')
        async for log in bot.logs_from(ctx.message.channel, limit):
            if log.author == ctx.message.author:
                counter += 1

        await self.bot.delete_message(tmp)
        await self.bot.say('{0.message.author.mention} You have sent `{1}` messages in this channel'.format(ctx, counter))
        print('[FTS] Calculation done and sent')

    @commands.command(pass_context=True, no_pm=True)
    async def emojis(self, ctx):
        """Donne la liste des emojis du serveur"""
        
        await self.bot.delete_message(ctx.message)

        EmojiEmbed = discord.Embed()
        EmojiEmbed.colour = 0x3498db
        EmojiEmbed.title = "Emojis for {0}".format(ctx.message.server.name)
        EmojiEmbed.description = formatEmojis(ctx.message.server.emojis)

        await self.bot.say(embed = EmojiEmbed)

    @commands.command(pass_context=True, no_pm=False)
    async def ld(self, ctx, *, pseudo:str):
        """Donne les stats d'un profil leveldown"""

        await self.bot.delete_message(ctx.message)
        tmp = await self.bot.say("Processing request...")

        try: 
            ldRequest = getLDStats(pseudo)
            Names = ldRequest['Names']
            Values = ldRequest['Values']

            LDEmbed = discord.Embed()
            LDEmbed.colour = 0x3498db
            LDEmbed.set_author(name = "LevelDown Stats for {0}".format(pseudo), icon_url = 'http://leveldown.fr/dist/images/webtv.png')
            LDEmbed.set_thumbnail(url=getLDIcon(pseudo))
            LDEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            for Name, Value in zip(Names, Values):
                LDEmbed.add_field(name = Name, value = Value)

            await self.bot.delete_message(tmp)
            await self.bot.say(embed=LDEmbed)

        except UnboundLocalError:
            await self.bot.delete_message(tmp)
            await self.bot.say("```css\nServer temporairement indisponible, l'opération ne peut être achevée\n```")

        except Exception as e:
            await self.bot.delete_message(tmp)
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

class Music:
    """Commandes Vocales"""
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Rejoindre un channel vocal"""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

        print('[FTS] Successfull joined {0} voice channel'.format(channel.name))

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Rejoint le channel vocal de l'émetteur"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
            print('[FTS] Successfull Summoned')
        else:
            await state.voice.move_to(summoned_channel)

        return True


    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Lance une musique

        Rejoint la fin de la queue

        Cette commande cherche la musique sur YouTube en priorité
        Liste des sites supportés disponible ici :
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

        print('[FTS] Playing ' + str(entry))

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Changer le volume de la musique en cours"""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

        print('[FTS] Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Met la musique en pause"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

        print('[FTS] Music Paused')

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Reprend la musique"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

        print('[FTS] Music Resumed')

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Coupe la musique en cours et quitte le channel vocal

        Clear également la queue
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

        print('[FTS] Music Stopped')

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote pour passer la musique. 
        La personne qui a demandé la musique peut la passer sans vote.

        3 votes sont nécessaires pour que la musique soit passée
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
            print('[FTS] Music skipped by Requester')

        elif voter.server_permissions.administrator == True:
            await self.bot.say('Admin requested skipping song...')
            state.skip()
            print('[FTS] Music skipped by Admin')

        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
                print('[FTS] Music skipped by vote')
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Montre quelle musique est jouée actuellement"""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))
            print('[FTS] Now playing {} [skips: {}/3]'.format(state.current, skip_count))

class Moderation:
    """Moderation related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = moderation.start()

    def getModChan(self, server):
        Channels = server.channels
        End = []
        Return = False
        for chan in list(Channels):
            Name = str(chan.name)
            Type = str(chan.type)
            if "moderation" in str(chan.name):
                if Type is "text":
                    ModChan = chan
                    Return = True
        if Return is not True:
            ModChan = self.bot.create_channel(server, 'moderation', type=discord.ChannelType.text)
        return ModChan

    @commands.command(pass_context=True, no_pm=True)
    async def warn(self, ctx, user:discord.Member):
        """Avertit un utilisateur
        Utilisable uniquement par la modération (permissions de ban et au-dessus)"""
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.server_permissions.ban_members == True:
            server = ctx.message.server
            ModChan = self.getModChan(server)
            self.data = moderation.warn(server, user, self.data)
            try:
                level = self.data[server.name][user.name]
            except KeyError:
                level = 1
            if level < 3:
                fmt = discord.Embed()
                fmt.title = ("ATTENTION")
                fmt.colour = 0x3498db
                fmt.set_thumbnail(url=server.icon_url)
                fmt.description = "Vous avez été averti-e par un-e modérateur-trice du serveur **{0}** en raison de votre comportement.\n\
Vous avez actuellement {1} avertissement(s) à votre actif. Au bout de trois, une motion de convocation disciplinaire sera lancée et vous serez lourdement sanctionné-e par l'administration de notre serveur.\n\
Merci de prendre garde à votre comportement à l'avenir.".format(server.name, str(level))
                await self.bot.send_message(user, embed=fmt)
                msg = "@here {0.name} a atteint {1} avertissement(s).".format(user, str(level))
                await self.bot.send_message(ModChan, msg)
            elif level == 3:
                fmt = discord.Embed()
                fmt.title = ("ATTENTION")
                fmt.colour = 0x3498db
                fmt.set_thumbnail(url=server.icon_url)
                fmt.description = "Vous avez été averti-e par un-e modérateur-trice du serveur **{0}** en raison de votre comportement.\n\
Vous avez actuellement {1} avertissement(s) à votre actif. Au bout de trois, une motion de convocation disciplinaire sera lancée et vous serez lourdement sanctionné-e par l'administration de notre serveur.\n\
Merci de prendre garde à votre comportement à l'avenir.".format(server.name, str(level))
                await self.bot.send_message(user, embed=fmt)
                msg = "@here {0.name} a atteint 3 avertissements. Merci de prendre les mesures nécessaires.".format(user)
                await self.bot.send_message(ModChan, msg)
            else:
                msg = "@here {0.name} a atteint {1} avertissements. Il ou elle a dépassé la limite. Merci de prendre les mesures nécessaires.".format(user, str(level))
                await self.bot.send_message(ModChan, msg)
        else:
            await self.bot.say("```\nVous n'avez pas la permission d'avertir un utilisateur\n```")


    @commands.command(pass_context=True, no_pm=True)
    async def pardon(self, ctx, user:discord.Member):
        """Pardonne un utilisateur (lui retire un avertissement)
        Utilisable uniquement par la modération (permissions de ban et au-dessus)"""
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.server_permissions.ban_members == True:
            server = ctx.message.server
            ModChan = self.getModChan(server)
            if server.name in self.data.keys():
                if user.name in self.data[server.name].keys():
                    level = self.data[server.name][user.name]
                    if level <= 1:
                        del self.data[server.name][user.name]
                        msg = "Un-e modérateur-trice a retiré votre seul avertissement. Vous n'avez plus aucun antécédent."
                        fmt = "@here {0.mention} a pardonné à {1.mention}. Il n'a plus aucun antécédent.".format(ctx.message.author, user)
                    else:
                        self.data[server.name][user.name] -= 1
                        level = self.data[server.name][user.name]
                        msg = "Un-e modérateur-trice vous a retiré un avertissement. Il vous reste {0} avertissement(s).".format(str(level))
                        fmt = "@here {0.mention} a pardonné à {1.mention}. Il n'a plus que {2} avertissements.".format(ctx.message.author, user, str(level))
                    await self.bot.send_message(user, msg)
                    await self.bot.send_message(ModChan, fmt)
                    f = open(fileName, "wb")
                    p = pickle.Pickler(f)
                    p.dump(self.data)
                    f.close()
                else:
                    await self.bot.say("```\nL'utilisateur n'a aucun antécédent\n```")
            else:
                await self.bot.say("```\nL'utilisateur n'a aucun antécédent\n```")
        else:
            await self.bot.say("```\nVous n'avez pas la permission de pardonner un utilisateur\n```")

    @commands.command(pass_context=True, no_pm=True)
    async def checkwarn(self, ctx, user:discord.Member):
        """Montre le nombre d'avertissements d'un utilisateur"""
        await self.bot.delete_message(ctx.message)
        server = ctx.message.server
        level = moderation.getWarns(server, user, self.data)
        fmt = discord.Embed()
        fmt.colour = 0x3498db
        fmt.set_author(name = user.name, icon_url=user.avatar_url)
        fmt.description = "{0} avertissements".format(str(level))
        await self.bot.say(embed=fmt)

    @commands.command(pass_context=True, no_pm=True)
    async def mute(self, ctx, *, user:discord.Member):
        """Mute un utilisateur
        Requiert la permission de kick"""

        await self.bot.delete_message(ctx.message)

        if ctx.message.author.server_permissions.kick_members == True:

            overwrite = ctx.message.channel.overwrites_for(user) or discord.PermissionOverwrite()
            overwrite.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrite)
            tmp = await self.bot.send_message(ctx.message.channel, "{} is now muted here !".format(user.mention))
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

        else:
            tmp = await self.bot.say("```\nVous n'avez pas la permission d'utiliser cette commande\n```")
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

    @commands.command(pass_context=True, no_pm=True)
    async def unmute(self, ctx, *, user:discord.Member):

        await self.bot.delete_message(ctx.message)

        if ctx.message.author.server_permissions.kick_members == True:

            overwrite = ctx.message.channel.overwrites_for(user) or discord.PermissionOverwrite()
            overwrite.send_messages = True
            await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrite)
            tmp = await self.bot.send_message(ctx.message.channel, "{} is no longer muted here! He/she can speak now!".format(user.mention))
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

        else:
            tmp = await self.bot.say("```\nVous n'avez pas la permission d'utiliser cette commande\n```")
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

class RSS:

    def __init__(self, bot):
        self.bot = bot
        self.channel = channel = discord.Object(id='189472786056478720')
        self.feed = youtube.start()

    @commands.command(pass_context=True, no_pm=True)    
    async def forceupdate(self, ctx):
        """[ADMIN] Teste le système d'update de flux RSS"""
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.server_permissions.administrator == True:
            update = youtube.update(self.feed)
            if update != "304":
                entry = youtube.getLastEntry()
                YTEmbed = discord.Embed()
                YTEmbed.colour = 0x3498db
                YTEmbed.title = "Nouvelle vidéo sur la chaîne de Sakiut ! `" + entry['title'] + "`"
                YTEmbed.description = "Vidéo : " + entry['link'] + "\nChaîne : " + entry['channel'] + "\nPosté le : " + entry['published']
                YTEmbed.set_thumbnail(url = entry['thumbnail'])
                YTEmbed.set_footer(text = "Posté par {0}".format(entry['author']))
                await self.bot.send_message(self.channel, "@everyone", embed = YTEmbed)
            else:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```Update failed```")
        else:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("```Vous n'avez pas la permission d'utiliser cette commande```")

    @commands.command(pass_context=True, no_pm=True)
    async def updatelastentry(self, ctx):
        """[ADMIN] Force la dernière entrée RSS"""
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.server_permissions.administrator == True:
            entry = youtube.getLastEntry()
            YTEmbed = discord.Embed()
            YTEmbed.colour = 0x3498db
            YTEmbed.title = "Nouvelle vidéo sur la chaîne de Sakiut ! `" + entry['title'] + "`"
            YTEmbed.description = "Vidéo : " + entry['link'] + "\nChaîne : " + entry['channel'] + "\nPosté le : " + entry['published']
            YTEmbed.set_thumbnail(url = entry['thumbnail'])
            YTEmbed.set_footer(text = "Posté par {0}".format(entry['author']))
            await self.bot.send_message(self.channel, "@everyone", embed = YTEmbed)
        else:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("```Vous n'avez pas la permission d'utiliser cette commande```")

bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description="Commandes Bot Fall to Sky")
bot.add_cog(Messages(bot))
bot.add_cog(Music(bot))
bot.add_cog(Admin(bot))
bot.add_cog(Vote(bot))
bot.add_cog(Jeux(bot))
bot.add_cog(LeagueOfLegends(bot))
bot.add_cog(Anime(bot))
bot.add_cog(RSS(bot))
bot.add_cog(Moderation(bot))

#YT RSS
async def my_background_task():
    client = discord.Client()
    await client.wait_until_ready()
    channel = discord.Object(id='189472786056478720')
    feed = youtube.start()
    while not client.is_closed:
        update = youtube.update(feed)
        if update != "304":
            entry = youtube.getLastEntry()
            YTEmbed = discord.Embed()
            YTEmbed.colour = 0x3498db
            YTEmbed.title = "Nouvelle vidéo sur la chaîne de Sakiut ! `" + entry['title'] + "`"
            YTEmbed.description = "Vidéo : " + entry['link'] + "\nChaîne : " + entry['channel'] + "\nPosté le : " + entry['published']
            YTEmbed.set_thumbnail(url = entry['thumbnail'])
            YTEmbed.set_footer(text = "Posté par {0}".format(entry['author']))
            await client.send_message(channel, "@everyone", embed = YTEmbed)
        feed = youtube.start()
        await asyncio.sleep(300)

@bot.event
async def on_member_join(member):
    server = member.server
    fmt = 'Bienvenue à {0.mention} sur {1.name} !'
    await bot.send_message(server, fmt.format(member, server))
    rules = getServerRules()
    await bot.send_message(member, rules)
    print('[FTS] {0.name} has joined the server'.format(member))

@bot.event
async def on_member_remove(member):
    server = member.server
    fmt = '{0.mention} est parti-e du serveur {1.name} !'
    await bot.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has left the server'.format(member))

@bot.event
async def on_member_ban(member):
    server = member.server
    fmt = '{0.mention} a été banni-e du serveur {1.name} !'
    await bot.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has been banned of the server'.format(member))

@bot.event
async def on_member_unban(server, member):
    fmt = "{0.mention} a été pardonné-e, il-elle n'est plus banni-e du serveur {1.name} !"
    await bot.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has been unbanned of the server'.format(member))

@bot.event
async def on_server_emojis_update(before, after):
    before = set(before)
    after = set(after)

    n_e = after - before
    n_e = list(n_e)

    for e in n_e:
        Emoji = "<:{0}:{1}>".format(e.name, e.id)
        Embed = discord.Embed()
        Embed.colour = 0x3498db
        Embed.description = Emoji
        await bot.send_message(e.server, "Nouvel emoji !", embed = Embed)

@bot.event
async def on_ready():
    print('--------------------------')
    print('[FTS] Logged in as')
    print('[FTS]', bot.user.name)
    print('[FTS]', bot.user.id)
    print('--------------------------')
    await bot.change_presence(game=discord.Game(name='sakiut.fr | .help'))

token = getToken()
bot.run(token)
