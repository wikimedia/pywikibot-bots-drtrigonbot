
"""
This is a part of pywikipedia framework, it is a deviation of config.py.

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
__version__='$Id: dtbext/config.py 0.2.0000 2009-08-26 15:54:00Z drtrigon $'
#

# Standard library imports
import re

# Application specific imports
import wikipedia


REGEX_eol		= re.compile('\n')


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

def getUsersConfig(page):
	'''
	get user list from [[Benutzer:DrTrigonBot/Diene_Mir!]]

	input:  page [page]
                self-objects
	returns:  [list] for use as iterator e.g.
	          format:    (user, param) [tuple]
	'''

	users = {}
	for item in REGEX_eol.split(page.get()):
		item = re.split(',', item, maxsplit=1)
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

def getJobQueue(page, queue_security, debug = False):
	'''
	check if the data queue security is ok to execute the jobs, if so read the jobs and reset the queue

	returns:  job queue [list]
	'''

	try:	actual = page.getVersionHistory(revCount=1)[0]
	except:	pass

	secure = False
	for item in queue_security[0]:
	    secure = secure or (actual[2] == item)

	secure = secure and (actual[3] == queue_security[1])

	if not secure: return []

	data = REGEX_eol.split(page.get())
	if debug:
		wikipedia.setAction(u'reset job queue')
		page.put(u'', minorEdit = True)
	else:
		wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

	queue = []
	for line in data:
		queue.append( line[1:].strip() )
	return queue

