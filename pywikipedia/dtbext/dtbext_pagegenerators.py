
"""
This is a part of pywikipedia framework, it is a deviation of pagegenerators.py and mainly provides
the same functions but enhanced.

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
__version__='$Id: dtbext/pagegenerators.py 0.2.0000 2009-06-21 16:42:00Z drtrigon $'
#

# Standard library imports
import urllib, StringIO, time
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces
import xml.utils.iso8601
import httplib, urllib
import re
from HTMLParser import HTMLParser

# Application specific imports
import wikipedia, config
import dtbext_query, dtbext_wikipedia


#REQUEST_ContributionsGen	= '/w/api.php?action=query&list=usercontribs&ucuser=%s&uclimit=%i&format=xml'
##REQUEST_getBacklinks		= '/w/api.php?action=query&list=backlinks&bltitle=%s&bllimit=%s&format=xml'
REQUEST_getGlobalWikiNotifys	= 'http://toolserver.org/~merl/UserPages/query.php?user=%s&format=xml'


# ====================================================================================================
#  exists in pywikipedia-framework
# ====================================================================================================

#def UserContributionsGenerator(username, number = 250, namespaces = [], site = None ):
def UserContributionsGenerator(username, number = 100, namespaces = [], site = wikipedia.Site(config.mylang)):
#def UserContributionsGenerator(username, number = 100, namespaces = [], site = wikipedia.getSite()):
	"""
	Same as in pagegenerators.py but with some minor changes.
	  - uses API
	  - no limit of 500 (since bot may 5000)
	  - 'namespaces' is IGNORED

	If you need a full list of referring pages, use this:
	    pages = [page for page in UserContributionsGenerator()]
	"""

	# according to http://osdir.com/ml/python.pywikipediabot.general/2006-02/msg00135.html
	# http://de.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuser=Merlissimo&uclimit=20
	# http://de.wikipedia.org/w/api.php
	#request = REQUEST_ContributionsGen % (urllib.quote(username.encode(config.textfile_encoding)), number)
	request = {
	    'action'	: 'query',
	    'list'	: 'usercontribs',
	    'ucuser'	: username,
	    'uclimit'	: number,
	    }
	#buf = dtbext_wikipedia.APIRequest( site,
	#				  request,
	#				  'usercontribs',
	#				  'item',
	#				  ['user', 'pageid', 'revid', 'ns', 'title', 'timestamp', 'top', 'comment'] )
	buf = dtbext_query.GetProcessedData(request,
						'usercontribs',
						'item',
						#['user', 'pageid', 'revid', 'ns', 'title', 'timestamp', 'top', 'comment'] )
						['user', 'pageid', 'revid', 'ns', 'title', 'timestamp', 'comment'] )

	# change time/date format and since it is a generator; set the page
	# title in index 0 of the tuple
	titleList = []
	for item in buf:
		#data.append( (item[4], item[0], item[1], item[2], item[3], dtbext_wikipedia.GetTime(item[5]), item[6], item[7]) )
		if not item[4] in titleList:
			titleList.append(item[4])
			yield dtbext_wikipedia.Page(site, item[4])

#def ReferringPageGenerator(referredPage, followRedirects=False,
#                           withTemplateInclusion=True,
#                           onlyTemplateInclusion=False):
def ReferringPageGenerator(referredPage, followRedirects=False,
				withTemplateInclusion=True,
				onlyTemplateInclusion=False, 
				number = 500):
	"""
	EXACT the same as in wikipedia.py but with 'number'.
	( THIS SHOULD PROBABLY BE CONTRIBUTED?! )

	If you need a full list of referring pages, use this:
	    pages = [page for page in ReferringPageGenerator()]
	"""
	for page in referredPage.getReferences(followRedirects,
						withTemplateInclusion,
						onlyTemplateInclusion,
						number = number):
		yield page


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

# created due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38)
def GlobalWikiNotificationsGenerator(username, site = wikipedia.Site(config.mylang)):
	"""
	Provides a list of results using the toolserver Merlissimo API, can also
	be used as Generator for 'SimplePageGenerator'

	If you need a full list of referring pages, use this:
	    pages = [page for page in GlobalWikiNotificationsGenerator()]

	returns page-objects with extradata dict in 'page.extradata'
	"""

	# according to 'ContributionsGen(...)' BUT changed to support simple HTML
	request = REQUEST_getGlobalWikiNotifys % urllib.quote(username.encode(config.textfile_encoding))
	wikipedia.get_throttle()
	buf = site.getUrl( request, no_hostname = True )

	#parser = dtbext_wikipedia.GetDataHTML()
	#parser.feed(buf)
	#parser.close()
	#buf = parser.textdata.split('\n')

	## since it is a generator; set the page title in index 0 of the tuple (keine doppelnennungen!!)
	##data = []
	#for item in buf:
	#	if (item[:2] == u'[['):
	#		#data.append( re.split(u': ', item, maxsplit=1) )
	#		yield dtbext_wikipedia.Page(site, re.split(u': ', item, maxsplit=1))

	if not buf: return	# nothing got (error?! how to catch later??)

	buf = dtbext_wikipedia.GetDataXML(buf, ['userpages'])
	for i in range(0, len(buf), 2):
		item = buf[i:(i+2)]
		data = {}
		data.update(item[0][1])
		data.update(item[1][1])
		#if data['user'] in [username, 'DrTrigonBot']: continue
		if data['user'] in [username]: continue

		data['timestamp'] =  time.strftime('%H:%M, %d. %b. %Y', time.strptime(data['timestamp'], '%Y%m%d%H%M%S')).decode(config.textfile_encoding)

		# ['revid', 'user', 'timestamp', 'comment', 'redirect'],
		#yield (data['revid'], data['user'], data['timestamp'], data['comment'], data['link'], data['url'], data['pageid'])
		try:
			page = dtbext_wikipedia.Page(site, data['link'])
			page.extradata = data
			yield page
		except wikipedia.NoPage:
			wikipedia.output(u'!!! WARNING [[%s]]: this wiki is not supported by framework, skipped!' % data['link'])

