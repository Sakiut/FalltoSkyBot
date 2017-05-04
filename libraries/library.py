# -*- coding: utf-8 -*-

import requests
from random import shuffle
import time
from decimal import *
import sys
import datetime

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

    fileName = './rules.txt'
    with open(fileName) as f: rulesLines = f.read()

    return rulesLines

#####################################################################################################################################################

def getToken():

    with open(fileName) as f: lines = f.read().splitlines()

    for line in lines:
        if line.startswith('token='):
            getLine = line
            Line = getLine.split('=')
            token = Line[1]

    return token

#####################################################################################################################################################

def getApiKey():

    with open(fileName) as f: lines = f.read().splitlines()

    for line in lines:
        if line.startswith('apikey='):
            getLine = line
            Line = getLine.split('=')
            ApiKey = Line[1]

    return ApiKey

#####################################################################################################################################################

def getServerIP():

    with open(fileName) as f: lines = f.read().splitlines()

    for line in lines:
        if line.startswith('serverip='):
            getLine = line
            Line = getLine.split('=')
            ServerIP = Line[1]

    return ServerIP

#####################################################################################################################################################

def getWebSite():

    with open(fileName) as f: lines = f.read().splitlines()

    for line in lines:
        if line.startswith('website='):
            getLine = line
            Line = getLine.split('=')
            WebSite = Line[1]

    return WebSite

#####################################################################################################################################################

def formatServerRegion(region):

	Region = str(region)
	Region = Region.replace("_", " ")
	Region = Region.replace("-", " ")
	Region = Region.upper()
	return Region

#####################################################################################################################################################

def formatServerRoles(rolesObjects:list):

	RoleFinal = ""

	for x in rolesObjects:
		roleName = x.name
		RoleFinal = RoleFinal + roleName + ", "

	RoleFinal = RoleFinal.rstrip(", @everyone, ")
	return RoleFinal 

#####################################################################################################################################################

def formatEmojis(emojisObjects:list):

	EmojisFinal = ""

	for x in emojisObjects:
		Emoji = "<:{0}:{1}>".format(x.name, x.id)
		EmojisFinal = EmojisFinal + Emoji + " "

	EmojisFinal = EmojisFinal.rstrip(" ")
	return EmojisFinal

#####################################################################################################################################################

def getServerEmojis(emojisObjects:list):

	EmojisFinal = "{0:6} {1:10} {2:18}\n----------------------------------------".format("Emote", "Name", 'ID')

	for x in emojisObjects:
		Emoji = "<:{0}:{1}>".format(x.name, x.id)
		line = "\n{0:6} {1:<10} {2:18}".format(Emoji, x.name, x.id)
		EmojisFinal += line

	return EmojisFinal

#####################################################################################################################################################

def getLDStats(pseudo):

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