# -*- coding: utf-8 -*-

import  asyncio
import  discord
import  random
import  math
from    discord.ext         import commands
from    libraries.library   import *
from    libraries           import casino

emotes = [
    u"\u0030\N{COMBINING ENCLOSING KEYCAP}", #0
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

class Jeux:
    """Jeux proposés par le bot"""

    def __init__(self,bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=False)
    async def casino(self, ctx):
        """Bienvenue au ZCasino !

        Misez une somme sur un nombre, si c'est le bon nombre vous récupérez
        trois fois votre mise, si le nombre est de la même couleur vous
        récupérez la moitié de votre mise ! Bonne chance !"""

        data    = casino.start()
        server  = ctx.message.server
        user    = ctx.message.author
        chan    = ctx.message.channel

        await self.bot.delete_message(ctx.message)

        res_embed           = discord.Embed()
        res_embed.colour    = 0x3498db
        res_embed.title     = "Choisissez votre mise (0-9)"
        res = await self.bot.say(embed = res_embed)

        for x in emotes:
            await self.bot.add_reaction(res, x)

        await asyncio.sleep(1)
        result  = await self.bot.wait_for_reaction(emotes, message = res)
        react   = result.reaction.emoji
        await self.bot.clear_reactions(res)
        await self.bot.delete_message(res)

        nb = emotes.index(react)

        money = casino.get(server, user, data)
        if money == 0:
            tmp = await self.bot.say("Votre cagnotte est vide, adressez-vous à Sakiut pour la remplir.")
            await asyncio.sleep(2)
            await self.bot.delete_message(tmp)
            return

        mon_embed           = discord.Embed()
        mon_embed.colour    = 0x3498db
        mon_embed.title     = "Vous avez une cagnotte de {}$".format(money)

        mise_embed          = discord.Embed()
        mise_embed.colour   = 0x3498db
        mise_embed.title    = "Combien souhaitez-vous miser ?"
        mise_embed.set_footer(text = "Répondre par message")

        mon = await self.bot.say(embed = mon_embed)
        mis = await self.bot.say(embed = mise_embed)
        ok  = False

        async def send_tmp(msg):
            tmp = await self.bot.say("Vous devez envoyer un nombre entier inférieur ou égal au \
                                    montant de votre cagnotte et supérieur à 0.")
            await self.bot.delete_message(msg)
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

        while ok is not True:
            ans = await self.bot.wait_for_message(author = user, channel = chan)
            try:
                mise = int(ans.content)
                if mise > money or mise <= 0:
                    await send_tmp(ans)
                    continue
                else:
                    ok = True
                    break
            except ValueError:
                await send_tmp(ans)
                continue

        await self.bot.delete_message(mon)
        await self.bot.delete_message(mis)
        await self.bot.delete_message(ans)

        cas_embed       = discord.Embed()
        cas_embed.title = "Bienvenue au ZCasino !"
        cas_embed.add_field(name = "Mise", value = str(mise))
        cas_embed.add_field(name = "Nombre", value = str(nb))

        cas = await self.bot.say(embed = cas_embed)
        await asyncio.sleep(2)
        result = random.randrange(0, 10)

        if nb % 2 == 0:
            nbpair = True
            nb_icon = "🔴"
        else:
            nbpair = False
            nb_icon = "🔵"

        if result % 2 == 0:
            pair = True
            res_icon = "🔴"
        else:
            pair = False
            res_icon = "🔵"

        rand_embed = discord.Embed()
        rand_embed.title = "Et le résultat est..."
        rand_embed.add_field(name = "Nombre départ", value = str(nb_icon) + " " + str(nb))
        rand_embed.add_field(name = "Résultat", value = str(res_icon) + " " + str(result))
        rand_embed.set_footer(text = "Joueur : {0}#{1}".format(user.name, user.discriminator), icon_url = ctx.message.author.avatar_url)

        rand = await self.bot.say(embed = rand_embed)
        await asyncio.sleep(0.5)
        await self.bot.delete_message(cas)

        if result == nb:
            win = mise * 3
            rand_embed.add_field(name = "_ _", value = "Vous avez gagné ! Vous récupérez " + str(win) + "$")

        elif nbpair is pair:
            win = mise / 2
            win = math.ceil(win)
            rand_embed.add_field(name = "_ _", value = "La couleur des nombres correspond, vous récupérez " + str(win) + "$.")

        else:
            win = 0
            rand_embed.add_field(name = "_ _", value = "Vous avez perdu, vous pouvez recommencer ! 😉")

        await self.bot.edit_message(rand, embed = rand_embed)

        money = money - mise + win
        casino.post(server, user, data, money)

    @commands.command(pass_context=True, no_pm=True)
    async def money(self, ctx, *, user:discord.Member=None):
        """Affiche votre cagnotte"""

        data        = casino.start()
        server      = ctx.message.server
        if not user:
            user    = ctx.message.author
        chan        = ctx.message.channel

        await self.bot.delete_message(ctx.message)
        money = casino.get(server, user, data)

        mon_embed           = discord.Embed()
        mon_embed.colour    = 0x3498db
        mon_embed.title     = "Cagnotte : {}$".format(str(money))
        mon_embed.set_footer(text = "{0}#{1}".format(user.name, user.discriminator), icon_url = user.avatar_url)
        await self.bot.say(embed = mon_embed)

    @commands.command(pass_context=True, no_pm=True)
    async def add_money(self, ctx, *, user:discord.Member=None):
        """Ajoute de l'argent à la cagnotte d'un utilisateur
        Bot Master uniquement"""

        data        = casino.start()
        server      = ctx.message.server
        if not user:
            user    = ctx.message.author
        chan        = ctx.message.channel

        if ctx.message.author.id == "187565415512276993":
            await self.bot.delete_message(ctx.message)
            tmp = await self.bot.say("Combien voulez-vous ajouter à la cagnotte de {} ?".format(user.name))
            ans = await self.bot.wait_for_message(author = ctx.message.author, channel = chan)
            money = int(ans.content)
            await self.bot.delete_message(ans)
            casino.post(server, user, data, money)
            await self.bot.delete_message(tmp)
            tmp = await self.bot.say("Done")
            await asyncio.sleep(3)
            await self.bot.delete_message(tmp)
        else:
            return