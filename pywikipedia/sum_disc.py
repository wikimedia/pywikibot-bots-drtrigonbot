# -*- coding: utf-8  -*-
"""
This bot is used for summarize discussions spread over the whole wiki
including all namespaces. It checks several users (at request), sequential 
(currently for the german wiki [de] only).

The bot will only change the user's discussion page by appending a summary
reports (that is also used as history for further runs).

The bot's operating procedure:
  -retrieve user list from [[Benutzer:DrTrigonBot/Diene_Mir!]]
  -check recent changes in [[Special:Contributions/<user>]] (Spezial:Beiträge/...)
  -retrieve history from file
  -checking each listed Discussion on time of latest change
  -checks relevancy by searching each heading with user signature in body, if any
   found, checks them on changes and finally if the user signature is the last one
   (or if there is any foreign signature behind it)
  -appending history to local user history file (same as summary report, can also
   be redirected on a page in the wiki if useful)
  -appending summary report to [[Benutzer Diskussion:<user>]]

This bot code and 'wikipedaiAPI.py' work with UTC/GMT ONLY beacuse of DST!! For
output to wiki in 'parseNews' the time is localized first!

The code is still very much alpha level and the scope of what it can do is
still rather limited, only 1 part of speech, only 1 (different) Wiktionary
output formats, no langnames matrix.

After running the bot the first time for an user there will be a log file
used as history. By running the bot about once a week or once a month should
be sufficient the be up-to-date. The bot could also be runned continous e.g.
on the toolserver, at a very low speed, what should be fast enougth to check
the few number of users.

Entries can be changed (deleted for example when the discussion is finished) that
will cause no problem for the bot, because the entries are also written to the
history.

The following parameters are supported:

&params;

All other parameters will be ignored.

Syntax example:
    python sum_disc.py
        Default operating mode. Run for all users requested.

    python sum_disc.py -compress_history:['User1','User2',...]
        Loads history of User and strips all redundant information, e.g. old
        entries from the file. (speeds up the reading and processing of history,
        shrinks the file size and creates also a backup of old history)

    python sum_disc.py -compress_history:[]
        (same as before but processes ALL users)

    python sum_disc.py -rollback_history:[number of runs to roll-back]
        Loads old history entry of all Users, e.g. for debuging.
"""
#
#    python sum_disc.py -test_run
#        Loads old history entry of all Users, e.g. for debuging.
#"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: sum_disc.py 0.2.0021 2009-11-15 00:38 drtrigon $'
#


import re, sys
import time, codecs, os, calendar
import threading
import copy #, zlib
import sets, string, datetime, hashlib

import config, pagegenerators, userlib
#import config, pagegenerators, userlib
import dtbext, dtbext_basic
# Splitting the bot into library parts
import wikipedia as pywikibot


bot_config = {	# unicode values
		'TemplateName':		u'Benutzer:DrTrigon/Entwurf/Vorlage:SumDisc',
		'userlist':		u'Benutzer:DrTrigonBot/Diene_Mir!',
		'maintenance_queue':	u'Benutzer:DrTrigonBot/Maintenance',
		'maintenance_page':	u'Benutzer Diskussion:DrTrigon#%s',
		'maintenance_mesg':	u'BOT MESSAGE',
		'globwiki_notify':	u'Notification',

		'queue_security':	([u'DrTrigon'], u'Bot: exec'),

		# NON (!) unicode values
		'script_path':		'',							# local on a PC
		'logger_path':		"logs/%s.log",						#
#		'script_path':		os.environ['HOME'] + '/pywikipedia/',			# on toolserver
#		'logger_path':		os.environ['HOME'] + "/public_html/DrTrigonBot/%s.log",	# ('/home/drtrigon' + ...)
		'logger_tmsp':		True,
		'backup_hist':		True,

		# regex values
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
debug = { 'write2wiki': False, 'user': True, 'write2hist': False, 'toolserver': False, }	# no write, skip users
##debug = { 'write2wiki': False, 'user': True, 'write2hist': True, 'toolserver': False, }	# write only history, skip users
##debug = { 'write2wiki': False, 'user': False, 'write2hist': False, 'toolserver': False, }	# no write, all users
##debug = { 'write2wiki': True, 'user': True, 'write2hist': True, 'toolserver': False, }	# write, skip users
debug = { 'write2wiki': False, 'user': False, 'write2hist': True, 'toolserver': False, }	# write only history (for code changes and smooth update)
##debug = { 'write2wiki': True, 'user': True, 'write2hist': False, 'toolserver': False, }	# write wiki, skip users
##debug = { 'write2wiki': False, 'user': False, 'write2hist': True, 'toolserver': True, }	# write only history (for code changes and smooth update), toolserver down

#trans_str = {		# from wikilanguage to 'en'
#	# translations for 'User'
#	u'Benutzer':	u'User',
#
#	# translations for 'Discussion'
#	u'Diskussion':	u'Discussion',
#}

docuReplacements = {
#    '&params;': pagegenerators.parameterHelp
    '&params;': u''
}


class SumDiscBot(dtbext_basic.BasicBot):
	'''
	Robot which will check your latest edits for discussions and your old
	discussions against recent changes, pages to check are provided by a
	list. (iterable like generators)
	'''
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	silent		= False
	rollback	= 0

	_param_default		= bot_config['param_default']			# same ref, no copy
	_eol_regex		= re.compile('\n')
	_bracketopen_regex	= re.compile('\[')
	_bracketclose_regex	= re.compile('\]')
	_reftag_err_regex	= re.compile(r'<strong class="error">Referenz-Fehler: Einzelnachweisfehler: <code>&lt;ref&gt;</code>-Tags existieren, jedoch wurde kein <code>&lt;references&#160;/&gt;</code>-Tag gefunden.</strong>')
	_timestamp_regex	= re.compile('--(.*?)\(CEST\)')

	_PS_warning	= 1	# serious or no classified warnings/errors that should be reported
	_PS_changed	= 2	# changed page   (if closed, will be removed)
	_PS_unchanged	= 3	# unchanged page
	_PS_new		= 4	# new page
	_PS_closed	= 5	# closed page (remove it from history)
	_PS_maintmsg	= 6	# maintenance message
	_PS_notify	= 7	# global wiki notification

	_global_warn	= []
	_oth_list	= {}

	def __init__(self, userListPage):
		'''Constructor of SumDiscBot(); setup environment, initialize needed consts and objects.
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 30, 17)

		dtbext_basic.BasicBot.__init__(self, bot_config)

		# init constants
        	self._userListPage = dtbext.pywikibot.Page(self.site, userListPage)
		#print [item[0] for item in self._getUsers()]		#enhance 'ignorepage_list'

		pywikibot.output(u'** Receiving User List (wishes): %s' % self._userListPage)
		self._user_list = dtbext.config.getUsersConfig(self._userListPage)

		pywikibot.output(u'** Receiving Job Queue (Maintenance Messages)')
		page = dtbext.pywikibot.Page(self.site, bot_config['maintenance_queue'])
		self.maintenance_msg = dtbext.config.getJobQueue(page, bot_config['queue_security'], debug = debug['write2wiki'])

		# init variable/dynamic objects

	def run(self):
		'''
		run SumDiscBot()
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24, 38, 17)


		#pywikibot.output(u'\03{lightgreen}* Processing User List (wishes): %s\03{default}' % self._userListPage)
		pywikibot.output(u'\03{lightgreen}* Processing User List (wishes):\03{default}')

		if debug['user']: pywikibot.output(u'\03{lightred}=== ! DEBUG MODE USERS WILL BE SKIPPED ! ===\03{default}')

		for user in self._user_list:					# may be try with PreloadingGenerator?!
			if (debug['user'] and (user[0] != 'DrTrigon')):	continue

			self._setUser(user)					# set user and init params

			pywikibot.output(u'\03{lightgreen}** Processing User: %s\03{default}' % self._user)

			self.loadMode(self._userPage)				# get operating mode
			self._work_list = {}

			#self._getHistory()					# get history entries
			self.getHistoryPYF(rollback=self.rollback)
			self._work_list.update( self._hist_list )

			# JUST A TEMPORARY PATCH FOR HISTORY			# SHOULD BE REMOVED LATER!
			# e.g. 'dewiki:...' --> 'de:...'
			self._work_list = dict([ (key.replace(u'wiki:', u':'), self._work_list[key]) for key in self._work_list.keys() ])

			addition = self.checkRecentEdits()			# check special pages for latest contributions
			self._work_list.update( addition )			#

			if self._param['getbacklinks_switch']:			# get the backlinks to user disc page
				addition = self.getUserBacklinks()		#
				self._work_list.update( addition )		#
				# all pages served from here ARE CURRENTLY SIGNED (have a Signature at the moment)

			# (history war bisher HIER)

			if self._param['globwikinotify_switch']:		# [F38] get global wiki notifications (toolserver/merl)
				addition = self.getGlobalWikiNotifications()	#
				self._work_list.update( addition )		#

			self.getLatestNews()					# check for news to report

			#print self._work_list
			continue
# debug here ^^^
			self._checkRelevancyTh()				# check self._news_list on relevancy, disc-thread oriented version...

			self._AddMaintenanceMsg()				# gehen auch in jede history... werden aber bei compress entfernt

			self._postDiscSum()					# post results to users Discussion page (with comments for history)

		pywikibot.output(u'\03{lightgreen}* Processing Warnings:\03{default}')

		for warning in self._global_warn:		# output all warnings to log (what about a special wiki page?)
			pywikibot.output( "%s: %s" % warning )	

	def compressHistory(self, users = []):
		'''
		read history, and re-write new history without any duplicates

		input:  users [list]
                        self-objects
		returns:  (truncated rewritten history file, nothing else)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 32, 17)

		if not users: users = [ item[0] for item in self._user_list ]

		pywikibot.output(u'* Compressing of histories:')

		if bot_config['backup_hist']:
			timestmp = dtbext.date.getTimeStmp()
			pathname = '%slogs/%s/' % (bot_config['script_path'], timestmp)	# according to '_setUser'
			os.mkdir(pathname)
			import shutil

		for user in users:
			self._setUser((user,{}))

			try:
				begin = float(os.path.getsize(self._datfilename))
			except OSError:		# OSError: [Errno 2] No such file or directory
				continue

			# backup old history
			if bot_config['backup_hist']:
				dst = os.path.join(pathname, os.path.basename(self._datfilename))
				shutil.copyfile(self._datfilename, dst)

			# truncate histroy (drop old entries)
			self.getHistoryPYF()

			# write new history
			os.remove(self._datfilename)
			self._appendFile( str(self._hist_list).decode('latin-1') )

			end = float(os.path.getsize(self._datfilename))

			pywikibot.output(u'** History of %s compressed and written. (%s %%)' % (user, (end/begin)*100))

	def getHistoryPYF(self, rollback = 0):
		buf = self.loadFile()
		buf = bot_config['page_regex'].sub('[]', buf)
		buf = self._eol_regex.split(buf)
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		# merge everything to one history
		news = {}
		usage = {}
		rollback_buf = []
		self._hist_list = {}
		for item in buf:
			if len(item.strip())==0: continue
			news_item = eval(item)
			#news.update( news_item )
			# news.update BUT APPEND the heading data in the last tuple arg
			# additionally provide backwards support and convert all formats to v5 (longer v3 / with dict)
			for key in news_item.keys():
				if (len(news_item[key]) == 5):				# old history format
					news_item[key] += (self._PS_unchanged,)
					usage['old history'] = True
				if key in news:		# APPEND the heading data in the last tuple arg
					if news_item[key][5] in [self._PS_closed]:
						del news[key]
					else:
						heads = news[key][4]
						heads.update( news_item[key][4] )
						news[key] = (news_item[key][0], news_item[key][1], news_item[key][2], news_item[key][3], heads)
				else:
					news[key] = news_item[key]
			rollback_buf.append( copy.deepcopy(news) )
		if rollback_buf:
			rollback_buf.reverse()
			i = min([rollback, (len(rollback_buf)-1)])
			self._hist_list = rollback_buf[i]
			del rollback_buf
			usage['rollback'] = i

		pywikibot.output(u'*** History recieved %s' % str(usage))

	def getLatestNews(self):
		'''
		check latest contributions on recent news

		input:  self._work_list [list]
                        self-objects
		returns:  self._news_list [dict]
		          keys are:  page titles [string (unicode)]
		          format:    (type_desc_str, page, lastedit_user, lastedit_time, checksum) [tuple]
                          self._oth_list [dict] (same format as self._news_list)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 30, 28, 17)

		#switch = self._param['reportchanged_switch']

		localinterwiki = self.site.dbName().replace('_p', '').lower() + ':'	# better than http://toolserver.org/~vvv/wikis.php
		localinterwiki_len = len(localinterwiki)

		# check for news to report
		self._news_list = {}
		self._oth_list = {}
		size = len(self._work_list)
		j = 0
		#sites = dtbext.pywikibot.Pages(self.site, self._work_list.keys())
		#actual_dict = sites.getVersionHistory()
#gen1 = pagegenerators.PagesFromTitlesGenerator(self._user_list)
## Preloads _contents and _versionhistory
## (DOES NOT USE API YET! / ThreadedGenerator would be nice!)
#gen2 = pagegenerators.PreloadingGenerator(gen)
		actual_dict = list(dtbext.pagegenerators.VersionHistoryGenerator(self._work_list.keys()))
		print len(actual_dict), len(self._work_list.keys())
		return
		#for item in self._work_list:
		for keys in self._work_list.keys():
			item = self._work_list[keys]

			if (len(item) >= 6) and (item[5] == self._PS_notify):		# global wiki notifications
				if (keys in self._hist_list.keys()) and (item[3] == self._hist_list[keys][3]): continue
				if (keys[:localinterwiki_len].lower() == localinterwiki):					# SKIP local global wiki notify
					pywikibot.output(u'INFO: skipping global wiki notify to local wiki [[%s]]' % keys)	#
					continue										#

				self._oth_list[keys] = item
				continue

			page = dtbext.pywikibot.Page(self.site, keys)		# oder auch 'dtbext.pywikibot.PageFromPage(page)' ...
			#if (self._transPage(page).title() == self._userPage.title()):	continue
			skip = False
			for check in self._param['ignorepage_list']:			# ignorelist
				#if (page.title()[-len(check):] == check):
				if check.search(page.title()):
					skip = True
					break
			if skip: continue
			if len(re.split('#', keys)) > 1:						# SKIP old BOT MESSAGES
				pywikibot.output(u'INFO: skipping old bot message at [[%s]]' % keys)	# (code BECOMES OBSOLETE !!!)
				continue								#

			actual = actual_dict[page.sectionFreeTitle()]

			if sites.isRedirectPage(keys):
				pywikibot.output(u'INFO: skipping redirect at [[%s]]' % keys)		#
				continue

			#try:	actual = page.getVersionHistory(revCount=1)[0]
			#except:	continue
			if not actual:			# no version history found, page deleted?
				#if (page.title() in self._hist_list) and (self._hist_list[page.title()][5] == self._PS_warning):
				#	pass
				#else:
				self._oth_list[page.title()] = (	u'no version history found, page deleted!', 
								page, 
								None, 
								None, 
								None, 
								self._PS_warning )
				#pywikibot.output(u'INFO: skipping [[%s]], no version history/page deleted/missing' % keys)
				continue

			actual = actual[0]
			j += 1
			if page.title() in self._hist_list:
				#if (not (self._hist_list[page.title()][3] == actual[1])) and switch:	# discussion has changed, some news?
				if (not (self._hist_list[page.title()][3] == actual[1])):		# discussion has changed, some news?
					self._news_list[page.title()] = (	u'Discussion changed', 
									page, 
									actual[2], 
									actual[1], 
									self._hist_list[page.title()][4], 
									self._PS_changed )
				else:									# nothing new to report (but keep for history and update it)
					self._oth_list[page.title()] = (	self._hist_list[page.title()][0], 
									page, 
									actual[2], 
									actual[1], 
									self._hist_list[page.title()][4], 
									self._PS_unchanged )
			else:										# new discussion, some news?
				self._news_list[page.title()] = (	u'New Discussion', 
								page, 
								actual[2], 
								actual[1], 
								{},
								self._PS_new )

		# time patch not needed anymore, the checksum in relevancy check will save you!! :)
		if ( (len(self._news_list) == j) and (j != 0) ):
			if self.silent:
				#pywikibot.output(u'!!! WARNING: POSSIBLE Time problem ignored!')
				self._oth_list[self._userPage.title()] = (	u'POSSIBLE Time problem ignored!', 
									self._userPage, 
									None, 
									None, 
									None, 
									self._PS_warning )
			else:
				choice = pywikibot.inputChoice('!!! WARNING: EVERYTHING (%i) seems to be new!? Time problem?? Continue anyway?' % j, ['Yes', 'No'], ['y', 'n'])
				if choice == 'n': sys.exit()

		pywikibot.output(u'*** Latest News searched')

	def checkRecentEdits(self):
		'''
		check wiki on recent contributions of specific user

		input:  self-objects
		returns:  [dict]
		          format:    like self._news_list
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		check_list = self._param['checkedit_list']
		count = self._param['checkedit_count']

		pywikibot.output(u'Getting latest contributions from user "%s" via API...' % self._user)	# should be done in framework

		# thanks to http://www.amk.ca/python/howto/regex/ and http://bytes.com/forum/thread24382.html
		usersumList = [p.title() for p in pagegenerators.UserContributionsGenerator(self._user, number = count)]

		work_list = {}
		for item in usersumList:
			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					work_list[match.group(1)] = ()
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'*** Latest %i Contributions checked' % len(usersumList))

		return work_list

	# created due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24)
	def getUserBacklinks(self):
		'''
		check wiki on backlinks to specific user

		input:  self-objects
		returns:  [dict]
		          format:    like self._news_list
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		# according to 'checkRecentEdits(...)'
		check_list = self._param['checkedit_list']

		userbacklicksList = []
		for item in self._param['backlinks_list']:
			page = dtbext.pywikibot.Page(self.site, item)		# important for the generator to use the API
			userbacklicksList += [p.title() for p in pagegenerators.ReferringPageGenerator(page, withTemplateInclusion=False)]	# DOES THIS PRESERVE THE ORDER?!?!??
		userbacklicksList = list(sets.Set(userbacklicksList))			# drop duplicates

		work_list = {}
		for item in userbacklicksList:
			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					work_list[match.group(1)] = ()
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'*** %i Backlinks to user checked' % len(userbacklicksList))

		return work_list

	# created due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38)
	def getGlobalWikiNotifications(self):
		'''
		check if there are any (global) messages on a other wiki for same user!!

		input:  self-objects
                        dtbext.pywikibot-objects
		returns:  [dict]
		          format:    like self._news_list
		'''

		if debug['toolserver']:
			pywikibot.output(u'\03{lightred}=== ! DEBUG MODE TOOLSERVER ACCESS WILL BE SKIPPED ! ===\03{default}')
			return

		# according to '_AddMaintenanceMsg(...)', 'getUserBacklinks'
		work_list = {}
		for page in dtbext.pagegenerators.GlobalWikiNotificationsGenerator(self._user):
			data = page.extradata
			#work_list[page.title()] = (bot_config['globwiki_notify'], page, data['user'], data['timestamp'], {u'':('',True,u'')}, self._PS_notify)
			work_list[data[u'link']] = (bot_config['globwiki_notify'], page, data['user'], data['timestamp'], {u'':('',True,u'')}, self._PS_notify)
			#self._hist_list[page.title()] = self._news_list[page.title()]

		pywikibot.output(u'*** %i Global wiki notifications added' % len(work_list))

		return work_list

	def _postDiscSum(self):
		'''
		post discussion summary of specific user to discussion page and write to histroy
		( history currently implemented as local file, but wiki page could also be used )

		input:  self._news_list [dict]
                        self.loadMode()
                        self-objects
		returns:  (appends self._news_list to the history file, nothing else)
		'''

		#count = len(self._news_list.keys())
		(buf, count) = self._parseNews()
		if (count > 0):
			pywikibot.output(u'='*50 + u'\n' + buf + u'\n' + u'='*50)
			pywikibot.output(u'[%i entries]' % count )

			if debug['write2wiki']:
				self.loadMode()			# get operating mode and contend AGAIN to be ACTUAL !!!
				#pywikibot.setAction(u'Diskussions Zusammenfassung hinzugefügt: %i neue und %i veränderte' % (3, 7))
				if not self._mode:
					# default: write direct to user disc page
					pywikibot.setAction(u'Diskussions-Zusammenfassung hinzugefügt: %i Einträge' % count)
					self._appendPage(self._userPage, buf, minorEdit = False)
				else:
					# enhanced (with template): update user disc page and write to user specified page
					tmplsite = pywikibot.Page(self.site, self._tmpl_data)
					pywikibot.setAction(u'Diskussions-Zusammenfassung aktualisiert: %i Einträge in [[%s]]' % (count, tmplsite.title()) )
					self.save(self._userPage, self._content, minorEdit = False)
					pywikibot.setAction(u'Diskussions-Zusammenfassung hinzugefügt: %i Einträge' % count)
					self._appendPage(tmplsite, buf)
				purge = dtbext.pywikibot.PageFromPage(self._userPage).purgeCache()	# I hope (!) this works now, but is it still needed?!??

				pywikibot.output(u'*** Discussion updates added to: %s (purge: %s)' % (self._userPage.title(asLink=True), purge))
			else:
				pywikibot.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

			if debug['write2hist']:
				#self._appendFile( str(self._news_list).decode('latin-1') )
				self._appendFile( str(self._hist_list).decode('latin-1') )
				#self._appendFile( str(self._hist_list).encode('zlib') )
				#self._appendFile( zlib.compress(str(self._hist_list).decode('latin-1'), 9) )
				pywikibot.output(u'*** History updated')
			else:
				pywikibot.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO HISTORY ! ===\03{default}')
		else:
			pywikibot.output(u'*** Discussion up to date: NOTHING TO DO')

	# look into (pywikibot.)textlib.translate()
	#
	#def _transPage(self, page):
	#	'''
	#	???
	#	'''
	#	title = page.title()
	#	for item in trans_str.keys():
	#		title = re.sub(item, trans_str[item], title)
	#	return pywikibot.Page(self.site, title)

	def _appendPage(self, page, data, minorEdit = True):
		'''
		append to wiki page

		input:  page
                        data [string (unicode)]
		returns:  (appends data to page on the wiki, nothing else)
		'''

		pywikibot.output(u'\03{lightblue}Appending to Wiki on %s...\03{default}' % page.title(asLink=True))
		try:
			content = page.get() + u'\n\n'
			#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
			#	pywikibot.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.title(asLink=True))
			#	continue
		except (pywikibot.NoPage, pywikibot.IsRedirectPage):
			content = u''

		#if archiveURL:
		#	archiveMsg = pywikibot.translate(self.site, talk_report_archive) % archiveURL
		#else:
		#	archiveMsg = u''
		#content += pywikibot.translate(self.site, talk_report) % (errorReport, archiveMsg)
		content += data
		try:
			if minorEdit:	page.put(content)
			else:		page.put(content, minorEdit = False)
		except pywikibot.SpamfilterError, error:
			pywikibot.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (page.title(asLink=True), "error.url"))

	def _checkRelevancyTh(self):
		'''
		check relevancy of page by searching specific users signature
		(improved, disc-thread oriented version)

		input:  self._news_list [dict]
                        self._oth_list [dict] (same format as self._news_list)
                        self.load() (with 'full=' and without)
                        dtbext.pywikibot-objects
                        self-objects (such as self._getThContent(), self._checkThData(), ...)
		returns:  self._news_list [dict]
		          keys are:  page titles [string (unicode)]
		          format:    (type_desc_str, page, lastedit_user, lastedit_time, checksum) [tuple]
                          self._hist_list [dict] (same format as self._news_list)
                (but checksum is updated and all irrelevant entries are deleted from output)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 29, 17)

		def test(timerobj): pywikibot.output(u'\03{lightaqua}progress: %.1f%s (%i of %i) ...\03{default}' % (((100.*timerobj.kwargs['u'])/timerobj.kwargs['size']), u'%', timerobj.kwargs['u'], timerobj.kwargs['size']))
		t = Timer(bot_config['timeout'], test, size = len(self._news_list.keys()), u = 0)

		# self._news_list contents all 'self._PS_changed' and 'self._PS_new'
		self._hist_list = copy.deepcopy(self._news_list)
		pages = dtbext.pywikibot.Pages(self.site, self._news_list.keys())
		# kleiner speed-up patch, als option/parameter aktivierbar
		if self._param['directgetfull_list']: issues = ( self._param['directgetfull_list'], ['full']*len(self._param['directgetfull_list']) )
		else:	issues = None
		if (t.kwargs['size'] != 0): t.run()
		for (site, buf) in self.loadPages( pages, issues=issues ):
			#(site, buf) = page
			keys = site.title()

			t.kwargs['u'] += 1
			#keys = re.split('#', keys)[0]		# Seiten mit Unterabschnitten (falls Abschn. weg aber Seite noch da)
								# (eigentlich nur für bot maint. messages)

			try:
				##if not (keys == u"Benutzer Diskussion:Merlissimo"): continue
				##site = self._news_list[keys][1]			# geht DAS ?!?

				(head, body) = self._getThContent(site, buf)

				relevant = False
				sign_rel = False
				try:	checksum = self._news_list[keys][4]
				except:	checksum = None
				#print keys, checksum
				checksum_new = {}
				for i, item in enumerate(head):		# iterate over all headings/sub sections
					item = body[i]
					heading = head[i][0].strip()

					skip = False								# ignorelist for headings
					for check in self._param['ignorehead_list']:				#
						if check.search(heading):					#
							skip = True						#
							break							#
					if skip: continue							#

					(probable, checksum_cur, hires_probable) = self._checkThData(item, checksum, heading)

					sign_rel = sign_rel or hires_probable['sign']	# signature check

					if not probable: continue	# we just want checksums for headings where user is parcitipating

					#relevant = relevant or probable					# is this page relevant?
					relevant = True								#
					checksum_new[heading] = (checksum_cur, probable, head[i][1].strip())	# is this heading relevant?
				d = self._news_list[keys]
				self._news_list[keys] = d[0:4] + (checksum_new,) + d[5:]
				self._hist_list[keys] = self._news_list[keys]
			except pywikibot.SectionError:	# is typically raised by ????????
				relevant = False

			# if no signature exists, don't list discussion because it's irrelevant
			if not relevant:
				entry = self._news_list[keys]

				del self._news_list[keys]
				if (entry[5] == self._PS_new): del self._hist_list[keys]

				if (not sign_rel) and (entry[5] == self._PS_changed):	# discussion closed (no signature on page anymore)
					self._news_list[keys] = (	u'Discussion closed', 
								site, 
								entry[2], 
								entry[3], 
								{}, 
								self._PS_closed )
					#del self._hist_list[keys]
					self._hist_list[keys] = self._news_list[keys]

		t.cancel()
		del t

		# self._oth_list contents all 'self._PS_unchanged' and warnings 'self._PS_warning'
		for keys in self._oth_list.keys():
			if (self._oth_list[keys][5] == self._PS_unchanged):	# 'self._PS_unchanged'
				#self._hist_list[keys] = self._oth_list[keys]
				pass
			elif (self._oth_list[keys][5] == self._PS_notify):	# 'self._PS_notify'
				self._news_list[keys] = self._oth_list[keys]
				self._hist_list[keys] = self._oth_list[keys]
			else:							# warnings: 'self._PS_warning', ...
				self._news_list[keys] = self._oth_list[keys]

		pywikibot.output(u'*** Relevancy of threads checked')

	def _getThContent(self, page, buf):
		'''
		helper for '_checkRelevancyTh' ('check relevancy of page by
		searching specific users signature')

		retrieves the page content and splits it to headings and bodies

		input:  page
                        buf [string (unicode)]
		returns:  [tuple]
		          format:    (head [list], body [list]) [tuple]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 26, 17)

		site = page

		dtbext.pywikibot.addAttributes( page )		# enhance to dtbext.pywikibot.Page
		#try:
		sections = page.getSections(minLevel=1, pagewikitext=buf)
		#except pywikibot.Error:
		#	pass	# sections could not be resoled, process the whole page at once

		if len(sections) == 0:
			head = [('','')]
			body = [buf]
		else:
			head = []
			body = []
			body_part = []
			actual_head = sections.pop(0)
			buf_list = buf.split('\n')
			for i, item in enumerate(buf_list):
				if (i == actual_head[0]):	# actual_head = (line, level, link, wikitext)
					body.append( u'\n'.join(body_part) )
					body_part = []
					head.append( actual_head[2:4] )
					try:	actual_head = sections.pop(0)
					except:	actual_head = (len(buf_list)+1,)
				else:
					body_part.append( item )
			body.append( u'\n'.join(body_part) )
			body.pop(0)

		return (head, body)

	def _checkThData(self, data, checksum, heading):
		'''
		helper for '_checkRelevancyTh' ('check relevancy of page by
		searching specific users signature')

		checks the relevancy of single body data by performing different tests

		input:  data [string (unicode)]
                        checksum
                        heading
                        self-objects
		returns:  [tuple]
		          format:    (probable, checksum) [tuple]
                (but checksum is updated)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 27, 28)

		item = data
		check_dict = {}

		# search for signature in every thread on page
		(probable, info, user, check) = self._SearchForSignature(item)
		check_dict['sign'] = probable
		if not probable: return (probable, None, check_dict)	# we just want checksums for headings where user is parcitipating
		#if not probable: return (False, None, check_dict)	#

		# check if thread has not changed (because user can be not last but thread has also not changed)
		# (introduce checksum with backwards compatibility)
		# converting of different data formats is now done in 'getHistoryPYF()'
		checksum_cur = hashlib.md5(item.encode('utf8').strip()).hexdigest()
		if ((checksum and (len(checksum) > 0)) and (heading in checksum)):
			# CHKSUM v5
			#probable = probable and (not (checksum.pop(heading)[0] == checksum_cur))
			probable = probable and (not (checksum[heading][0] == checksum_cur))
			check_dict['chksum'] = probable

		# check if user was last editor
		# if signature found check part after '\n', after each signature is at least one '\n'
		c = info[-1]
		#c = info[1]
		c = self._eol_regex.split(c + '\n', 1)[1]
		#print re.split('',c)
		#c = re.sub(u'\|\}',u'',c,1)						# [B40.2] for signatures at the end of tables (welcome templates, a.o.)
		#(relevant, info, user, check) = self._SearchForSignature(c, '')	# check for other signature
		probable = probable and (len(c.strip()) > 0)				# just check for add. text (more paranoid)
		check_dict['lastword'] = probable

		return (probable, checksum_cur, check_dict)				# is this body data relevant?

	def _appendFile(self, data):
		'''
		append data (history) to file

		input:  data
                        self-objects
		returns:  (appends data to the data/history file, nothing else)
		'''

		# könnte history dict mit pickle speichern (http://www.thomas-guettler.de/vortraege/python/einfuehrung.html#link_12.2)
		# verwende stattdessen aber wiki format! (bleibt human readable und kann in wiki umgeleitet werden bei bedarf)
		datfile = codecs.open(self._datfilename, encoding=config.textfile_encoding, mode='a+')
		#datfile = codecs.open(self._datfilename, encoding='zlib', mode='a+b')
		datfile.write(u'\n\n' + data)
		#datfile.write(data)
		datfile.close()

	def _setUser(self, user):
		'''
		set all internal user info

		input:  user [tuple] (see _getUsers(...) for format)
                        self-objects
                        bot_config
		returns:  self._user [string (unicode)]
		returns:  self._userPage [page]
		returns:  self._param [dict]
		          keys are:  parameters/options [string] (see 'sum_disc_conf.py')
		          format:    (differs from param to param)
		returns:  self._datfilename [string]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 30, 28, 17)

		# defaults settings
		# thanks to http://mail.python.org/pipermail/python-list/2005-September/339147.html
		# and http://docs.python.org/library/copy.html
		self._user  = user[0]
		#self._userPage = pywikibot.Page(self.site, "User_Discussion:%s" % self._user)		# LANG. PROB. HERE??? (...also? to be causious)
		self._userPage = dtbext.pywikibot.Page(self.site, u'Benutzer_Diskussion:%s' % self._user)	#
		userdiscpage = self._userPage.title()
		#self._param = dict(self._param_default)
		self._param = copy.deepcopy(self._param_default)

		# user settings
		# (wenn nötig smooth update: alle keys mit namen '_list' einzeln updaten, dann werden sie ergänzt statt überschrieben)
		self._param.update(user[1])
		# re-add defaults to lists in self._param else they are overwritten
		for key in bot_config['default_keep']:
			if key in user[1]: self._param[key] += copy.deepcopy(self._param_default[key])
		user = user[0]
		self._param['ignorepage_list'].append( self._userPage.title() )	# disc-seite von user IMMER ausschliessen
		if 'userResultPage' in self._param:				# user with extended info (extra page to use)
			self._userPage = dtbext.pywikibot.Page(self.site, u'Benutzer:%s' % self._param['userResultPage'])
			self._param['ignorepage_list'].append( self._userPage.title() )
		self._datfilename = '%slogs/sum_disc-%s-%s-%s.dat' % (bot_config['script_path'], 'wikipedia', 'de', self._user)

		# substitute variables for use in user defined parameters/options
		param_vars = {	'username':	self._user,
				'userdiscpage':	userdiscpage,
				}
		for item in bot_config['vars_subst']:
			self._param[item] = [ subitem % param_vars for subitem in self._param[item] ]

		# pre-compile regex
		# (probably try to pre-compile 'self._param_default' once int __init__ and reuse the unchanged ones here)
		for item in bot_config['regex_compile']:
			self._param[item] = map(re.compile, self._param[item])

        def _parseNews(self):
		'''
		filter and parse all the info and rewrite in in wiki-syntax, to be put on page

		input:  self._news_list [dict]
                        self-objects
		returns:  (result wiki text, message count) [tuple (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		switch = self._param['reportchanged_switch']
		switch2 = self._param['reportclosed_switch']
		if not switch:	ps_types_a = [self._PS_new, self._PS_maintmsg]
		else:		ps_types_a = [self._PS_new, self._PS_changed, self._PS_maintmsg]
		if not switch2:	ps_types_b = []
		else:		ps_types_b = [self._PS_closed]
		ps_types = (ps_types_a, ps_types_b)

		buf = []
		if (len(self._news_list.keys()) > 0):
			for keys in self._news_list.keys():
				data = self._news_list[keys]
				if   data[5] in ps_types[0]:
					headings = []
					#for item in data[4]:
					for subkey in data[4].keys():
						item = (subkey,) + data[4][subkey]
						if not item[2]: continue		# is this heading relevant?
						renderitem = dtbext.pywikibot.getParsedString(item[3], plaintext=True)	# replaces '_renderWiki()'
						subitem = item[0]
						subitem = self._bracketopen_regex.sub(u'.5B', subitem)	# urllib.quote(...) sets '%' instead of '.'
						subitem = self._bracketclose_regex.sub(u'.5D', subitem)	#
						if not (item[0] == ""):
							headings.append( u'[[%s#%s|%s]]' % (data[1].title(), subitem, renderitem) )
					if (len(headings) == 0):			# no subsections on page...
						data = (data[0], data[1].title(), self._getLastHumanEditor(data[2]), self.localizeDateTime(data[3]))
						data = u'*%s: [[%s]] - last edit by %s (%s)' % data
					else:
						data = (data[0], data[1].title(), string.join(headings, u', '), self._getLastHumanEditor(data[2]), self.localizeDateTime(data[3]))
						data = u'*%s: [[%s]] at %s - last edit by %s (%s)' % data
				elif data[5] in ps_types[1]:
					data = (data[0], data[1].title(), self._getLastHumanEditor(data[2]), self.localizeDateTime(data[3]))
					data = u'*%s: [[%s]] all discussions have finished (surveillance stopped) - last edit by %s (%s)' % data
				elif data[5] in [self._PS_warning]:
					data = (data[1].title(), data[0])
					data = u'*Bot warning message: [[%s]] "\'\'%s\'\'"' % data
					self._global_warn.append( (self._user, data) )
					if not self._param['reportwarn_switch']: continue
				elif data[5] in [self._PS_notify]:
					data = (data[0], data[1].extradata['url'], data[1].title(), data[2], self.localizeDateTime(data[3]))
					data = u'*%s: <span class="plainlinks">[%s %s]</span> - last edit by [[User:%s]] (%s)' % data
				else:
					continue	# skip append
				buf.append( data )

		count = len(buf)
		if (count > 0):
			buf[-1] += u'<noinclude>'
			buf.append( u'Summary generated from and at: ~~~~</noinclude>' )
			buf = string.join(buf, u'\n')
                else:
			buf = u''

		return (buf, count)

	def _AddMaintenanceMsg(self):
		'''
		check if there are any bot maintenance messages and add them to every users news!!

		input:  maintenance_msg [list]
                        wikipedia-objects
		returns:  self._news_list [dict] (with appended bot messages)
		          keys are:  page titles [string (unicode)]
		          format:    (type_desc_str, page, lastedit_user, lastedit_time, checksum) [tuple]
                          self._hist_list [dict] (same format as self._news_list)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		if (self.maintenance_msg == []):	return

		#for item in maintenance_msg:
		for item in self.maintenance_msg:
			page = pywikibot.Page(self.site, bot_config['maintenance_page'] % "")
			tmst = time.strftime('%H:%M, %d. %b. %Y')
			tmst = u'%s' % re.sub(' 0', ' ', tmst)
			#self._news_list[bot_config['maintenance_page'] % item] = (bot_config['maintenance_mesg'], page, u'DrTrigon', tmst, [(item,'',True)])
			self._news_list[page.title()] = ( bot_config['maintenance_mesg'], page, u'DrTrigon', tmst, 
							{ pywikibot.sectionencode(item,config.textfile_encoding):('',True,item) }, self._PS_maintmsg )
			self._hist_list[page.title()] = self._news_list[page.title()]

		pywikibot.output(u'*** Bot maintenance messages added')

	#def _SearchForSignature(self, text, user = None):
	# (to get this version back, simply remove 'checksign_list' from 'regex_compile' and it is like it was before)
	def _SearchForSignature(self, text):
		'''
		check if there are (any or) a specific user signature resp. link to user page in text

		input:  text [string (unicode)]
                        self-objects
		returns:  relevance info [tuple]
		          format:    (relevant [bool], info [list], user [string (unicode)], check [string]) [tuple]
		'''

		#if not user: user = self._user

		sign_list  = self._param['altsign_list']
		check_list = self._param['checksign_list']

		relevant = False
		info_len = 2*len(text)
		result = (relevant, '', self._user, '')
		for user in sign_list:
			for check in check_list:
				#print user, check
				#info = check.split(text)
				info = re.split(check % {'usersig':user}, text)
				#print info
				relevant = relevant or (len(info) > 1)
				if relevant: break	# to get the most recent 'info' and speed up
			#if relevant: break		# (but check for all possible sign.)
			if ((len(info) > 1) and (len(info[-1]) < info_len)):	# get and return last/most recent sign.
				info_len = len(info[-1])			#
				result = (relevant, info, user, check)		#
		#return (relevant, info, self._user, check)
		return result

	def _getLastHumanEditor(self, username):
		'''
		search the last 10 edits/revisions for the most recent human editor and replaces that
		one. (the non-human/bot)

		input:  user [text]
                        self-objects
		returns:  last human user name [string]
		'''

		if not (u'bot' in userlib.User(self.site, username).groups()):
			return username

		result = ''
		for info in page.getVersionHistory(revCount=10)[1:]:
			groups = userlib.User(self.site, info[2]).groups()
			#print info[2], groups
			if not (u'bot' in groups):
				result = info[2]
				break

		if (result == ''):
			return '?/[[User:%s]]' % username
		else:
			#return '[[User:%s]]' % result
			return '[[User:%s]]/[[User:%s]]' % (result, username)
			#return '[[User:%s]] <small>([[User:%s]])</small>' % (result, username)


class Timer(threading.Thread):
	'''
	Timer thread that runs completely stand-alone in sperate thread and continous until 'cancel' is called.
	Variables to use in 'func' have to be stored internally in 'kwargs'.
	'''

	def __init__(self, sec, func, **kwargs):
		threading.Thread.__init__(self)
		self.seconds = sec
		self.function = func
		self.kwargs = kwargs
		self._t = threading.Timer(self.seconds, self._action)
		self._watchdog = [None]*5
	def _action(self):
		self._watchdog = self._watchdog.append(self.kwargs)		# watchdog (for security)
		self._watchdog.pop(0)						#
		if (self._watchdog[0] == self._watchdog[-1]): self.cancel()	#
		self.function(self)
		del self._t
		self._t = threading.Timer(self.seconds, self._action)
		self._t.start()
	def run(self):
		#self._t.start()
		self._action()
	def cancel(self):
		self._t.cancel()

def main():
	bot = SumDiscBot(bot_config['userlist'])	# for several user's, but what about complete automation (continous running...)
	if len(pywikibot.handleArgs()) > 0:
		for arg in pywikibot.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if 	arg[:17] == "-compress_history":
			#if 	arg[:17] == "-compress_history":
				bot.compressHistory( eval(arg[18:]) )
				return
			elif	(arg[:17] == "-rollback_history"):
				bot.rollback = int( arg[18:] )
			elif	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
				bot.silent = True
			elif	(arg == "-all") or ("-sum_disc" in arg):
				pass
			#elif	(arg == "-test_run"):
			#	debug = ...
			else:
				pywikibot.showHelp()
				return
	bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

