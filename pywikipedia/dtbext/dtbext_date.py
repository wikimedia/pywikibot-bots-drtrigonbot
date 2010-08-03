
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
__version__='$Id: dtbext/date.py 0.2.0000 2009-08-26 15:54:00Z drtrigon $'
#

# Standard library imports
import time
import xml.utils.iso8601

# Application specific imports
import config


# ====================================================================================================
#  DOES NOT exist in pywikipedia-framework
# ====================================================================================================

def getTimeStmp(full = False, humanreadable = False, local = False):
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

######## Unicode library functions ########

# thanks to: http://docs.python.org/library/time.html
# http://www.mediawiki.org/wiki/API:Data_formats
# http://www.w3.org/TR/NOTE-datetime
# http://pytz.sourceforge.net/
def GetTime(timestamp):
	# use only UTC for internal timestamps
	# could also be used as given by the API, but is converted here for compatibility
	secs = xml.utils.iso8601.parse(timestamp)
	return time.strftime('%H:%M, %d. %b. %Y', time.gmtime(secs)).decode(config.textfile_encoding)

