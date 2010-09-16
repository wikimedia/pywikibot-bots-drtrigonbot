# -*- coding: utf-8  -*-
"""
...
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
__version__='$Id: dtbext_basic.py 0.2.0022 2009-11-15 16:52 drtrigon $'
#


import re, sys
import time, codecs, os, calendar
import threading
import copy #, zlib
import sets, string, datetime, hashlib

import config, pagegenerators, userlib, basic
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


class BasicBot(basic.BasicBot):
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	#silent		= False
	#rollback	= 0

	_REGEX_eol		= re.compile('\n')
	#REGEX_subster_tag	= '<!--SUBSTER-%(var)s-->%(cont)s<!--SUBSTER-%(var)s-->'	# from 'subster.py'
	_REGEX_subster_tag	= '<!--SUBSTER-%(var)s-->'					#

	def __init__(self, bot_config):
		'''Constructor of BasicBot(); setup environment, initialize needed consts and objects.
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 30, 17)

		#basic.BasicBot.__init__(self, generator, dry)

		# modification of timezone to be in sync with wiki
		os.environ['TZ'] = 'Europe/Amsterdam'
		time.tzset()
		pywikibot.output(u'Setting process TimeZone (TZ): %s' % str(time.tzname))	# ('CET', 'CEST')

		# init constants
		self._bot_config = bot_config
		self._template_regex = re.compile('\{\{' + self._bot_config['TemplateName'] + '(.*?)\}\}', re.S)

		# init variable/dynamic objects
		self.site = pywikibot.getSite()
		dtbext.pywikibot.addAttributes( self.site )		# enhance to dtbext.pywikibot.Site

	def loadMode(self, page):
		'''Get operating mode from user's disc page by searching for the template.

		   input:  page [page]
                           self.load()
                           self-objects
		   returns:  self._mode [bool]
                             self._tmpl_data [string (unicode)]
                             self._param['ignorepage_list'] (with appended excludes)
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 17)

		self._mode = False
		self._tmpl_data = u''

		page_buf = self.load(page)
		self._content = page_buf

		for tmpl in pywikibot.extract_templates_and_params(page_buf):
			if tmpl[0] == self._bot_config['TemplateName']:
				# enhanced: with template
				self._mode = True
				self._tmpl_data = tmpl[1][u'data']
				self._param['ignorepage_list'].append( re.compile(self._tmpl_data) )

				# update template and content
				tmpl[1][u'timestamp'] = u'--~~~~'
				tmpl_text = dtbext.pywikibot.glue_template_and_params( tmpl )
				tmpl_pos  = self._template_regex.search(page_buf)
				self._content = page_buf[:tmpl_pos.start()] + tmpl_text + page_buf[tmpl_pos.end():]
				break

	# ADDED
	# REASON: common interface to bot user settings on wiki
	def loadUsersConfig(self, page):
		"""Get user list from wiki page, e.g. [[Benutzer:DrTrigonBot/Diene_Mir!]].
		   ADDED METHOD: common interface to bot user settings on wiki

		   @param page: Wiki page containing user list and config.
		   @type  page: page

		   Returns a list with entries: (user, param)
		   This list may be empty.
		"""

		#users = {}
		final_users = []
		for item in self._REGEX_eol.split(page.get()):
			item = re.split(',', item, maxsplit=1)
			#print "A"
			if (len(item) > 1):	# for compatibility with 'subster.py' (if needed)
				#item[1] = re.compile((self._REGEX_subster_tag%{'var':'.*?','cont':'.*?'}), re.S | re.I).sub(u'', item[1])
				item[1] = re.compile((self._REGEX_subster_tag%{'var':'.*?'}), re.S | re.I).sub(u'', item[1])
			#print item
			try:	param = eval(item[1])
			except:	param = {}
			item = item[0]
			try:
				if not (item[0] == u'*'):	continue
			except:	continue
			item = item[1:]
			item = re.sub(u'\[', u'', item)
			item = re.sub(u'\]', u'', item)
			item = re.sub(u'Benutzer:', u'', item)
			subitem = re.split('\/', item)		# recognize extended user entries with ".../..."
			if len(subitem) > 1:			#  "
				param['userResultPage'] = item	# save extended user info (without duplicates)
				item = subitem[0]
			#users[item] = param			# drop duplicates directly
			user = userlib.User(self.site, item.encode('unicode_escape'))
			user.param = param
			final_users.append( user )

		return final_users

	# ADDED
	# REASON: common interface to bot job queue on wiki
	def loadJobQueue(self, page, queue_security, debug = False):
		"""Check if the data queue security is ok to execute the jobs,
		   if so read the jobs and reset the queue.
		   ADDED METHOD: common interface to bot job queue on wiki

		   @param page: Wiki page containing job queue.
		   @type  page: page
		   @param queue_security: This string must match the last edit
			                  comment, or else nothing is done.
		   @type  queue_security: string
		   @param debug: Parameter to prevent writing to wiki in debug mode.
		   @type  debug: bool

		   Returns a list of jobs. This list may be empty.
		"""

		try:	actual = page.getVersionHistory(revCount=1)[0]
		except:	pass

		secure = False
		for item in queue_security[0]:
		    secure = secure or (actual[2] == item)

		secure = secure and (actual[3] == queue_security[1])

		if not secure: return []

		data = self._REGEX_eol.split(page.get())
		if debug:
			pywikibot.setAction(u'reset job queue')
			page.put(u'', minorEdit = True)
		else:
			pywikibot.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

		queue = []
		for line in data:
			queue.append( line[1:].strip() )
		return queue

	def load(self, page, full=False):
		'''
		load wiki page

		input:  page
		returns:  page content [string (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28)

		if full:	(mode, info) = ('full', ' using "getFull()" mode')
		else:		(mode, info) = ('default', '')

		#pywikibot.output(u'\03{lightblue}Reading Wiki at %s...\03{default}' % page.title(asLink=True))
		pywikibot.output(u'\03{lightblue}Reading Wiki%s at %s...\03{default}' % (info, page.title(asLink=True)))
		try:
			content = page.get()
			#content = page.get(mode=mode)
			#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
			#	pywikibot.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.title(asLink=True))
			#	continue
		except (pywikibot.NoPage, pywikibot.IsRedirectPage):
			content = u''
		return content

	def loadPages(self, pages, issues=None):
		'''
		load wiki pages (as generator no exceptions but saves memory)

		input:  pages
                        issues = (regex, modes)   for handling of known prolematic pages
		returns:  (page, content) [tuple]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28)

		pages.drop_dups()
		if issues:
			(regex, modes) = issues
			modes.append('default')			# because of len(pages_list) = len(regex)+1
			pages_list = pages.filterPages(regex)	# (one entry form not filtered items)
		else:
			modes = 'default'
			pages_list = [pages]

		for i, pages in enumerate(pages_list):
			for (page, content) in pages.get(mode=modes[i]):
				if pages._requesting_data: pywikibot.output(u"\03{lightblue}Reading a set of Wiki pages (mode='%s')...\03{default}"%modes[i])
				pywikibot.output(u'\03{lightblue}Got Wiki at %s...\03{default}' % page.title(asLink=True))

				#except (pywikibot.NoPage, pywikibot.IsRedirectPage):
				#	content = u''
				if not content: 
					content = u''

				#keys = content.title()

				#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
				#	pywikibot.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.title(asLink=True))
				#	continue

				yield (page, content)

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

	def save(self, page, data, minorEdit = True):
		'''
		save wiki page

		input:  page
                        data [string (unicode)]
		returns:  (saves data to page on the wiki, nothing else)
		'''

		pywikibot.output(u'\03{lightblue}Writing to Wiki on %s...\03{default}' % page.title(asLink=True))

		content = data
		try:
			if minorEdit:	page.put(content)
			else:		page.put(content, minorEdit = False)
		except pywikibot.SpamfilterError, error:
			pywikibot.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (page.title(asLink=True), "error.url"))

	def loadFile(self):
		'''
		load data (history) file

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

	def localizeDateTime(self, timestamp):
		'''
		returns a localized datetime

		input:  timestamp
		returns:  localized time [time]
		'''
		# see also in 'dtbext/dtbext_wikipedia.py', 'GetTime' ...
		# is localized to the actual date/time settings, cannot localize timestamps that are
		#    half of a year in the past or future!
		timestamp = time.strptime(timestamp.encode(config.textfile_encoding), '%H:%M, %d. %b. %Y')
		secs = calendar.timegm(timestamp)
		return time.strftime('%H:%M, %d. %b. %Y', time.localtime(secs)).decode(config.textfile_encoding)


#def main():
#	bot = SumDiscRobot(bot_config['userlist'])	# for several user's, but what about complete automation (continous running...)
#	if len(pywikibot.handleArgs()) > 0:
#		for arg in pywikibot.handleArgs():
#			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
#			if 	arg[:17] == "-compress_history":
#			#if 	arg[:17] == "-compress_history":
#				bot.compressHistory( eval(arg[18:]) )
#				return
#			elif	(arg[:17] == "-rollback_history"):
#				bot.rollback = int( arg[18:] )
#			elif	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
#				bot.silent = True
#			elif	(arg == "-all") or ("-sum_disc" in arg):
#				pass
#			#elif	(arg == "-test_run"):
#			#	debug = ...
#			else:
#				pywikibot.showHelp()
#				return
#	bot.run()
#
#if __name__ == "__main__":
#    try:
#        main()
#    finally:
#        pywikibot.stopme()

