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
__version__='$Id: dtbext_wikipedia.py 0.2.0020 2009-11-14 11:50 drtrigon $'
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

	# ADDED (is older approach and works with older api; e.g. without 'byteoffset' but still needs api
	#        or 'anchor'. for non-api: use '_getSectionsByteOffset' BUT how to get 'anchor'?)
	# REASON: needed by various bots BUT has problems with complex page structures and constructs
	def getSectionsOldApi(self, minLevel=2, getter=None, pagewikitext=None, sectionsonly = False):
		"""Parses the page with API and return section information.
		   ADDED METHOD: needed by various bots BUT has problems with complex page structures and constructs

		   ATTENTION: API DOES NOT WORK IF THERE ARE PARSE-ERRORS ON TH PAGE (e.g. <references />)
		   ( http://de.wikipedia.org/w/index.php?title=Benutzer:DrTrigonBot&oldid=78708072#Funktionsweise )

		   getter: because get() in API version and default dont give the same
		            results (html comments are stripped or not ...) you can choose
		            here which function to use. default is the API version.
		   pagewikitext: if content is already known, you can use this shortcut!
		   sectionsonly: return only the recived section headings (for compression e.g.)
		"""
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 35.3)

		if (getter == None): getter = self.get			# default
		#if (getter == None): getter = self._getFullContent	# default

		# according to tip in wiki from Merlissimo: http://de.wikipedia.org/wiki/Benutzer_Diskussion:DrTrigon#Bot:_Linkfehler
		# http://de.wikipedia.org/w/api.php?action=parse&text={{:Wikipedia:Fragen_zur_Wikipedia/Archiv/2009/Woche_10}}__TOC__&prop=sections
		# http://de.wikipedia.org/w/api.php
		request = []
		#request.append( REQUEST_getSections      % urllib.quote(self.title().encode(config.textfile_encoding)) )
		#request.append( REQUEST_getSections_page % urllib.quote(self.title().encode(config.textfile_encoding)) )
		request.append( {   'action'	: 'parse',
				    'text'	: '{{%s}}__TOC__'%self.title(),
				    'prop'	: 'sections',
				    } )
		request.append( {   'action'	: 'parse',
				    'page'	: self.title(),
				    'prop'	: 'sections',
				    } )
		sections = []
		for item in request:
		#	sections = APIRequest( self.site(),
		#			  item,
		#			  'sections',
		#			  's',
		#			  ['toclevel', 'level', 'line'] )
			pywikibot.get_throttle()
			old_sections = sections
			# look at revisions older than r18 for this code or replace with query.GetData()
			sections = dtbext_query.GetProcessedData(item,
								'sections',
								's',
								['toclevel', 'level', 'line'] )
			#if sections: break
			if len(old_sections) > len(sections):
				sections = old_sections

		#if not sections: return ([], True)

		#eigentlich nicht mehr noetig nach dieses Aenderungen/Updates:
		#http://de.wikipedia.org/w/index.php?title=Wikipedia:Projektneuheiten&oldid=61569059#Vorschau
		#https://bugzilla.wikimedia.org/show_bug.cgi?id=18720
		#
		# nummerize twice appearing headings (should be done by the API!!)
		unique = {}
		for i, item in enumerate(sections):
			if item[2] in unique:	unique[item[2]] += 1
			else:			unique[item[2]] = 1
			if unique[item[2]] > 1:
				item = ( item[0], item[1], u'%s %i'%(item[2], unique[item[2]]) )
			sections[i] = item

		if sectionsonly: return (sections, True)

		# process page text
		if (pagewikitext == None):
			#wikitext = self.get().split('\n')
			wikitext = getter().split('\n')
			#print wikitext
		else:	wikitext = pagewikitext.split('\n')

		# sync headings in text
		info = []
		first = 0
		for item in sections:
			level = int(item[1])
			#if level == 1:		# work-a-round to get level 1 headings
			#	ptrn = '^='
			#	cnt = 1
			#else:
			#	ptrn = '='
			#	cnt = 2
			for i in range(first, len(wikitext)):
				#match = re.findall(ptrn*level, wikitext[i])
				#match = re.findall('='*level, wikitext[i])
				spacer = '='*level									# make special case for '========' headings?!?!
				match = re.split(spacer, wikitext[i])
				#if ((len(match) >= cnt) and (wikitext[i][0] == u'=')):					# UND am Anfang der Zeile! (koennte
				#if ((len(match) >= 2) and (wikitext[i][0] == u'=')):					#  einheitlich mit '^' gemacht werden!)
				#if ((len(match) == 3) and (len(match[0]) == 0) and (len(match[2].strip()) == 0)):	#
				#if ((len(match) == 3) and (len(match[0]) == 0) and (match[2].strip() in ['', '='])):	#
				#print match
				#is_section  = ((len(match) == 3) and (len(match[0]) == 0) and (match[2].strip() in ['', '=']))
				is_section  = ((len(match) in [3,4]) and (len(match[0]) == 0) and (match[(len(match)-1)].strip() in ['', '=']))
				is_section |= ((level == 1) and (len(match) == 4) and (len(match[0]) == 0) and (match[2].strip() == ''))
				if is_section:
					#title = re.split('='*level, wikitext[i])[1]			# fester index hier koennte probleme machen...!!
					#spacer = '='*level						# make special case for '========' headings?!?!
					#title = spacer.join(re.split(spacer, wikitext[i])[1:-1])	#
					title = spacer.join(match[1:-1]) + match[2].strip()		#
					#print title
					info.append( (i, level, item[2], title.strip()) )
					first = i+1
					break

		v1 = (len(info) == len(sections))
		v2 = not REGEX_wikiSection.search( self._wikisectionpatch(u'\n'.join(wikitext[first:])) )
		verify = (v1 and v2)
		if not verify:
			#raise pywikibot.SectionError('Was not able to get Sections of %s properly!' % self.title(asLink=True))
			#pywikibot.output(u'!!! WARNING [[%s]]: was not able to get Sections properly!' % self.title())
			raise Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.title(asLink=True))

		# check min. level
		data = []
		for item in info:
			if (item[1] < minLevel): continue
			data.append( item )

		return data

	# ADDED
	# REASON: needed by 'getSectionsOldApi'
	def _wikisectionpatch(self, text):
		"""Patch/adjust wiki section syntax, to allow full heading recognition."""

		buf = text

		# convert <h?> und </h?> in wiki heading syntax (to be VERY SURE!)
		# (this are <h> tags inserted by users writing the wiki! not the parser or something like this...)
		# (help 'getSections()' to detect the headings correct)
		pre  = lambda m: '\n' + '='*int(m.groups()[0])
		post = lambda m: '='*int(m.groups()[0]) + '\n'
		buf = REGEX_hTagOpen.sub(pre, buf)
		buf = REGEX_hTagClose.sub(post, buf)

		# convert headings in <nowiki>, ... tags by replaceing all
		# '=' to '&#61;' which is not recognized by the wiki parser
		# as heading (and so are '=' in <nowiki>-tags) but displayed
		# correct in the browser 
		# (help 'getSections()' to detect the headings correct)
		tag  = lambda m: REGEX_eqChar.sub('&#61;', m.groups()[0])
		buf = REGEX_nowikiTag.sub(tag, buf)
		# same for <pre>-tags
		buf = REGEX_preTag.sub(tag, buf)
		# same for <source>-tags
		buf = REGEX_sourceTag.sub(tag, buf)

		# same for <noinclude>-tags
		buf = REGEX_noincludeTag.sub(tag, buf)
		# from pages with <onlyinclude>...</onlyinclude> NO SECTION DATA can be retrieved,
		# since they have no text to expand, except that within the tag
		buf_list = REGEX_onlyincludeTag.split(buf)
		if (len(buf_list) > 1):
			for i in range(0, len(buf_list), 4):
				buf_list[i] = REGEX_eqChar.sub('&#61;', buf_list[i])
			buf = u''.join(buf_list)
		# probably <noinclude> and <onlyinclude> should be handled in a way, that the page
		# text is rendered in the same way like the page itself is, NOT the page when used 
		# as template (means use page.get, remove <noinclude>-tags, remove <onlyinclude>-tags
		# and their contents, then pass the page text to 'action=parse&text=__TOC__%s&prop=sections'
		# and at last use the patches here)

		return buf

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
			#raise Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.title(asLink=True))
			#pywikibot.output(...)

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

# ADDED
# REASON: ...
#         (this here is just a patch, should be done in framework)
	def getEnh(self, expandtemplates=True):
		"""Return the wiki text of the page in various formats.
		   ADDED METHOD: ...

		   force   is ignored; the page is NOT cached
		   ......
		"""

		raise NotImplementedError('This should be implemented into \'wikipedia.get()\' directly, request placed on maillist!!')
		# -> JIRA ticket

		params = {
		    u'action'		: u'query',
		    u'prop'		: u'revisions',
		    u'titles'		: self.title(),
		    u'rvprop'		: u'content',
		    }
		if expandtemplates: params[u'rvexpandtemplates'] = u''

		pywikibot.get_throttle()
		pywikibot.output(u"Purging page cache for %s." % self.title(asLink=True))

		result = query.GetData(params, self.site())
		r = result[u'query'][u'pages'].values()[0]

		missing = (u'missing' in r)

		#contents = r[u'revisions'][0][u'*']

		# and a lot of more code, raise exceptions, ... look at wikipedia.get() and it's sub methods
		# preferrably to be included into wikipedia.get(), request was placed on maillist...


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


