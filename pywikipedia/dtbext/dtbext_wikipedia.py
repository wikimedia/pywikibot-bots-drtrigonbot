
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

# Application specific imports
import wikipedia, config, query
import dtbext_query, dtbext_date


##REQUEST_getVersionHistory	= '/w/api.php?action=query&titles=%s&rvprop=ids|timestamp|flagged|user|flags&prop=revisions|info&rvlimit=%i&format=xml'
#REQUEST_getVersionHistory	= '/w/api.php?action=query&titles=%s&rvprop=ids|timestamp|flagged|user|flags|comment&prop=revisions|info&rvlimit=%i&format=xml'
#REQUEST_getSections		= '/w/api.php?action=parse&text={{%s}}__TOC__&prop=sections&format=xml'
#REQUEST_getSections_page        = '/w/api.php?action=parse&page=%s&prop=sections&format=xml'
#REQUEST_getParsedContent	= '/w/api.php?action=parse&text=%s&format=xml'
#REQUEST_purgePageCache		= '/w/api.php?action=purge&titles=%s&format=xml'
#REQUEST_getWikiTextContent      = '/w/api.php?action=expandtemplates&text={{%s}}&format=xml'
##REQUEST_getWikiTextContentB     = '/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&rvexpandtemplates&rvgeneratexml&format=xml'
#                                    /w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&rvexpandtemplates&format=xml
#REQUEST_getBacklinks		= '/w/api.php?action=query&list=backlinks&bltitle=%s&bllimit=%s&format=xml'

#REQUEST_getVersionHistory_s	= '/w/api.php?action=query&titles=%s&rvprop=ids|timestamp|flagged|user|flags|comment&prop=revisions|info&format=xml'
#REQUEST_getContent_s		= '/w/api.php?action=query&prop=revisions&titles=%s&rvprop=timestamp|user|comment|content&format=xml'

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

class Page(wikipedia.Page):
	"""Page: A MediaWiki page

	   look at wikipedia.py for more information!
	"""

	_isRedirectPage = None

	#def __init__(self, site, title, insite=None, defaultNamespace=0):
	#	wikipedia.Page.__init__(self, site, title, insite, defaultNamespace)

	#def getVersionHistory(self, forceReload=False, reverseOrder=False,
	#			getAll=False, revCount=500):
	def getVersionHistory(self, forceReload=False, reverseOrder=False, 
				getAll=False, revCount=500):
		"""
		Same as in wikipedia.py but with some minor changes.
		  - uses API
		  - 'forceReload' is IGNORED
		  - 'getAll' is IGNORED
		"""

		# according to http://osdir.com/ml/python.pywikipediabot.general/2006-02/msg00135.html
		# http://de.wikipedia.org/wiki/Benutzer_Diskussion:Merlissimo/Sig#Frage_bez.C3.BCglich_pywikipediabot
		# http://de.wikipedia.org/w/api.php?action=query&titles=Benutzer%20Diskussion:Merlissimo&rvprop=ids|timestamp|flagged|user|flags&prop=revisions|info&rvlimit=10
		# http://de.wikipedia.org/w/api.php
		#request = REQUEST_getVersionHistory % (urllib.quote(self.title().encode(config.textfile_encoding)), revCount)
		request = {
		    'action'	: 'query',
		    'titles'	: self.title(),
		    'rvprop'	: 'ids|timestamp|flagged|user|flags|comment',
		    'prop'	: 'revisions|info',
		    'rvlimit'	: revCount,
		    }
		#buf = APIRequest( self.site(),
		#		  request,
		#		  'revisions',
		#		  'rev',
		#		  ['revid', 'user', 'timestamp', 'comment'] )
		wikipedia.get_throttle()
		buf = dtbext_query.GetProcessedData(request,
							'revisions',
							'rev',
		#					['revid', 'user', 'timestamp', 'comment'] )
							['revid', 'user', 'timestamp', 'comment', 'redirect'],
							pages = 'pages' )
		redirect  = (u'redirect' in buf[0])

		self._isRedirectPage = redirect

		# change time/date format
		data = []
		for item in buf:
			data.append( (u'%s'%item[0], dtbext_date.GetTime(item[2]), item[1], item[3]) )

		if reverseOrder: data.reverse()

		return data

	#def isRedirectPage(self):
	def isRedirectPage(self):
		"""Return True if this is a redirect, False if not or not existing."""
		if (self._isRedirectPage == None):
			self.getVersionHistory(revCount=1)
		return self._isRedirectPage

	#  DOES NOT exist in pywikipedia-framework
	def getSections(self, minLevel=2, getter=None, pagewikitext=None, sectionsonly = False):
		"""Parses the page with API and return section information.
		   (NEW FUNCTION)

		   ATTENTION: API DOES NOT WORK IF THERE ARE PARSE-ERRORS ON TH PAGE (e.g. <references />)

		   getter: because get() in API version and default dont give the same
                           results (html comments are stripped or not ...) you can choose
                           here which function to use. default is the API version.
                   pagewikitext: if content is already known, you can use this shortcut!
                   sectionsonly: return only the recived section headings (for compression e.g.)
		"""
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 35.3)

		# 'BYTEOFFSET' angekuendigt

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
			wikipedia.output(u'!!! WARNING [[%s]]: was not able to get Sections properly!' % self.title())

		# check min. level
		data = []
		for item in info:
			if (item[1] < minLevel): continue
			data.append( item )

		return (data, verify)

	#def purge_address(self, s):	# class Site
	def purgePageCache(self):
		"""Purges the page cache with API and return xml content.
		   (NEW NEW (newer) FUNCTION)
		"""
		"""Return URL path to purge cache and retrieve page 's'."""

		notpurged_def  = u'not purged'
		notmissing_def = u'not missing'

		#request = REQUEST_purgePageCache % ( urllib.quote(self.title().encode(config.textfile_encoding)) )
		request = {
		    'action'	: 'purge',
		    'titles'	: self.title(),
		    }
		#buf = APIRequest( self.site(),
		#		  request,
		#		  'purge',
		#		  'page',
		#		  [('purged', notpurged_def), ('missing', notmissing_def)] )
		wikipedia.get_throttle()
		buf = dtbext_query.GetProcessedData(request,
							'purge',
							'page',
							[] )
		#purged  = not (buf[0][0] == notpurged_def)
		#missing = not (buf[0][1] == notmissing_def)
		purged  = (u'purged' in buf[0])
		missing = (u'missing' in buf[0])

		if missing: raise wikipedia.NoPage('Was not able to purge cache of %s because it is missing!' % self.aslink())

		return purged

	#def get(self, force=False, get_redirect=False, throttle=True,
	#	sysop=False, change_edit_time=True):
	def get(self, force=False, get_redirect=False, throttle=True,
		sysop=False, change_edit_time=True,
		mode='default', plaintext=False):
		"""
		Same as in wikipedia.py but with some minor changes. Switches between all available
		read modes. (default API read not yet implemented)
		  - uses API with mode='full' and mode='parse'
		  - these modes IGNORE all other options except of
		  - plaintext: switch for choosing between HTML or plain text output
		"""

		if 	(mode == 'full'):	# getFull
			return self._getFullContent(plaintext=plaintext)
		elif	(mode == 'parse'):	# getParsed
			buf = getParsedString('{{%s}}' % self.title(), plaintext=plaintext, site=self.site())
			if re.search(('title="%(title)s \(Seite nicht vorhanden\)">%(title)s</a>'%{'title':self.title()}), buf):
				raise wikipedia.NoPage(self.site(), self.aslink(forceInterwiki = True),"Page does not exist." )
			return buf
		else:				# default
			return wikipedia.Page.get(self, force=force, get_redirect=get_redirect, throttle=throttle,
							sysop=sysop, change_edit_time=change_edit_time)

	#  DOES NOT exist in pywikipedia-framework
	def _getFullContent(self, plaintext=False):
		"""Return the full expanded wiki-text of the page.

		Do not use this directly, use get() instead. Except as getter for getSections().
		"""

		#request = REQUEST_getWikiTextContent % ( urllib.quote(self.title().encode(config.textfile_encoding)) )
		#request = {
		#    'action'	: 'expandtemplates',
		#    'text'	: '{{%s}}'%self.title(),
		#    }
		request = {
		    'action'		: 'query',
		    'prop'		: 'revisions',
		    'titles'		: self.title(),
		    'rvprop'		: 'content',
		    'rvexpandtemplates'	: '',
		    }
		#buf = APIRequest( self.site(),
		#		  request,
		#		  'api',
		#		  'expandtemplates',
		#		  [] )
		#buf = dtbext_query.GetProcessedData(request,
		#					'api',
		#					'expandtemplates',
		#					[] )
		wikipedia.get_throttle()
		buf = dtbext_query.GetProcessedData(request,
							'revisions',
							'rev',
							['title', '*'],
							pages = 'pages' )
		#buf = buf[u'*']
		buf = buf[0][1]

		if buf == (u'[[:%s]]'%self.title()): raise wikipedia.NoPage(self.site(), self.aslink(forceInterwiki = True),"Page does not exist." )

		# Patch/adjust wiki section syntax, to enabled full heading recognition
		buf = wikisectionpatch(buf)

		if plaintext: buf = html2notagunicode(buf)

		#return buf.strip()
		return buf

	# - EXPERIMENTAL -
#	def getFullB(self, force=False, get_redirect=False, throttle=True,
#			sysop=False, change_edit_time=True):
#		"""Return the full expanded wiki-text of the page.
#
#		Return value is a string. NO force, NO get_redirect,
#		NO throttle, NO sysop, NO change_edit_time!!
#		"""
#
#		request = REQUEST_getWikiTextContentB % ( urllib.quote(self.title().encode(config.textfile_encoding)) )
#		buf = APIRequest( self.site(),
#				  request,
#				  'revisions',
#				  'rev',
#				  ['parsetree'] )
#
#		return buf

	#def getReferences(self,
	#	follow_redirects=True, withTemplateInclusion=True,
	#	onlyTemplateInclusion=False, redirectsOnly=False):
	def getReferences(self,
		follow_redirects=True, withTemplateInclusion=True,
		onlyTemplateInclusion=False, redirectsOnly=False, 
		number = 500):
		"""
		Same as in wikipedia.py but with some minor changes. Important for ReferringPageGenerator().
		  - uses API
		  - 'follow_redirects' is IGNORED
                  - 'withTemplateInclusion' same function as in original (also returns pages where self is
                                            used as a template
		  - 'onlyTemplateInclusion' is IGNORED
		  - 'redirectsOnly' is IGNORED

		If you need a full list of referring pages, use this:
		    pages = [page for page in s.getReferences()]
		"""

		# according to 'ContributionsGen(...)'

		# Lists pages that link to a given page, similar to Special:Whatlinkshere. Ordered by linking page title.
		# (http://www.mediawiki.org/wiki/API:Query_-_Lists#backlinks_.2F_bl)
		# request = REQUEST_getBacklinks % (urllib.quote(self.title().encode(config.textfile_encoding)), number)
		request = {
		    'action'	: 'query',
		    'list'	: 'backlinks',
		    'bltitle'	: self.title(),
		    'bllimit'	: number,
		    }
		wikipedia.output(u'Getting references to %s' % self.aslink())
		#buf = APIRequest( self.site(),
		#		  request,
		#		  'backlinks',
		#		  'bl',
		#		  ['pageid', 'ns', 'title'] )
		wikipedia.get_throttle()
		buf = dtbext_query.GetProcessedData(request,
							'backlinks',
							'bl',
							['pageid', 'ns', 'title'] )

		# List pages that include a certain page.
		# (http://www.mediawiki.org/wiki/API:Query_-_Lists#embeddedin_.2F_ei)
		# http://de.wikipedia.org/w/api.php?action=query&list=embeddedin&eititle=Benutzer:DrTrigon/Entwurf/Vorlage:AutoMail&eilimit=5
		if withTemplateInclusion:
			request = {
			    'action'	: 'query',
			    'list'	: 'embeddedin',
			    'eititle'	: self.title(),
			    'eilimit'	: number,
			    }
			#buf = APIRequest( self.site(),
			#		  request,
			#		  'backlinks',
			#		  'bl',
			#		  ['pageid', 'ns', 'title'] )
			wikipedia.get_throttle()
			buf += dtbext_query.GetProcessedData(request,
								'embeddedin',
								'ei',
								['pageid', 'ns', 'title'] )
			buf = buf[:number]

		# since it is a generator; set the page title in index 0 of the tuple
        	refPages = []
		for item in buf:
			#data.append( (item[2], item[0], item[1]) )
			if not item[2] in refPages:
				refPages.append(item[2])
				yield Page(self.site(), item[2])


#def output(text, decoder = None, newline = True, toStdout = False, timestmp = True):
#	"""Output a message to the user via the userinterface.
#
#	( according to wikipedia.output(...) )
#	"""
#	if timestmp: text = dtbext_date.getTimeStmp(full = True, humanreadable = True, local = True) + '::' + text
#	wikipedia.output(text, decoder, newline, toStdout)


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

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

	#def get(self, force=False, get_redirect=False, throttle=True,
	#	sysop=False, change_edit_time=True):
	def get(self, force=False, get_redirect=False, throttle=True,
		sysop=False, change_edit_time=True,
		mode='default'):
		"""
		...

		  - uses API
		  - 'force' is IGNORED
		  - 'get_redirect' is IGNORED
		  - 'sysop' is IGNORED
		  - 'change_edit_time' is IGNORED

		GENERATOR: this way only a packet of len self._min_request is held in memory
		           instead of ALL pages, therefore it is IMPORTANT to use 'drop_dups()'
                           before to be in sync with outer/other lists!
			   AND there is no NoPage-exception thrown on error instead content=None
		"""

		if 	(mode == 'full'):	# getFull
			request_default = { 'rvexpandtemplates': '' }
			# Patch/adjust wiki section syntax, to enabled full heading recognition
			postprocessing = wikisectionpatch
		else:				# default
			request_default = {}
			postprocessing = lambda x: x	# (do nothing)

		(pages, joined_bundle) = self._bundle_list(self._pages, joiner=None)
		(bundle, joined_bundle) = self._bundle_list(self._titles, size=self._min_request)
		for i, entry in enumerate(joined_bundle):
			self._requesting_data = True

			if throttle:
				wikipedia.get_throttle()

			#request = REQUEST_getContent_s % (urllib.quote(joined_bundle[i].encode(config.textfile_encoding)))
			#request = {
			request = dict(request_default)
			request.update( {
			    'action'	: 'query',
			    'prop'	: 'revisions',
			    'titles'	: entry,
			    'rvprop'	: 'timestamp|user|comment|content',
			    } )
			#buf = APIRequest( self._site,
			#			request,
			#			'revisions',
			#			'rev',
			#			[], 
			#			pages = 'page' )
			buf = dtbext_query.GetProcessedData(request,
								'revisions',
								'rev',
								['title', '*'],
								#['title', '*', 'missing'],
								pages = 'pages' )

			result = buf
			buf = {}
			for item in result:
				#if ('missing' in item): raise wikipedia.NoPage(self._site, item[0], "Page does not exist." )
				if ('missing' in item):
					buf[item[0]] = None
					wikipedia.output( u"WARNING: Page [[%s]] does not exist." % item[0] )
				else:
					# do postprocessing
					buf[item[0]] = postprocessing(item[1])
			for j, item in enumerate(bundle[i]):
				#yield (Page(self._site, bundle[i][j]), buf[pages[i][j]])
				yield (pages[i][j], buf[ pages[i][j].sectionFreeTitle() ])
				self._requesting_data = False


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

def SendMail(user, subject, text, CCme = False):
	"""Bot sends a mail from wiki with API and return success.
	   (NEW FUNCTION)

	   user:    user to send the mail to
	   subject: mail subject
	   text:    mail text
	   CCme:    send CC to bot's mail address
	"""

	# get token needed to send a mail
	#http://de.wikipedia.org/w/api.php?action=query&prop=info&intoken=email&titles=User:DrTrigon
	request = {
	    'action'	: 'query',
	    'prop'	: 'info',
	    'intoken'	: 'email',
	    'titles'	: 'User:%s' % user,
	    }
	wikipedia.get_throttle()
	buf = dtbext_query.GetProcessedData(request,
						'page',
						'',
						['emailtoken'],
						pages = 'pages' )
	emailtoken = buf[0][0]

	# send mail by POST request
	request = {
	    'action'	: 'emailuser',
	    'target'	: user,
	    'subject'	: subject,
	    'text'	: text,
	    'token'	: emailtoken,
	    }
	if CCme: request['ccme'] = '1'
	buf = dtbext_query.GetProcessedData(request,
						'emailuser',
						'',
						[],
						post = True )

	return (buf[u'result'] == u'Success')

######## Unicode library functions ########

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

## thanks to: http://pyxml.sourceforge.net/topics/howto/xml-howto.html
#class GetData(saxutils.DefaultHandler):
#	"""
#	Parse XML output of wiki API interface
#	"""
#	def __init__(self, parent, content, values = [], pages = None):
#		self.get_parent, self.get_content, self.get_values = parent, content, values
#		self._parent, self._content = "", ""
#		self._page = ''
#		#self.data = []
#		self.data = {'':[]}
#		#self.chars = ""
#		self.chars = {'':""}
#		self.pages = pages
#
#	def startElement(self, name, attrs):
#		if (name == self.pages):	# new page
#			self._page = attrs.get('title', '')
#			self.data[self._page] = []
#			self.chars[self._page] = ""
#
#		self._content = name
#		if not ((self._parent == self.get_parent) and (self._content == self.get_content)):
#			self._content = ""
#			self._parent = name
#			return
#		data = []
#		for item in self.get_values:
#			#data.append( attrs.get(item, "") )
#			try:	(val, default) = item
#			except:	(val, default) = (item, "")
#			data.append( attrs.get(val, default) )
#		self.data[self._page].append( tuple(data) )
#
#	def characters(self, content):
#		if not (self._content == self.get_content): return
#		#self.chars += content
#		self.chars[self._page] += content

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

#def APIRequest(site, request, parent, content, values, pages = None):
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

