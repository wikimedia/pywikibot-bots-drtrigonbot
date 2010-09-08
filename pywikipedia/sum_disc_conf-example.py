# -*- coding: utf-8  -*-

# ####################################################################################################
#
#   This is an example Version for notice and use.
#
#   Rename or copy this file to 'sum_disc_conf.py' and set the options you want.
#
# ####################################################################################################

import re#, os

tmpl_SumDisc = u'''{{Benutzer:DrTrigon/Entwurf/Vorlage:SumDisc
|data=%s
|timestamp=--~~~~%s}}'''

conf = {	# unicode values
		'userlist':			u'Benutzer:DrTrigonBot/Diene_Mir!',
		'maintenance_queue':	u'Benutzer:DrTrigonBot/Maintenance',
		'maintenance_page':	u'Benutzer Diskussion:DrTrigon#%s',
		'maintenance_mesg':	u'BOT MESSAGE',
		'globwiki_notify':	u'Notification',

		'queue_security':	([u'DrTrigon'], u'Bot: exec'),

		# NON (!) unicode values
		##'sitepath':		'/wiki/%s',
		#'sitepath':		'/w/index.php?title=%s',
		'script_path':		'',							# local on a PC
		'logger_path':		"logs/%s.log",						#
#		'script_path':		os.environ['HOME'] + '/pywikipedia/',			# on toolserver
#		'logger_path':		os.environ['HOME'] + "/public_html/DrTrigonBot/%s.log",	# ('/home/drtrigon' + ...)
		'logger_tmsp':		True,
		'backup_hist':		True,

		# regex values
		'tmpl_regex':		re.compile('\{\{Benutzer:DrTrigon/Entwurf/Vorlage:SumDisc(.*?)\}\}', re.S),
		'tmpl_params_regex':	re.compile('(.*?)data=(.*?)\|timestamp=(.*)', re.S),
		'page_regex':		re.compile(r'Page\{\[\[(.*?)\]\]\}'),

		# numeric values
		'timeout':		15.0,							# timeout for progress info display

		# list values
		# which lists are regex to compile ('backlinks_list' are no regex)
		#'regex_compile':	[ 'checkedit_list', 'checksign_list', 'ignorepage_list', 'directgetfull_list', ],
		'regex_compile':	[ 'checkedit_list', 'ignorepage_list', 'directgetfull_list', 'ignorehead_list', ],
		# which lists may contain variables to substitute
		#'vars_subst':		[ 'checkedit_list', 'checksign_list', 'ignorepage_list', 'backlinks_list', 'altsign_list' ],
		'vars_subst':		[ 'checkedit_list', 'ignorepage_list', 'backlinks_list', 'altsign_list' ],	# + 'ignorehead_list' ?
		# which lists should preserve/keep their defaults (instead of getting it overwritten by user settings)
		'default_keep':		[ 'checkedit_list', 'altsign_list' ],

		# bot paramater/options (modifiable by user)
		'param_default':	{ 'checkedit_count':	500,				# CHECK recent EDITs, a COUNT
					#'checkedit_count':	1000,
					'reportchanged_switch':	True,				# REPORT CHANGED discussions, a SWITCH
					'getbacklinks_switch':	False,				# GET BACKLINKS additionally, a SWITCH
					'reportwarn_switch':	True,				# (not published yet)
#					'reportwarn_switch':	False,				# 
					'globwikinotify_switch':False,				# GET OTHER WIKIS NOTIFICATIONS additionally, a SWITCH
					'reportclosed_switch':	True,				# (not published yet)
					# LIST of talks/discussions to SEARCH, a LIST
					'checkedit_list':	[ '^(.*?Diskussion:.*)',
								u'^(Wikipedia:Löschkandidaten/.*)',
								u'^(Wikipedia:Qualitätssicherung/.*)',
								u'^(Wikipedia:Löschprüfung)',
								'^(Wikipedia:Fragen zur Wikipedia)',
								'^(Portal:.*)',
								'^(Wikipedia:WikiProjekt.*)',
								'^(Wikipedia:Redaktion.*)',
								'^(Wikipedia:Auskunft)',
								u'^(Wikipedia:Café)',
								u'^(Wikipedia:Verbesserungsvorschläge)',	# macht ev. probleme wegen level 1 überschr.
								'^(Wikipedia:Tellerrand)',
								'^(Wikipedia:Urheberrechtsfragen)',
								'^(Wikipedia:Vandalismusmeldung)',
								u'^(Wikipedia:Administratoren/Anfragen)',
								u'^(Wikipedia:Administratoren/Notizen)',
								#u'^(Wikipedia:Administratoren/.*)',
								u'^(Wikipedia:Diskussionen über Bilder)',
								u'^(Wikipedia:Fotowerkstatt)',				# [F46]
								u'^(Wikipedia:Bilderwünsche)',				#
								u'^(Wikipedia:Grafikwerkstatt)',			#
								u'^(Wikipedia:Grafikwerkstatt/Grafikwünsche)',		#
								u'^(Wikipedia:Kartenwerkstatt)',			#
								u'^(Wikipedia:Kartenwerkstatt/Kartenwünsche)', ],	#
					# (not published yet)
					# ev. sogar [\]\|/#] statt nur [\]\|/] ...?! dann kann Signatur auch links auf Unterabschn. enth.
					# liefert leider aber auch falsch positive treffer... wobei seiten, die mal die aufmerksamkeit geweckt
					# haben (auf RecentChanges-Liste waren) und links in user-namensraum enthalten, sind auch interessant!!
					# (und eher selten, etwa 1 pro user bei ca. 100 in history)
					'checksign_list':	[ '\[\[Benutzer:%(usersig)s[\]\|/]',			
								'\[\[Benutzer[ _]Diskussion:%(usersig)s[\]\|/]',
								'\[\[User:%(usersig)s[\]\|/]',			
								'\[\[User[ _]talk:%(usersig)s[\]\|/]', ],
					# LIST of SIGNATUREs to USE, a LIST
					'altsign_list':		[ '%(username)s' ],
					# LIST of PAGEs to IGNORE, a LIST
					# Alles mit '.*/Archiv.*' könnte man ruhig ausschließen - da passiert ja eh nichts
					# und der Bot muss sich nicht mit so großen Seiten rumschlagen. -- Merlissimo 14:03, 31. Jan. 2009 (CET)
					# (sofern auf diesen Seiten nichts geändert wird, tauchen sie gar nicht auf...)
					'ignorepage_list':	[ u'(.*?)/Archiv', ],		# + weitere 
					# (not published yet)
					'backlinks_list':	[ u'%(userdiscpage)s',
								u'Benutzer:%(username)s', ],
					# (not published yet: LIST OF PAGEs to use MODE=FULL for reading DIRECTly, a LIST)
					'directgetfull_list':	[ u'^(Wikipedia:Löschkandidaten/\d.*)' ],
					# (hidden)
					#userResultPage: default is NOT DEFINED - this is a SPECIAL PARAM it is not
					#		 thought to be used explicit, it is defined by the page link (implicit).
					# (not published yet: LIST of HEADs to IGNORE, a LIST)
					'ignorehead_list':	[ u'(.*?) \(erl.\)', ],
					}
}

# debug tools
#debug = { 'write2wiki': True,				# operational mode (default)
#	  'user':	False,
#	  'write2hist': True,
#	  'toolserver': False, }
##debug = { 'write2wiki': False, 'user': True, 'write2hist': False, 'toolserver': False, }	# no write, skip users
##debug = { 'write2wiki': False, 'user': True, 'write2hist': True, 'toolserver': False, }	# write only history, skip users
##debug = { 'write2wiki': False, 'user': False, 'write2hist': False, 'toolserver': False, }	# no write, all users
##debug = { 'write2wiki': True, 'user': True, 'write2hist': True, 'toolserver': False, }	# write, skip users
debug = { 'write2wiki': False, 'user': False, 'write2hist': True, 'toolserver': False, }	# write only history (for code changes and smooth update)
##debug = { 'write2wiki': True, 'user': True, 'write2hist': False, 'toolserver': False, }	# write wiki, skip users
##debug = { 'write2wiki': False, 'user': False, 'write2hist': True, 'toolserver': True, }	# write only history (for code changes and smooth update), toolserver down

