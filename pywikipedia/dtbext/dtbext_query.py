
"""
This is a part of pywikipedia framework, it is a deviation of query.py and mainly provides
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
__version__='$Id: dtbext/query.py 0.2.0000 2009-06-21 16:42:00Z drtrigon $'
#

# Standard library imports
import sys, time
import simplejson, urllib

# Application specific imports
import wikipedia, query


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

def GetProcessedData(params, parent, content, values, pages = None, post = False):
	# to be able to catch error messages
	if values and ('missing' not in values): values.append( 'missing' )

	#data = GetData(params, useAPI = True, encodeTitle = False, post = post)
	data = query.GetData(params, site = wikipedia.getSite(), encodeTitle = False)
	#print data
	try:
		# We don't know the page's id, if any other better idea please change it
		# THIS IS MY BETTER IDEA! ;)
		val = data[params['action']]
		if not values: return val
		if pages:
			pagedata = val[pages].values()
			val = []
			for item in pagedata:
				#print item
				entry = {}
				for val_item in values:	# pass all requested values
					if val_item in item: entry[val_item] = item[val_item]
				# pass special/important values
				if parent in item:	entry.update( item[parent][0] )
				if u'title' in item:	entry[u'title'] = item[u'title']
				#if u'missing' in item:	entry[u'missing'] = item[u'missing']
				if u'missing' in item:	entry[u'missing'] = u'missing'
				if u'redirect' in item:	entry[u'redirect'] = u'redirect'
				val.append( entry )
		else:
			while True:
				if parent in val: break
				val = val[ val.keys()[0] ]
			val = val[parent]
		#print val
		result = []
		for nickdata in val:
			#print nickdata
			#result.append( tuple([nickdata[item] for item in values]) )
			result.append( tuple([nickdata.get(item, None) for item in values]) )
		return result
	except KeyError:
		raise wikipedia.NoPage(u'API Error, nothing found in the APIs; %s'%str(sys.exc_info()))

