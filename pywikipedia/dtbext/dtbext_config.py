# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of config.py.

...
"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: dtbext_config.py 0.2.0020 2009-11-14 11:54 drtrigon $'
#

# Standard library imports
import re

# Application specific imports
import wikipedia as pywikibot


REGEX_eol		= re.compile('\n')
#REGEX_subster_tag	= '<!--SUBSTER-%(var)s-->%(cont)s<!--SUBSTER-%(var)s-->'	# from 'subster.py'
REGEX_subster_tag	= '<!--SUBSTER-%(var)s-->'					#


# ADDED
# REASON: common interface to bot user settings on wiki
def getUsersConfig(page):
	"""Get user list from wiki page, e.g. [[Benutzer:DrTrigonBot/Diene_Mir!]].
	   ADDED METHOD: common interface to bot user settings on wiki

	   @param page: Wiki page containing user list and config.
	   @type  page: page

	   Returns a list with entries: (user, param)
	   This list may be empty.
	"""

	users = {}
	for item in REGEX_eol.split(page.get()):
		item = re.split(',', item, maxsplit=1)
		#print "A"
		if (len(item) > 1):	# for compatibility with 'subster.py' (if needed)
			#item[1] = re.compile((REGEX_subster_tag%{'var':'.*?','cont':'.*?'}), re.S | re.I).sub(u'', item[1])
			item[1] = re.compile((REGEX_subster_tag%{'var':'.*?'}), re.S | re.I).sub(u'', item[1])
		#print item
		try:	param = eval(item[1])
		except:	param = {}
		item = item[0]
		try:
			if not (item[0] == u'*'):	continue
		except:	continue
		item = item[1:]
		item = re.sub(u'\[', u'', item)
		item = re.sub(u'\]', u'', item)
		item = re.sub(u'Benutzer:', u'', item)
		subitem = re.split('\/', item)		# recognize extended user entries with ".../..."
		if len(subitem) > 1:			#  "
			param['userResultPage'] = item	# save extended user info (without duplicates)
			item = subitem[0]
		users[item] = param			# drop duplicates directly
	final_users = []								# geht auch noch kompakter!!
	for item in users.keys(): final_users.append( (item, users[item]) )	#

	return final_users

# ADDED
# REASON: common interface to bot job queue on wiki
def getJobQueue(page, queue_security, debug = False):
	"""Check if the data queue security is ok to execute the jobs,
	   if so read the jobs and reset the queue.
	   ADDED METHOD: common interface to bot job queue on wiki

	   @param page: Wiki page containing job queue.
	   @type  page: page
	   @param queue_security: This string must match the last edit
	                          comment, or else nothing is done.
	   @type  queue_security: string
	   @param debug: Parameter to prevent writing to wiki in debug mode.
	   @type  debug: bool

	   Returns a list of jobs. This list may be empty.
	"""

	try:	actual = page.getVersionHistory(revCount=1)[0]
	except:	pass

	secure = False
	for item in queue_security[0]:
	    secure = secure or (actual[2] == item)

	secure = secure and (actual[3] == queue_security[1])

	if not secure: return []

	data = REGEX_eol.split(page.get())
	if debug:
		pywikibot.setAction(u'reset job queue')
		page.put(u'', minorEdit = True)
	else:
		pywikibot.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

	queue = []
	for line in data:
		queue.append( line[1:].strip() )
	return queue

