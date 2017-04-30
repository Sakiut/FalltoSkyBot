import requests
from random import shuffle
import time
from decimal import *
import sys
import datetime

from riotwatcher import RiotWatcher
from riotwatcher import EUROPE_WEST
from riotwatcher import LoLException, error_404, error_429
from urllib import request
import linecache
import ast

ApiKey = 'RGAPI-cf47a674-15d9-404e-aa6e-67ac5282289b'

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
	icon = 'https://avatar.leagueoflegends.com/EUW1/' + summoner + '.png'
	return icon

#####################################################################################################################################################

def getChampionIconUrl(champ):
	"""Récupère l'icone' d'un champion"""
	icon = 'https://opgg-static.akamaized.net/images/lol/champion/' + champ + '.png'
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

def getRankedStats(summonerid:str):
	"""Récupère les stats complètes d'un invocateur en Ranked"""

	summonerid = str(summonerid)
	request = w.get_stat_summary(summonerid)

	StatSummary = request['playerStatSummaries']
	Ranked = filter(lambda x: x.get("playerStatSummaryType") == "RankedSolo5x5", StatSummary)
	RankedList = list(Ranked)
	RankedDict = RankedList[0]
	return RankedDict

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

def msToHourConverter(ms:int):
	"""Convertit les millisecondes en compteur horaire"""
	s = ms / 1000
	counter = datetime.datetime.fromtimestamp(s).strftime('%H h %M min %S.%f sec')
	return counter

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