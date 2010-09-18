# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of pagegenerators.py and mainly provides
the same functions but enhanced.

...
"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: dtbext_pagegenerators.py 0.2.0025 2009-11-18 23:42 drtrigon $'
#

# Standard library imports
import urllib, StringIO, time
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces

# Application specific imports
import config, query
import wikipedia as pywikibot
import dtbext_wikipedia as dtbext_pywikibot


REQUEST_getGlobalWikiNotifys	= 'http://toolserver.org/~merl/UserPages/query.php?user=%s&format=xml'


# ADDED
# REASON: due to http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38)
#         (MAY BE MOVE THIS INTO dtbext_userlib.py AND dtbext_pagegenerators.py ANALOG TO UserContributionsGenerator)
# !!!	  [ use 'BeautifulSoup' for this ]
def GlobalWikiNotificationsGenerator(username, site=pywikibot.Site(config.mylang)):
	"""Provides a list of results using the toolserver Merlissimo API, can also
	   be used as Generator for 'SimplePageGenerator'
	   ADDED METHOD: needed by various bots

	    If you need a full list of referring pages, use this:
	        pages = [page for page in GlobalWikiNotificationsGenerator()]

	   @param username: The user for which the data should be retrieved.
	   @type  username: string
	   @param site: The default Site from which data should be retrieved.

	   Returns a page-objects with extradata dict in 'page.extradata'
	"""

	request = REQUEST_getGlobalWikiNotifys % urllib.quote(username.encode(config.textfile_encoding))

	pywikibot.get_throttle()
	pywikibot.output(u"Reading GlobalWikiNotifications from toolserver (via 'API')...")

	buf = site.getUrl( request, no_hostname = True )

	if not buf: return	# nothing got (error?! how to catch later??)

	buf = _GetDataXML(buf, [u'userpages'])
	for i in range(0, len(buf), 2):
		item = buf[i:(i+2)]
		data = {}
		data.update(item[0][1])
		data.update(item[1][1])
		#if data[u'user'] in [username, u'DrTrigonBot']: continue
		if data[u'user'] in [username]: continue

		data[u'timestamp'] =  time.strftime(u'%H:%M, %d. %b. %Y', time.strptime(data[u'timestamp'], u'%Y%m%d%H%M%S')).decode(config.textfile_encoding)

		# [u'revid', u'user', u'timestamp', u'comment', u'redirect'],
		#yield (data[u'revid'], data[u'user'], data[u'timestamp'], data[u'comment'], data[u'link'], data[u'url'], data[u'pageid'])

		data[u'link'] = _convert_interwiki_link(site, data[u'link'])

		page = pywikibot.Page(site, data[u'link'])
		page.globalwikinotify = data
		yield page

# ADDED
# REASON: needed by 'GlobalWikiNotificationsGenerator' (due to http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38))
#         [ into 'dtbext.xmlreader' ?! ]
def _GetDataXML(data, root):
	#pywikibot.get_throttle()
	#APIdata = site.getUrl( request )

	data = StringIO.StringIO(data.encode(config.textfile_encoding))
	parser = make_parser()				# Create a XML parser
	parser.setFeature(feature_namespaces, 0)	# Tell the parser we are not interested in XML namespaces
	dh = _GetGenericData(root)			# Create the handler
	parser.setContentHandler(dh)			# Tell the parser to use our handler
	parser.parse(data)				# Parse the input

	del parser
	data.close()

	return dh.data

# ADDED
# REASON: needed by 'GlobalWikiNotificationsGenerator' (thanks to http://pyxml.sourceforge.net/topics/howto/xml-howto.html)
#         [ into 'dtbext.xmlreader' ?! ]
class _GetGenericData(saxutils.DefaultHandler):
	"""Parse XML output of wiki API interface."""
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

# ADDED: (r22)
# REASON: needed also by 'getHistoryPYF' in sum_disc, BUT ONLY TEMPORARY
def _convert_interwiki_link(site, link):
	"""Try to convert Merlissimos format of links to other languages and projects."""
	new_link = link
	for family in site.fam().get_known_families(site).values():
		title = link.replace(u'%s:' % family.decode('unicode_escape'), u':')	# e.g. 'dewiki:...' --> 'de:...'
		if not (title == link):
			new_link = u'%s:%s' % (family, title)
			# [ framework claims to know 'wiki' but does not / JIRA ticket? ]
			new_link = new_link.replace(u'wiki:', u'')
	return new_link

