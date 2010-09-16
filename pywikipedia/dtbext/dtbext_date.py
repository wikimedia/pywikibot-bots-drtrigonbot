# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of date.py.

...
"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: dtbext_date.py 0.2.0022 2009-11-15 21:13 drtrigon $'
#

# Standard library imports
import time

# Application specific imports
import config
import wikipedia as pywikibot


# ADDED
# REASON: need for some standard timestamp formats
def getTimeStmpNow(full = False, humanreadable = False, local = False):
#def getTimeStmpNow(full = True, humanreadable = False, local = False):	# framework default
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

