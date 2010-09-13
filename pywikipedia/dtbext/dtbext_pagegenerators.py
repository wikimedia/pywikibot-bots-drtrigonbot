
"""
This is a part of pywikipedia framework, it is a deviation of pagegenerators.py and mainly provides
the same functions but enhanced.

...
"""

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
__version__='$Id: dtbext/pagegenerators.py 0.2.0019 2009-11-13 23:42 drtrigon $'
#

# Standard library imports
import urllib, StringIO, time
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces

# Application specific imports
import wikipedia, config, query


REQUEST_getGlobalWikiNotifys	= 'http://toolserver.org/~merl/UserPages/query.php?user=%s&format=xml'


# ADDED: new (r19)
# REASON: needed by various bots BUT SHOULD BE ALSO DONE BY THE PreloadingGenerator
#         (this here is just a patch, should be done in framework)
def VersionHistoryGenerator(iterable, site=wikipedia.Site(config.mylang), number=5000):
	"""Provides a list of page names with VersionHistory for the pages.
	   ADDED METHOD: needed by various bots BUT SHOULD BE DONE BY PreloadingGenerator

	    If you need a full list of referring pages, use this:
	        pages = [page for page in GlobalWikiNotificationsGenerator()]

	   @param iterable: The page title list to retrieve VersionHistory of.
	   @type  iterable: list
	   @param site: The default Site from which data should be retrieved.
	   @param number: Number of pages per request.
	   @type  number: int

	   Returns a list with entries: (title, revid, timestamp, user, comment)
	"""

	il = list(iterable)
	for i in range(0, len(il), number):	# split into pakets of len = len(number)
		item = il[i:(i+len(il))]

		# call the wiki to get info
		params = {
			u'action'	: u'query',
			u'titles'	: item,
			u'rvprop'	: [u'ids', u'timestamp', u'flagged', u'user', u'flags', u'comment'],
			u'prop'		: [u'revisions', u'info'],
		}
		if number > config.special_page_limit:
			if number > 5000:
				params[u'rvlimit'] = 5000

		wikipedia.get_throttle()
		wikipedia.output(u"Reading a set of %i pages." % len(item))

		result = query.GetData(params, site)		# 1 result per page
		r = result[u'query'][u'pages'].values()

		for item in r:
			if u'missing' in item:
                		#raise NoPage(site, item[u'title'],"Page does not exist." )
				wikipedia.output( str(wikipedia.NoPage(site, item[u'title'],u"Page does not exist." )) )
			else:
				entry = item[u'revisions'][0]
				yield (item[u'title'], entry[u'revid'], entry[u'timestamp'], entry[u'user'], entry[u'comment'])
		return


# ADDED
# REASON: due to http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38)
def GlobalWikiNotificationsGenerator(username, site=wikipedia.Site(config.mylang)):
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
	wikipedia.get_throttle()
	buf = site.getUrl( request, no_hostname = True )

	if not buf: return	# nothing got (error?! how to catch later??)

	buf = dtbext_wikipedia._GetDataXML(buf, [u'userpages'])
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
		try:
			page = dtbext_wikipedia.Page(site, data[u'link'])
			page.extradata = data
			yield page
		except wikipedia.NoPage:
			wikipedia.output(u'!!! WARNING [[%s]]: this wiki is not supported by framework, skipped!' % data[u'link'])

# ADDED
# REASON: needed by 'GlobalWikiNotificationsGenerator' (due to http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38))
def _GetDataXML(data, root):
	#wikipedia.get_throttle()
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

