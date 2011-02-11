# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of wikipedia.py and mainly subclasses
the page class from there.

...
"""
## @package dtbext.dtbext_wikipedia
#  @brief   Deviation of @ref wikipedia
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

# Standard library imports
import difflib, re
# Splitting the bot into library parts
from dtbext_pywikibot import *

# Application specific imports
import wikipedia as pywikibot
import query, config


debug = False


## @since   r19 (ADDED)
#  @remarks needed to convert wikipedia.Page, Site ... objects to dtbext.dtbext_wikipedia.Page, Site, ... objects
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
		obj.__dict__['append']			= lambda *args, **kwds: Page.__dict__['append'](obj, *args, **kwds)
	elif "class 'wikipedia.Site'" in str(type(obj)):
		obj.__dict__['getParsedString']		= lambda *args, **kwds: Site.__dict__['getParsedString'](obj, *args, **kwds)


## @since   ? (MODIFIED)
#  @remarks (look below)
class Page(pywikibot.Page):
	"""Page: A MediaWiki page

	   look at wikipedia.py for more information!
	"""

	## @since   ? (MODIFIED)
	#  @remarks should be faster than original (look into re-write for something similar!)
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

	## @since   r33 (MODIFIED)
	#  @remarks to support 'force' with dtbext.dtbext_wikipedia.Page.getSections()
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

	## @since   r18 (ADDED)
	#  @remarks needed by various bots
	#
	#  @todo    patch needed by dtbext.dtbext_wikipedia.Page._findSection() for some pages
	#           \n[ JIRA ticket? ]
	def getSections(self, minLevel=2, sectionsonly=False, force=False):
		"""Parses the page with API and return section information.
		   ADDED METHOD: needed by various bots

		   @param minLevel: The minimal level of heading for section to be reported.
		   @type  minLevel: int
		   @param sectionsonly: Report only the result from API call, do not assign
                            the headings to wiki text (for compression e.g.).
		   @type  sectionsonly: bool
		   @param force: Use API for full section list resolution, works always but
                     is extremely slow, since each single section has to be retrieved.
		   @type  force: bool

		   Returns a list with entries: (byteoffset, level, wikiline, line, anchor)
		   This list may be empty and if sections are embedded by template, the according
		   byteoffset and wikiline entries are None. The wikiline is the wiki text,
		   line is the parsed text and anchor ist the (unique) link label.
		"""
		# replace 'byteoffset' ALWAYS by self calculated, since parsed does not match wiki text
		# bug fix: DRTRIGON-82

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
			#pywikibot.output(u"  Reading wiki page text (if not already done).")

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

			pos = 0
			for i, item in enumerate(r):
				l = int(item[u'level'])
				if item[u'byteoffset'] and item[u'line']:
					# section on this page and index in format u"%i"
					self._getSectionByteOffset(item, pos, force)		# raises 'Error' if not sucessfull !
					pos                 = item[u'wikiline_bo'] + len(item[u'wikiline'])
					item[u'byteoffset'] = item[u'wikiline_bo']
				else:
					# section embedded from template (index in format u"T-%i") or the
					# parser was not able to recongnize section correct (e.g. html) at all
					# (the byteoffset, index, ... may be correct or not)
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
		self._sections = [ (item[u'byteoffset'], item[u'level'], item[u'wikiline'], item[u'line'], item[u'anchor']) for item in r ]

		return self._sections

	## @since   r18 (ADDED)
	#  @remarks needed by dtbext.dtbext_wikipedia.Page.getSections()
	def _getSectionByteOffset(self, section, pos, force):
        	"""determine the byteoffset of the given section (can be slow due another API call).
		   ADDED METHOD: needed by 'getSections'
		"""
		wikitextlines = self._contents[pos:].splitlines()
		possible_headers = []

		if not force:
			# how the heading should look like (re)
			l = int(section[u'level'])
			headers = [ u'^(\s*)%(spacer)s(\s*)(.*?)(\s*)%(spacer)s((<!--(.*?)-->)?)(\s*)$' % {'line': section[u'line'], 'spacer': u'=' * l},
				    u'^(\s*)<h%(level)i>s(\s*)(.*?)(\s*)</h%(level)i>((<!--(.*?)-->)?)(\s*)$' % {'line': section[u'line'], 'level': l}, ]

			# try to give exact match for heading
			for h in headers:
				ph = re.search(h, self._contents[pos:], re.M)
				if ph:
					ph = ph.group(0).strip()
					possible_headers += [ (ph, h) ]

			# how the heading could look like (difflib)
			headers = [ u'%(spacer)s %(line)s %(spacer)s' % {'line': section[u'line'], 'spacer': u'=' * l},
				    u'<h%(level)i>%(line)s</h%(level)i>' % {'line': section[u'line'], 'level': l}, ]

			# give possible match for heading
			# http://stackoverflow.com/questions/2923420/fuzzy-string-matching-algorithm-in-python
			# http://docs.python.org/library/difflib.html
			# (http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/)
			for h in headers:
				ph = difflib.get_close_matches(h, wikitextlines, cutoff=0.70)	# cutoff=0.6 (default)
				possible_headers += [ (p, h) for p in ph ]
				#print h, possible_headers

		if (len(possible_headers) == 0) and section[u'index']:		# nothing found, try 'prop=revisions (rv)'
			# call the wiki to get info
			params = {
				u'action'	: u'query',
				u'titles'	: self.title(),
				u'prop'		: u'revisions',
				u'rvprop'	: u'content',
				u'rvsection'	: section[u'index'],
			}

			pywikibot.get_throttle()
			pywikibot.output(u"  Reading section %s from %s via API..." % (section[u'index'], self.title(asLink=True)))

			result = query.GetData(params, self.site())
			r = result[u'query'][u'pages'].values()[0]
			pl = r[u'revisions'][0][u'*'].splitlines()

			if pl:
				possible_headers = [ (pl[0], pl[0]) ]

		# find the most probable match for heading
		best_match = (0.0, None)
		for (ph, header) in possible_headers:
			#print u'    ', difflib.SequenceMatcher(None, header, ph).ratio(), header, ph
			mr = difflib.SequenceMatcher(None, header, ph).ratio()
			if mr > best_match[0]: best_match = (mr, ph)
		#print u'    ', best_match

		# prepare resulting data
		section[u'wikiline']    = best_match[1]
		section[u'wikiline_mq'] = best_match[0]	 # match quality
		section[u'wikiline_bo'] = -1             # byteoffset
		if section[u'wikiline']:
			section[u'wikiline_bo'] = self._contents.find(section[u'wikiline'], pos)
		if section[u'wikiline_bo'] < 0:		# nothing found, report/raise error !
			#page._getexception = ...
			raise pywikibot.Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.title(asLink=True))
			#pywikibot.output(...)
			# (or create a own error, e.g. look into interwiki.py)

	## @since   ? (ADDED; non-api purge can be done with wikipedia.Page.purge_address())
	#  @remarks needed by various bots
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

	## @since   r24 (ADDED)
	#  @remarks needed by various bots
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
		import botlist # like watchlist
		if not botlist.isBot(username):
			self._userNameHuman = username
			return username

		# search the last human
		self._userNameHuman = None
		for vh in self.getVersionHistory()[1:]:
			(revid, timestmp, username, comment) = vh[:4]

			if username and (not botlist.isBot(username)):
				# user is a human (not a bot)
				self._userNameHuman = username
				break

		# store and return info
		return self._userNameHuman

	## @since   r49 (ADDED)
	#  @remarks to support appending to single sections
	#
	#  @todo    submit upstream and include into framework, maybe in wikipedia.Page.put()
	#           (this function is very simple and not mature/worked out yet, has to be completed)
	#           \n[ JIRA: ticket? ]
	def append(self, newtext, comment=None, minorEdit=True, section=0):
		"""Append the wiki-text to the page.
		   ADDED METHOD: to support appending to single sections

		   Returns the result of text append to page section number 'section'.
		   0 for the top section, 'new' for a new section.
		"""

        	# If no comment is given for the change, use the default
        	comment = comment or pywikibot.action

		# send mail by POST request
		params = {
		    'action'		: 'edit',
		    #'title'		: self.title().encode(self.site().encoding()),
		    'title'		: self.title(),
		    'section'		: '%i' % section,
		    'appendtext'	: self._encodeArg(newtext, 'text'),
		    'token'		: self.site().getToken(),
		    'summary'		: self._encodeArg(comment, 'summary'),
		    'bot'		: 1,
		    }

		if minorEdit:
			params['minor'] = 1
		else:
			params['notminor'] = 1

                response, data = query.GetData(params, self.site(), back_response = True)

		if not (data['edit']['result'] == u"Success"):
			raise PageNotSaved('Bad result returned: %s' % data['edit']['result'])

		return response.code, response.msg, data


## @since   r19 (ADDED)
#  @remarks needed by various bots
class Site(object):
	"""A MediaWiki site.

	   look at wikipedia.py for more information!
	"""

	## @since   r19 (ADDED)
	#  @remarks needed by various bots
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


