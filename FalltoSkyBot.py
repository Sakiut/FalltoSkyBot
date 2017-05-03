import discord
import asyncio
import random
import os
import math

client = discord.Client()

print('[FTS] Connecting...')
print('--------------------------')

freshestMemes = ["mem/meme1.jpeg", "mem/meme2.jpeg", "mem/meme3.jpeg", "mem/meme6.jpeg", "mem/meme7.jpeg", "mem/meme8.jpeg", "mem/meme9.jpeg", "mem/meme10.jpeg", "mem/meme11.jpeg", "mem/meme12.jpeg", "mem/meme14.jpeg","mem/meme15.jpeg"]

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Bienvenue à {0.mention} sur {1.name} !'
    await client.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has joined the server'.format(member))

@client.event
async def on_member_left(member):
    server = member.server
    fmt = '{0.mention} est parti-e du serveur {1.name} !'
    await client.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has left the server'.format(member))

@client.event
async def on_member_banned(member):
    server = member.server
    fmt = '{0.mention} a été banni-e du serveur {1.name} !'
    await client.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has been banned of the server'.format(member))

@client.event
async def on_member_unbanned(member):
    server = member.server
    fmt = "{0.mention} a été pardonné-e, il-elle n'est plus banni-e du serveur {1.name} !"
    await client.send_message(server, fmt.format(member, server))
    print('[FTS] {0.name} has been unbanned of the server'.format(member))

@client.event
async def on_ready():
    print('[FTS] Logged in as')
    print('[FTS]', client.user.name)
    print('[FTS]', client.user.id)
    print('--------------------------')

@client.event
async def on_message(e):
	#MESSCOUNT
    if e.content.startswith('.messcount'):
        counter = 0
        tmp = await client.send_message(e.channel, 'Calculating messages...')
        print('[FTS] Calculating...')
        async for log in client.logs_from(e.channel, limit=1000):
            if log.author == e.author:
                counter += 1

        await client.edit_message(tmp, 'You have sent `{}` messages in this channel'.format(counter))
        print('[FTS] Calculation done and sent')

    #SLEEP
    if e.content.startswith('.sleep'):
        await asyncio.sleep(5)
        await client.send_message(e.channel, 'Done sleeping')
        print('[FTS] Done sleeping')

    #HI
    if e.content.startswith('.hi'):
        msg = 'Hello {0.author.mention}'.format(e)
        await client.send_message(e.channel, msg)
        print('[FTS] Hello Message sent')

    #SEND
    if e.content.startswith('.send'):
    	await client.send_message(e.channel, 'Waiting for type...')
    	mess = input('[FTS] Type your message : ')
    	async for log in client.logs_from(e.channel, limit=2):
        	await client.delete_message(log)

    	await client.send_message(e.channel, mess)
    	print('[FTS] Message sent')

    #TTS
    if e.content.startswith('.tts'):
    	await client.send_message(e.channel, 'Waiting for type...')
    	mess = input('[FTS] Type your tts : ')
    	async for log in client.logs_from(e.channel, limit=2):
        	await client.delete_message(log)

    	await client.send_message(e.channel, mess, tts=True)
    	print('[FTS] TTS sent')

	#IP
    if e.content.startswith('.ip'):
    	await client.send_message(e.channel, '{0.author.mention} IP du serveur HolyFTS : holyfts.boxtoplay.com'.format(e))
    	print('[FTS] IP sent')

	#WEBSITE
    if e.content.startswith('.website'):
    	await client.send_message(e.channel, '{0.author.mention} Site web du serveur : http://sakiut.fr/discord'.format(e))
    	print('[FTS] Website\'s URL sent')

    #HELP
    if e.content.startswith('.help'):
    	await client.send_message(e.channel, '{0.author.mention} \n Commandes utilisables : \n 	*.messcount* - Donne le nombre de messages envoyés dans le channel par l\'utilisateur sur les 1000 derniers messages \n 	*.sleep* - Fall to Sky dort pendant 5 secondes \n 	*.hi* - Fall to Sky vous salue \n 	*.send* - Envoie un message tapé dans la console du bot \n 	*.tts* - Envoie un tts tapé dans la console du bot \n 	*.ip* - Affiche l\'IP du Serveur HolyFTS \n 	*.help* - Affiche ce message \n 	*.website* - Affiche le site web du serveur \n 	*.meme* - Envoie une meme au hasard parmi la bibliothèque \n 	*.purge* - Supprime les 100 derniers messages envoyés dans le chan.'.format(e))
    	print('[FTS] Help message sent')

    #PURGE
    if e.content.startswith('.purge'):
    	print('[FTS] Proceding purge...')
    	async for log in client.logs_from(e.channel, limit=100):
        	await client.delete_message(log)

    	print('[FTS] Purge done')

    #MEMES
    if e.content.startswith('.meme'):
    	print('[FTS] Sending Meme...')
    	mem = random.choice(freshestMemes)
    	await client.send_file(e.channel, mem)
    	print('[FTS] Meme Sent')

client.run('MjgzMzc5NzMyNTM4NzIwMjU2.C4098g.HJVW-oMNB2W0IEzIIWQn4s1dENI')