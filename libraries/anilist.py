# -*- coding: utf-8 -*-

import requests
from random import shuffle
import time
from decimal import *
import sys
import datetime

from libraries.perms import *
from libraries.library import *

from urllib import request
import linecache
import ast

#####################################################################################################################################################

def auth(params):
	q = requests.post('https://anilist.co/api/auth/access_token', params=params)
	auth = q.json()
	token = auth['access_token']

	return token

#####################################################################################################################################################

def getAnimes(anime, token):
	anime = str(anime)
	q = requests.get('https://anilist.co/api/anime/search/{0}'.format(anime), params={'access_token':token})
	data = q.json()
	titles = []
	try:
		if data['error'] == {'status': 200, 'messages': ['No Results.']}:
			raise KeyError('Anime not found')
	except KeyError:
		raise KeyError('Anime not found')
	except Exception:
		pass

	for dt in data:
		titles.append([dt["title_english"], dt["type"]])


	return titles

#####################################################################################################################################################

def getAnimeInfo(anime, token, index:int):
	anime = str(anime)
	q = requests.get('https://anilist.co/api/anime/search/{0}'.format(anime), params={'access_token':token})
	data = q.json()
	data = data[index]
	return data

#####################################################################################################################################################

def getAnimeGenres(data):
	List = data['genres']
	genres = ""

	for genre in List:
		genres += genre + ", "

	genres = genres.rstrip(', ')

	return genres

#####################################################################################################################################################

def formatAnimeDescription(data):
	desc = data['description']
	desc = desc.replace("<br>", "")
	if len(desc) > 800:
		desc = desc[:800]
		desc += "..."
	return desc

#####################################################################################################################################################

def formatAnimeDate(data):

	Message = ""
	date = data['start_date']

	date = str(date)
	split1 = date.split("T")
	date = split1[0]
	split2 = date.split("-")
	date = "{0}/{1}/{2}".format(split2[2], split2[1], split2[0])

	Message += "Started : " + date
	date = data['end_date']

	if date == None :
		return Message
	else:
		date = str(date)
		split1 = date.split("T")
		date = split1[0]
		split2 = date.split("-")
		date = "{0}/{1}/{2}".format(split2[2], split2[1], split2[0])

		Message += " | Finished : " + date

		return Message

#####################################################################################################################################################

def getMangas(manga, token):
	manga = str(manga)
	q = requests.get('https://anilist.co/api/manga/search/{0}'.format(manga), params={'access_token':token})
	data = q.json()
	titles = []
	try:
		if data['error'] == {'status': 200, 'messages': ['No Results.']}:
			raise KeyError('Manga not found')
	except KeyError:
		raise KeyError('Manga not found')
	except Exception:
		pass

	for dt in data:
		titles.append([dt["title_english"], dt["type"]])

	return titles

#####################################################################################################################################################

def getMangaInfo(manga, token, index:int):
	manga = str(manga)
	q = requests.get('https://anilist.co/api/manga/search/{0}'.format(manga), params={'access_token':token})
	data = q.json()
	data = data[index]
	return data

#####################################################################################################################################################