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
__version__='$Id: sum_disc.py 0.2.0026 2009-11-19 18:29 drtrigon $'
#


import re, sys
import time, codecs, os, calendar
import threading
import copy #, zlib
import sets, string, datetime, hashlib

import config, pagegenerators, userlib
import dtbext
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
					'checksign_list':	[ '--\s?\[\[Benutzer:%(usersig)s[\]\|/]',			
								'--\s?\[\[Benutzer[ _]Diskussion:%(usersig)s[\]\|/]',
								'--\s?\[\[User:%(usersig)s[\]\|/]',			
								'--\s?\[\[User[ _]talk:%(usersig)s[\]\|/]', ],
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


class SumDiscBot(dtbext.basic.BasicBot):
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

		pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

		dtbext.basic.BasicBot.__init__(self, bot_config)

		# init constants
        	self._userListPage = pywikibot.Page(self.site, userListPage)
		#print [item[0] for item in self._getUsers()]		# enhance 'ignorepage_list'

		pywikibot.output(u'\03{lightred}** Receiving User List (wishes): %s\03{default}' % self._userListPage)
		self._user_list = self.loadUsersConfig(self._userListPage)

		pywikibot.output(u'\03{lightred}** Receiving Job Queue (Maintenance Messages)\03{default}')
		page = pywikibot.Page(self.site, bot_config['maintenance_queue'])
		self.maintenance_msg = self.loadJobQueue(page, bot_config['queue_security'], debug = debug['write2wiki'])

		# init variable/dynamic objects

	def run(self):
		'''
		run SumDiscBot()
		'''

		#pywikibot.output(u'\03{lightgreen}* Processing User List (wishes): %s\03{default}' % self._userListPage)
		pywikibot.output(u'\03{lightgreen}* Processing User List (wishes):\03{default}')

		if debug['user']: pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE USERS WILL BE SKIPPED ! ===\03{default}')

		for user in self._user_list:					# may be try with PreloadingGenerator?!
			if (debug['user'] and (user.name() != 'DrTrigon')): continue

			# set user and init params
			self._setUser(user)

			#pywikibot.output(u'\03{lightred}** Processing User: %s\03{default}' % self._user.name())
			pywikibot.output(u'\03{lightred}** Processing User: %s\03{default}' % self._user)

			# get operating mode
			self.loadMode(self._userPage)
			self._work_list = {}

			# get history entries
			self.loadHistory(rollback=self.rollback)
			self._work_list.update( self._hist_list )
			# (HistoryPageGenerator)

			# check special pages for latest contributions
			addition = self.checkRecentEdits()
			self._work_list.update( addition )
			# RecentEditsPageGenerator

			# get the backlinks to user disc page
			if self._param['getbacklinks_switch']:
				addition = self.getUserBacklinks()
				self._work_list.update( addition )
				# all pages served from here ARE CURRENTLY
				# SIGNED (have a Signature at the moment)
				# UserBacklinksPageGenerator

			# check for news to report
			if self._param['globwikinotify_switch']:
				# get global wiki notifications (toolserver/merl)		
				if debug['toolserver']:
					pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE TOOLSERVER ACCESS WILL BE SKIPPED ! ===\03{default}')
					globalwikinotify = []
				else:
					#pywikibot.output(u'\03{lightpurple}*** %i Global wiki notifications added\03{default}' % len(work_list))
					dtbext.userlib.addAttributes(self._user)
					globalwikinotify = self._user.globalnotifications()

				self.getLatestNews(globalwikinotify=globalwikinotify)
			else:
				self.getLatestNews()
			# CombinedPageGenerator from previous 2 (or 3) generators
			# feed this generator into a DuplicateFilterPageGenerator
			# and pass this with GlobalWikiNotificationsPageGen to
			# getLatestNews



			#print self._work_list
			continue
# debug here ^^^

# idea: may be create a class for storage of sum_disc_data and for easy save load (history) and else... ?!???
			self.checkRelevancy()				# check self._news_list on relevancy, disc-thread oriented version...

			#print self._work_list
			continue
# debug here ^^^
			self.AddMaintenanceMsg()				# gehen auch in jede history... werden aber bei compress entfernt

			self.postDiscSum()					# post results to users Discussion page (with comments for history)

		pywikibot.output(u'\03{lightgreen}* Processing Warnings:\03{default}')

		for warning in self._global_warn:		# output all warnings to log (what about a special wiki page?)
			pywikibot.output( "%s: %s" % warning )	

	def compressHistory(self, users = []):
		"""Read history, and re-write new history without any duplicates.

		   @param users: List of users supported by bot (and thus in history).
		   @type  users: list

		   Load, truncate and re-write history in files.
		"""

		if not users: users = [ item[0] for item in self._user_list ]

		pywikibot.output(u'* Compressing of histories:')

		if bot_config['backup_hist']:
			timestmp = dtbext.date.getTimeStmp()
			pathname = '%slogs/%s/' % (bot_config['script_path'], timestmp)	# according to '_setUser'
			os.mkdir(pathname)
			import shutil

		for user in users:
			u = userlib.User(self.site, user)
			u.extradata = {}
			self._setUser(u)

			try:
				begin = float(os.path.getsize(self._datfilename))
			except OSError:		# OSError: [Errno 2] No such file or directory
				continue

			# backup old history
			if bot_config['backup_hist']:
				dst = os.path.join(pathname, os.path.basename(self._datfilename))
				shutil.copyfile(self._datfilename, dst)

			# truncate history (drop old entries)
			self.loadHistory()

			# write new history
			os.remove(self._datfilename)
			self.putHistory(self._hist_list)

			end = float(os.path.getsize(self._datfilename))

			pywikibot.output(u'\03{lightred}** History of %s compressed and written. (%s %%)\03{default}' % (user, (end/begin)*100))

	def loadHistory(self, rollback = 0):
		"""Read history, and restore the page objects with sum_disc_data.

		   @param rollback: Number of history entries to go back (re-use older history).
		   @type  rollback: int

		   Returns nothing but adds self._hist_list filled with archived entries.
		"""

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
			for key in news_item.keys():
				if (len(news_item[key]) == 5):			# old history format
					news_item[key] += (self._PS_unchanged,)
					usage['old history'] = True
				if news_item[key][5] in [self._PS_notify]:
					continue # skip
				if key in news:	# APPEND the heading data in the last tuple arg
					if news_item[key][5] in [self._PS_closed]:
						del news[key]
					else:
						heads = news[key][4]
						heads.update( news_item[key][4] )
						news[key] = (news_item[key][0], news_item[key][1], news_item[key][2], news_item[key][3], heads, news_item[key][5])
				else:
					news[key] = news_item[key]
			rollback_buf.append( copy.deepcopy(news) )
		if rollback_buf:
			rollback_buf.reverse()
			i = min([rollback, (len(rollback_buf)-1)])
			self._hist_list = rollback_buf[i]
			del rollback_buf
			usage['rollback'] = i

		# create page list
		new = {}
		for name in self._hist_list.keys():
			page = pywikibot.Page(self.site, name)
			page.sum_disc_data = self._hist_list[name]
			new[name] = page
		self._hist_list = new

		pywikibot.output(u'\03{lightpurple}*** History recieved %s\03{default}' % str(usage))

	def putHistory(self, data_dict):
		"""Write history.

		   Returns nothing but the history file gets filled with archived entries.
		"""

		# extract important data from page list
		buf = {}
		for key in data_dict.keys():
			buf[key] = data_dict[key].sum_disc_data

		# write new history
		self.appendFile( str(buf).decode('latin-1') )
		#self.appendFile( str(buf).encode('zlib') )
		#self.appendFile( zlib.compress(str(buf).decode('latin-1'), 9) )

		pywikibot.output(u'\03{lightpurple}*** History updated\03{default}')

	def getLatestNews(self, globalwikinotify=[]):
		"""Check latest contributions on recent news.

		   Returns nothing but adds self._news_list and self._oth_list filled
		   with new/changed entries.
		"""

		f = open('/home/ursin/debug.txt', 'w')
		f.write( str(self._work_list.keys()) )
		f.close()

		# check for news to report
		self._news_list = {}
		self._oth_list = {}
		size = len(self._work_list)
		jj = 0
		gen1 = pagegenerators.PagesFromTitlesGenerator(self._work_list.keys())
		# PageTitleFilterPageGenerator; or use RegexFilterPageGenerator (look ignorelist)
		#gen2 = pagegenerators.PageTitleFilterPageGenerator(gen1, ignore_list)
		# Preloads _contents and _versionhistory
		# [ DOES NOT USE API YET! / ThreadedGenerator would be nice! / JIRA ticket? ]
		# WithoutInterwikiPageGenerator, 
		gen3 = pagegenerators.PreloadingGenerator(gen1)
		#gen4 = pagegenerators.RedirectFilterPageGenerator(gen3)
		for page in gen3:
			# count page number (for debug not to loose pages)
			jj+=1

			name = page.title()
			print name
			page.sum_disc_data = self._work_list[name].sum_disc_data

			# ignorelist
			# [ RegexFilterPageGenerator; but has to be modified and a patch sent upstream for this / JIRA ticket? ]
			#if (self._transPage(page).title() == self._userPage.title()):	continue
			skip = False
			for check in self._param['ignorepage_list']:
				if check.search(name):
					skip = True
					break
			if skip: continue

			# get history (was preloaded)
			#actual = actual_dict[page.sectionFreeTitle()]
			# use preloaded with revCount=1
			try:
				actual = page.getVersionHistory(revCount=1)
			except pywikibot.NoPage:
			#	page.sum_disc_data = (	u'no version history found, page deleted!', 
			#				None, # obsolete (and recursive)
			#				None, 
			#				None, 
			#				None, 
			#				self._PS_warning )
			#	self._oth_list[name] = page				
				pywikibot.output(u'\03{lightaqua}INFO: skipping not available (deleted) page at [[%s]]\03{default}' % name)
				continue
			except pywikibot.IsRedirectPage:
				pywikibot.output(u'\03{lightaqua}INFO: skipping redirect page at [[%s]]\03{default}' % name)
				continue

			# actual/new status of page, has something changed?
			if name in self._hist_list:
				if (not (self._hist_list[name].sum_disc_data[3] == actual[0][1])):
					# discussion has changed, some news?
					page.sum_disc_data = (	u'Discussion changed', 
								None, # obsolete (and recursive)
								actual[0][2], 
								actual[0][1], 
								self._hist_list[name].sum_disc_data[4], 
								self._PS_changed )
					self._news_list[name] = page
				else:
					# nothing new to report (but keep for history and update it)
					page.sum_disc_data = (	self._hist_list[name].sum_disc_data[0], 
								None, # obsolete (and recursive)
								actual[0][2], 
								actual[0][1], 
								self._hist_list[name].sum_disc_data[4], 
								self._PS_unchanged )
					self._oth_list[name] = page
			else:
				# new discussion, some news?
				page.sum_disc_data = (	u'New Discussion', 
							None, # obsolete (and recursive)
							actual[0][2], 
							actual[0][1], 
							{},
							self._PS_new )
				self._news_list[name] = page

# DOES THE PreloadingGenerator WORK ???
		if not (len(self._work_list.keys()) == jj):
			raise pywikibot.Error(u'PreloadingGenerator has lost some pages!')

		# check for GlobalWikiNotifications to report
		localinterwiki = self.site.language()
		for (page, data) in globalwikinotify:
			# skip to local disc page, since this is the only page the user should watch itself
			if page.site().language() == localinterwiki:
				pywikibot.output(u'\03{lightaqua}INFO: skipping global wiki notify to local wiki %s\03{default}' % page.title(asLink=True))
				continue

			#data = page.globalwikinotify
			page.sum_disc_data = (	bot_config['globwiki_notify'], 
						None, 
						data['user'], 
						data['timestamp'], 
						{u'':('',True,u'')}, 
						self._PS_notify )
			self._oth_list[data[u'link']] = page
			#self._hist_list[page.title()] = self._news_list[page.title()]

		pywikibot.output(u'\03{lightpurple}*** Latest News searched\03{default}')

	def checkRecentEdits(self):
		"""Check wiki on recent contributions of specific user.

		   Returns list with results formatted like self._news_list.
		"""

		check_list = self._param['checkedit_list']
		count = self._param['checkedit_count']

		# [ should be done in framework / JIRA ticket? ]
		pywikibot.output(u'Getting latest contributions from user "%s" via API...' % self._user.name())

		# thanks to http://www.amk.ca/python/howto/regex/ and http://bytes.com/forum/thread24382.html
		#usersumList = [p.title() for p in pagegenerators.UserContributionsGenerator(self._user.name(), number = count)]
		usersumList = [p[0].title() for p in self._user.contributions(limit = count)]

		work_list = {}
		for item in usersumList:
			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					#work_list[match.group(1)] = ()
					name = match.group(1)
					page = pywikibot.Page(self.site, name)
					page.sum_disc_data = ()
					work_list[name] = page
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'\03{lightpurple}*** Latest %i Contributions checked\03{default}' % len(usersumList))

		return work_list

	# created due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24)
	def getUserBacklinks(self):
		"""Check wiki on backlinks to specific user.

		   Returns list with results formatted like self._news_list.
		"""

		check_list = self._param['checkedit_list']

		userbacklicksList = []
		for item in self._param['backlinks_list']:
			page = pywikibot.Page(self.site, item)		# important for the generator to use the API
			#userbacklicksList += [p.title() for p in pagegenerators.ReferringPageGenerator(page, withTemplateInclusion=False)]
			userbacklicksList += [p.title() for p in page.getReferences(withTemplateInclusion=False)]
		userbacklicksList = list(sets.Set(userbacklicksList))			# drop duplicates

		work_list = {}
		for item in userbacklicksList:
			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					#work_list[match.group(1)] = ()
					name = match.group(1)
					page = pywikibot.Page(self.site, name)
					page.sum_disc_data = ()
					work_list[name] = page
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'\03{lightpurple}*** %i Backlinks to user checked\03{default}' % len(userbacklicksList))

		return work_list

	def postDiscSum(self):
		"""Post discussion summary of specific user to discussion page and write to histroy
		   (history currently implemented as local file, but wiki page could also be used).

		   Returns nothing but appends self._news_list to the history file and writes changes
		   to the wiki page.
		"""

		(buf, count) = self.parseNews()
		if (count > 0):
			pywikibot.output(u'='*50 + u'\n' + buf + u'\n' + u'='*50)
			pywikibot.output(u'[%i entries]' % count )

			if debug['write2wiki']:
				self.loadMode()			# get operating mode and contend AGAIN to be ACTUAL !!!
				#comment = u'Diskussions Zusammenfassung hinzugefügt: %i neue und %i veränderte' % (3, 7)
				if not self._mode:
					# default: write direct to user disc page
					comment = u'Diskussions-Zusammenfassung hinzugefügt: %i Einträge' % count
					self.append(self._userPage, buf, comment=comment, minorEdit=False)
				else:
					# enhanced (with template): update user disc page and write to user specified page
					tmplsite = pywikibot.Page(self.site, self._tmpl_data)
					comment = u'Diskussions-Zusammenfassung aktualisiert: %i Einträge in [[%s]]' % (count, tmplsite.title())
					self.save(self._userPage, self._content, comment=comment, minorEdit=False)
					comment = u'Diskussions-Zusammenfassung hinzugefügt: %i Einträge' % count
					self.append(tmplsite, buf, comment=comment)
				dtbext.pywikibot.addAttributes(self._userPage)
				purge = self._userPage.purgeCache()

				pywikibot.output(u'\03{lightpurple}*** Discussion updates added to: %s (purge: %s)\03{default}' % (self._userPage.title(asLink=True), purge))
			else:
				pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

			if debug['write2hist']:
				self.putHistory(self._hist_list)
			else:
				pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO HISTORY ! ===\03{default}')
		else:
			pywikibot.output(u'\03{lightpurple}*** Discussion up to date: NOTHING TO DO\03{default}')

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

	def checkRelevancy(self):
		"""Check relevancy of page by splitting it into sections and searching
		   each for specific users signature.

		   Returns nothing but updates self._news_list and self._hist_list
                   (but checksum is updated and all irrelevant entries are deleted from output).
		"""

#		def test(timerobj): pywikibot.output(u'\03{lightaqua}progress: %.1f%s (%i of %i) ...\03{default}' % (((100.*timerobj.kwargs['u'])/timerobj.kwargs['size']), u'%', timerobj.kwargs['u'], timerobj.kwargs['size']))
#		t = Timer(bot_config['timeout'], test, size = len(self._news_list.keys()), u = 0)

		# self._news_list contents all 'self._PS_changed' and 'self._PS_new'
		self._hist_list = copy.deepcopy(self._news_list)
#		# kleiner speed-up patch, als option/parameter aktivierbar
#		if self._param['directgetfull_list']: issues = ( self._param['directgetfull_list'], ['full']*len(self._param['directgetfull_list']) )
#		else:	issues = None
#		if (t.kwargs['size'] != 0): t.run()
		#for (page, buf) in self.loadPages( pages, issues=issues ):
		for page in self._news_list:
			keys = page.title()
			# get content (was preloaded)
			#buf = self.load(page)

#			t.kwargs['u'] += 1

#			try:
			strt = time.time()
			entries = self.splitIntoSections(page)
			end = time.time()
			diff1 = end-strt
			strt = time.time()
			page.getSections()
			end = time.time()
			diff2 = end-strt
			print "speed check:", diff1, diff2
#should be loaded now, make speed check here!!!

			# iterate over all sections in page and check their relevancy
			page_rel    = False
			page_signed = False
			#try:	checksum = self._news_list[keys][4]
			try:	checksum = page.sum_disc_data[4]
			except:	checksum = None
			#print keys, checksum
			checksum_new = {}
			for i, (head, body) in enumerate(entries): # iterate over all headings/sub sections
				# wikiline is wiki text, line is parsed and anchor is the unique link label
				(wikiline, line, anchor) = head[:3]

				# ignorelist for headings
				skip = False								
				for check in self._param['ignorehead_list']:
					if check.search(wikiline):
						skip = True
						break
				if skip: continue

				# check relevancy of section
				(rel, checksum_cur, checks) = self.checkSectionRelevancy(body, checksum, anchor)

				# is page signed?
				page_signed = page_signed or checks['signed'] # signature check

				# is page relevant?
				if not rel: continue

				# page IS relevant, update checksum
				page_rel = True
				checksum_new[anchor] = (checksum_cur, rel, line)

			# update sum_disc_data in page (checksums, relevancies, ...)
			#d = self._news_list[keys]
			#self._news_list[keys] = d[0:4] + (checksum_new,) + d[5:]
			page.sum_disc_data = page.sum_disc_data[:4] + (checksum_new,) + page.sum_disc_data[5:]
			self._news_list[keys] = page
			#self._hist_list[keys] = self._news_list[keys]
			self._hist_list[keys] = page
#			except pywikibot.SectionError:	# is typically raised by ????????
#				page_rel = False

			# if page is not relevant, don't list discussion
			if not page_rel:
				#entry = self._news_list[keys]
				entry = page.sum_disc_data

				del self._news_list[keys]
				if (entry[5] == self._PS_new): del self._hist_list[keys]

				if (not page_signed) and (entry[5] == self._PS_changed):	# discussion closed (no signature on page anymore)
					self._news_list[keys] = (	u'Discussion closed', 
									None, 
									entry[2], 
									entry[3], 
									{}, 
									self._PS_closed )
					#del self._hist_list[keys]
					self._hist_list[keys] = self._news_list[keys]

#		t.cancel()
#		del t

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

		pywikibot.output(u'\03{lightpurple}*** Relevancy of threads checked\03{default}')

	def splitIntoSections(self, page):
		"""Retrieves the page content and splits it to headings and bodies ('check relevancy
		   of page by searching specific users signature').

		   @param page: Page to process.

		   Returns a list of tuples containing the sections with info and wiki text.
		"""

		# enhance to dtbext.pywikibot.Page
		dtbext.pywikibot.addAttributes(page)
		#try:
		# get sections and content (content was preloaded earlier)
		sections = page.getSections(minLevel=1)
		#except pywikibot.Error:
		#	pass	# sections could not be resoled, process the whole page at once

		if len(sections) == 0:
			entries = [ ((u'',u'',u''), buf) ]
		else:
			# append 'EOF' to sections list
			# (byteoffset, level, wikiline, line, anchor)
			sections.append( (len(buf) + 1, None, None, None, None) )

			entries = []
			for i, s in enumerate(sections[:-1]):
				bo_start = s[0]
				bo_end   = sections[i+1][0] - 1

				entries.append( (s[2:], buf[bo_start:bo_end]) )

		return entries

	def checkSectionRelevancy(self, data, checksum, anchor):
		"""Checks the relevancy of single body data by performing different tests
		   ('check relevancy of page by searching specific users signature').

		   @param data: Section wiki text to check.
		   @type  data: string
		   @param checksum: Checksum given from history to compaire against.
		   @type  checksum: string
		   @param anchor: Anchor of wiki text section heading given by mediawiki
		                  software.
		   @type  anchor: string

		   Returns a tuple (True, checksum_cur, checks).
		"""

		checks = {}

		# check if thread has changed
		checks['changed'] = True
		checksum_cur = hashlib.md5(data.encode('utf8').strip()).hexdigest()
		if ((checksum and (len(checksum) > 0)) and (anchor in checksum)):
			checks['changed'] = (not (checksum[anchor][0] == checksum_cur))

		if not checks['changed']:
			return (False, checksum_cur, checks)

		# search for signature in section/thread
		(signs_pos, signs) = self.searchForSignature(data)
		checks['signed'] = (len(signs_pos) > 0) # are signatures present
		info = signs[signs_pos[-1]]

		if not checks['signed']:
			return (False, checksum_cur, checks)

		# check if user was last editor
		# look at part after '\n', after each signature is at least one '\n'
		#c = info[-1]
		data = data[signs_pos[-1]:] + u'\n'
		data = self._eol_regex.split(data, maxsplit=1)[1]
		checks['lasteditor'] = not (len(c.strip(u' \n')) > 0) # just check for add. text (more paranoid)

		if checks['lasteditor']:
			return (False, checksum_cur, checks)

		return (True, checksum_cur, checks)

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
		self._user  = user
		#self._userPage = pywikibot.Page(self.site, "User_Discussion:%s" % self._user.name())		# LANG. PROB. HERE??? (...also? to be causious)
		self._userPage = pywikibot.Page(self.site, u'Benutzer_Diskussion:%s' % self._user.name())	#
		userdiscpage = self._userPage.title()
		#self._param = dict(self._param_default)
		self._param = copy.deepcopy(self._param_default)

		# user settings
		# (wenn nötig smooth update: alle keys mit namen '_list' einzeln updaten, dann werden sie ergänzt statt überschrieben)
		self._param.update(user.param)
		# re-add defaults to lists in self._param else they are overwritten
		for key in bot_config['default_keep']:
			if key in user.param: self._param[key] += copy.deepcopy(self._param_default[key])
		self._param['ignorepage_list'].append( self._userPage.title() )	# disc-seite von user IMMER ausschliessen
		if 'userResultPage' in self._param:				# user with extended info (extra page to use)
			self._userPage = pywikibot.Page(self.site, u'Benutzer:%s' % self._param['userResultPage'])
			self._param['ignorepage_list'].append( self._userPage.title() )
		self._datfilename = '%slogs/sum_disc-%s-%s-%s.dat' % (bot_config['script_path'], 'wikipedia', 'de', self._user.name())

		# substitute variables for use in user defined parameters/options
		param_vars = {	'username':	self._user.name(),
				'userdiscpage':	userdiscpage,
				}
		for item in bot_config['vars_subst']:
			self._param[item] = [ subitem % param_vars for subitem in self._param[item] ]

		# pre-compile regex
		# (probably try to pre-compile 'self._param_default' once int __init__ and reuse the unchanged ones here)
		for item in bot_config['regex_compile']:
			self._param[item] = map(re.compile, self._param[item])

        def parseNews(self):
		"""Filter and parse all the info and rewrite in in wiki-syntax, to be put on page.

		   Returns a tuple (result wiki text, message count).
		"""

		switch = self._param['reportchanged_switch']
		switch2 = self._param['reportclosed_switch']
		if not switch:	ps_types_a = [self._PS_new, self._PS_maintmsg]
		else:		ps_types_a = [self._PS_new, self._PS_changed, self._PS_maintmsg]
		if not switch2:	ps_types_b = []
		else:		ps_types_b = [self._PS_closed]
		ps_types = (ps_types_a, ps_types_b)

		buf = []
		for name in self._news_list.keys():
			page = self._news_list[name]
			#data = self._news_list[name]
			data = page.sum_disc_data
			if data[5] in ps_types[0]:
				# new and changed
				report = []
				for anchor in data[4].keys(): # iter over sections/checksum
					(checksum_cur, rel, line) = data[4][anchor]

					# is this section/heading relevant?
					if not rel: continue

					# were we able to divide the page into subsections?
					if not anchor: continue

					# append relevant sections
					report.append( u'[[%s#%s|%s]]' % (page.title(), anchor, line) )

				if report:
					# subsections on page
					data = (data[0], page.title(), string.join(report, u', '), self.getLastEditor(page, data[2]), self.localizeDateTime(data[3]))
					data = u'*%s: [[%s]] at %s - last edit by %s (%s)' % data
				else:
					# no subsections on page
					data = (data[0], page.title(), self.getLastEditor(page, data[2]), self.localizeDateTime(data[3]))
					data = u'*%s: [[%s]] - last edit by %s (%s)' % data
			elif data[5] in ps_types[1]:
				# closed
				data = (data[0], page.title(), self.getLastEditor(page, data[2]), self.localizeDateTime(data[3]))
				data = u'*%s: [[%s]] all discussions have finished (surveillance stopped) - last edit by %s (%s)' % data
			elif data[5] in [self._PS_warning]:
				# warnings
				data = (page.title(), data[0])
				data = u'*Bot warning message: [[%s]] "\'\'%s\'\'"' % data
				self._global_warn.append( (self._user.name(), data) )
				if not self._param['reportwarn_switch']: continue
			elif data[5] in [self._PS_notify]:
				# global wiki notifications
				data = (data[0], data[1].extradata['url'], page.title(), data[2], self.localizeDateTime(data[3]))
				data = u'*%s: <span class="plainlinks">[%s %s]</span> - last edit by [[User:%s]] (%s)' % data
			else:
				continue # skip append
			buf.append( data )

		count = len(buf)
		if (count > 0):
			buf[-1] += u'<noinclude>'
			buf.append( u'Summary generated from and at: ~~~~</noinclude>' )
			buf = string.join(buf, u'\n')
                else:
			buf = u''

		return (buf, count)

	def getLastEditor(self, page, lastuser):
		"""Search the last 500 edits/revisions for the most recent human editor
		   and returns that one. (the non-human/bot).

		   @param page: Page to check.
		   @param lastuser: User made the most recent edit to page.
		   @type  lastuser: string

		   Returns a link with the most recent and most recent human editors of
		   page.
		"""

		humaneditor = page.userNameHuman()
		if humaneditor:
			return u'[[User:%s]]/[[User:%s]]' % (humaneditor, lastuser)
		else:
			# no human editor found; use last editor
			return u'[[User:%s]] (no human editor found)' % lastuser

	def AddMaintenanceMsg(self):
		"""Check if there are any bot maintenance messages and add them to every users news.

		   Returns nothing but updates self._news_list and self._hist_list.
		"""

		if (self.maintenance_msg == []): return

		for item in self.maintenance_msg:
			page = pywikibot.Page(self.site, bot_config['maintenance_page'] % "")
			tmst = time.strftime('%H:%M, %d. %b. %Y')
			tmst = u'%s' % re.sub(' 0', ' ', tmst)
			page.sum_disc_data = (	bot_config['maintenance_mesg'],
						None,
						u'DrTrigon',
						tmst,
						{ pywikibot.sectionencode(item,self.site.encoding()):('',True,item) },
						self._PS_maintmsg )
			self._news_list[page.title()] = page
			self._hist_list[page.title()] = self._news_list[page.title()]

		pywikibot.output(u'\03{lightpurple}*** Bot maintenance messages added\03{default}')

	def searchForSignature(self, text):
		"""Check if there are (any or) a specific user signature resp. link to
		   user page in text.

		   @param text: Text content to search for signatures.
		   @type  text: string

		   Returns a tuple containing a list with byteoffsets and a dict with
		   the according match object.
		"""

		sign_list  = self._param['altsign_list']
		check_list = self._param['checksign_list']

		signs = {}
		for user in sign_list:
			for check in check_list:
				for m in re.finditer(check % {'usersig':user}, text):
					signs[m.start()] = m
		signs_pos = signs.keys()
		signs_pos.sort()

		return (signs_pos, signs)


#class Timer(threading.Thread):
#	'''
#	Timer thread that runs completely stand-alone in sperate thread and continous until 'cancel' is called.
#	Variables to use in 'func' have to be stored internally in 'kwargs'.
#	'''
#
#	def __init__(self, sec, func, **kwargs):
#		threading.Thread.__init__(self)
#		self.seconds = sec
#		self.function = func
#		self.kwargs = kwargs
#		self._t = threading.Timer(self.seconds, self._action)
#		self._watchdog = [None]*5
#	def _action(self):
#		self._watchdog = self._watchdog.append(self.kwargs)		# watchdog (for security)
#		self._watchdog.pop(0)						#
#		if (self._watchdog[0] == self._watchdog[-1]): self.cancel()	#
#		self.function(self)
#		del self._t
#		self._t = threading.Timer(self.seconds, self._action)
#		self._t.start()
#	def run(self):
#		#self._t.start()
#		self._action()
#	def cancel(self):
#		self._t.cancel()

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

