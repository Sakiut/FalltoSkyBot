# -*- coding: utf-8 -*-

import  asyncio
import  discord
from    discord.ext import commands

from    libraries.library import *

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

class Messages:
    """Commandes Textuelles"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=False)
    async def hi(self, ctx):
        """Fall to Sky vous salue"""
        await self.bot.say("Salut {0.message.author.mention} !".format(ctx))

    @commands.command(pass_context=True, no_pm=False)
    async def ip(self, ctx):
        """Envoie l'IP du serveur Minecraft"""
        await self.bot.say("{0.message.author.mention} IP du serveur Minecraft : {1}".format(ctx, getServerIP()))

    @commands.command(pass_context=True, no_pm=False)
    async def website(self, ctx):
        """Affiche le site web du serveur"""
        await self.bot.say("{0.message.author.mention} Site web du serveur : {1}".format(ctx, getWebSite()))

    @commands.command(pass_context=True, no_pm=False)
    async def meme(self, ctx):
        """Affiche une meme random parmi la bibliothèque"""
        mem = random.choice(freshestMemes)
        await self.bot.send_file(ctx.message.channel, mem)

    @commands.command(pass_context=True, no_pm=False)
    async def echo(self, ctx, *, mess : str):
        """Répète le message de l'utilisateur"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say(mess)

    @commands.command(pass_context=True, no_pm=True)
    async def mpecho(self, ctx, user:discord.Member, *, mess : str):
        """Envoie un MP via le bot"""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(user, mess)

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

    @commands.command(pass_context=True, no_pm=False)
    async def addme(self, ctx):
        """Envoie le lien d'ajout du bot"""
        await self.bot.delete_message(ctx.message)
        await self.bot.say("{0.message.author.mention} Pour m'ajouter, utiliser ce lien : https://discordapp.com/oauth2/authorize?client_id=283379732538720256&scope=bot&permissions=8".format(ctx))

    @commands.command(pass_context=True, no_pm=False)
    async def messcount(self, ctx, limit=1000):
        """Donne le nombre de messages envoyés dans le channel"""
        await self.bot.delete_message(ctx.message)
        counter = 0
        tmp = await self.bot.say('Calculating messages...')
        async for log in bot.logs_from(ctx.message.channel, limit):
            if log.author == ctx.message.author:
                counter += 1

        await self.bot.delete_message(tmp)
        await self.bot.say('{0.message.author.mention} You have sent `{1}` messages in this channel'.format(ctx, counter))

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