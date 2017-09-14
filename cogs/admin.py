# -*- coding: utf-8 -*-

import  asyncio
import  discord
from    discord.ext         import commands

from    libraries.perms     import *
from    libraries.library   import *

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
        else:
            await self.bot.say("Vous n'êtes pas administrateur")

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

    @commands.command(pass_context=True, no_pm=False)
    async def disconnect(self, ctx):
        """Déconnecte le bot - Bot Master uniquement"""
        requester = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if requester.id == '187565415512276993':
            print('[FTS] Déconnexion...')
            await self.bot.logout()
            print('[FTS] Logged out')
            await self.bot.close()
            print('[FTS] Connexions closed')
            exit()
        else:
            tmp = await self.bot.say("Vous n'êtes pas le Bot Master")
            await asyncio.sleep(5)
            await self.bot.delete_message(tmp)

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