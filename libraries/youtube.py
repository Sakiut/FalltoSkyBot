# -*- coding: utf-8 -*-
"""Youtube.com's RSS requester"""

from libraries.perms import *
from libraries.library import *

import feedparser

yt_id = getYoutubeID()

url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + yt_id

#####################################################################################################################################################

def start():
	feed = feedparser.parse(url)
	return feed

#####################################################################################################################################################

def getLastEntry():

	feed = feedparser.parse(url)

	o = feed['entries']
	o = o[0]

	title = o['title']
	author = o['author']
	link = o['link']
	published = o['published']
	published = formatRSSdate(published)
	thumbnail = o['media_thumbnail'][0]['url']
	channel = o['authors'][0]['href']

	entry = {
		'title' : title,
		'author' : author,
		'link' : link,
		'published' : published,
		'channel' : channel,
		'thumbnail' : thumbnail
	}

	return entry

#####################################################################################################################################################

def getAllEntries():

	feed = feedparser.parse(url)

	entries = feed['entries']
	output = []

	for o in entries:
		title = o['title']
		author = o['author']
		link = o['link']
		published = o['published']
		published = formatRSSdate(published)
		thumbnail = o['media_thumbnail'][0]['url']
		channel = o['authors'][0]['href']

		entry = {
			'title' : title,
			'author' : author,
			'link' : link,
			'published' : published,
			'channel' : channel,
			'thumbnail' : thumbnail
		}

		output.append(entry)

	return output

#####################################################################################################################################################

def update(feed):

	last_etag = feed.etag
	last_modified = feed.modified

	feed_update = feedparser.parse(url, etag=last_etag, modified=last_modified)

	o = feed['entries']
	o = o[0]

	if feed_update.status == 304:
		return "304"
	else:
		return "200"

#####################################################################################################################################################