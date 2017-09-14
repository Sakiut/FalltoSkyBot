# -*- coding: utf-8 -*-

import asyncio
import discord
from discord.ext import commands

from libraries.library import *

class Vote:

    def __init__(self,bot):
        self.bot = bot
        self.VoteState = None
        self.Mess = None
        self.Requester = None
        self.subject = None
        self.Voters = []
        self.oui = None
        self.non = None

    @commands.group(pass_context=True)
    async def vote(self, ctx):
        """Commandes de vote.

        Utilisation :
            .vote start <sujet du vote>
            .vote stop"""

        if ctx.invoked_subcommand is None:
            await self.bot.delete_message(ctx.message)
            await self.bot.say("```md\nSyntaxe invalide. Voir .help vote pour plus d'informations sur comment utiliser cette commande.\n```")

    @vote.command(pass_context=True, no_pm=True)
    async def start(self, ctx, *, subject : str):
        """Démarrer un vote"""

        await self.bot.delete_message(ctx.message)
        if self.VoteState == None:

            self.subject = subject
            self.Requester = ctx.message.author
            self.VoteState = True
            self.Voters = []
            self.oui = 0
            self.non = 0

            self.VoteEmbed = discord.Embed()
            self.VoteEmbed.title = "Vote : " + self.subject
            self.VoteEmbed.colour = 0x3498db
            self.VoteEmbed.set_footer(text = "Requested by {0}".format(self.Requester.name), icon_url = self.Requester.avatar_url)
            self.VoteEmbed.add_field(name = "✅", value = self.oui)
            self.VoteEmbed.add_field(name = "❎", value = self.non)

            mess = await self.bot.say(embed=self.VoteEmbed)
            self.Mess = mess

            await self.bot.add_reaction(mess, "✅")
            await self.bot.add_reaction(mess, "❎")
            await asyncio.sleep(1)

            while self.VoteState == True:
                res = await self.bot.wait_for_reaction(["✅","❎"], message = self.Mess)
                user = res.user
                reaction = res.reaction

                if user not in self.Voters:
                    if reaction.emoji == "✅":
                        await self.bot.remove_reaction(reaction.message, "✅", user)
                        self.Voters.append(user)
                        self.oui += 1
                        self.VoteEmbed.set_field_at(0, name = "✅", value = self.oui)

                        await self.bot.edit_message(self.Mess, embed=self.VoteEmbed)

                    elif reaction.emoji == "❎":
                        await self.bot.remove_reaction(reaction.message, "❎", user)
                        self.Voters.append(user)
                        self.non += 1
                        self.VoteEmbed.set_field_at(1, name = "❎", value = self.non)

                        await self.bot.edit_message(self.Mess, embed=self.VoteEmbed)
                    else:
                        await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                else:
                    await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                    tmp = await self.bot.send_message(self.Mess.channel, "{0.mention} Vous avez déjà voté".format(user))
                    await asyncio.sleep(5)
                    await self.bot.delete_message(tmp)

        else:
            tmp = await self.bot.say('Vote déjà en cours')
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

    @vote.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Arrêter le vote en cours
        Utilisable uniquement par le demandeur du vote déjà en cours."""

        await self.bot.delete_message(ctx.message)
        if self.VoteState == True:
            self.VoteEmbed.title = "Vote : " + self.subject + " [TERMINÉ]"
            await self.bot.edit_message(self.Mess, embed=self.VoteEmbed)
            await self.bot.clear_reactions(self.Mess)
            self.VoteState = None
        else:
            tmp = await self.bot.say('Aucun vote en cours')
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)