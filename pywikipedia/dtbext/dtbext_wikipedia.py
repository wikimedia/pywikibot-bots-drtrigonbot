
"""
This is a part of pywikipedia framework, it is a deviation of wikipedia.py and mainly subclasses
the page class from there.

...
"""

# dbtext/wikipedia.py - USAGE:
#	import dbtext
#	...
#	page2 = dbtext.wikipedia.PageFromPage(page1)
#	print page1.getVersionHistory()[0]	# original
#	print page2.getVersionHistory()[0]	# my API version
#	...
#	print dbtext.wikipedia.ContributionsGen(user)
#	for i in dbtext.wikipedia.SimplePageGenerator(user, dbtext.wikipedia.ContributionsGen): print i
#
# !! 2 NEUE FUNKTIONEN NOCH DOKUMENTIEREN... !!!
# ?? noch mehr mittlerweile!!

# ====================================================================================================
#
# ToDo-Liste (Bugs, Features, usw.):
# http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste
#
# READ THE *DOGMAS* FIRST!
# 
# ====================================================================================================

#
# (C) Dr. Trigon, 2009
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', 'sum_disc-conf.py', ...
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id: dtbext/wikipedia.py 0.2.0000 2009-06-21 16:42:00Z drtrigon $'
#

# Standard library imports
import urllib, StringIO
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces
import httplib, urllib
import re, sets
from HTMLParser import HTMLParser
#import difflib
# Splitting the bot into library parts
from pywikibot import *

# Application specific imports
import config, query
import dtbext_query, dtbext_date


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


# ====================================================================================================
#  exists in pywikipedia-framework
# ====================================================================================================

# MODIFIED
# REASON: (look below)
class Page(wikipedia.Page):
	"""Page: A MediaWiki page

	   look at wikipedia.py for more information!
	"""

	_isRedirectPage = None

	# MODIFIED
	# REASON: should be faster than original
	def isRedirectPage(self):
		"""Return True if this is a redirect, False if not or not existing.
		   MODIFIED METHOD: should be faster than original
		"""

		if (self._isRedirectPage == None):
			params = {
				u'action'	: u'query',
				u'titles'	: self.title(),
				u'prop'		: u'info',
				u'rvlimit'	: 1,
			}

			wikipedia.get_throttle()
			wikipedia.output(u"Reading redirect info from %s." % self.aslink())

			result = query.GetData(params, self.site())
			r = result['query']['pages'].values()[0]

			self._isRedirectPage  = (u'redirect' in r)
		return self._isRedirectPage

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
			wikipedia.get_throttle()
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
		v2 = not REGEX_wikiSection.search( wikisectionpatch(u'\n'.join(wikitext[first:])) )
		verify = (v1 and v2)
		if not verify:
			#raise wikipedia.SectionError('Was not able to get Sections of %s properly!' % self.aslink())
			#wikipedia.output(u'!!! WARNING [[%s]]: was not able to get Sections properly!' % self.title())
			raise Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.aslink())

		# check min. level
		data = []
		for item in info:
			if (item[1] < minLevel): continue
			data.append( item )

		return data

	# ADDED: new (r18)
	# REASON: needed by various bots
	def getSections(self, minLevel=2, sectionsonly=False, getter=None, pagewikitext=None):
		"""Parses the page with API and return section information.
		   ADDED METHOD: needed by various bots

		   sectionsonly: return only the recived section headings (for compression e.g.)
#		   getter: because get() in API version and default dont give the same
#		            results (html comments are stripped or not ...) you can choose
#		            here which function to use. default is the API version.
#		   pagewikitext: if content is already known, you can use this shortcut!

		   Returns a list with entries: (byteoffset, level, wikiline, line, anchor)
		   This list may be empty and if sections are embedded by template, the according
		   byteoffset and wikiline entries are None.
		"""
# - check calling params

		# Old exceptions and contents do not apply any more.
		for attr in ['_getexception', '_sections']:
			if hasattr(self, attr):
				delattr(self,attr)

		params = {
			u'action'	: u'parse',
			u'page'		: self.title(),
			u'prop'		: u'sections',
		}

		wikipedia.get_throttle()
		wikipedia.output(u"Reading section info from %s." % self.aslink())

		result = query.GetData(params, self.site())
		r = result[u'parse'][u'sections']
		#print r

		if not sectionsonly:
			# assign sections with wiki text and section byteoffset
			wikipedia.output(u"\tReading wiki page text from %s (if not already done)." % self.aslink())
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
			#wikipedia.get_throttle()
			#wikipedia.output(u"\tReading section %i from %s." % (section[u'number'], self.aslink()))
			# if not successfull too, report error/problem
			# raise Error('Problem occured during attempt to retrieve and resolve sections in %s!' % self.aslink())

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

		params = {
			u'action'	: u'purge',
			u'titles'	: self.title(),
		}

		wikipedia.get_throttle()
		wikipedia.output(u"Purging page cache for %s." % self.aslink())

		result = query.GetData(params, self.site())
		r = result['purge'][0]

		purged  = (u'purged' in r)
		missing = (u'missing' in r)

		if missing: raise wikipedia.NoPage('Was not able to purge cache of %s because it is missing!' % self.aslink())

		return purged

# ADDED
# REASON: ...
	def getEnh(self, expandtemplates=True):
		"""Return the wiki text of the page in various formats.
		   ADDED METHOD: ...

		   force   is ignored; the page is NOT cached
		   ......
		"""

		params = {
		    u'action'		: u'query',
		    u'prop'		: u'revisions',
		    u'titles'		: self.title(),
		    u'rvprop'		: u'content',
		    }
		if expandtemplates: params[u'rvexpandtemplates'] = u''

		wikipedia.get_throttle()
		wikipedia.output(u"Purging page cache for %s." % self.aslink())

		result = query.GetData(params, self.site())
		r = result[u'query'][u'pages'].values()[0]

		missing = (u'missing' in r)

		#contents = r[u'revisions'][0][u'*']


		# and a lot of more code, raise exceptions, ... look at wikipedia.get() and it's sub methods
		# preferrably to be included into wikipedia.get(), request was placed on maillist...

		raise NotImplementedError('This should be implemented into \'wikipedia.get()\' directly, request placed on maillist!!')


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

# ADDED
# REASON: faster and less traffic intense big pageset processing
class Pages():
	"""Pages: A set of MediaWiki pages
	"""

	_max_request = 50
	_min_request = 10

	_requesting_data = False

	_isRedirectPage = None

	def __init__(self, site, titles, insite=None, defaultNamespace=0):
		"""
		...
		"""

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
			wikipedia.output( u"WARNING: Page [[%s]] gave no API result." % item )

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

	def getVersionHistory(self, revCount=500):
		"""
		...
		"""

		## according to Page.getVersionHistory()
		(bundle, joined_bundle) = self._bundle_list(self._titles, size=self._max_request)
		#result = {}
		result = []
		self._requesting_data = True
		for item in joined_bundle:
			# es kommt PRO PAGE/TITLE GENAU 1 RESULTAT zurueck, deshalb ist Zuordnung einfach
			#request = REQUEST_getVersionHistory_s % (urllib.quote(item.encode(config.textfile_encoding)))
			request = {
			    'action'	: 'query',
			    'titles'	: item,
			    'rvprop'	: 'ids|timestamp|flagged|user|flags|comment',
			    'prop'	: 'revisions|info',
			    }
			#buf = APIRequest( self._site,
			#		  request,
			#		  'revisions',
			#		  'rev',
			#		  ['revid', 'user', 'timestamp', 'comment'], 
			#		  pages = 'page' )
			wikipedia.get_throttle()
			buf = dtbext_query.GetProcessedData(request,
								'revisions',
								'rev',
								#['revid', 'user', 'timestamp', 'comment', 'title'],
								['revid', 'user', 'timestamp', 'comment', 'title', 'redirect'],
								pages = 'pages' )
			#result.update( buf )
			result += buf
		self._requesting_data = False
		buf = result

		# change time/date format
		#for item in result.keys():
		result = {}
		self._isRedirectPage = []
		for item in buf:
			#try: result[item] = [(result[item][0][0], dtbext_date.GetTime(result[item][0][2]), result[item][0][1], result[item][0][3])]
			#except: pass
			#if ('missing' in item): raise wikipedia.NoPage(self._site, item[4], "Page does not exist." )
			if ('missing' in item):
				result[item[4]] = None
				wikipedia.output( u"WARNING: Page [[%s]] does not exist." % item[4] )
			elif ('redirect' in item):
				result[item[4]] = [(u'%s'%item[0], dtbext_date.GetTime(item[2]), item[1], item[3])]
				self._isRedirectPage.append( item[4] )
				wikipedia.output( u"WARNING: Page [[%s]] is a redirect." % item[4] )
			else:
				result[item[4]] = [(u'%s'%item[0], dtbext_date.GetTime(item[2]), item[1], item[3])]

		# validity check, append omitted pages (because the list should be complete)
		return self._append_missing_pages(result, self._titles, set_item=None)		# 'None' like 'missing' page

	#def isRedirectPage(self):
	def isRedirectPage(self, title):
		"""Return True if this is a redirect, False if not or not existing."""
		if (self._isRedirectPage == None):
			self.getVersionHistory()
		return (title in self._isRedirectPage)

	#def getSections(self, minLevel=2, getter=None, pagewikitext=None, sectionsonly = False):

	# ADDED
	# REASON: needed by various bots
	def get(self, force=False, get_redirect=False, throttle=True,
		sysop=False, change_edit_time=True,
		mode='default'):
		"""
		...

		  - 'force' is IGNORED
		  - 'get_redirect' is IGNORED
		  - 'sysop' is IGNORED
		  - 'change_edit_time' is IGNORED

		GENERATOR: this way only a packet of len self._min_request is held in memory
		           instead of ALL pages, therefore it is IMPORTANT to use 'drop_dups()'
                           before to be in sync with outer/other lists!
			   AND there is no NoPage-exception thrown on error instead content=None

		RETURNS PAGE OBJECT THAT USES CACHED/BUFFERED CONTENT AND HAS NOT TO READ FROM API/NET AGAIN!!!
		"""

		if 	(mode == 'full'):	# getFull
			params_default = { 'rvexpandtemplates': '' }
			# Patch/adjust wiki section syntax, to enabled full heading recognition
			postprocessing = wikisectionpatch
		else:				# default
			params_default = {}
			postprocessing = lambda x: x	# (do nothing)

		(pages, joined_bundle) = self._bundle_list(self._pages, joiner=None)
		(bundle, joined_bundle) = self._bundle_list(self._titles, size=self._min_request)
		for i, entry in enumerate(joined_bundle):
			self._requesting_data = True

			params = dict(params_default)
			params.update( {
			    u'action'	: u'query',
			    u'prop'	: u'revisions|info',
			    u'titles'	: entry,
			    u'rvprop'	: u'ids|timestamp|user|comment|content',
			    } )

			if throttle:
				wikipedia.get_throttle()
			wikipedia.output(u"Reading and caching a set of pages.")

			result = query.GetData(params, self._site)
			r = result[u'query'][u'pages'].values()

			buf = {}
			for pageInfo in r:
				# create page object
				page = Page(self._site, pageInfo[u'title'], defaultNamespace=pageInfo[u'ns'])

				# modify and fill it with actual state (as if 'get' was executed)
				if 'missing' in pageInfo:
					page._getexception = NoPage
					#raise NoPage(page.site(), page.aslink(forceInterwiki = True),
					#             "Page does not exist. In rare cases, if you are certain the page does exist, look into overriding family.RversionTab" )
					wikipedia.output( str(NoPage(page.site(), page.aslink(forceInterwiki = True),
							"Page does not exist. In rare cases, if you are certain the page does exist, look into overriding family.RversionTab" )) )
					yield page
					continue
				elif 'invalid' in pageInfo:
					raise BadTitle('BadTitle: %s' % page)

				if 'revisions' in pageInfo: #valid Title
					lastRev = pageInfo['revisions'][0]

				page.editRestriction = ''
				page.moveRestriction = ''

				page._revisionId = lastRev['revid']

				page._isWatched = False #cannot handle in API in my research for now.

				pagetext = lastRev['*'].rstrip()

				if 'redirect' in pageInfo:
					if get_redirect:
                				pass
					else:
						page._getexception = IsRedirectPage
						#raise IsRedirectPage(redirtarget)
						wikipedia.output( str(IsRedirectPage("Page is a redirect.")) )
						yield page
						continue

				page._contents = pagetext	# manipulate page object to use cached/buffered content

				yield page

#				#if ('missing' in item): raise wikipedia.NoPage(self._site, item[0], "Page does not exist." )
#				if ('missing' in item):
#					buf[item[0]] = None
#					wikipedia.output( u"WARNING: Page [[%s]] does not exist." % item[0] )
#				else:
#					# do postprocessing
#					buf[item[0]] = postprocessing(item[1])
#			for j, item in enumerate(bundle[i]):
#				print "*", item
#				#yield (Page(self._site, bundle[i][j]), buf[pages[i][j]])
#				yield (pages[i][j], buf[ pages[i][j].sectionFreeTitle() ])
#				self._requesting_data = False


def PageFromPage(page):
	return Page(page._site, page.title(), defaultNamespace=page._namespace)

def getParsedString(string, plaintext=False, site=wikipedia.getSite()):
	"""Parses the string with API and return html content.
	   (NEW FUNCTION)

	   plaintext: switch for choosing between HTML or plain text
	              output
	"""

	#request = REQUEST_getParsedContent % urllib.quote(string.encode(config.textfile_encoding))
	request = {
	    'action'	: 'parse',
	    'text'	: string,
	    }
	#buf = APIRequest( site,
	#		  request,
	#		  'parse',
	#		  'text',
	#		  [] )
	wikipedia.get_throttle()
	buf = dtbext_query.GetProcessedData(request,
						'parse',
						'text',
						[] )
	buf = buf[u'text'][u'*']

	if plaintext: buf = html2notagunicode(buf)

	return buf.strip()

######## Unicode library functions ########

# try to replace with 'pywikibot.textlib.removeDisabledParts()' !!
#
def html2notagunicode(text, keep_wikitags=False):
	"""Remove all HTML tags in text."""

	# thanks to http://www.hellboundhackers.org/articles/841-using-python-39;s-htmlparser-class.html
	parser = GetDataHTML()
	if keep_wikitags: parser._wikitags = ['tt', 'nowiki', 'small', 'sup']
	parser.feed(text)
	parser.close()
	return parser.textdata

def wikisectionpatch(text):
	"""Patch/adjust wiki section syntax, to enabled full heading recognition."""

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

# thanks to: http://pyxml.sourceforge.net/topics/howto/xml-howto.html
class GetGenericData(saxutils.DefaultHandler):
	"""
	Parse XML output of wiki API interface
	"""
	def __init__(self, root):
		self._root = root
		self._path = []
		self._parent = False

		self.data = []

	def startElement(self, name, attrs):
		if (self._path == self._root):
			self._parent = True
		self._path.append( name )

		if self._parent:
			dictdata = dict([ [item, attrs.get(item, '')] for item in attrs.getQNames() ])
			self.data.append( (name, dictdata) )

	def endElement(self, name):
		if (self._path == self._root):
			self._parent = False
		self._path.reverse()
		self._path.remove( name )
		self._path.reverse()

# thanks to http://docs.python.org/library/htmlparser.html
class GetDataHTML(HTMLParser):
	textdata = u''
	#_wikitags = ['tt', 'nowiki', 'small', 'sup']
	_wikitags = []

	def handle_data(self, data):
		self.textdata += data

# IMPORTANT for handling of wiki-tags like <tt>, <nowiki>, ...
#
	def handle_starttag(self, tag, attrs):
		#print "Encountered the beginning of a %s tag" % tag
		if tag in self._wikitags: self.textdata += u"<%s>" % tag

	def handle_endtag(self, tag):
		#print "Encountered the end of a %s tag" % tag
		if tag in self._wikitags: self.textdata += u"</%s>" % tag

def GetDataXML(data, root):
	#wikipedia.get_throttle()
	#APIdata = site.getUrl( request )

	data = StringIO.StringIO(data.encode(config.textfile_encoding))
	parser = make_parser()				# Create a XML parser
	parser.setFeature(feature_namespaces, 0)	# Tell the parser we are not interested in XML namespaces
	#dh = GetData(parent, content, values)		# Create the handler
	#dh = GetData(parent, content, values, pages)	# Create the handler
	dh = GetGenericData(root)			# Create the handler
	parser.setContentHandler(dh)			# Tell the parser to use our handler
	parser.parse(data)				# Parse the input

	del parser
	data.close()

	##if (values == []): return dh.chars
	##return dh.data
	#if (values == []):	result = dh.chars
	#else:			result = dh.data
	#if pages:
	#	del result['']
	#	return result
	#else:
	#	return result['']

	return dh.data

