# -*- coding: utf-8 -*-

import requests
from random import shuffle
import time
from decimal import *
import sys
import datetime
import discord

from riotwatcher import RiotWatcher
from riotwatcher import EUROPE_WEST
from riotwatcher import LoLException, error_404, error_429
from libraries.perms import *
from urllib import request
import linecache
import ast

fileName = './config.txt'

#####################################################################################################################################################

def get_user_roles(user):
	"""Retourne une série de str, les roles de l'utilisateur"""

	roles = user.roles
	RoleList = []
	RoleStr = ""

	for x in range(len(roles)):
		role = roles[x].name
		RoleList.append(role)

	del RoleList[0]

	for x in range(len(RoleList)):
		role = RoleList[x]
		RoleStr += role + ", "

	RoleFinal = RoleStr.rstrip(', ')

	return RoleFinal

#####################################################################################################################################################

def getServerRules():
	"""Récupère les règles du serveur depuis le fichier où elles sont enregistrées"""

	fileName = './rules.txt'
	with open(fileName) as f: rulesLines = f.read()

	return rulesLines

#####################################################################################################################################################

def getToken():
	"""Récupère le token depuis le fichier `config.txt`"""

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('token='):
			getLine = line
			Line = getLine.split('=')
			token = Line[1]

	return token

#####################################################################################################################################################

def getApiKey():
	"""Récupère la clé d'API depuis le fichier `config.txt`"""

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('apikey='):
			getLine = line
			Line = getLine.split('=')
			ApiKey = Line[1]

	return ApiKey

#####################################################################################################################################################

def getAniClientID():

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('anilistClientID='):
			getLine = line
			Line = getLine.split('=')
			ClientID = Line[1]

	return ClientID

#####################################################################################################################################################

def getAniClientSecret():

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('anilistClientSecret='):
			getLine = line
			Line = getLine.split('=')
			ClientSecret = Line[1]

	return ClientSecret

#####################################################################################################################################################

def getServerIP():
	"""Récupère l'IP depuis le fichier `config.txt`"""

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('serverip='):
			getLine = line
			Line = getLine.split('=')
			ServerIP = Line[1]

	return ServerIP

#####################################################################################################################################################

def getWebSite():
	"""Récupère le site web affilié au serveur depuis `config.txt`"""

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('website='):
			getLine = line
			Line = getLine.split('=')
			WebSite = Line[1]

	return WebSite

#####################################################################################################################################################

def formatServerRegion(region):
	"""Formate l'affichage de l'option Server Region"""

	Region = str(region)
	Region = Region.replace("_", " ")
	Region = Region.replace("-", " ")
	Region = Region.upper()
	return Region

#####################################################################################################################################################

def formatServerRoles(rolesObjects:list):
	"""Reformate la liste des Roles du serveur"""

	RoleFinal = ""

	for x in rolesObjects:
		roleName = x.name
		RoleFinal = RoleFinal + roleName + ", "

	RoleFinal = RoleFinal.rstrip(", @everyone, ")
	return RoleFinal 

#####################################################################################################################################################

def formatEmojis(emojisObjects:list):
	"""Reformate la liste des Emojis du serveur"""

	EmojisFinal = ""

	for x in emojisObjects:
		Emoji = "<:{0}:{1}>".format(x.name, x.id)
		EmojisFinal = EmojisFinal + Emoji + " "

	EmojisFinal = EmojisFinal.rstrip(" ")
	return EmojisFinal

#####################################################################################################################################################

def getServerEmojis(emojisObjects:list):
	"""Récupère les emojis du serveur"""

	EmojisFinal = "{0:6} {1:10} {2:18}\n----------------------------------------".format("Emote", "Name", 'ID')

	for x in emojisObjects:
		Emoji = "<:{0}:{1}>".format(x.name, x.id)
		line = "\n{0:6} {1:<10} {2:18}".format(Emoji, x.name, x.id)
		EmojisFinal += line

	return EmojisFinal

#####################################################################################################################################################

def getLDStats(pseudo):
	"""Récupère les stats leveldown depuis leur site"""

	pseudo = str(pseudo)
	url = "http://leveldown.fr/profile/{}".format(pseudo)
	fileName = "./ldsource/{}.html".format(pseudo)
	request.urlretrieve(url, fileName)

	with open(fileName) as f: lines = f.read().splitlines()

	Names = []
	Values = []

	for line in lines:
		if line.startswith('				<div><span>'):
			getLine = line.rstrip("</div>")
			Line = getLine.replace("<div><span", "")
			Line = Line.replace("</span>", "|")
			Line = Line.split(">")
			Line = Line[1]
			Line = Line.split("|")

			Names.append(Line[0])
			Values.append(Line[1])

	LDStats = {'Names' : Names, 'Values' : Values}

	return LDStats

#####################################################################################################################################################

def getLDIcon(pseudo):
	"""Récupère l'icone leveldown depuis leur site"""

	pseudo = str(pseudo)
	url = "http://leveldown.fr/profile/{}".format(pseudo)
	fileName = "./ldsource/{}.html".format(pseudo)
	request.urlretrieve(url, fileName)

	with open(fileName) as f: lines = f.read().splitlines()

	Names = []
	Values = []

	for line in lines:
		if line.startswith('							<div class="avatar"'):
			getLine = line.rstrip(');"></div>')
			Line = getLine.split("(")
			Line = Line[1]

	return Line

#####################################################################################################################################################

def getTextChannels(server):
	"""Retourne la liste des channels textuels du serveur"""

	Channels = server.channels
	End = []

	for chan in Channels:
		Type = str(chan.type)
		if Type is 'text':
			End.append(chan.name)

	return End

#####################################################################################################################################################

def getVoiceChannels(server):
	"""Retourne la liste des channels vocaux du serveur"""

	Channels = server.channels
	End = []

	for chan in Channels:
		Type = str(chan.type)
		if Type is 'voice':
			End.append(chan.name)

	return End

#####################################################################################################################################################

def getServerMembers(server):
	"""Retourne la liste des noms des membres du serveur"""

	Members = server.members
	End = []

	for member in Members:
		End.append(member.name)

	return End

#####################################################################################################################################################

def dateConverter(date:str):
	"""Convertit le format de lecture d'une date"""
	date = str(date)

	date2 = date.split('-')
	date3 = date2[2]
	date4 = date3.split(' ')
	date5 = date4[1]
	date6 = date5.split('.')
	date7 = date6[0]
	date8 = date7.split(':')

	FinalDate = '{0}/{1}/{2} à {3}'.format(date4[0], date2[1], date2[0], date6[0])
	return FinalDate

#####################################################################################################################################################

def getSplittedRules():
	FileName = './rules.txt'
	with open(FileName) as f: lines = f.readlines()

	Split = []
	for line in lines:
		if line.startswith('[>]'):
			Split.append(line)

	return Split

#####################################################################################################################################################

def getYoutubeID():
	"""Récupère l'ID YouTube depuis le fichier `config.txt`"""

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('youtubeid='):
			getLine = line
			Line = getLine.split('=')
			yt_id = Line[1]

	return yt_id

#####################################################################################################################################################

def formatRSSdate(date:str):
	"""2017-06-07T17:20:20+00:00"""

	date = date[:-6]
	splittedDate = date.split("T")
	hour = splittedDate[1]
	Date = splittedDate[0]
	splittedDate = Date.split("-")
	year = splittedDate[0]
	mounth = splittedDate[1]
	day = splittedDate[2]

	finalDate = "{0}-{1}-{2}, {3}".format(day, mounth, year, hour)
	return finalDate

#####################################################################################################################################################