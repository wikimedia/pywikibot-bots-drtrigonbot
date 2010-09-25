# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of wikipedia.py and mainly subclasses
the page class from there.

...
"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: dtbext_wikipedia.py 0.2.0033 2009-11-25 22:10 drtrigon $'
#

# Standard library imports
import difflib
# Splitting the bot into library parts
from dtbext_pywikibot import *

# Application specific imports
import wikipedia as pywikibot
import query, userlib, config


debug = False


# ADDED: new (r19)
# REASON: needed to convert wikipedia.Page, Site ... objects to dtbext.wikipedia.Page, Site, ... objects
def addAttributes(obj):
	"""Add methods to various classes to convert them to the dtbext modified version."""
	# http://mousebender.wordpress.com/2007/02/17/copying-methods-in-python/
	# http://code.activestate.com/recipes/52192-add-a-method-to-a-class-instance-at-runtime/
	if "class 'wikipedia.Page'" in str(type(obj)):
		# this cannot be looped because of lambda's scope (which is important for page)
		# look also at http://www.weask.us/entry/scope-python-lambda-functions-parameters
		obj.__dict__['isRedirectPage']		= lambda *args, **kwds: Page.__dict__['isRedirectPage'](obj, *args, **kwds)
		obj.__dict__['getSections']		= lambda *args, **kwds: Page.__dict__['getSections'](obj, *args, **kwds)
		obj.__dict__['_getSectionByteOffset']	= lambda *args, **kwds: Page.__dict__['_getSectionByteOffset'](obj, *args, **kwds)
		obj.__dict__['_findSection']		= lambda *args, **kwds: Page.__dict__['_findSection'](obj, *args, **kwds)
		obj.__dict__['purgeCache']		= lambda *args, **kwds: Page.__dict__['purgeCache'](obj, *args, **kwds)
		obj.__dict__['userNameHuman']		= lambda *args, **kwds: Page.__dict__['userNameHuman'](obj, *args, **kwds)
	elif "class 'wikipedia.Site'" in str(type(obj)):
		obj.__dict__['getParsedString']		= lambda *args, **kwds: Site.__dict__['getParsedString'](obj, *args, **kwds)


# MODIFIED
# REASON: (look below)
class Page(pywikibot.Page):
	"""Page: A MediaWiki page

	   look at wikipedia.py for more information!
	"""

	# MODIFIED
	# REASON: should be faster than original (look into re-write for something similar!)
	def isRedirectPage(self):
		"""Return True if this is a redirect, False if not or not existing.
		   MODIFIED METHOD: should be faster than original
		"""

		# was there already a call? already some info available?
		if hasattr(self, '_getexception') and (self._getexception == pywikibot.IsRedirectPage):
			return True

		if hasattr(self, '_redir'):	# prevent multiple execute of code below,
			return self._redir	#  if page is NOT a redirect!

		# call the wiki to get info
		params = {
			u'action'	: u'query',
			u'titles'	: self.title(),
			u'prop'		: u'info',
			u'rvlimit'	: 1,
		}

		pywikibot.get_throttle()
		pywikibot.output(u"Reading redirect info from %s." % self.title(asLink=True))

		result = query.GetData(params, self.site())
		r = result[u'query'][u'pages'].values()[0]

		# store and return info
		self._redir = (u'redirect' in r)
		if self._redir:
			self._getexception == pywikibot.IsRedirectPage

		return self._redir

	# MODIFIED: new (r33)
	# REASON: to support 'force' with 'getSections'
	def get(self, *args, **kwds):
		"""Return the wiki-text of the page.
		   MODIFIED METHOD: to support 'force' with 'getSections'
		"""

		if kwds.get('force', False):
			# Old exceptions and contents do not apply any more.
			for attr in ['_sections']:
				if hasattr(self, attr):
					delattr(self,attr)

		return pywikibot.Page.get(self, *args, **kwds)

	# ADDED: new (r18)
	# REASON: needed by various bots
	def getSections(self, minLevel=2, sectionsonly=False):
		"""Parses the page with API and return section information.
		   ADDED METHOD: needed by various bots

		   @param minLevel: The minimal level of heading for section to be reported.
		   @type  minLevel: int
		   @param sectionsonly: Report only the result from API call, do not assign
                                        the headings to wiki text (for compression e.g.).
		   @type  sectionsonly: bool

		   Returns a list with entries: (byteoffset, level, wikiline, line, anchor)
		   This list may be empty and if sections are embedded by template, the according
		   byteoffset and wikiline entries are None. The wikiline is the wiki text,
		   line is the parsed text and anchor ist the (unique) link label.
		"""

		# was there already a call? already some info available?
		if hasattr(self, '_sections'):
			return self._sections

		# Old exceptions and contents do not apply any more.
		for attr in ['_sections']:
			if hasattr(self, attr):
				delattr(self,attr)

		# call the wiki to get info
		params = {
			u'action'	: u'parse',
			u'page'		: self.title(),
			u'prop'		: u'sections',
		}

		pywikibot.get_throttle()
		pywikibot.output(u"Reading section info from %s via API..." % self.title(asLink=True))

		result = query.GetData(params, self.site())
		r = result[u'parse'][u'sections']
		debug_data = str(r) + '\n'

		if not sectionsonly:
			# assign sections with wiki text and section byteoffset
			pywikibot.output(u"  Reading wiki page text (if not already done).")

			debug_data += str(len(self._contents)) + '\n'
			self.get()
			debug_data += str(len(self._contents)) + '\n'
			debug_data += self._contents + '\n'

			# code debugging
			if debug:
				#err = ''
				#pywikibot.debugDump( 'dtbext.Page.getSections', self.site, err, debug_data.decode(config.textfile_encoding) )
				f = open('debug.txt', 'a')
				f.write( debug_data.encode('utf8') + '\n' )
				f.close()

			# [ patch needed by '_findSection' for some pages / JIRA ticket? ]
			self._contents = self._contents.replace(u'\r\n', u'\n')

			for i, item in enumerate(r):
				l = int(item[u'level'])
				if item[u'byteoffset'] and item[u'index']:
					# section on this page and index in format u"%i"
					item[u'wikiline'] = self._findSection(item)
					if (len(item[u'wikiline']) == 0) and (len(item[u'line'].strip()) > 0):
						self._getSectionByteOffset(item)		# raises 'Error' if not sucessfull !
						item[u'byteoffset'] = item[u'wikiline_bo']
						item[u'wikiline']   = self._findSection(item)
				else:
					# section ebemdded from template (index in format u"T-%i") or the
					# parser was not able to recongnize section correct (e.g. html) at all
					# (the byteoffset and index may be correct or not...)
					item[u'wikiline'] = None

				item[u'level'] = l

				r[i] = item

		# check min. level
		data = []
		for item in r:
			if (item[u'level'] < minLevel): continue
			data.append( item )
		r = data

		# prepare resulting data
		self._sections = [ (item[u'byteoffset'], item[u'level'], item.get(u'wikiline', None), item[u'line'], item[u'anchor']) for item in r ]

		return self._sections

	# ADDED: new (r18)
	# REASON: needed by 'getSections'
	def _getSectionByteOffset(self, section):
        	"""determine the byteoffset of the given section (can be slow due another API call).
		   ADDED METHOD: needed by 'getSections'
		"""
		wikitextlines = self._contents.splitlines()

		# how the heading could look like
		l = int(section[u'level'])
		#header = u'%(spacer)s %(line)s %(spacer)s' % {'line': section[u'line'], 'spacer': u'=' * l}
		headers = [ u'%(spacer)s %(line)s %(spacer)s' % {'line': section[u'line'], 'spacer': u'=' * l},
			    u'<h%(level)i>%(line)s</h%(level)i>' % {'line': section[u'line'], 'level': l}, ]

		# give possible match for heading
		# http://stackoverflow.com/questions/2923420/fuzzy-string-matching-algorithm-in-python
		# http://docs.python.org/library/difflib.html
		# (http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/)
		possible_headers = []
		for h in headers:
			ph = difflib.get_close_matches(h, wikitextlines)	# cutoff=0.6
			possible_headers += [ (p, h) for p in ph ]
			#print h, possible_headers

		if len(possible_headers) == 0:		# nothing found, try 'prop=revisions (rv)' or else report/raise error !
			raise NotImplementedError('The call to API to get exact matching section heading is not implemented yet!')
			# ?action=query&prop=revisions&titles=Benutzer_Diskussion:DrTrigon&rvprop=content&rvsection=1
			# section[u'number'] for 'rvsection'
			#params = {
			#	u'action'	: u'query',
			#	u'titles'	: self.title(),
			#	u'prop'		: u'revisions',
			#	u'rvprop'	: u'content',
			#	u'rvsection'	: section[u'number'],
			#}
			#pywikibot.get_throttle()
			#pywikibot.output(u"    Reading section %i from %s." % (section[u'number'], self.title(asLink=True)))
			# if not successfull too, report error/problem
			#page._getexception = ...
			#raise pywikibot.Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.title(asLink=True))
			#pywikibot.output(...)
			# (or create a own error, e.g. look into interwiki.py)

		# find the most probable match for heading
		best_match = (0.0, None)
		for (ph, header) in possible_headers:
			#print u'    ', difflib.SequenceMatcher(None, header, ph).ratio(), ph
			mr = difflib.SequenceMatcher(None, header, ph).ratio()
			if mr > best_match[0]: best_match = (mr, ph)
		#print u'    ', best_match

		# prepare resulting data
		section[u'wikiline']    = best_match[1]
		section[u'wikiline_mq'] = best_match[0]					# match quality
		section[u'wikiline_bo'] = self._contents.find(section[u'wikiline'])	# byteoffset

	# ADDED: new (r18)
	# REASON: needed by 'getSections'
	def _findSection(self, section):
        	"""find and extract section.
		   ADDED METHOD: needed by 'getSections'
		"""
		bo  = section[u'byteoffset']
		end = self._contents.find(u'\n', bo)
		#l = int(section[u'level'])
		#return self._contents[(bo+l):(end-l)].strip()
		return self._contents[bo:end].strip()

	# ADDED (non-api purge can be done with 'Page.purge_address()')
	# REASON: needed by various bots
	def purgeCache(self):
		"""Purges the page cache with API.
		   ADDED METHOD: needed by various bots
		"""

		# Make sure we re-raise an exception we got on an earlier attempt
		if hasattr(self, '_getexception'):
			return self._getexception

		# call the wiki to execute the request
		params = {
			u'action'	: u'purge',
			u'titles'	: self.title(),
		}

		pywikibot.get_throttle()
		pywikibot.output(u"Purging page cache for %s." % self.title(asLink=True))

		result = query.GetData(params, self.site())
		r = result[u'purge'][0]

		# store and return info
		if (u'missing' in r):
		        self._getexception = pywikibot.NoPage
		        raise pywikibot.NoPage(self.site(), self.title(asLink=True),"Page does not exist. Was not able to purge cache!" )

		return (u'purged' in r)

	# ADDED: new (r24)
	# REASON: needed by various bots
	def userNameHuman(self):
		"""Return name or IP address of last human/non-bot user to edit page.
		   ADDED METHOD: needed by various bots

		   Returns the most recent human editor out of the last revisions
		   (optimal used with getAll()). If it was not able to retrieve a
		   human user returns None.
		"""

		# was there already a call? already some info available?
		if hasattr(self, '_userNameHuman'):
			return self._userNameHuman

		# get history (use preloaded if available)
		(revid, timestmp, username, comment) = self.getVersionHistory(revCount=1)[0][:4]

		# is the last/actual editor already a human?
		site = self.site()
		try:
			groups = userlib.User(site, username).groups()
			if not (u'bot' in groups):
				self._userNameHuman = username
				return username
		except userlib.InvalidUser:
			pass

		# search the last human
		result = None
		bots = [] # cache the bot users (prevent multiple identical requests)
		for vh in self.getVersionHistory()[1:]:
			(revid, timestmp, username, comment) = vh[:4]

			if username not in bots:
				# user unknown, request info
				try:
					groups = userlib.User(site, username).groups()
				except userlib.InvalidUser:
					continue

				if (u'bot' in groups):
					# user is a bot
					bots.append(username)
				else:
					# user is a human
					result = username
					break

		# store and return info
		self._userNameHuman = username
		return result


# ADDED: new (r19)
# REASON: needed by various bots
class Site(object):
	"""A MediaWiki site.

	   look at wikipedia.py for more information!
	"""

	# ADDED
	# REASON: needed by various bots
	def getParsedString(self, string, keeptags = [u'*']):
		"""Parses the string with API and return html content.
		   ADDED METHOD: needed by various bots

		   @param string: String that should be parsed.
		   @type  string: string
		   @param keeptags: Defines which tags (wiki, HTML) should be NOT removed.
		   @type  keeptags: list

		   Returns the string given, parsed through the wiki parser.
		"""

		# call the wiki to get info
		params = {
			u'action'	: u'parse',
			u'text'		: string,
		}

		pywikibot.get_throttle()
		pywikibot.output(u"Parsing string through the wiki parser.")

		result = query.GetData(params, self)
		r = result[u'parse'][u'text'][u'*']

		r = pywikibot.removeDisabledParts(r, tags = ['comments']).strip()		# disable/remove comments

		if not (keeptags == [u'*']):							# disable/remove ALL tags
			r = removeHTMLParts(r, keeptags = keeptags).strip()	#

		return r


