# -*- coding: utf-8 -*-

from 	libraries.library import *
import 	os
import 	pickle

fileName = "./data/casino.data"

########################################################################################################################

def start():
	if os.path.exists(fileName):
		f = open(fileName, "rb")
		d = pickle.Unpickler(f)
		data = d.load()
		f.close()
	else:
		data = {}

	return data

########################################################################################################################

def post(server, user, data, money):
	if server.name in data.keys():
		if user.name in data[server.name].keys():
			data[server.name][user.name] = money
		else:
			uniqueData = {user.name: 500}
			data[server.name].update(uniqueData)
	else:
		uniqueData = {server.name:{user.name: 500}}
		data.update(uniqueData)

	f = open(fileName, "wb")
	p = pickle.Pickler(f)
	p.dump(data)
	f.close()

	return data

########################################################################################################################

def get(server, user, data):
	if server.name in data.keys():
		if user.name in data[server.name].keys():
			return data[server.name][user.name]
		else:
			return 500
	else:
		return 500

########################################################################################################################