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
output to wiki in 'parse_news' the time is localized first!

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
## @package sum_disc
#  @brief   Summarize Discussions Robot
#
#  @copyright Dr. Trigon, 2008-2010
#
#  @section FRAMEWORK
#
#  Python wikipedia robot framework, DrTrigonBot.
#  @see http://pywikipediabot.sourceforge.net/
#  @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
#  @section LICENSE
#
#  Distributed under the terms of the MIT license.
#  @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
__version__ = '$Id$'
#


import re, sys
import time, codecs, os, calendar
import threading
import copy #, zlib
import string, datetime, hashlib

import config, pagegenerators, userlib
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


_PS_warning	= 1	# serious or no classified warnings/errors that should be reported
_PS_changed	= 2	# changed page   (if closed, will be removed)
_PS_unchanged	= 3	# unchanged page
_PS_new		= 4	# new page
_PS_closed	= 5	# closed page (remove it from history)
_PS_maintmsg	= 6	# maintenance message
_PS_notify	= 7	# global wiki notification


_REGEX_eol		= re.compile('\n')


bot_config = {	# unicode values
		'TemplateName':		u'Benutzer:DrTrigon/Entwurf/Vorlage:SumDisc',
		'userlist':		u'Benutzer:DrTrigonBot/Diene_Mir!',
		'maintenance_queue':	u'Benutzer:DrTrigonBot/Maintenance',
		'maintenance_page':	u'Benutzer Diskussion:DrTrigon#%s',

		'queue_security':	([u'DrTrigon'], u'Bot: exec'),

		# NON (!) unicode values
		'logger_tmsp':		True,
		'backup_hist':		True,

		# regex values
		'tmpl_params_regex':	re.compile('(.*?)data=(.*?)\|timestamp=(.*)', re.S),
		'page_regex':		re.compile(r'Page\{\[\[(.*?)\]\]\}'),

		# numeric values
		'timeout':		15.0,							# timeout for progress info display

		# list values
		# which lists are regex to compile ('backlinks_list' are no regex)
		#'regex_compile':	[ 'checkedit_list', 'checksign_list', 'ignorepage_list', ],
		#'regex_compile':	[ 'checkedit_list', 'ignorepage_list', 'ignorehead_list', ],
		'regex_compile':	[ 'checkedit_list', 'ignorehead_list', ],
		# which lists may contain variables to substitute
		#'vars_subst':		[ 'checkedit_list', 'checksign_list', 'ignorepage_list', 'backlinks_list', 'altsign_list' ],
		'vars_subst':		[ 'checkedit_list', 'ignorepage_list', 'backlinks_list', 'altsign_list' ],	# + 'ignorehead_list' ?
		# which lists should preserve/keep their defaults (instead of getting it overwritten by user settings)
		'default_keep':		[ 'checkedit_list', 'altsign_list' ],
		# which lists should be translated according to site's lang
		'translate':		[ 'notify_msg', 'parse_msg' ],

		'msg': {
			'de':	( u'Bot: ',
				u'Diskussions-Zusammenfassung hinzugefügt (%i Einträge)',
				u'Diskussions-Zusammenfassung aktualisiert (%i Einträge in %s)',
				),
			'en':	( u'robot ',
				u'Discussion summary added: %i entries',
				u'Discussion summary updated: %i entries in %s',
				),
		},

		# bot paramater/options (modifiable by user)
		'param_default':	{ 'checkedit_count':	500,				# CHECK recent EDITs, a COUNT
					#'checkedit_count':	1000,
					'reportchanged_switch':	True,				# REPORT CHANGED discussions, a SWITCH
					'getbacklinks_switch':	False,				# GET BACKLINKS additionally, a SWITCH
					'reportwarn_switch':	True,				# (not published yet)
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
								u'^(Wikipedia:Kartenwerkstatt/Kartenwünsche)',		#
								u'^(Wikipedia:Bots/.*)', ],				# DRTRIGON-11
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
					# LIST of SIGNATUREs to USE, a LIST
					'backlinks_list':	[ u'%(userdiscpage)s',
								u'Benutzer:%(username)s', ],
					# (hidden)
					#userResultPage: default is NOT DEFINED - this is a SPECIAL PARAM it is not
					#		 thought to be used explicit, it is defined by the page link (implicit).
					# (not published yet: LIST of HEADs to IGNORE, a LIST)
					'ignorehead_list':	[ u'(.*?) \(erl.\)', ],

					# (hidden)
					'notify_msg': {
						'de':	{
							_PS_changed:	u'Diskussion verändert',
							_PS_new:	u'Neue Diskussion',
							_PS_closed:	u'Diskussion abgeschlossen', 
							_PS_maintmsg:	u'BOT MESSAGE',
							_PS_notify:	u'Benachrichtigung',
							},
						'en':	{
							_PS_changed:	u'Discussion changed',
							_PS_new:	u'New Discussion',
							_PS_closed:	u'Discussion closed', 
							_PS_maintmsg:	u'BOT MESSAGE',
							_PS_notify:	u'Notification',
							},
						},
					# (hidden)
					'parse_msg': {
						'de':	{
							u'*':		u'*%s: %s - letzte Bearbeitung von %s (%s)',
							_PS_closed:	u'*%s: %s alle Diskussionen wurden beendet (Überwachung gestoppt) - letzte Bearbeitung von %s (%s)',
							_PS_notify:	u'*%s: <span class="plainlinks">[%s %s]</span> - letzte Bearbeitung von [[User:%s]] (%s)',
							_PS_warning:	u'*Bot Warn-Nachricht: %s "\'\'%s\'\'"',
							u'end':		u'<noinclude>\nZusammenfassung erstellt von und um: ~~~~</noinclude>',
							u'nonhuman':	u'(keinen menschlichen Bearbeiter gefunden)',
							},
						'en':	{
							u'*':		u'*%s: %s - last edit by %s (%s)',
							_PS_closed:	u'*%s: %s all discussions have finished (surveillance stopped) - last edit by %s (%s)',
							_PS_notify:	u'*%s: <span class="plainlinks">[%s %s]</span> - last edit by [[User:%s]] (%s)',
							_PS_warning:	u'*Bot warning message: %s "\'\'%s\'\'"',
							u'end':		u'<noinclude>\nSummary generated from and at: ~~~~</noinclude>',
							u'nonhuman':	u'(no human editor found)',
							},
						}
					},
}

# debug tools
# 'write2wiki', 'write2hist'		# operational mode (default)
# 'user'				# no write, skip users
# 'user', 'write2hist'			# write only history, skip users
# 'write2wiki', 'user', 'write2hist'	# write, skip users
# 'write2hist'				# write only history (for code changes and smooth update)
# 'write2wiki', 'user'			# write wiki, skip users
# 'write2hist', 'toolserver'		# write only history (for code changes and smooth update), toolserver down
debug = []				# no write, all users
#debug.append( 'write2wiki' )		# write to wiki (operational mode)
#debug.append( 'user' )			# skip users
debug.append( 'write2hist' )		# write history
#debug.append( 'toolserver' )		# toolserver down
#debug.append( 'code' )			# code debugging

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

	rollback	= 0

	_param_default	= bot_config['param_default']	# same ref, no copy

	_global_warn	= []

	def __init__(self):
		'''Constructor of SumDiscBot(); setup environment, initialize needed consts and objects.'''

		pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

		dtbext.basic.BasicBot.__init__(self, bot_config)

		# init constants
        	self._userListPage = pywikibot.Page(self.site, bot_config['userlist'])
		#print [item[0] for item in self._getUsers()]		# enhance 'ignorepage_list'

		pywikibot.output(u'\03{lightred}** Receiving User List (wishes): %s\03{default}' % self._userListPage)
		self._user_list = self.loadUsersConfig(self._userListPage)

		# [JIRA: DRTRIGON-8, DRTRIGON-32]
		# (this is a possible but dangerous solution, could
		# inhibit notifications between the bot users disc. pages)
		#bot_user_ignorepage = []
		#for user in self._user_list:
		#	_userPage = pywikibot.Page(self.site, u'Benutzer_Diskussion:%s' % user.name())
 		#	if _userPage.isRedirectPage():
 		#		_userPage = _userPage.getRedirectTarget()
 		#	self.loadMode(_userPage)
		#	if   self._mode:
		#		bot_user_ignorepage.append( self._tmpl_data )
		#	elif (u'userResultPage' in user.param):
		#		bot_user_ignorepage.append( u'Benutzer:%s' % user.param['userResultPage'] )
		#if 'ignorepage_list' in bot_config['regex_compile']:
		#	bot_user_ignorepage = [re.compile(item) for item in bot_user_ignorepage]
		#self._param_default['ignorepage_list'] += bot_user_ignorepage

		pywikibot.output(u'\03{lightred}** Receiving Job Queue (Maintenance Messages)\03{default}')
		page = pywikibot.Page(self.site, bot_config['maintenance_queue'])
		self.maintenance_msg = self.loadJobQueue(page, bot_config['queue_security'], debug = ('write2wiki' in debug))

		self._wday = time.gmtime().tm_wday

		# init variable/dynamic objects

		# code debugging
		dtbext.pywikibot.debug = ('code' in debug)

	## @todo re-write some functions to be pagegenerators and use pagegenerators.CombinedPageGenerator()
	#        and others to combine and use them
	#        \n[ JIRA: ticket? ]
	#  @todo limitted backlinks: try to take the most recent ones
	#        \n[ JIRA: ticket? ]
	def run(self):
		'''Run SumDiscBot().'''

		pywikibot.output(u'\03{lightgreen}* Processing User List (wishes):\03{default}')

		if 'user' in debug: pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE USERS WILL BE SKIPPED ! ===\03{default}')

		for user in self._user_list:					# may be try with PreloadingGenerator?!
			if (('user' in debug) and (user.name() != u'DrTrigon')): continue

			# set user and init params
			self.setUser(user)
			self.pages = SumDiscPages(self.site, self._param)

			pywikibot.output('\03{lightred}** Processing User: %s\03{default}' % self._user)
			#pywikibot.output(u'\03{lightred}** Processing User: %s\03{default}' % self._user.name())

			# get operating mode
			self.loadMode(self._userPage, regex_compile=('ignorepage_list' in bot_config['regex_compile']))

			# get history entries
			self.loadHistory(rollback=self.rollback)
			# (HistoryPageGenerator)

			# check special pages for latest contributions
			self.checkRecentEdits()
			# RecentEditsPageGenerator

			# get the backlinks to user disc page
			# (limitted backlinks: some return >> 500 backlinks, thus check only once a week ALL/2000 those)
			if self._param['getbacklinks_switch']:
				self.getUserBacklinks()
				# all pages served from here ARE CURRENTLY
				# SIGNED (have a Signature at the moment)
				# UserBacklinksPageGenerator

			# get global wiki notifications (toolserver/merl)		
			if self._param['globwikinotify_switch']:
				self.AddGlobWikiNotify()

			# check for news to report and those on relevancy
			# (disc-thread oriented version)
			self.getLatestRelevantNews()

			# CombinedPageGenerator from previous 2 (or 3) generators
			# feed this generator into a DuplicateFilterPageGenerator
			# and pass this (maybe with GlobalWikiNotificationsPageGen)
			# to getLatestRelevantNews
			# [ JIRA: ticket? ]

			# gehen auch in jede history... werden aber bei compress entfernt
			self.AddMaintenanceMsg()

			# post results to users Discussion page (with comments for history)
			self.postDiscSum()

			# free the memory again
			del self.pages

		pywikibot.output(u'\03{lightgreen}* Processing Warnings:\03{default}')

		# warnings/exceptions are printed to log, could be get by panel.py from there!
		# (separate and explicit warning handling not used anymore)
		#for warning in self._global_warn:		# output all warnings to log (what about a special wiki page?)
		#	pywikibot.output( "%s: %s" % warning )	

	def compressHistory(self, users = []):
		"""Read history, and re-write new history without any duplicates.

		   @param users: List of users supported by bot (and thus in history).
		   @type  users: list

		   Load, truncate and re-write history in files.
		"""

		if not users: users = [ item for item in self._user_list ]

		pywikibot.output(u'* Compressing of histories:')

		if bot_config['backup_hist']:
			timestmp = dtbext.date.getTimeStmpNow()
			pathname = pywikibot.config.datafilepath('logs/%s/' % timestmp, '')	# according to 'setUser'
			import shutil

		for user in users:
			self.setUser(user)

			try:
				begin = float(os.path.getsize(self._datfilename))
			except OSError:		# OSError: [Errno 2] No such file or directory
				continue

			# backup old history
			if bot_config['backup_hist']:
				dst = os.path.join(pathname, os.path.basename(self._datfilename))
				shutil.copyfile(self._datfilename, dst)

			# truncate history (drop old entries)
			self.pages = SumDiscPages(self.site, self._param)
			self.loadHistory()

			# write new history
			os.remove(self._datfilename)
			self.putHistory(self.pages.hist)

			end = float(os.path.getsize(self._datfilename))

			pywikibot.output(u'\03{lightred}** History of %s compressed and written. (%s %%)\03{default}' % (user.name(), (end/begin)*100))

	def setUser(self, user):
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
		self._datfilename = pywikibot.config.datafilepath('logs', 'sum_disc-%s-%s-%s.dat' % (self.site.family.name, self.site.lang, self._user.name()))

		# substitute variables for use in user defined parameters/options
		param_vars = {	'username':	self._user.name(),
				'userdiscpage':	userdiscpage,
				}
		for item in bot_config['vars_subst']:
			self._param[item] = [ subitem % param_vars for subitem in self._param[item] ]

		# pre-compile regex
		# (probably try to pre-compile 'self._param_default' once in __init__ and reuse the unchanged ones here)
		for item in bot_config['regex_compile']:
			self._param[item] = map(re.compile, self._param[item])

		# translate according to site's lang
		for item in bot_config['translate']:
			self._param[item] = pywikibot.translate(self.site.lang, self._param[item])

	def loadHistory(self, rollback = 0):
		"""Read history, and restore the page objects with sum_disc_data.

		   @param rollback: Number of history entries to go back (re-use older history).
		   @type  rollback: int

		   Returns nothing, but feeds to self.pages class instance.
		"""

		buf = self.loadFile()
		buf = bot_config['page_regex'].sub('[]', buf)
		buf = _REGEX_eol.split(buf)
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		# merge everything to one history
		news = {}
		usage = {}
		rollback_buf = []
		hist = {}
		for item in buf:
			if len(item.strip())==0: continue

			news_item = eval(item)
			#news.update( news_item )
			# news.update BUT APPEND the heading data in the last tuple arg
			for key in news_item.keys():
				# old history format
				# (after compression not needed anymore and can thus be removed in the future)
				if (len(news_item[key]) == 5):
					news_item[key] += (_PS_unchanged,)
					usage['old history'] = True
				# notify tag error
				# (origin could be 'old history' but is not clear, but can be removed in the future, eg. after comp.)
				if (news_item[key][0] == u'Notification') and (news_item[key][5] <> _PS_notify):
					news_item[key] = news_item[key][:-1] + (_PS_notify,)
					usage['notify tag error'] = True

				if key in news:	# APPEND the heading data in the last tuple arg
					if news_item[key][5] in [_PS_closed]:
						del news[key]
					else:
						heads = news[key][4]
						heads.update( news_item[key][4] )
						#news[key] = (news_item[key][0], news_item[key][1], news_item[key][2], news_item[key][3], heads, news_item[key][5])
						news[key] = news_item[key][:4] + (heads, news_item[key][5])
				else:
					news[key] = news_item[key]

			rollback_buf.append( copy.deepcopy(news) )

		if rollback_buf:
			rollback_buf.reverse()
			i = min([rollback, (len(rollback_buf)-1)])
			hist = rollback_buf[i]
			del rollback_buf
			usage['rollback'] = i

		# feed data to pages
		self.pages.hist = hist

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

		pywikibot.output(u'\03{lightpurple}*** History updated\03{default}')

	## @todo should be done in framework, in userlib.User.contributions() or else
	#        \n[ JIRA: DRTRIGON-59 ]
	def checkRecentEdits(self):
		"""Check wiki on recent contributions of specific user.

		   Returns nothing, but feeds to self.pages class instance.
		"""

		check_list = self._param['checkedit_list']
		count = self._param['checkedit_count']

		# [ JIRA: DRTRIGON-59 ]
		pywikibot.output(u'Getting latest contributions from user "%s" via API...' % self._user.name())

		# thanks to http://www.amk.ca/python/howto/regex/ and http://bytes.com/forum/thread24382.html
		#usersumList = [p.title() for p in pagegenerators.UserContributionsGenerator(self._user.name(), number = count)]
		usersumList = [p[0].title() for p in self._user.contributions(limit = count)]

		work = {}
		for item in usersumList:
			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					#work[match.group(1)] = ()
					name = match.group(1)
					page = pywikibot.Page(self.site, name)
					page.sum_disc_data = ()
					work[name] = page
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'\03{lightpurple}*** Latest %i Contributions checked\03{default}' % len(usersumList))

		# feed data to pages
		self.pages.update_work(work)

	## @todo generate a time sorted backling list and use the 2000 newest ones!
	#        \n[ JIRA: DRTRIGON-8 ]
	def getUserBacklinks(self):
		"""Check wiki on backlinks to specific user.

		   Returns nothing, but feeds to self.pages class instance.
		"""

		check_list = self._param['checkedit_list']

		userbacklinksList = []
		for item in self._param['backlinks_list']:
			page = pywikibot.Page(self.site, item)		# important for the generator to use the API
			#userbacklinksList += [p.title() for p in pagegenerators.ReferringPageGenerator(page, withTemplateInclusion=False)]
			userbacklinksList += [p.title() for p in page.getReferences(withTemplateInclusion=False)]
		userbacklinksList = list(set(userbacklinksList))	# drop duplicates

		work = {}
		count = 0
		# (some return >> 500 backlinks, thus check
		# only once a week ALL/2000 those, else limit)
		#if (self._wday == 0):
		if (self._wday == 6): # So
			#max_count = len(userbacklinksList)
			max_count = 2000
		else:
			max_count = 500
		for item in userbacklinksList:
			count += 1

			# drop the rest if limited
			if (len(work) > max_count):
				break

			#item = item[0]
			for check in check_list:
				match = check.search(item)
				if match:
					#work[match.group(1)] = ()
					name = match.group(1)
					page = pywikibot.Page(self.site, name)
					page.sum_disc_data = ()
					work[name] = page
					break		# should only match one of the possibilities, anyway just add it once!

		pywikibot.output(u'\03{lightpurple}*** %i Backlinks to user checked (limited to %i)\03{default}' % (len(userbacklinksList), max_count))

		# feed data to pages
		self.pages.update_work(work)

	## @todo speed up by catching all pages (used the same day) to disk, look into diskcache.py (@ref diskcache)
	#        \n[ JIRA: ticket? (think about it!) ]
	#  @todo preloading does not use API yet, should be done within pywikipedia framework
	#        \n[ JIRA: ticket? ]
	#  @todo wikipedia.Page.getVersionHistory() is not able to check page exceptions always and
	#        crashes sometimes, u'Benutzer Diskussion:MerlBot' for example
	#        \n[ JIRA: ticket? ]
	def getLatestRelevantNews(self):
		"""Check latest contributions on recent news and check relevancy of page by
		   splitting it into sections and searching each for specific users signature,
		   this is all done by PageSections class.

		   Returns nothing, but feeds to self.pages class instance.
		"""

		# check for news to report
		hist = self.pages.hist
		work = self.pages.work
		self.pages.start_promotion()
		gen1 = pagegenerators.PagesFromTitlesGenerator(work.keys())
		gen2 = pagegenerators.RegexFilterPageGenerator(gen1,
							       self._param['ignorepage_list'], 
							       inverse = True, 
							       ignore_namespace = False)
		# Preloads _contents and _versionhistory / [ JIRA: ticket? ]
		# WithoutInterwikiPageGenerator, 
		#gen3 = pagegenerators.PreloadingGenerator(gen2)
		gen3 = pagegenerators.ThreadedGenerator(target=pagegenerators.PreloadingGenerator,
							args=(gen2,),
							qsize=60)
		#gen4 = pagegenerators.RedirectFilterPageGenerator(gen3)
		# lets hope that no generator loses pages... (since sometimes this may happen)
		for page in gen3:
			name = page.title()
			#print ">>>", name, "<<<"
			page.sum_disc_data = work[name].sum_disc_data

			# get history (was preloaded)
			#actual = actual_dict[page.sectionFreeTitle()]
			# use preloaded with revCount=1
			try:
				actual = page.getVersionHistory(revCount=1)

				# check page exceptions / [ JIRA: ticket? ]
				if hasattr(page, u'_getexception'):
					raise page._getexception
			except pywikibot.NoPage:
				pywikibot.output(u'\03{lightaqua}WARNING: skipping not available (deleted) page at %s\03{default}' % page.title(asLink=True))
				continue
			except pywikibot.IsRedirectPage:
				pywikibot.output(u'\03{lightaqua}WARNING: skipping redirect page at %s\03{default}' % page.title(asLink=True))
				continue

			# actual/new status of page, has something changed?
			news = False
			if name in hist:
				if (not (hist[name].sum_disc_data[3] == actual[0][1])):
					# discussion has changed, some news?
					self.pages.edit_news(page, sum_disc_data=(self._param['notify_msg'][_PS_changed], 
										  None, # obsolete (and recursive)
										  actual[0][2], 
										  actual[0][1], 
										  hist[name].sum_disc_data[4], 
										  _PS_changed ) )
					news = True
				else:
					# nothing new to report (but keep for history and update it)
					self.pages.edit_oth(page, sum_disc_data=(hist[name].sum_disc_data[0], 
										 None, # obsolete (and recursive)
										 actual[0][2], 
										 actual[0][1], 
										 hist[name].sum_disc_data[4], 
										 _PS_unchanged ) )
			else:
				# new discussion, some news?
				self.pages.edit_news(page, sum_disc_data=(self._param['notify_msg'][_PS_new], 
									  None, # obsolete (and recursive)
									  actual[0][2], 
									  actual[0][1], 
									  {}, 
									  _PS_new ) )
				news = True

			# checkRelevancy: Check relevancy of page by splitting it into sections and searching
			if not news:
				continue

			self.pages.promote_page() # hist -> news

			entries = PageSections(page, self._param)
			try:
				page.getSections()
			except:
				pass

			(page, page_rel, page_signed) = entries.check_rel()

			# update sum_disc_data in page (checksums, relevancies, ...)
			self.pages.edit_news(page)
			self.pages.edit_hist(page)

			# if page is not relevant, don't list discussion
			if not page_rel:
				self.pages.promote_page_irrel(page, page_signed)

			# free the memory again
			del entries

		gen3.stop()

		self.pages.end_promotion()

		pywikibot.output(u'\03{lightpurple}*** Latest News searched and relevancy of threads checked\03{default}')

	def AddGlobWikiNotify(self):
		"""Check if there are any global wiki notifications and add them to every users news.

		   Returns nothing, but feeds to self.pages class instance.
		"""

		hist = self.pages.hist

		# get global wiki notifications (toolserver/merl)		
		if 'toolserver' in debug:
			pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE TOOLSERVER ACCESS WILL BE SKIPPED ! ===\03{default}')
			globalnotify = []
		else:
			dtbext.userlib.addAttributes(self._user)
			globalnotify = self._user.globalnotifications()

		# check for GlobalWikiNotifications to report
		localinterwiki = self.site.language()
		count = 0
		for (page, data) in globalnotify:
			count += 1

			# skip to local disc page, since this is the only page the user should watch itself
			if (page.site().language() == localinterwiki) and \
			   (page.site().family.name == u'wikipedia'):
				pywikibot.output(u'\03{lightaqua}WARNING: skipping global wiki notify to local wiki %s\03{default}' % page.title(asLink=True))
				continue

			# actual/new status of page, has something changed?
			if (data[u'link'] in hist.keys()) and \
			   (data[u'timestamp'] == hist[data[u'link']].sum_disc_data[3]):
				continue

			#data = page.globalwikinotify
			self.pages.edit_oth(page, sum_disc_data=(self._param['notify_msg'][_PS_notify], 
								 None, # obsolete (and recursive)
								 data['user'], 
								 data['timestamp'], 
								 {u'':('',True,u'')}, 
								 _PS_notify ),
						 title=data[u'link'])
			#self.pages.edit_hist(self._news_list[page.title()])

		if globalnotify:
			pywikibot.output(u'\03{lightpurple}*** %i Global wiki notifications checked\03{default}' % count)

	def AddMaintenanceMsg(self):
		"""Check if there are any bot maintenance messages and add them to every users news.

		   Returns nothing, but feeds to self.pages class instance.
		"""

		if (self.maintenance_msg == []): return

		for item in self.maintenance_msg:
			page = pywikibot.Page(self.site, bot_config['maintenance_page'] % "")
			tmst = time.strftime('%H:%M, %d. %b. %Y')
			tmst = u'%s' % re.sub(' 0', ' ', tmst)
			page.sum_disc_data = ( self._param['notify_msg'][_PS_maintmsg],
					       None,
					       u'DrTrigon',
					       tmst,
					       { pywikibot.sectionencode(item,self.site.encoding()):('',True,item) },
					       _PS_maintmsg )
			self.pages.edit_news(page)
			self.pages.edit_hist(page)

		pywikibot.output(u'\03{lightpurple}*** Bot maintenance messages added\03{default}')

	def postDiscSum(self):
		"""Post discussion summary of specific user to discussion page and write to histroy
		   (history currently implemented as local file, but wiki page could also be used).

		   Returns nothing but dumps self.pages class instance to the history file and writes changes
		   to the wiki page.
		"""

		(buf, count) = self.pages.parse_news(self._param)
		if (count > 0):
			pywikibot.output(u'===='*15 + u'\n' + buf + u'\n' + u'===='*15)
			pywikibot.output(u'[%i entries]' % count )

			if 'write2wiki' in debug:
				head, add, mod = pywikibot.translate(self.site.lang, bot_config['msg'])
				if not self._mode:
					# default: write direct to user disc page
					comment = head + add % count
					self.append(self._userPage, buf, comment=comment, minorEdit=False)
				else:
					# enhanced (with template): update user disc page and write to user specified page
					tmplsite = pywikibot.Page(self.site, self._tmpl_data)
					comment = head + mod % (count, tmplsite.title(asLink=True))
					self.save(self._userPage, self._content, comment=comment, minorEdit=False)
					comment = head + add % count
					self.append(tmplsite, buf, comment=comment)
				dtbext.pywikibot.addAttributes(self._userPage)
				purge = self._userPage.purgeCache()

				pywikibot.output(u'\03{lightpurple}*** Discussion updates added to: %s (purge: %s)\03{default}' % (self._userPage.title(asLink=True), purge))
			else:
				pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

			if 'write2hist' in debug:
				self.putHistory(self.pages.hist)
			else:
				pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO HISTORY ! ===\03{default}')
		else:
			pywikibot.output(u'\03{lightpurple}*** Discussion up to date: NOTHING TO DO\03{default}')


class SumDiscPages(object):
	"""An object representing all pages relevant for processing a user.

	"""

	def __init__(self, site, param):
		self._hist_list = {}		# archived pages from history
		self._work_list = {}		# pages to check for news
		self._news_list = {}		# news to check for relevancy and report afterwards
		self._oth_list = {}		# ...?

		self.site = site

		self.param = param

	def set_hist(self, hist):
		# set history
		self._hist_list = hist

		# create work list (out of page instances)
		work = {}
		for name in hist.keys():
			page = pywikibot.Page(self.site, name)
			page.sum_disc_data = hist[name]
			hist[name] = page

			# worklist (without globalnotify)
			if page.sum_disc_data[5] not in [_PS_notify]:
				work[name] = page

		# add to work list
		self.update_work(work)

	def get_hist(self):
		return self._hist_list

	# http://docs.python.org/library/functions.html
	hist = property(get_hist, set_hist, doc="History dict property.")

	def edit_hist(self, histpage):
		# add hist page to hist page list
		self._hist_list[histpage.title()] = histpage

	def update_work(self, work):
		# update/merge present work list with additional work
		self._work_list.update(work)

	def get_work(self):
		return self._work_list

	work = property(get_work, doc="Work dict property.")

	def get_news(self):
		return self._news_list

	news = property(get_news, doc="News dict property.")

	def edit_news(self, newspage, sum_disc_data=None):
		# add sum_disc_data if present
		if sum_disc_data:
			newspage.sum_disc_data = sum_disc_data

		# add news page to news page list
		self._news_list[newspage.title()] = newspage

		self.newspage = newspage # for promote_page

	def edit_oth(self, othpage, sum_disc_data=None, title=None):
		# add sum_disc_data if present
		if sum_disc_data:
			othpage.sum_disc_data = sum_disc_data

		# add news page to news page list
		if not title:
			title = othpage.title()
		self._oth_list[title] = othpage

	def exists(self, page):
		fulldict = {}
		fulldict.update( self._hist_list )
		fulldict.update( self._work_list )
		fulldict.update( self._news_list )
		fulldict.update( self._oth_list )
		return (page.title() in fulldict.keys())

	def start_promotion(self):
		# start relevancy check page promotion to news
		# (and re-create an actual history)
		self._hist_list = {}

	def promote_page(self):
		# do relevancy check page promotion to news
		# (and re-create an actual history)
		self._hist_list[self.newspage.title()] = self.newspage

	def end_promotion(self):
		# finish relevancy check page promotion to news
		# (re-assign/-sort the pages into the right categories)

		# self._oth_list contents all '_PS_unchanged' and warnings '_PS_warning'
		for title in self._oth_list.keys():
			if (self._oth_list[title].sum_disc_data[5] == _PS_unchanged):
				# '_PS_unchanged'
				#self._hist_list[title] = self._oth_list[title]
				pass
			elif (self._oth_list[title].sum_disc_data[5] == _PS_notify):
				# '_PS_notify'
				self._news_list[title] = self._oth_list[title]
				self._hist_list[title] = self._oth_list[title]
			else:
				# warnings: '_PS_warning', ...
				self._news_list[title] = self._oth_list[title]

	def promote_page_irrel(self, page, signed):
		# page is not relevant, thus don't list discussion

		title         = page.title()
		sum_disc_data = page.sum_disc_data

		del self._news_list[title]
		if (sum_disc_data[5] == _PS_new):
			del self._hist_list[title]

		# discussion closed (no signature on page anymore)
		if (not signed) and (sum_disc_data[5] == _PS_changed):
			page.sum_disc_data = ( self.param['notify_msg'][_PS_closed], 
					       None, 
					       sum_disc_data[2], 
					       sum_disc_data[3], 
					       {}, 
					       _PS_closed )
			self.edit_news(page)
			#del self._hist_list[title]
			self.edit_hist(page)

        def parse_news(self, param):
		"""Filter and parse all the info and rewrite in in wiki-syntax, to be put on page.

		   Returns a tuple (result wiki text, message count).
		"""

		switch  = param['reportchanged_switch']
		switch2 = param['reportclosed_switch']
		if not switch:	ps_types =  ( [_PS_new, _PS_maintmsg], )
		else:		ps_types =  ( [_PS_new, _PS_changed, _PS_maintmsg], )
		if not switch2:	ps_types += ( [], )
		else:		ps_types += ( [_PS_closed], )

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

				# default: if no subsections on page
				item = page.title(asLink=True)
				if report:
					# subsections on page
					item = u'%s → %s' % (page.title(asLink=True), string.join(report, u', '))

				data = (data[0], item, self._getLastEditor(page, data[2]), dtbext.date.getTime(data[3]))
				data = self.param['parse_msg'][u'*'] % data
			elif data[5] in ps_types[1]:
				# closed
				data = (data[0], page.title(asLink=True), self._getLastEditor(page, data[2]), dtbext.date.getTime(data[3]))
				data = self.param['parse_msg'][_PS_closed] % data
			#elif data[5] in [_PS_warning]:
			#	# warnings
			#	data = (page.title(asLink=True), data[0])
			#	data = self.param['parse_msg'][_PS_warning] % data
			#	self._global_warn.append( (self._user.name(), data) )
			#	if not param['reportwarn_switch']: continue
			elif data[5] in [_PS_notify]:
				# global wiki notifications
				data = (data[0], page.globalwikinotify['url'], page.title(), data[2], dtbext.date.getTime(data[3]))
				data = self.param['parse_msg'][_PS_notify] % data
			else:
				continue # skip append
			buf.append( data )

		count = len(buf)
		if (count > 0):
			buf =  string.join(buf, u'\n')
			buf += self.param['parse_msg'][u'end']
                else:
			buf = u''

		return (buf, count)

	def _getLastEditor(self, page, lastuser):
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
			if humaneditor == lastuser:
				return u'[[User:%s]]' % humaneditor
			else:
				return u'[[User:%s]]/[[User:%s]]' % (humaneditor, lastuser)
		else:
			# no human editor found; use last editor
			return (u'[[User:%s]] ' % lastuser) + self.param['parse_msg'][u'nonhuman']


class PageSections(object):
	"""An object representing all sections on a page.

	"""

	def __init__(self, page, param):
		"""Retrieves the page content and splits it to headings and bodies ('check relevancy
		   of page by searching specific users signature').

		   @param page: Page to process.
		   @param param: Additional parameters to use for processing.
		   @type  param: dict

		   Returns a list of tuples containing the sections with info and wiki text.
		"""

		self._entries = []

		self._page = page
		self._param = param

		# code debugging
		if 'code' in debug:
			pywikibot.output(page.title())

		# enhance to dtbext.pywikibot.Page
		dtbext.pywikibot.addAttributes(page)

		# get content and sections (content was preloaded earlier)
		force = False
		retries = 0
		while retries < 3:
			try:
				#buf = self.load(page)
				buf = page.get(force=force)
				sections = page.getSections(minLevel=1)
				break
			except pywikibot.Error:
				# sections could not be resoled, try again by forcing (3 tries max.)
				# or else process the whole page at once
				sections = []
				force = True
				retries += 1

				pywikibot.output(u'\03{lightaqua}WARNING: problem trying to retrieve section data for %s\03{default}' % page.title(asLink=True))

		# drop from templates included headings (are None)
		sections = [ s for s in sections if s[0] ]

		if len(sections) == 0:
			self._entries = [ ((u'',u'',u''), buf) ]
		else:
			# append 'EOF' to sections list
			# (byteoffset, level, wikiline, line, anchor)
			sections.append( (len(buf) + 1, None, None, None, None) )

			for i, s in enumerate(sections[:-1]):
				bo_start = s[0]
				bo_end   = sections[i+1][0] - 1

				self._entries.append( (s[2:], buf[bo_start:bo_end]) )

	def check_rel(self):
		# iterate over all sections in page and check their relevancy

		page = self._page

		page_rel    = False
		page_signed = False
		try:	checksum = page.sum_disc_data[4]
		except:	checksum = None
		checksum_new = {}

		for i, (head, body) in enumerate(self._entries): # iterate over all headings/sub sections
			# wikiline is wiki text, line is parsed and anchor is the unique link label
			(wikiline, line, anchor) = head[:3]

			# ignorelist for headings
			if wikiline:
				skip = False
				for check in self._param['ignorehead_list']:
					if check.search(wikiline):
						skip = True
						break
				if skip: continue

			# check relevancy of section
			(rel, checksum_cur, checks) = self._check_sect_rel(body, checksum, anchor)

			# is page signed?
			page_signed = page_signed or checks['signed'] # signature check

			# is page relevant?
			if not rel: continue

			# page IS relevant, update checksum
			page_rel = True
			checksum_new[anchor] = (checksum_cur, rel, line)

		# update sum_disc_data in page (checksums, relevancies, ...)
		page.sum_disc_data = page.sum_disc_data[:4] + (checksum_new,) + page.sum_disc_data[5:]

		return (page, page_rel, page_signed)

	def _check_sect_rel(self, data, checksum, anchor):
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

		# per default assume relevancy
		checks = { 'changed':    True,
			   'signed':     True,
			   'lasteditor': False, }

		# check if thread has changed
		checksum_cur = hashlib.md5(data.encode('utf8').strip()).hexdigest()
		if ((checksum and (len(checksum) > 0)) and (anchor in checksum)):
			checks['changed'] = (not (checksum[anchor][0] == checksum_cur))

		if not checks['changed']:
			return (False, checksum_cur, checks)

		# search for signature in section/thread
		(signs_pos, signs) = self._search_sign(data)
		checks['signed'] = (len(signs_pos) > 0) # are signatures present

		if not checks['signed']:
			return (False, checksum_cur, checks)

		# check if user was last editor
		# look at part after '\n', after each signature is at least one '\n'
		data = data[signs_pos[-1]:] + u'\n'
		data = _REGEX_eol.split(data, maxsplit=1)[1]
		checks['lasteditor'] = not (len(data.strip(u' \n')) > 0) # just check for add. text (more paranoid)

		if checks['lasteditor']:
			return (False, checksum_cur, checks)

		return (True, checksum_cur, checks)

	def _search_sign(self, text):
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


# idea: may be create a class for storage of sum_disc_data and for
# easy save load (history) and else... ?!???


def main():
	bot = SumDiscBot()
	if len(pywikibot.handleArgs()) > 0:
		for arg in pywikibot.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if   arg[:17] == "-compress_history":
			#if 	arg[:17] == "-compress_history":
				bot.compressHistory( eval(arg[18:]) )
				return
			elif (arg[:17] == "-rollback_history"):
				bot.rollback = int( arg[18:] )
			elif (arg[:5] == "-auto") \
			     or (arg[:5] == "-cron"):
				pass
			elif (arg == "-all") \
			     or (arg == "-default") \
			     or ("-sum_disc" in arg):
				pass
			#elif	(arg == "-test_run"):
			#	debug = ...
			else:
				pywikibot.showHelp()
				return
	try:
		bot.run()
	except KeyboardInterrupt:
		pywikibot.output('\nQuitting program...')

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

