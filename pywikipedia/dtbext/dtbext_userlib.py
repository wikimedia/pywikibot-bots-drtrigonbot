
"""
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
__version__='$Id: dtbext/userlib.py 0.2.0001 2009-12-17 21:51:00Z drtrigon $'
#

# Application specific imports
import wikipedia, userlib, config, query
import dtbext_query, dtbext_date

class User(userlib.User):
	"""
	A class that represents a Wiki user.
	Has getters for the user's User: an User talk: (sub-)pages,
	as well as methods for blocking and unblocking.
	"""

	#def __init__(self, site, name):

	def getGroups(self, userCount=1):
		"""
		Returns the groups this user is a member of.
		"""

		request = {
		    'action'	: 'query',
		    'list'	: 'allusers',
		    'aufrom'	: self.name,
		    'aulimit'	: userCount,
		    'auprop'	: 'blockinfo|groups|editcount|registration',
		    }
		wikipedia.get_throttle()
		buf = dtbext_query.GetProcessedData(request,
							'allusers',
							'u',
							['name', 'blockedby', 'blockreason', 'editcount', 'registration', 'groups'])

		result = []
		for item in buf:
			(name, blockedby, blockreason, editcount, registration, groups, add) = item
			result.append( groups )

		if (userCount == 1): result = result[0]

		return result

