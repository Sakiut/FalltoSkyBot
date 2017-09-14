import asyncio
import discord
from discord.ext import commands

from libraries.library import *
from libraries import youtube

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
                await self.bot.say("```Update failed```")
        else:
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
            await self.bot.say("```Vous n'avez pas la permission d'utiliser cette commande```")