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
from libraries.library import *

from urllib import request
import linecache
import ast

ApiKey = getApiKey()

w = RiotWatcher(ApiKey, default_region=EUROPE_WEST)

#####################################################################################################################################################

def getSummonerInfo(summoner):
	"""Récupère les données d'un invocateur"""
	try:
		user = w.get_summoner(name=summoner)
		return user
	except LoLException as e:
		if e == error_429:
			error = '```py\nWe should retry in {} seconds.\n```'.format(e.headers['Retry-After'])
			return error
		elif e == error_404:
			error = '```py\nSummoner not found.\n```'
			return error

#####################################################################################################################################################

def getSummonerScore(summonerid):
	"""Récupère le score d'un invocateur"""

	summonerid = str(summonerid)
	request = requests.get('https://euw.api.riotgames.com/championmastery/location/EUW1/player/' + summonerid + '/score?api_key=' + ApiKey)

	if request.status_code == 200:
		JsonRequest = request.json()

	return JsonRequest

#####################################################################################################################################################

def getSummonerIconUrl(summoner):
	"""Récupère l'icône d'un invocateur"""
	icon = 'https://avatar.leagueoflegends.com/euw/' + summoner + '.png'
	return icon

#####################################################################################################################################################

def getUnrankedWins(summonerid:str):
    """Récupère le nombre de wins d'un invocateur en Unranked"""

    summonerid = str(summonerid)
    request = requests.get('https://euw.api.riotgames.com/api/lol/EUW/v1.3/stats/by-summoner/' + summonerid + '/summary?api_key=' + ApiKey)

    if request.status_code == 200:
        JsonRequest = request.json()

    StatSummary = JsonRequest['playerStatSummaries']
    Unranked = filter(lambda x: x.get("playerStatSummaryType") == "Unranked", StatSummary)
    UnrankedList = list(Unranked)
    UnrankedDict = UnrankedList[0]
    Wins = UnrankedDict['wins']
    return Wins

#####################################################################################################################################################

def getUnrankedStats(summonerid:str):
    """Récupère les stats complètes d'un invocateur en Unranked"""

    summonerid = str(summonerid)
    request = requests.get('https://euw.api.riotgames.com/api/lol/EUW/v1.3/stats/by-summoner/' + summonerid + '/summary?api_key=' + ApiKey)

    if request.status_code == 200:
        JsonRequest = request.json()

    StatSummary = JsonRequest['playerStatSummaries']
    Unranked = filter(lambda x: x.get("playerStatSummaryType") == "Unranked", StatSummary)
    UnrankedList = list(Unranked)
    UnrankedDict = UnrankedList[0]
    Stats = UnrankedDict['aggregatedStats']
    return Stats

#####################################################################################################################################################

def getGameInfo(summonerid:str):
	"""Récupère les stats complètes d'une game en cours"""

	summonerid = str(summonerid)
	request = requests.get("https://euw.api.riotgames.com/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/" + summonerid + "?api_key=" + ApiKey)

	if request.status_code == 200:
		JsonRequest = request.json()

	elif request.status_code == 404:
		JsonRequest = {"gameId":'404'}

	return JsonRequest

#####################################################################################################################################################

def getRankedStats(summonerid:str):
	"""Récupère les stats complètes d'un invocateur en Ranked"""

	summonerid = str(summonerid)
	request = w.get_stat_summary(summonerid)

	StatSummary = request['playerStatSummaries']
	Ranked = filter(lambda x: x.get("playerStatSummaryType") == "RankedSolo5x5", StatSummary)
	RankedList = list(Ranked)
	if RankedList == []:
		RankedDict = {"wins": 0, "aggregatedStats": {}, "losses": 0, "playerStatSummaryType": "RankedSolo5x5"}
	else:
		RankedDict = RankedList[0]
	return RankedDict

#####################################################################################################################################################

def getRank(summonerid:str):

    try:
        summonerid = str(summonerid)
        summoner = [summonerid]
        request = w.get_league_entry(summoner_ids=summoner, region=EUROPE_WEST)

        Summary = request.get(str(summonerid))
        EntryDict = Summary[0]
        League = EntryDict['tier']
        Entries = EntryDict['entries']
        DivDict = Entries[0]
        Division = DivDict['division']

        Rank = str(League + ' ' + Division)

    except LoLException as e:
        if e == error_404:
            Rank = 'UNRANKED'
        else:
            raise TypeError('Problème de Rank')

    return Rank

#####################################################################################################################################################

def getChampionIconUrl(champ):
    """Récupère l'icone' d'un champion"""
    champ = champ.lower().capitalize()
    icon = 'http://ddragon.leagueoflegends.com/cdn/7.12.1/img/champion/'+ champ +'.png'
    return icon

#####################################################################################################################################################

def getChampionStats(champion):
	"""Récupère les stats d'un champion"""

	champion = str(champion)
	request = requests.get('https://global.api.riotgames.com/api/lol/static-data/EUW/v1.2/champion?api_key=' + ApiKey)

	if request.status_code == 200:
		JsonRequest = request.json()

	DataSummary = JsonRequest['data']
	Champ = DataSummary[champion]
	return Champ

#####################################################################################################################################################

def getChampionInfo(champid):
	"""Récupère les infos d'un champion"""

	champid = str(champid)
	request = requests.get('https://euw.api.riotgames.com/api/lol/EUW/v1.2/champion/' + champid + '?api_key=' + ApiKey)

	if request.status_code == 200:
		request = request.json()

	return request

#####################################################################################################################################################

def getChampionName(champid):
	"""Récupère le nom d'un champion"""

	champid = str(champid)
	request = requests.get('https://global.api.riotgames.com/api/lol/static-data/EUW/v1.2/champion/' + champid + '?api_key=' + ApiKey)

	if request.status_code == 200:
		request = request.json()

	return request['name']

#####################################################################################################################################################

def getChampionGG(champion):

	champion = str(champion)
	url = "http://champion.gg/champion/{}".format(champion)
	fileName = "./lolsource/{}.html".format(champion)
	request.urlretrieve(url, fileName)

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('  matchupData.champion ='):
			getLine = line.rstrip(";\n")
			splitLine = getLine.split("=")
			Lines = splitLine[1].lstrip()
			line3430 = ast.literal_eval(Lines)

	with open(fileName) as f: lines = f.read().splitlines()

	for line in lines:
		if line.startswith('  matchupData.championData'):
			getLine = line.rstrip(";\n")
			splitLine = getLine.split("=")
			Lines = splitLine[1].lstrip()
			line3432 = ast.literal_eval(Lines)

	championStat = {'3430' : line3430, '3432' : line3432}

	return championStat

#####################################################################################################################################################

def getFreeChamps():

	request = requests.get("https://euw1.api.riotgames.com/lol/platform/v3/champions?freeToPlay=true&api_key=" + ApiKey)

	if request.status_code == 200:
		request = request.json()

	content = request['champions']
	freeChamps = []

	for x in content:
		Id = x['id']
		freeChamps.append(str(Id))

	return freeChamps

#####################################################################################################################################################

def getSummonerStats(summoner:str):

	q = requests.get("https://euw1.api.riotgames.com/lol/summoner/v3/summoners/by-name/"+summoner+"?api_key="+ApiKey)

	if q.status_code == 200:
		q = q.json()
	elif q.status_code == 404:
		raise NameError("Summoner not found")
	elif q.status_code == 401:
		raise ImportError("Access denied")
	elif q.status_code == 503:
		raise ImportError("Service down. Please try again later.")
	else:
		raise Exception("An error occured processing this request. Code: {0}".format(str(q.status_code)))

	level = q['summonerLevel']
	name = q['name']
	sum_id = str(q['id'])
	icon = 'https://avatar.leagueoflegends.com/EUW1/' + summoner + '.png'

	#League

	r = requests.get("https://euw1.api.riotgames.com/lol/league/v3/positions/by-summoner/"+sum_id+"?api_key="+ApiKey)

	if r.status_code == 200:
		r = r.json()
	elif r.status_code == 404:
		raise NameError("Summoner not found")
	elif r.status_code == 401:
		raise ImportError("Access denied")
	elif r.status_code == 503:
		raise ImportError("Service down. Please try again later.")
	else:
		raise Exception("An error occured processing this request. Code: {0}".format(str(r.status_code)))

	tier5c5 = "Unranked"
	rank5c5 = "_ _"
	winr5c5 = 'N/A'

	tierflex = "Unranked"
	rankflex = "_ _"
	winrflex = "N/A"

	tier33 = "Unranked"
	rank33 = '_ _'
	winr33 = 'N/A'

	if not r:
		pass
	else:
		for x in r:
			if x['queueType'] == "RANKED_SOLO_5x5":
				tier5c5 = x['tier']
				rank5c5 = x['rank']
				winr5c5 = str("{0:3.2f}".format((x['wins'] / (x['wins'] + x['losses'])) * 100)) + " %"
			elif x['queueType'] == "RANKED_FLEX_SR":
				tierflex = x['tier']
				rankflex = x['rank']
				winrflex = str("{0:3.2f}".format((x['wins'] / (x['wins'] + x['losses'])) * 100)) + " %"
			elif x['queueType'] == "RANKED_FLEX_TT":
				tier33 = x['tier']
				rank33 = x['rank']
				winr33 = str("{0:3.2f}".format((x['wins'] / (x['wins'] + x['losses'])) * 100)) + " %"

	#Champ

	r = requests.get("https://euw1.api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/"+sum_id+"?api_key="+ApiKey)

	if r.status_code == 200:
		r = r.json()
	elif r.status_code == 404:
		raise NameError("Summoner not found")
	elif r.status_code == 401:
		raise ImportError("Access denied")
	elif r.status_code == 503:
		raise ImportError("Service down. Please try again later.")
	else:
		raise Exception("An error occured processing this request. Code: {0}".format(str(r.status_code)))

	r = r[:3]

	champ_names = [
		"N/A",
		"N/A",
		"N/A"
	]

	champ_levels = [
		"N/A",
		"N/A",
		"N/A"
	]

	champ_points = [
		"N/A",
		"N/A",
		"N/A"
	]

	if not r:
		pass
	else:
		i = 0
		for x in r:
			champ_names[i] = getChampionName(x['championId'])
			champ_levels[i] = x['championLevel']
			champ_points[i] = x['championPoints']
			i += 1

	best_champ = champ_names[0]
	best_level = champ_levels[0]
	best_point = champ_points[0] / 1000

	sec_champ = champ_names[1]
	sec_level = champ_levels[1]
	sec_point = champ_points[1] / 1000

	tri_champ = champ_names[2]
	tri_level = champ_levels[2]
	tri_point = champ_points[2] / 1000

	data = {
		"name": name,
		"id": sum_id,
		"level": level,
		"icon": icon,
		"tier5c5": tier5c5,
		"rank5c5": rank5c5,
		"winr5c5": winr5c5,
		"tierflex": tierflex,
		"rankflex": rankflex,
		"winrflex": winrflex,
		"tier33": tier33,
		"rank33": rank33,
		"winr33": winr33,
		"best_champ": best_champ,
		"best_level": best_level,
		"best_point": best_point,
		"sec_champ": sec_champ,
		"sec_level": sec_level,
		"sec_point": sec_point,
		"tri_champ": tri_champ,
		"tri_level": tri_level,
		"tri_point": tri_point
	}

	return data

#####################################################################################################################################################

def getChampion(champion):

    champion = str(champion)
    url = "http://champion.gg/champion/{}".format(champion)
    fileName = "./lolsource/{}.html".format(champion)
    request.urlretrieve(url, fileName)
    roles = []
    MainStats = []

    with open(fileName) as f: lines = f.read().splitlines()

    for line in lines:
        if line.startswith('  matchupData.champion ='):
            getLine = line.rstrip(";\n")
            splitLine = getLine.split("=")
            Lines = splitLine[1].lstrip()
            line3430 = ast.literal_eval(Lines)
        if line.startswith('  matchupData.championData'):
            getLine = line.rstrip(";\n")
            splitLine = getLine.split("=")
            Lines = splitLine[1].lstrip()
            line3432 = ast.literal_eval(Lines)

    for role in line3430['roles']:
        roles.append(role['title'])

    id = line3430['id']
    MainStats.append(id)
    stats = {roles[0]: line3432['stats']}
    MainStats.append(stats)

    del roles[0]

    for role in roles:
        url = "http://champion.gg/champion/{}/{}".format(champion, role)
        fileName = "./lolsource/{} - {}.html".format(champion, role)
        request.urlretrieve(url, fileName)

        with open(fileName) as f: ls = f.read().splitlines()

        for l in ls:
            if l.startswith('  matchupData.championData'):
                getLine = l.rstrip(";\n")
                splitLine = getLine.split("=")
                Lines = splitLine[1].lstrip()
                Line3432 = ast.literal_eval(Lines)

        stats = {role: Line3432['stats']}
        MainStats.append(stats)

    return MainStats

#####################################################################################################################################################