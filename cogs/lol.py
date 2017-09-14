# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands

from libraries.library import *
from libraries import lol

import traceback
import urllib

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