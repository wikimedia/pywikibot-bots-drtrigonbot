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
__version__='$Id: dtbext_wikipedia.py 0.2.0022 2009-11-15 16:01 drtrigon $'
#

# Standard library imports
import StringIO
import re, sets
import difflib
# Splitting the bot into library parts
from dtbext_pywikibot import *

# Application specific imports
import wikipedia as pywikibot
import config, query
import dtbext_date


# needed by 'getSectionsOldApi'
REGEX_hTagOpen			= re.compile('<h(\d).*?>')
REGEX_hTagClose			= re.compile('</h(\d).*?>')
REGEX_nowikiTag			= re.compile('<nowiki>(.*?)</nowiki>', re.S | re.I)
REGEX_preTag			= re.compile('<pre>(.*?)</pre>', re.S | re.I)
REGEX_sourceTag			= re.compile('<source.*?>(.*?)</source>', re.S | re.I)
REGEX_noincludeTag		= re.compile('<noinclude>(.*?)</noinclude>', re.S | re.I)
REGEX_onlyincludeTag		= re.compile('(</?onlyinclude>)', re.S | re.I)
REGEX_eqChar			= re.compile('=')
#REGEX_wikiSection		= re.compile('(?<=\n)==([^=].*?)==(?=\s)')
#REGEX_wikiSection		= re.compile('(?<=\n)(=+)(.*?)(=+)(?=\s)')
REGEX_wikiSection		= re.compile('^(=+)(.*?)(=+)(?=\s)', re.M)


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
	elif "class 'wikipedia.Site'" in str(type(obj)):
		obj.__dict__['getParsedString']		= lambda *args, **kwds: Site.__dict__['getParsedString'](obj, *args, **kwds)


# MODIFIED
# REASON: (look below)
class Page(pywikibot.Page):
	"""Page: A MediaWiki page

	   look at wikipedia.py for more information!
	"""

	# MODIFIED
	# REASON: should be faster than original
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

	# ADDED: new (r18)
	# REASON: needed by various bots
	def getSections(self, minLevel=2, sectionsonly=False, getter=None, pagewikitext=None):
		"""Parses the page with API and return section information.
		   ADDED METHOD: needed by various bots

		   @param minLevel: The minimal level of heading for section to be reported.
		   @type  minLevel: int
		   @param sectionsonly: Report only the result from API call, do not assign
                                        the headings to wiki text (for compression e.g.).
		   @type  sectionsonly: bool
#		   getter: because get() in API version and default dont give the same
#		            results (html comments are stripped or not ...) you can choose
#		            here which function to use. default is the API version.
#		   pagewikitext: if content is already known, you can use this shortcut!

		   Returns a list with entries: (byteoffset, level, wikiline, line, anchor)
		   This list may be empty and if sections are embedded by template, the according
		   byteoffset and wikiline entries are None.
		"""
# - check calling params

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
		pywikibot.output(u"Reading section info from %s." % self.title(asLink=True))

		result = query.GetData(params, self.site())
		r = result[u'parse'][u'sections']
		#print r

		if not sectionsonly:
			# assign sections with wiki text and section byteoffset
			pywikibot.output(u"\tReading wiki page text from %s (if not already done)." % self.title(asLink=True))
			self.get()
			for i, item in enumerate(r):
				l = int(item[u'level'])
				if item[u'byteoffset']:
					# section on this page (index in format u"%i")
					item[u'wikiline'] = self._findSection(item)

					if (len(item[u'wikiline']) == 0) and (len(item[u'line'].strip()) > 0):
						self._getSectionByteOffset(item)		# raises 'Error' if not sucessfull !
						item[u'byteoffset'] = item[u'wikiline_bo']
						item[u'wikiline']   = self._findSection(item)
				else:
					# section ebemdded from template (index in format u"T-%i")
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
			ph = difflib.get_close_matches(h, wikitextlines)
			possible_headers += [ (p, h) for p in ph ]
		#print header, possible_headers

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
			#pywikibot.output(u"\tReading section %i from %s." % (section[u'number'], self.title(asLink=True)))
			# if not successfull too, report error/problem
			#page._getexception = ...
			#raise pywikibot.Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.title(asLink=True))
			#pywikibot.output(...)
			# (or create a own error, e.g. look into interwiki.py)

		# find the most probable match for heading
		best_match = (0.0, None)
		for (ph, header) in possible_headers:
			#print u'\t', difflib.SequenceMatcher(None, header, ph).ratio(), ph
			mr = difflib.SequenceMatcher(None, header, ph).ratio()
			if mr > best_match[0]: best_match = (mr, ph)
		#print u'\t', best_match

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


# ADDED
# REASON: faster and less traffic intense big pageset processing
#         (this here is just a patch, should be done in framework)
class Pages():
	"""Pages: A set of MediaWiki pages
	"""

	_max_request = 50
	_min_request = 10

	_requesting_data = False

	def __init__(self, site, titles, insite=None, defaultNamespace=0):
		"""
		...
		"""

		raise NotImplementedError('Use PreloadingGenerator for get and the same for getVersionHistory is requested on maillist!!')
		# -> JIRA ticket

		self._site, self._insite, self._defaultNamespace = site, insite, defaultNamespace
		self._titles = titles

		#self._titles_str = "|".join(self._titles)
		self._pages = [ Page(self._site, title, insite=self._insite, defaultNamespace=self._defaultNamespace) for title in self._titles ]
		#self._pages = [ Page(self._site, title, insite=self._insite, defaultNamespace=self._defaultNamespace) for title in titles ]
		#self._titles = [ page.sectionFreeTitle() for page in self._pages ]

	def _bundle_list(self, inlist, joiner="|", size=None):
		"""
		...
		"""

		if not size: size = self._min_request

		bundle = []
		pack = []
		joined_bundle = []
		max_i = len(inlist) - 1
		for i, item in enumerate(inlist):
			pack.append( inlist[i] )
			if (((i+1)%size) == 0) or (i == max_i):
				bundle.append( pack )
				if joiner: joined_bundle.append( joiner.join(pack) )
				pack = []
		return (bundle, joined_bundle)

	# thanks to: http://www.daniweb.com/forums/thread40718.html
	def _append_missing_pages(self, outdict, inlist, set_item=None):
		"""
		...
		"""

		diff_list = [item for item in inlist if not item in outdict.keys()]
		for i, item in enumerate(diff_list):
			outdict[item] = set_item
			pywikibot.output( u"WARNING: Page [[%s]] gave no API result." % item )

		return outdict

	def has_dups(self):
		"""
		...
		"""

		return not (len(self._titles) == len(self.drop_dups()[0]))

	def drop_dups(self):
		"""
		...
		"""

		self._titles = list(sets.Set(self._titles))	# drop duplicates (wiki drops it too!)
		self._pages = [ Page(self._site, title, insite=self._insite, defaultNamespace=self._defaultNamespace) for title in self._titles ]

		return (self._titles, self._pages)

	def filterPages(self, regex):
		"""
		...
		"""

		titles = list(self._titles)
		result = []
		for item in regex:
			page_list = []
			i = 0
			while (i<len(titles)):
				if item.search(titles[i]):
					page_list.append( titles.pop(i) )
				else: 	i += 1
			result.append( Pages(self._site, page_list) )
		result.append( Pages(self._site, titles) )	# append the not filtered pages at the end

		return result


