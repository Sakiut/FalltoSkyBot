import requests
from random import shuffle
import time
from decimal import *
import sys
import datetime

from libraries.perms import *
from libraries.library import *

import asyncio
import os
import aiohttp
import html
from bs4 import BeautifulSoup

MAL_USERNAME = getMalID()
MAL_PASSWORD = getMalPasswd()

loop = asyncio.get_event_loop()
auth = aiohttp.BasicAuth(login = MAL_USERNAME, password = MAL_PASSWORD)
session = aiohttp.ClientSession(auth = auth)

#####################################################################################################################################################

def getMalAnime(anime):

	@asyncio.coroutine
	def find_anime(anime):
		result = yield from (
			yield from session.request(
				"GET", 'https://myanimelist.net/api/anime/search.xml', params={"q":anime})).read()
		return result

	q = loop.run_until_complete(find_anime(anime))
	soup = BeautifulSoup(q, 'xml')

	JSON = []

	i = 0
	for entry in soup.find_all('entry'):
		entryDict = {}
		for item in entry.find_all():
			tst = item.encode("utf-8").decode("utf-8")
			tst = tst.split('>')
			title = tst[0].replace('<','')
			title = title.replace('/', '')
			content = tst[1].split('<')[0]
			line = {title:content}
			entryDict.update(line)
		JSON.append(entryDict)
		i += 1

	return JSON

#####################################################################################################################################################

def getMalManga(manga):

	@asyncio.coroutine
	def find_anime(manga):
		result = yield from (
			yield from session.request(
				"GET", 'https://myanimelist.net/api/manga/search.xml', params={"q":manga})).read()
		return result

	q = loop.run_until_complete(find_anime(manga))
	soup = BeautifulSoup(q, 'xml')

	JSON = []

	i = 0
	for entry in soup.find_all('entry'):
		entryDict = {}
		for item in entry.find_all():
			tst = item.encode("utf-8").decode("utf-8")
			tst = tst.split('>')
			title = tst[0].replace('<','')
			title = title.replace('/', '')
			content = tst[1].split('<')[0]
			line = {title:content}
			entryDict.update(line)
		JSON.append(entryDict)
		i += 1

	return JSON

#####################################################################################################################################################

def extractTitles(data):
	titles = []
	for x in data:
		titles.append([x['title'],x['type']])
	return titles

#####################################################################################################################################################