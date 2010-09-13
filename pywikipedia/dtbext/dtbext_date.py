
"""
This is a part of pywikipedia framework, it is a deviation of date.py.

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
__version__='$Id: dtbext/date.py 0.2.0019 2009-11-13 23:42 drtrigon $'
#

# Standard library imports
import time

# Application specific imports
import config, pywikibot


# ADDED
# REASON: need for some standard timestamp formats
def getTimeStmpNow(full = False, humanreadable = False, local = False):
	"""Produce different timestamp formats."""

	format = "%Y%m%d"
	getter = time.gmtime

	if full: format += "%H%M%S"

	if humanreadable:
		format = format.replace("%Y%m%d", "%Y/%m/%d")
		format = format.replace("%H%M%S", " %H:%M:%S")

	if local: getter = time.localtime

	# according to/taken from 'runbotrun.py'
	return time.strftime(format, getter())		

# ADDED
# REASON: need to convert wiki timestamp format to python
def getTime(timestamp):
	"""Convert wiki timestamp to python."""
	# thanks to: http://docs.python.org/library/time.html
	# http://www.mediawiki.org/wiki/API:Data_formats
	# http://www.w3.org/TR/NOTE-datetime
	# http://pytz.sourceforge.net/
	# use only UTC for internal timestamps
	# could also be used as given by the API, but is converted here for compatibility
	return pywikibot.Timestamp.fromISOformat(timestamp).strftime('%H:%M, %d. %b. %Y')

