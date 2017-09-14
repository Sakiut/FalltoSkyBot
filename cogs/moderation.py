# -*- coding: utf-8 -*-

import  asyncio
import  discord
from    discord.ext         import commands
from    libraries.perms     import *
from    libraries.library   import *
from    libraries           import moderation

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
        """Unute un utilisateur
        Requiert la permission de kick"""

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

    @commands.command(pass_context=True, no_pm=True)
    async def purge(self, ctx, limit=10):
        """Supprime le nombre de messages spécifié

        10 Messages seront supprimés par défaut

        Cette commande ne peut être utilisée que par les utilisateurs ayant la permission de gérer les messages
        """

        await self.bot.delete_message(ctx.message)
        member = ctx.message.author
        if member.server_permissions.manage_messages == True:
            await self.bot.purge_from(ctx.message.channel, limit = limit)
        else:
            await self.bot.say("Vous n'avez pas l'autorisation de gérer les messages")

    @commands.command(pass_context=True, no_pm=True)
    async def purge_user(self, ctx, limit=10, *, user:discord.Member):
        """Supprime le nombre de messages spécifié du membre choisi

        10 Messages seront scannés par défaut

        Cette commande ne peut être utilisée que par les utilisateurs ayant la permission de gérer les messages
        """
        await self.bot.delete_message(ctx.message)

        member = ctx.message.author
        if member.server_permissions.manage_messages == True:

            def compare(m):
                return m.author == user

            deleted = await self.bot.purge_from(ctx.message.channel, limit = limit, check = compare)
            FeedBack = await self.bot.say("```{2} messages de {0} parmi les {1} derniers messages supprimés```".format(user.name, limit, len(deleted)))

        else:
            FeedBack = await self.bot.say("Vous n'avez pas l'autorisation de gérer les messages")

        await asyncio.sleep(5)
        await self.bot.delete_message(FeedBack)

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
                    raise ValueError("Seuls soit un entier soit la mention all (insensible à la casse) sont attendus")

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
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))