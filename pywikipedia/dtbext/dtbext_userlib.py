# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of userlib.py and mainly provides
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
__version__='$Id: dtbext_userlib.py 0.3.0040 2010-10-02 20:13 drtrigon $'
#

# Standard library imports
import urllib, time
from xml.etree.cElementTree import XML
# or if cElementTree not found, you can use BeautifulStoneSoup instead

# Application specific imports
import userlib
import wikipedia as pywikibot


REQUEST_getGlobalWikiNotifys	= 'http://toolserver.org/~merl/UserPages/query.php?user=%s&format=xml'


# ADDED: new (r26)
# REASON: needed to convert userlib.User, ... objects to dtbext.userlib.User, ... objects
def addAttributes(obj):
	"""Add methods to various classes to convert them to the dtbext modified version."""
	# http://mousebender.wordpress.com/2007/02/17/copying-methods-in-python/
	# http://code.activestate.com/recipes/52192-add-a-method-to-a-class-instance-at-runtime/
	if "class 'userlib.User'" in str(type(obj)):
		# this cannot be looped because of lambda's scope (which is important for page)
		# look also at http://www.weask.us/entry/scope-python-lambda-functions-parameters
		obj.__dict__['globalnotifications'] = lambda *args, **kwds: User.__dict__['globalnotifications'](obj, *args, **kwds)


# MODIFIED
# REASON: (look below)
class User(userlib.User):
	"""A class that represents a Wiki user.

	   look at userlib.py for more information!
	"""

	# ADDED
	# REASON: due to http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 38)
	def globalnotifications(self):
		"""Provides a list of results using the toolserver Merlissimo API (can also
		   be used for a Generator analog to UserContributionsGenerator).
		   ADDED METHOD: needed by various bots

		   Returns a tuple containing the page-object and an extradata dict.
		"""

		request = REQUEST_getGlobalWikiNotifys % urllib.quote(self.name().encode(self.site().encoding()))

		pywikibot.get_throttle()
		pywikibot.output(u"Reading global wiki notifications from toolserver (via 'API')...")

		buf = self.site().getUrl( request, no_hostname = True )

		tree = XML( buf.encode(self.site().encoding()) )
		#import xml.etree.cElementTree
		#print xml.etree.cElementTree.dump(tree)

		for t in tree:
			# get data in Element t
			data = dict(t.items())

			# get data in child Element c of Element t
			for c in t.getchildren():
				child_data = dict(c.items())
				data.update(child_data)

			# skip changes by user itself
			#if data[u'user'] in [self.name(), u'DrTrigonBot']: continue
			if data[u'user'] in [self.name()]: continue

			# process timestamp
			data[u'timestamp'] =  str(pywikibot.Timestamp.fromtimestampformat(data[u'timestamp']))

			# convert link to valid interwiki link
			link = data[u'link']
			for family in self.site().fam().get_known_families(self.site()).values():
				title = link.replace(u'%s:' % family.decode('unicode_escape'), u':')	# e.g. 'dewiki:...' --> 'de:...'
				if not (title == link):
					data[u'link'] = u'%s:%s' % (family, title)
					# [ framework claims to know 'wiki' but does not / JIRA: DRTRIGON-60 ]
					data[u'link'] = data[u'link'].replace(u'wiki:', u'')

			# return page object with additional data
			try:
				page = pywikibot.Page(self.site(), data[u'link'])
				page.globalwikinotify = data
				yield (page, data)
			except pywikibot.exceptions.NoPage, e:
				pywikibot.output(u'%s' %e)

