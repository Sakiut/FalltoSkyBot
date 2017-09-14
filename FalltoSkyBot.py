# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext        import commands

from libraries.perms    import *
from libraries.library  import *
from libraries          import anilist
from libraries          import mal
from libraries          import lol
from libraries          import youtube
from libraries          import moderation

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

bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description="Commandes Bot Fall to Sky")

from cogs.messages      import Messages
from cogs.music         import Music
from cogs.admin         import Admin
from cogs.vote          import Vote
from cogs.jeux          import Jeux
from cogs.lol           import LeagueOfLegends
from cogs.anime         import Anime
from cogs.rss           import RSS
from cogs.moderation    import Moderation

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
    if server.id == "187566036747419648":
        rules = getServerRules()
        await bot.send_message(member, rules)

@bot.event
async def on_member_remove(member):
    server = member.server
    fmt = '{0.mention} est parti-e du serveur {1.name} !'
    await bot.send_message(server, fmt.format(member, server))

@bot.event
async def on_member_ban(member):
    server = member.server
    fmt = '{0.mention} a été banni-e du serveur {1.name} !'
    await bot.send_message(server, fmt.format(member, server))

@bot.event
async def on_member_unban(server, member):
    fmt = "{0.mention} a été pardonné-e, il/elle n'est plus banni-e du serveur {1.name} !"
    await bot.send_message(server, fmt.format(member, server))

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
