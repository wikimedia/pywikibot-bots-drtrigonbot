# -*- coding: utf-8  -*-
"""
THIS IS AN EXPERIMENTAL BOT CODE (BETA) FOR 'Artikel des Tages' DISCUSSION SUMMARY.
ALL COMMENTS AND INFOS HERE HAVE TO BE ADAPTED!!


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

# ====================================================================================================
#
# ToDo-Liste (Bugs, Features, usw.):
# http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste
#
# READ THE *DOGMAS* FIRST!
# 
# ====================================================================================================

## @package page_disc
#  @brief   Summarize Page Discussions Robot (like sum_disc)
#
#  @copyright Dr. Trigon, 2010
#
#  @todo      The whole code here has to be adapted to he new bot style.
#             May be the simplest could be to do a re-write with code from
#             sum_disc. But this makes no sense as long as not reply has
#             come from Hæggis.
#             \n[ JIRA: DRTRIGON-49 ]
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


import config, pagegenerators
import dtbext
import re, sys
#import codecs, pickle
#import httplib, socket, urlparse, urllib, urllib2
import time, codecs, os, calendar
import threading
import copy #, zlib
# Splitting the bot into library parts
import wikipedia as pywikibot

import string, datetime, hashlib
#import titletranslate
#from datetime import datetime, timedelta


## ====================================================================================================
##
## read external config vars
##exec(open("sum_disc-conf.py","r").read(-1))
#from sum_disc_conf import *
##
## ====================================================================================================


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


class PageDiscRobot(dtbext.basic.BasicBot):
	'''
	Robot which will check your latest edits for discussions and your old
	discussions against recent changes, pages to check are provided by a
	list. (iterable like generators)
	'''
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	silent		= False
	rollback	= 0

	#_param_default		= conf['param_default']			# same ref, no copy
	_eol_regex		= re.compile('\n')
	_bracketopen_regex	= re.compile('\[')
	_bracketclose_regex	= re.compile('\]')
	_reftag_err_regex	= re.compile(r'<strong class="error">Referenz-Fehler: Einzelnachweisfehler: <code>&lt;ref&gt;</code>-Tags existieren, jedoch wurde kein <code>&lt;references&#160;/&gt;</code>-Tag gefunden.</strong>')
	_page_regex		= re.compile(r'Page\{\[\[(.*?)\]\]\}')

	_PS_warning	= 1	# serious or no classified warnings/errors that should be reported
	_PS_changed	= 2	# changed page   (if closed, will be removed)
	_PS_unchanged	= 3	# unchanged page
	_PS_new		= 4	# new page
	_PS_closed	= 5	# closed page (remove it from history)
	_PS_maintmsg	= 6	# maintenance message
	_PS_notify	= 7	# global wiki notification

	_global_warn	= []
	_oth_list	= {}

	def __init__(self):#, userListPage):
		'''
		constructor of SumDiscBot(), initialize needed vars
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 30, 17)

		pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

		# modification of timezone to be in sync with wiki
		os.environ['TZ'] = 'Europe/Amsterdam'
		time.tzset()
		pywikibot.output(u'** Set TZ: %s' % str(time.tzname))	# ('CET', 'CEST')

		pywikibot.output(u'** Setting Page List (source and target)')
		self._page_list = []
		for item in [u"Benutzer_Diskussion:Hæggis"]:
			self._page_list.append( dtbext.pywikibot.Page(pywikibot.getSite(), item) )
		self._target = [ {'page': dtbext.pywikibot.Page(pywikibot.getSite(), u"Benutzer:DrTrigon/Spielwiese"), 'section': 3} ]

		#self._script_path = '/home/ursin/data/toolserver_bak/pywikipedia/'	# local
		self._script_path = os.environ['HOME'] + '/pywikipedia/'		# on toolserver

	def run(self):
		'''
		run SumDiscBot()
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24, 38, 17)


		pywikibot.output(u'\03{lightgreen}* Processing Page List:\03{default}')

		for page in self._page_list:
			#self._setUser(user)					# set user and init params
			#self._datfilename = '%slogs/page_disc-%s-%s-%s.dat' % (conf['script_path'], 'wikipedia', 'de', page.title())
			self._datfilename = '%slogs/page_disc-%s-%s-%s.dat' % (self._script_path, 'wikipedia', 'de', page.title())

			pywikibot.output(u'\03{lightgreen}** Processing Page: %s\03{default}' % page.title(asLink=True))

			self._work_list = {}
			self._work_list[page] = True

			self._getHistoryPYF()#rollback=self.rollback)

			self._getLatestNews()					# check for news to report

			self._checkRelevancyTh()				# check self._news_list on relevancy, disc-thread oriented version...

			self._postDiscSum()					# post results to users Discussion page (with comments for history)

		#pywikibot.output(u'\03{lightgreen}* Processing Warnings:\03{default}')

		#for warning in self._global_warn:		# output all warnings to log (what about a special wiki page?)
		#	pywikibot.output( "%s: %s" % warning )	

	def _getHistoryPYF(self, rollback = 0):
		buf = self._readFile()
		buf = self._page_regex.sub('[]', buf)
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
				#print type(news_item[key][4]), len(news_item[key]), key in news
				#if key in news:		# APPEND the heading data in the last tuple arg
				#	if news_item[key][5] in [self._PS_closed]:
				#		del news[key]
				#	else:
				#		heads = news[key][4]
				#		heads.update( news_item[key][4] )
				#		news[key] = (news_item[key][0], news_item[key][1], news_item[key][2], news_item[key][3], heads)
				#else:
				#	news[key] = news_item[key]
				news[key] = news_item[key]
			rollback_buf.append( copy.deepcopy(news) )
		if rollback_buf:
			rollback_buf.reverse()
			i = min([rollback, (len(rollback_buf)-1)])
			self._hist_list = rollback_buf[i]
			del rollback_buf
			usage['rollback'] = i

		pywikibot.output(u'*** History recieved %s' % str(usage))

	def _getLatestNews(self):
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

		# check for news to report
		self._news_list = {}
		#sites = dtbext.pywikibot.Pages(pywikibot.getSite(), self._work_list.keys())
		#actual_dict = sites.getVersionHistory()
		for keys in self._work_list.keys():
			site = page = keys
			actual_dict = site.getVersionHistory()
			actual = actual_dict[0]

			# wenn möglich im ganzen ablauf nur 1 mal (bis auf wiederholungen bei problemen)...
			(sections, verify) = site.getSections(minLevel=1)

			for j, section in enumerate(sections):
				if section[2] in self._hist_list:					# already seen, but changed or unchanged
					self._news_list[section[2]] = (	u'Modifikation', 
									(j, section), 
									actual[2], 
									actual[1], 
									self._hist_list[section[2]][4], 
									self._PS_changed )
				else:									# new (never seen)
					self._news_list[section[2]] = (	u'Neuer Eintrag', 
									(j, section), 
									actual[2], 
									actual[1], 
									{},
									self._PS_new )

		pywikibot.output(u'*** Latest News searched')

	def _postDiscSum(self):
		'''
		post discussion summary of specific user to discussion page and write to histroy
		( history currently implemented as local file, but wiki page could also be used )

		input:  self._news_list [dict]
                        self._getMode()
                        self-objects
		returns:  (appends self._news_list to the history file, nothing else)
		'''

		#count = len(self._news_list.keys())
		(buf, count) = self._parseNews()
		if (count > 0):
			pywikibot.output(u'='*50 + u'\n' + buf + u'\n' + u'='*50)
			pywikibot.output(u'[%i entries]' % count )

			pywikibot.setAction(u'Diskussions-Zusammenfassung für Unterseite hinzugefügt: %i Einträge' % count)
			if not self.append(self._target[0]['page'], u'\n' + buf, section = self._target[0]['section']):
				pywikibot.output(u'*** ERROR: Writing of data to Wiki was not possible !')

			self._writeFile( str(self._hist_list).decode('latin-1') )
			pywikibot.output(u'*** History updated')
		else:
			pywikibot.output(u'*** Discussion up to date: NOTHING TO DO')

	#def _transPage(self, page):
	#	'''
	#	???
	#	'''
	#	title = page.title()
	#	for item in trans_str.keys():
	#		title = re.sub(item, trans_str[item], title)
	#	return pywikibot.Page(pywikibot.getSite(), title)

	def _readPage(self, page, full=False):
		'''
		read wiki page

		input:  page
		returns:  page content [string (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28)

		if full:	(mode, info) = ('full', ' using "getFull()" mode')
		else:		(mode, info) = ('default', '')

		#pywikibot.output(u'\03{lightblue}Reading Wiki at %s...\03{default}' % page.title(asLink=True))
		pywikibot.output(u'\03{lightblue}Reading Wiki%s at %s...\03{default}' % (info, page.title(asLink=True)))
		try:
			#content = page.get()
			content = page.get(mode=mode)
			#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
			#	pywikibot.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.title(asLink=True))
			#	continue
		except (pywikibot.NoPage, pywikibot.IsRedirectPage):
			content = u''
		return content

	def _checkRelevancyTh(self):
		'''
		check relevancy of page by searching specific users signature
		(improved, disc-thread oriented version)

		input:  self._news_list [dict]
                        self._oth_list [dict] (same format as self._news_list)
                        self._readPage() (with 'full=' and without)
                        dtbext.pywikibot-objects
                        self-objects (such as self._getThContent(), self._checkThData(), ...)
		returns:  self._news_list [dict]
		          keys are:  page titles [string (unicode)]
		          format:    (type_desc_str, page, lastedit_user, lastedit_time, checksum) [tuple]
                          self._hist_list [dict] (same format as self._news_list)
                (but checksum is updated and all irrelevant entries are deleted from output)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 29, 17)

		#def test(timerobj): pywikibot.output(u'\03{lightaqua}progress: %.1f%s (%i of %i) ...\03{default}' % (((100.*timerobj.kwargs['u'])/timerobj.kwargs['size']), u'%', timerobj.kwargs['u'], timerobj.kwargs['size']))
		#t = Timer(conf['timeout'], test, size = len(self._work_list.keys()), u = 0)

		# self._news_list contents all 'self._PS_changed' and 'self._PS_new'
		self._hist_list = copy.deepcopy(self._news_list)
		# kleiner speed-up patch, als option/parameter aktivierbar
		#if (t.kwargs['size'] != 0): t.run()
		for site in self._work_list.keys():
			#(site, buf) = page
			keys = site.title()
			#print site.get(section=2)
			#return

			try:
				content = self._readPage(site)
				(head, body) = self._getThContent(site, content)
				for i, key in enumerate(head):		# iterate over all headings/sub sections
					item = body[i]
					heading = head[i][0].strip()
					key = key[0]
					#j = self._news_list[key][1][0]

					## THIS IS VERY UNEFFICIENT AND SLOW, SLOW, SLOW!!! (BUT EASY TO CODE) SHOULD BE DONE AS IN THE sum_disc.py BUT IS MORE PROBLEMATIC!!
					## WRITE ONE SINGLE CODE TO SPLIT A PAGE INTO SECTIONS, USE HEADING LINE NUMBER... MAYBE ALREADY IN MEDIAWIKI API FRAMEWORK IMPLEMENTED...?!??!!
					#pywikibot.output(u"\03{lightblue}Reading Wiki page section '%s'...\03{default}"%key)
					#
					#item = site.get(section=j+1)

					if   (self._news_list[key][5] == self._PS_new):
						(probable, new_chksum) = self._checkThData(item, None)
						d = self._news_list[key]
						self._news_list[key] = d[0:4] + (new_chksum,) + d[5:]
						self._hist_list[key] = self._news_list[key]
					elif (self._news_list[key][5] == self._PS_changed):
						checksum = self._news_list[key][4]
						(probable, new_chksum) = self._checkThData(item, checksum)
						if probable:					# has changed
							d = self._news_list[key]
							self._news_list[key] = d[0:4] + (new_chksum,) + d[5:]
							self._hist_list[key] = self._news_list[key]
						else:						# is unchanged
							del self._news_list[key]
			except pywikibot.SectionError:	# is typically raised by ????????
				pass

			#t.kwargs['u'] += 1
			##keys = re.split('#', keys)[0]		# Seiten mit Unterabschnitten (falls Abschn. weg aber Seite noch da)
								# (eigentlich nur für bot maint. messages)

		#t.cancel()
		#del t

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

		#(sections, verify) = siteAPI.getSections(minLevel=1, getter=site.get)
		(sections, verify) = site.getSections(minLevel=1, pagewikitext=buf)
		if not verify:
			#pywikibot.output(u'!!! WARNING: Have to use "getFull"...')
			pywikibot.output(u"\03{lightblue}Re-Reading Wiki page (mode='full') at %s...\03{default}" % site.title(asLink=True))
			buf = site.get(mode='full')
			#buf = self._readPage( site, full=True )
			(sections, verify) = site.getSections(minLevel=1, pagewikitext=buf)
			if not verify:
				pywikibot.output(u"\03{lightblue}Re-Reading Wiki page (mode='parse') at %s...\03{default}" % site.title(asLink=True))
				parse_buf = site.get(mode='parse')
				if self._reftag_err_regex.search(parse_buf):
					#self._oth_list[site.title()] = (	u'was not able to get Sections properly, because of missing <references /> tag!', 
					#				site, 
					#				None, 
					#				None, 
					#				None, 
					#				self._PS_warning )
					pywikibot.output(u'was not able to get Sections properly, because of missing <references /> tag!')
				else:
					#self._oth_list[site.title()] = (	u'was not able to get Sections properly!', 
					#				site, 
					#				None, 
					#				None, 
					#				None, 
					#				self._PS_warning )
					pywikibot.output(u'was not able to get Sections properly!')
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

	def _checkThData(self, data, checksum):
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

		# check if thread has not changed (because user can be not last but thread has also not changed)
		# (introduce checksum with backwards compatibility)
		# converting of different data formats is now done in '_getHistoryPYF()'
		checksum_cur = hashlib.md5(item.encode(pywikibot.getSite().encoding()).strip()).hexdigest()
		return (not (checksum_cur == checksum), checksum_cur)				# is this body data relevant?

	def _readFile(self):
		'''
		read data (history) file

		input:  codecs.open(...).read(...)
                        self-objects
		returns:  file content [string]
		'''

		# unicode text schreiben, danke an http://www.amk.ca/python/howto/unicode
		try:
			datfile = codecs.open(self._datfilename, encoding=config.textfile_encoding, mode='r')
			#datfile = open(self._datfilename, mode='rb')
			buf = datfile.read()
			datfile.close()
			return buf
		except:	return u''

	def _writeFile(self, data):
		'''
		append data (history) to file

		input:  data
                        self-objects
		returns:  (appends data to the data/history file, nothing else)
		'''

		# könnte history dict mit pickle speichern (http://www.thomas-guettler.de/vortraege/python/einfuehrung.html#link_12.2)
		# verwende stattdessen aber wiki format! (bleibt human readable und kann in wiki umgeleitet werden bei bedarf)
		#datfile = codecs.open(self._datfilename, encoding=config.textfile_encoding, mode='a+')
		datfile = codecs.open(self._datfilename, encoding=config.textfile_encoding, mode='w')
		#datfile = codecs.open(self._datfilename, encoding='zlib', mode='a+b')
		datfile.write(u'\n\n' + data)
		#datfile.write(data)
		datfile.close()

        def _parseNews(self):
		'''
		filter and parse all the info and rewrite in in wiki-syntax, to be put on page

		input:  self._news_list [dict]
                        self-objects
		returns:  (result wiki text, message count) [tuple (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 17)

		switch = True
		switch2 = False
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
					#for subkey in data[4].keys():
					subkey = data[1][1][2]					# link
					item = (subkey,) + (data[4], True, data[1][1][3])	# actual_head = (link, ..., ..., wikitext)
					if not item[2]: continue		# is this heading relevant?
					#renderitem = dtbext.pywikibot.getParsedString(item[3], plaintext=True)	# replaces '_renderWiki()'
					# try without 'plaintext', gives full html result but we want wikitext which is only some
					# parts of the html tags striped, thus use 'removeHTMLParts' with 'keep_wikitags' (NOT USED IN 'sum_disc.py'... WHY?!???)
					renderitem = dtbext.pywikibot.removeHTMLParts(dtbext.pywikibot.getParsedString(item[3], plaintext=False)).strip()
					subitem = item[0]
					subitem = dtbext.pywikibot.removeHTMLParts(subitem, tags = [])	# remove any remainig html tags (NOT USED IN 'sum_disc.py'... WHY ARE THERE NO REMAINING TAGS?!???)
					subitem = self._bracketopen_regex.sub(u'.5B', subitem)	# urllib.quote(...) sets '%' instead of '.'
					subitem = self._bracketclose_regex.sub(u'.5D', subitem)	#
					if not (item[0] == ""):
						#headings.append( u'[[%s#%s|%s]]' % (data[1].title(), subitem, renderitem) )
						headings.append( u'[[%s#%s|%s]]' % (self._work_list.keys()[0].title(), subitem, renderitem) )
					if (len(headings) == 0):			# no subsections on page...
						#data = (data[0], data[1].title(), data[2], self._localizeDateTime(data[3]))
						#data = u'*%s: [[%s]] - last edit by [[User:%s]] (%s)' % data
						data = (data[0], self._localizeDateTime(data[3]))
						data = u'*%s: zuletzt um %s' % data
					else:
						#data = (data[0], data[1].title(), string.join(headings, u', '), data[2], self._localizeDateTime(data[3]))
						#data = u'*%s: [[%s]] at %s - last edit by [[User:%s]] (%s)' % data
						data = (data[0], string.join(headings, u', '), self._localizeDateTime(data[3]))
						data = u'*%s: %s zuletzt um %s' % data
				#elif data[5] in ps_types[1]:
				#	data = (data[0], data[1].title(), data[2], self._localizeDateTime(data[3]))
				#	data = u'*%s: [[%s]] all discussions have finished (surveillance stopped) - last edit by [[User:%s]] (%s)' % data
				elif data[5] in [self._PS_warning]:
					data = (data[1].title(), data[0])
					data = u'*Bot warning message: [[%s]] "\'\'%s\'\'"' % data
					self._global_warn.append( (self._user, data) )
					if not self._param['reportwarn_switch']: continue
				#elif data[5] in [self._PS_notify]:
				#	data = (data[0], data[1].extradata['url'], data[1].title(), data[2], self._localizeDateTime(data[3]))
				#	data = u'*%s: [%s %s] - last edit by [[User:%s]] (%s)' % data
				else:
					continue	# skip append
				buf.append( data )

		count = len(buf)
		if (count > 0):
			buf = string.join(buf, u'\n')
		else:
			buf = u''

		return (buf, count)

	def _localizeDateTime(self, timestamp):
		'''
		returns a localized datetime

		input:  timestamp
		returns:  localized time [time]
		'''
		# see also in 'dtbext/dtbext_wikipedia.py', 'GetTime' ...
		# is localized to the actual date/time settings, cannot localize timestamps that are
		#    half of a year in the past or future!
		timestamp = time.strptime(timestamp.encode(pywikibot.getSite().encoding()), '%H:%M, %d. %b. %Y')
		secs = calendar.timegm(timestamp)
		return time.strftime('%H:%M, %d. %b. %Y', time.localtime(secs)).decode(pywikibot.getSite().encoding())

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
	def _action(self):
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
	bot = PageDiscRobot()#conf['userlist'])	# for several user's, but what about complete automation (continous running...)
	if len(pywikibot.handleArgs()) > 0:
		for arg in pywikibot.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if 	arg[:17] == "-compress_history":
			#if 	arg[:17] == "-compress_history":
				bot.compressHistory( eval(arg[18:]) )
				return
			elif	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
				bot.silent = True
			elif	(arg == "-skip_clean_user_sandbox"):
				pass
			elif	(arg[:17] == "-rollback_history"):
				bot.rollback = int( arg[18:] )
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

