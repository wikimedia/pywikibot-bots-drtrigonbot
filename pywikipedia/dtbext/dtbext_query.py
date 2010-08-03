
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
#  exists in pywikipedia-framework
# ====================================================================================================

def GetData(params, site = None, verbose = False, useAPI = False, retryCount = 5, encodeTitle = True, post = False):
	"""Get data from the query api, and convert it into a data object
	"""
	# 'verbose' is useless now
	if post:
		# according to 'query.py' (minimalized) with 'postForm' instead of 'getUrl'
		if site is None:
			site = wikipedia.getSite()

		params['format'] = 'json'

		#if useAPI:
		#	path = site.api_address() + urllib.urlencode(params.items())
		#else:
		#	path = site.query_address() + urllib.urlencode(params.items())
		# updated with new framework to support 'emailuser' and 'edit' correct
		postAC = [
			'edit', 'login', 'purge', 'rollback', 'delete', 'undelete', 'protect', 'parse',
			'block', 'unblock', 'move', 'emailuser','import', 'userrights', 'upload',
		]
		if useAPI:
			if params['action'] in postAC:
				path = site.api_address()
				cont = ''
			else:
				path = site.api_address() + site.urlEncode(params.items())
		else:
			path = site.query_address() + site.urlEncode(params.items())

		# (according to 'GetData()' in 'query.py')
		lastError = None
		retry_idle_time = 5
		while retryCount >= 0:
			try:
				jsontext = "Nothing received"
				params = dict([ (val, str(params[val])) for val in params ])
				(response, jsontext) = site.postForm(path, params)

				# This will also work, but all unicode strings will need to be converted from \u notation
				# decodedObj = eval( jsontext )
				return simplejson.loads( jsontext )

			except ValueError, error:
				retryCount -= 1
				wikipedia.output(u"Error downloading data: %s" % error)
				wikipedia.output(u"Request %s:%s" % (site.lang, path))
				wikipedia.debugDump('ApiGetDataParse', site, str(error) + '\n%s' % path, jsontext)
				lastError = error
				if retryCount >= 0:
					wikipedia.output(u"Retrying in %i seconds..." % retry_idle_time)
					time.sleep(retry_idle_time)
					# Next time wait longer, but not longer than half an hour
					retry_idle_time *= 2
					if retry_idle_time > 300:
						retry_idle_time = 300

		raise lastError
	else:
		return query.GetData(params, site = site, useAPI = useAPI, retryCount = retryCount, encodeTitle = encodeTitle)


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

def GetProcessedData(params, parent, content, values, pages = None, post = False):
	# to be able to catch error messages
	if values and ('missing' not in values): values.append( 'missing' )

	#data = query.GetData(params, useAPI = True, encodeTitle = False)
	data = GetData(params, useAPI = True, encodeTitle = False, post = post)
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

