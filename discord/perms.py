# -*- coding: utf-8 -*-

"""Ces fonctions sont utilisées afin de permettre
de récupérer la totalité des données de permissions
des utilisateurs.

Créé par @Sakiut25#7390 (c)"""

#####################################################################################################################################################

def get_perm_admin(user):
	"""Retourne si l'utilisateur a les permissions administrateur ou non"""
	if user.server_permissions.administrator == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_create_instant_invite(user):
	"""Retourne si l'utilisateur a la permission de créer une invitation ou non"""
	if user.server_permissions.create_instant_invite == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_kick_members(user):
	"""Retourne si l'utilisateur a la permission de kick un membre ou non"""
	if user.server_permissions.kick_members == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_ban_members(user):
	"""Retourne si l'utilisateur a la permission de bannir un membre ou non"""
	if user.server_permissions.ban_members == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_channels(user):
	"""Retourne si l'utilisateur a la permission de gérer les channels ou non"""
	if user.server_permissions.manage_channels == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_server(user):
	"""Retourne si l'utilisateur a la permission de gérer le serveur ou non"""
	if user.server_permissions.manage_server == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_add_reactions(user):
	"""Retourne si l'utilisateur a la permission d'ajouter des réactions aux messages ou non"""
	if user.server_permissions.add_reactions == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_send_tts_messages(user):
	"""Retourne si l'utilisateur a la permission d'envoyer des TTS ou non"""
	if user.server_permissions.send_tts_messages == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_messages(user):
	"""Retourne si l'utilisateur a la permission de gérer les messages ou non"""
	if user.server_permissions.manage_messages == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_mute(user):
	"""Retourne si l'utilisateur a la permission de mute ou non"""
	if user.server_permissions.mute_members == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_deafen(user):
	"""Retourne si l'utilisateur a la permission d'assourdir ou non"""
	if user.server_permissions.deafen_members == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_send_embed_links(user):
	"""Returns True if a user’s messages will automatically be embedded by Discord."""
	if user.server_permissions.embed_links == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_attach_files(user):
	"""Retourne si l'utilisateur a la permission d'envoyer des fichiers ou non"""
	if user.server_permissions.attach_files == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_mention_everyone(user):
	"""Retourne si l'utilisateur a la permission de mentionner @everyone ou non"""
	if user.server_permissions.mention_everyone == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_external_emojis(user):
	"""Retourne si l'utilisateur a la permission d'utiliser les emojis externes au serveur ou non"""
	if user.server_permissions.external_emojis == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_change_nickname(user):
	"""Retourne si l'utilisateur a la permission de changer de pseudo ou non"""
	if user.server_permissions.change_nickname == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_nicknames(user):
	"""Retourne si l'utilisateur a la permission de gérer les pseudos des membres du serveur ou non"""
	if user.server_permissions.manage_nicknames == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_roles(user):
	"""Retourne si l'utilisateur a la permission de gérer les rôles du serveur ou non"""
	if user.server_permissions.manage_roles == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_webhooks(user):
	"""Retourne si l'utilisateur a la permission de gérer les webhooks du serveur ou non"""
	if user.server_permissions.manage_webhooks == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

#####################################################################################################################################################

def get_perm_manage_emojis(user):
	"""Retourne si l'utilisateur a la permission de gérer les emojis du serveur ou non"""
	if user.server_permissions.manage_emojis == True:
		return 'Autorisé'
	else:
		return 'Non autorisé'

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
	
	fileName = './token.txt'
	with open(fileName) as f: token = f.read()
	
	return token

#####################################################################################################################################################
