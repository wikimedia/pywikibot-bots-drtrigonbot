# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of basic.py.

...
"""
#
#    python sum_disc.py -test_run
#        Loads old history entry of all Users, e.g. for debuging.
#"""
## @package dtbext.dtbext_basic
#  @brief   Deviation of @ref basic
#
#  @copyright Dr. Trigon, 2010
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
import time, codecs, os

import config, userlib, basic
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


class BasicBot(basic.BasicBot):
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	#silent		= False
	#rollback	= 0

	_REGEX_eol		= re.compile(u'\n')
	_REGEX_subster_tag	= u'<!--SUBSTER-%(var)s-->'

	## @since   ? (MODIFIED)
	#  @remarks needed by various bots
	def __init__(self, bot_config={}):
		"""Constructor of BasicBot(); setup environment, initialize needed consts and objects.
		   MODIFIED METHOD: needed by various bots

		   @param bot_config: The configuration of the running bot.
		   @type  bot_config: dict
		"""

		#basic.BasicBot.__init__(self, generator, dry)

		# modification of timezone to be in sync with wiki
		os.environ['TZ'] = 'Europe/Amsterdam'
		time.tzset()
		pywikibot.output(u'Setting process TimeZone (TZ): %s' % str(time.tzname))	# ('CET', 'CEST')

		# Default action
		pywikibot.setAction('Wikipedia python library / dtbext (DrTrigonBot extensions)')

		if bot_config:
			# init constants
			self._bot_config = bot_config
			self._template_regex = re.compile('\{\{' + self._bot_config['TemplateName'] + '(.*?)\}\}', re.S)

			# init variable/dynamic objects
			self.site = pywikibot.getSite()
			dtbext.pywikibot.addAttributes( self.site )		# enhance to dtbext.pywikibot.Site

	## @since   ? (ADDED)
	#  @remarks needed by sum_disc
	def loadMode(self, page, regex_compile=False):
		"""Get operating mode from user's disc page by searching for the template.
		   ADDED METHOD: needed by SumDiscBot

		   @param page: The user (page) for which the data should be retrieved.
		   @param regex_compile: If True the value added to the ignore_list will
                                         be compiled first.

		   Sets self._mode and self._tmpl_data which represent the settings how
		   to report news to the user. Sets self._content also which is the touched
		   page content to notify the user. The self._param is modified too.
		"""

		templates = self.loadTemplates(page)

		self._mode = False
		self._tmpl_data = u''

		if templates:
			tmpl = templates[0]

			# enhanced: with template
			self._mode = True
			self._tmpl_data = tmpl[u'data']
			if regex_compile:
				self._tmpl_data = re.compile(self._tmpl_data)
			#if hasattr(self, '_param'):  # [JIRA: DRTRIGON-8, DRTRIGON-32]
			self._param['ignorepage_list'].append( self._tmpl_data )

			# update template and content
			tmpl[u'timestamp'] = u'--~~~~'
			tmpl_text = dtbext.pywikibot.glue_template_and_params( (self._bot_config['TemplateName'], tmpl) )
			tmpl_pos  = self._template_regex.search(self._content)
			self._content = self._content[:tmpl_pos.start()] + tmpl_text + self._content[tmpl_pos.end():]

	## @since   ? (ADDED)
	#  @remarks needed by various bots
	def loadTemplates(self, page, default={}):
		"""Get operating mode from page with template by searching the template.
		   ADDED METHOD: needed by various bots

		   @param page: The user (page) for which the data should be retrieved.

		   Returns a list of dict with the templates parameters found.
		"""

		self._content = self.load(page)

		templates = []
		for tmpl in pywikibot.extract_templates_and_params(self._content):
			if tmpl[0] == self._bot_config['TemplateName']:
				param_default = {}
				param_default.update(default)
				param_default.update(tmpl[1])
				templates.append( param_default )
		return templates

	## @since   ? (ADDED)
	#  @remarks common interface to bot user settings on wiki
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
		#for item in self._REGEX_eol.split(page.get()):
		for item in self._REGEX_eol.split(self.load(page)):
			item = re.split(u',', item, maxsplit=1)
			if (len(item) > 1):	# for compatibility with 'subster.py' (if needed)
				#item[1] = re.compile((self._REGEX_subster_tag%{'var':'.*?','cont':'.*?'}), re.S | re.I).sub(u'', item[1])
				item[1] = re.compile((self._REGEX_subster_tag%{u'var':u'.*?'}), re.S | re.I).sub(u'', item[1])
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
			subitem = re.split(u'\/', item)		# recognize extended user entries with ".../..."
			if len(subitem) > 1:			#  "
				param[u'userResultPage'] = item	# save extended user info (without duplicates)
				item = subitem[0]
			#users[item] = param			# drop duplicates directly
			user = userlib.User(self.site, item)
			user.param = param
			final_users.append( user )

		return final_users

	## @since   ? (ADDED)
	#  @remarks common interface to bot job queue on wiki
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
			pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

		queue = []
		for line in data:
			queue.append( line[1:].strip() )
		return queue

	## @since   ? (MODIFIED)
	#  @remarks needed by various bots
	def save(self, page, text, comment=None, minorEdit=True):
		pywikibot.output(u'\03{lightblue}Writing to wiki on %s...\03{default}' % page.title(asLink=True))

		comment_output = comment or pywikibot.action
		pywikibot.output(u'\03{lightblue}Comment: %s\03{default}' % comment_output)

		#pywikibot.showDiff(page.get(), text)

		for i in range(3): # try max. 3 times
			try:
				# Save the page
				page.put(text, comment=comment, minorEdit=minorEdit)
			except pywikibot.LockedPage:
				pywikibot.output(u"\03{lightblue}Page %s is locked; skipping.\03{default}" % page.aslink())
			except pywikibot.EditConflict:
				pywikibot.output(u'\03{lightblue}Skipping %s because of edit conflict\03{default}' % (page.title()))
			except pywikibot.SpamfilterError, error:
				pywikibot.output(u'\03{lightblue}Cannot change %s because of spam blacklist entry %s\03{default}' % (page.title(), error.url))
			else:
				return True
		return False

	## @since   ? (ADDED)
	#  @remarks needed by various bots
	def append(self, page, text, comment=None, minorEdit=True, section=None):
		if section:
			pywikibot.output(u'\03{lightblue}Appending to wiki on %s in section %s...\03{default}' % (page.title(asLink=True), section))

			for i in range(3): # try max. 3 times
				try:
					# enhance to dtbext.pywikibot.Page
					dtbext.pywikibot.addAttributes(page)

					# Append to page section
					page.append(text, comment=comment, minorEdit=minorEdit, section=section)
				except pywikibot.PageNotSaved, error:
					pywikibot.output(u'\03{lightblue}Cannot change %s because of %s\03{default}' % (page.title(), error))
				else:
					return True
		else:
			content = self.load( page )

			content += u'\n\n'
			content += text

			return self.save(page, content, comment=comment, minorEdit=minorEdit)

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

	def appendFile(self, data):
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

