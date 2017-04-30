# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands
from discord.perms import *
from discord import lol
from discord.lol import msToHourConverter

import random
import os
import math

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

print('[FTS] Connecting...')

freshestMemes = ["mem/meme1.jpeg", "mem/meme2.jpeg", "mem/meme3.jpeg", "mem/meme6.jpeg", "mem/meme7.jpeg", "mem/meme8.jpeg", "mem/meme9.jpeg", "mem/meme10.jpeg", "mem/meme11.jpeg", "mem/meme12.jpeg", "mem/meme14.jpeg","mem/meme15.jpeg"]
emojis = ["<:fts:287890580627914752>", "<:_3:288319958008463360>", "<:fts_white:287890229707276288>", '<:like:297409746833637377>', '<:dislike:297410671258107904>']

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
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

class LeagueOfLegends:
    """Commandes reliées à League of Legends"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=True)
    async def summoner(self, ctx, *, user:str):
        """Récupère les informations d'un invocateur"""
        try:
            tmp = await self.bot.say("Processing request...")
            await self.bot.delete_message(ctx.message)

            try:
                summoner = lol.getSummonerInfo(user)
                SummonerWins = lol.getUnrankedWins(summoner['id'])
                SummonerRank = lol.getRank(summoner['id'])

                SummonerEmbed = discord.Embed()
                SummonerEmbed.colour = 0x3498db
                SummonerEmbed.title = 'League of Legends Basic stats for ' + summoner['name'] + ' (' + str(summoner['id']) + ')'
                SummonerEmbed.set_thumbnail(url=lol.getSummonerIconUrl(summoner['name']))
                SummonerEmbed.add_field(name = 'ID Icône', value = str(summoner['profileIconId']))
                SummonerEmbed.add_field(name = 'Niveau', value = str(summoner['summonerLevel']))
                SummonerEmbed.add_field(name = 'Wins', value = str(SummonerWins))
                SummonerEmbed.add_field(name = 'Rank', value = str(SummonerRank))
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

    @commands.command(pass_context=True, no_pm=True)
    async def rankedfullinfo(self, ctx, *, user:str):
        """Récupère les informations concernant les rankeds d'un invocateur"""
        try:
            tmp = await self.bot.say("Processing request...")
            await self.bot.delete_message(ctx.message)

            try:
                summoner = lol.getSummonerInfo(user)
                SummonerStats = lol.getRankedStats(summoner['id'])
                SummonerRank = lol.getRank(summoner['id'])

                SummonerEmbed = discord.Embed()
                SummonerEmbed.colour = 0x3498db
                SummonerEmbed.title = 'Ranked League of Legends stats for ' + summoner['name'] + ' (' + str(summoner['id']) + ')'
                SummonerEmbed.set_thumbnail(url=lol.getSummonerIconUrl(summoner['name']))
                SummonerEmbed.add_field(name = 'ID Icône', value = str(summoner['profileIconId']))
                SummonerEmbed.add_field(name = 'Niveau', value = str(summoner['summonerLevel']))
                SummonerEmbed.add_field(name = 'Wins', value = str(SummonerStats['wins']))
                SummonerEmbed.add_field(name = 'Losses', value = str(SummonerStats['losses']))
                SummonerEmbed.add_field(name = 'Rank', value = str(SummonerRank))
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

    @commands.command(pass_context=True, no_pm=True)
    async def unrankedfullinfo(self, ctx, *, user:str):
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
    @commands.command(pass_context=True, no_pm=True)
    async def champion(self, ctx, *, champion:str):
        """Récupère les informations d'un champion

        Source : http://champion.gg/
        """
        try:
            tmp = await self.bot.say("Processing request...")
            await self.bot.delete_message(ctx.message)

            try:
                champstat = lol.getChampionStats(champion)
                champinfo = lol.getChampionInfo(champstat['id'])
                champgg = lol.getChampionGG(champion)
                champ3430 = champgg['3430']
                champ3432 = champgg['3432']
                champ3432Stats = champ3432['stats']
                WinRate = champ3432Stats['winRate'] * 100
                PlayRate = champ3432Stats['playRate'] * 100
                BanRate = champ3432Stats['banRate'] * 100

                ChampionEmbed = discord.Embed()
                ChampionEmbed.colour = 0x3498db
                ChampionEmbed.title = 'Stats for ' + champstat['name'] + ' (' + str(champstat['id']) + ')'
                ChampionEmbed.set_thumbnail(url=lol.getChampionIconUrl(champstat['name']))
                ChampionEmbed.add_field(name = 'Title', value = champstat['title'])
                ChampionEmbed.add_field(name = 'Free', value = champinfo['freeToPlay'])
                ChampionEmbed.add_field(name = 'Role', value = champ3430['role'])
                ChampionEmbed.add_field(name = 'Win Rate', value = str(WinRate) + ' %')
                ChampionEmbed.add_field(name = 'Play Rate', value = str(PlayRate) + ' %')
                ChampionEmbed.add_field(name = 'Ban Rate', value = str(BanRate) + ' %')
                ChampionEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)
                await self.bot.delete_message(tmp)
                await self.bot.say(embed=ChampionEmbed)

            except KeyError:
                await self.bot.say("```py\nChampion not found\n```")
                await self.bot.delete_message(tmp)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    @commands.command(pass_context=True, no_pm=True)
    async def game(self, ctx, *, user:str):
        """[EN DEV] Montre les statistiques d'une game en cours"""

        tmp = await self.bot.say("Processing request...")
        await self.bot.delete_message(ctx.message)

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

            for x in Team1:
                i += 1

                SummonerName = x['summonerName']
                SummonerID = x['summonerId']

                print("[FTS][GAME][TEAM I][J"+i+"] Valiables définies")

                Rank = lol.getRank(SummonerID)
                ranks1 += [Rank]

                print("[FTS][GAME][TEAM I][J"+i+"] Rank collected")

                ChampID = x['championId']
                Champ = lol.getChampionName(ChampID)
                champs1 += [Champ]

                print("[FTS][GAME][TEAM I][J"+i+"] Champion collected")

                summonersNames1 += [SummonerName]

                print("[FTS][GAME][TEAM I][J"+i+"] Summoner's name collected")

                Player = lol.getSummonerInfo(SummonerName)

                print("[FTS][GAME][TEAM I][J"+i+"] Summoner's ID collected")

                SummonerStats = lol.getRankedStats(Player['id'])

                print("[FTS][GAME][TEAM I][J"+i+"] Summoner's Stats collected")

                if SummonerStats['losses'] != 0:
                    WRate = SummonerStats['wins'] / SummonerStats['losses'] * 100
                else:
                    WRate = SummonerStats['wins']

                WRate = float(WRate)
                WinRate1 += [WRate]

                print("[FTS][GAME][TEAM I][J"+i+"] Summoner's WinRate collected")

                Games = SummonerStats['wins'] + SummonerStats['losses']
                games1 += [Games]

                print("[FTS][GAME][TEAM I][J"+i+"] Summoner's Games collected")

            TeamI = {'Rank':ranks1, 'Champ':champs1, 'Name':summonersNames1, 'WRate':WinRate1, 'Games':games1}

            print("[FTS][GAME][TEAM I] Team I Complete")
            print(TeamI)

            MsgBase = "```py\n"
            msg1 = MsgBase

            for x in range(5):
                MsgRank = TeamI['Rank']
                MsgChamp = TeamI['Champ']
                MsgName = TeamI['Name']
                MsgWRate = TeamI['WRate']
                MsgGames = TeamI['Games']

                msg1 += "{0:13}{1:15}{2:17}W/L: {3:>4.1f} % {4:4} games\n".format(MsgRank[x], MsgChamp[x], MsgName[x], MsgWRate[x], MsgGames[x])

            MsgT1 = "Team 1 :\n" + msg1 + "```"

            for x in Team2:

                SummonerName = x['summonerName']
                SummonerID = x['summonerId']

                Rank = lol.getRank(SummonerID)
                ranks2 += [Rank]

                ChampID = x['championId']
                Champ = lol.getChampionName(ChampID)
                champs2 += [Champ]

                summonersNames2 += [SummonerName]

                player = lol.getSummonerInfo(SummonerName)
                playerID = player['id']
                SummonerStatsII = lol.getRankedStats(playerID)

                if SummonerStatsII['losses'] != 0:
                    WRate = SummonerStatsII['wins'] / SummonerStatsII['losses'] * 100
                else:
                    WRate = SummonerStatsII['wins']

                WRate = float(WRate)
                WinRate2 += [WRate]

                Games = SummonerStatsII['wins'] + SummonerStatsII['losses']
                games2 += [Games]

            TeamII = {'Rank':ranks2, 'Champ':champs2, 'Name':summonersNames2, 'WRate':WinRate2, 'Games':games2}

            msg2 = MsgBase

            for x in range(5):
                Msg2Rank = TeamII['Rank']
                Msg2Champ = TeamII['Champ']
                Msg2Name = TeamII['Name']
                Msg2WRate = TeamII['WRate']
                Msg2Games = TeamII['Games']

                msg2 += "{0:13}{1:15}{2:17}W/L: {3:>4.1f} % {4:4} games\n".format(Msg2Rank[x], Msg2Champ[x], Msg2Name[x], Msg2WRate[x], Msg2Games[x])

            MsgT2 = "Team 2 :\n" + msg2 + "```"

            MSG = MsgT1 + "\n" + MsgT2

            await self.bot.delete_message(tmp)
            await self.bot.say(MSG)

class Vote:
    """Commandes de Vote"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}
        self.VoteMess = None
        self.Requester = None
        self.VoteTitle = None

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

            await self.bot.say(embed=VoteEmbed)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def vote(self, ctx, *, answer:str='oui'):
        """Répondre à un vote par oui ou non"""

        try:
            if self.VoteMess != None:
                    if answer == 'oui' or answer == "Oui" or answer == "OUI":

                        oui = self.VoteMess['oui']
                        oui = int(oui) + 1
                        self.VoteMess['oui'] = oui

                        await self.bot.delete_message(ctx.message)
                        await self.bot.say("{0} Votre vote a bien été pris en compte".format(ctx.message.author.mention))

                    elif answer == 'non' or answer == 'Non' or answer == "NON":

                        non = self.VoteMess['non']
                        non = int(non) + 1
                        self.VoteMess['non'] = non

                        await self.bot.delete_message(ctx.message)
                        await self.bot.say("{0} Votre vote a bien été pris en compte".format(ctx.message.author.mention))

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
        try:
            if self.VoteMess != None:
                await self.bot.delete_message(ctx.message)
                VoteEmbed = discord.Embed()
                VoteEmbed.title = "Résultats du Vote : " + self.VoteTitle
                VoteEmbed.colour = 0x3498db
                VoteEmbed.add_field(name = 'Oui', value = str(self.VoteMess['oui']))
                VoteEmbed.add_field(name = 'Non', value = str(self.VoteMess['non']))
                VoteEmbed.set_footer(text = "Requested by {0}".format(self.Requester.name), icon_url = self.Requester.avatar_url)
                await self.bot.say(embed=VoteEmbed)
                self.VoteMess = None
                self.VoteTitle = None
                self.Requester = None
                await self.bot.say('```\nVOTE TERMINÉ !\n```')
            else:
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```\nAucun vote n'est en cours\n```")

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            await self.bot.delete_message(ctx.message)

class Jeux:
    """Jeux proposés par le bot FtS"""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=True)
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

            admin = get_perm_admin(member)
            cii = get_perm_create_instant_invite(member)
            kick = get_perm_kick_members(member)
            ban = get_perm_ban_members(member)
            m_chans = get_perm_manage_channels(member)
            m_srv = get_perm_manage_server(member)
            add_react = get_perm_add_reactions(member)
            tts = get_perm_send_tts_messages(member)
            m_mess = get_perm_manage_messages(member)
            mute = get_perm_mute(member)
            deafen = get_perm_deafen(member)
            sd_embed = get_perm_send_embed_links(member)
            attach_files = get_perm_attach_files(member)
            everyone = get_perm_mention_everyone(member)
            ext_emo = get_perm_external_emojis(member)
            nick = get_perm_change_nickname(member)
            m_nick = get_perm_change_nickname(member)
            m_roles = get_perm_manage_roles(member)
            m_webhooks = get_perm_manage_webhooks(member)
            m_emo = get_perm_manage_emojis(member)

            await self.bot.delete_message(ctx.message)
            await self.bot.delete_message(tmp)
            await self.bot.say(ctx.message.author.mention + " Voici les permissions de " + member.mention + " : ```Permissions administrateur : " + admin + "\nCréer invitations : " + cii + "\nÉjecter les membres : " + kick + "\nBannir les membres : " + ban + "\nGérer les channels : " + m_chans + "\nGérer le serveur : " + m_srv + "\nAjouter une réaction : " + add_react + "\nEnvoyer des messages tts : " + tts + "\nGérer les messages : " + m_mess + "\nRendre muets les utilisateurs : " + mute + "\nRendre sourds les utilisateurs : " + deafen + "\nEnvoyer des messages intégrés : " + sd_embed + "\nEnvoyer des pièces jointes : " + attach_files + "\nMentionner everyone : " + everyone + "\nUtiliser des emojis externes au serveur : " + ext_emo + "\nChanger son pseudo : " + nick + "\nGérer les pseudonymes : " + m_nick + "\nGérer les rôles : " + m_roles + "\nGérer les webhooks : " + m_webhooks + "\nGérer les emojis : " + m_emo + "```")
            
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
                createdAt = lol.dateConverter(member.created_at)
                joinedAt = lol.dateConverter(member.joined_at)
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
    async def convoque(self, ctx, user=None, *, reason):
        """Envoie une convocation au joueur cité"""

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
            ConvocEmbed.description = "Vous avez été convoqué par l'administration du serveur {0} pour la raison qui suit. Vous êtes prié de vous rendre sur le serveur dans les plus brefs délais et de vous mettre en contact avec un des administrateurs ou des modérateurs".format(ctx.message.server.name)
            ConvocEmbed.add_field(name = 'Raison', value = reason)
            ConvocEmbed.set_footer(text = "Requested by {0}".format(ctx.message.author.name), icon_url = ctx.message.author.avatar_url)

            await self.bot.delete_message(tmp)
            await self.bot.send_message(member, embed=ConvocEmbed)
            await self.bot.send_message(bot.get_channel('298029242871185408'), "@here Une convocation a été envoyée à {0} par {1}, raison : {2}".format(member.mention, ctx.message.author.mention, reason))

        else:
            await self.bot.say("```\nVous n'avez pas la permission de convoquer un utilisateur\n```")

class Messages:
    """Commandes Textuelles"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(pass_context=True, no_pm=True)
    async def hi(self, ctx):
        """Fall to Sky vous salue"""
        await self.bot.say("Salut {0.message.author.mention} !".format(ctx))
        print('[FTS] Hello Message sent')

    @commands.command(pass_context=True, no_pm=True)
    async def ip(self, ctx):
        """Envoie l'IP du serveur HolyFTS"""
        await self.bot.say("{0.message.author.mention} IP du serveur HolyFTS : holyfts.boxtoplay.com".format(ctx))
        print('[FTS] IP sent')

    @commands.command(pass_context=True, no_pm=True)
    async def website(self, ctx):
        """Affiche le site web du serveur"""
        await self.bot.say("{0.message.author.mention} Site web du serveur : http://sakiut.fr/discord".format(ctx))
        print("[FTS] Website's URL sent")

    @commands.command(pass_context=True, no_pm=True)
    async def meme(self, ctx):
        """Affiche une meme random parmi la bibliothèque"""
        print('[FTS] Sending Meme...')
        mem = random.choice(freshestMemes)
        await self.bot.send_file(ctx.message.channel, mem)
        print('[FTS] Meme Sent')

    @commands.command(pass_context=True, no_pm=True)
    async def echo(self, ctx, *, mess : str):
        """Répète le message de l'utilisateur"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say(mess)
        print('[FTS] Message sent :', mess)

    @commands.command(pass_context=True, no_pm=True)
    async def report(self, ctx, user: discord.Member, *, reason: str):
        """Reporte un utilisateur au staff"""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(bot.get_channel('298029242871185408'), "{0} a été report par {1}, raison : {2}, @here".format(user.mention, ctx.message.author.mention, reason))
        print('[FTS] {0} has been reported by {1}'.format(user, ctx.message.author))

    @commands.command(pass_context=True, no_pm=True)
    async def bug(self, ctx, *, subject:str):
        """Rapporte un bug du bot à l'équipe de dev"""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(bot.get_channel('307799958965190656'), "Un bug a été report par {0}, sujet : {1}, @here".format(ctx.message.author.mention, subject))

    @commands.command(pass_context=True, no_pm=True)
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
    async def purge(self, ctx, limit=100):
        """Supprime le nombre de messages spécifié

        100 Messages seront supprimés par défaut

        Cette commande ne peut être utilisé que par les utilisateurs ayant la permission de gérer les messages
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

        100 Messages seront supprimés par défaut

        Cette commande ne peut être utilisé que par les utilisateurs ayant la permission de gérer les messages
        """

        if ctx.message.author.server_permissions.manage_messages == True:
            print('[FTS] Proceding purge...')
            async for log in self.bot.logs_from(ctx.message.channel, limit):
                if log.author == user:
                    await self.bot.delete_message(log)

            await self.bot.delete_message(ctx.message)
            await self.bot.say("Supression des messages de {0} parmi les {1} derniers messages".format(user.name, limit))
            print('[FTS] Purge done')
            print('[FTS] Deleted {0} messages'.format(limit))
        else:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("Vous n'avez pas l'autorisation de gérer les messages")
            print('[FTS] Purge : Command aborted : User do not have manage_messages permission')

    @commands.command(pass_context=True, no_pm=True)
    async def addme(self, ctx):
        """Envoie le lien d'ajout du bot"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say("{0.message.author.mention} Pour m'ajouter, utiliser ce lien : https://discordapp.com/oauth2/authorize?client_id=283379732538720256&scope=bot&permissions=8".format(ctx))
        print('[FTS] Add message sent')

    @commands.command(pass_context=True, no_pm=True)
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
    async def emoji(self, ctx, emoji=1):
        """Donne un emoji parmi la liste des emotes ajoutés sur le serveur

        1 - :fts:
        2 - :_3:
        3 - :fts_white:
        4 - :like:
        5 - :dislike:
        """
        emoji = emoji - 1
        msg = emojis[emoji]
        await self.bot.delete_message(ctx.message)
        await self.bot.say(msg)
        print('[FTS] Emoji n°{} sent'.format(emoji))

    @commands.command(pass_context=True, no_pm=True)
    async def allemoji(self, ctx, limit=5):
        """Donne la liste des x premiers emojis du serveur"""
        await self.bot.delete_message(ctx.message)
        if limit < 1:
            await self.bot.say("Sended 0 emojis")
        else:
            i = 0
            for a in range(limit):
                msg = emojis[i]
                await self.bot.say(msg)
                i = i + 1
            print('[FTS] Sended {} emojis'.format(limit))

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

bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description="Commandes Bot Fall to Sky")
bot.add_cog(Messages(bot))
bot.add_cog(Music(bot))
bot.add_cog(Admin(bot))
bot.add_cog(Vote(bot))
bot.add_cog(Jeux(bot))
bot.add_cog(LeagueOfLegends(bot))

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
async def on_ready():
    print('--------------------------')
    print('[FTS] Logged in as')
    print('[FTS]', bot.user.name)
    print('[FTS]', bot.user.id)
    print('--------------------------')
    await bot.change_presence(game=discord.Game(name='sakiut.fr | .help'))  

bot.run('MjgzMzc5NzMyNTM4NzIwMjU2.C4098g.HJVW-oMNB2W0IEzIIWQn4s1dENI')
