# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of date.py.

...
"""
## @package dtbext.dtbext_date
#  @brief   Deviation of @ref date
#
#  @copyright Dr. Trigon, 2009-2010
#
#  @section FRAMEWORK
#
#  Python wikipedia robot framework, DrTrigonBot.
#  @see http://pywikipediabot.sourceforge.net/
#  @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
#  @section LICENSE
#
#  Distributed under the terms of the MIT license.
#  @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
__version__ = '$Id$'
#

# Standard library imports
import time, calendar

# Application specific imports
import config
import wikipedia as pywikibot


## @since   ? (ADDED)
#  @remarks need for some standard timestamp formats
def getTimeStmpNow(full = False, humanreadable = False, local = False):
#def getTimeStmpNow(full = True, humanreadable = False, local = False):	# framework default
	"""Produce different timestamp formats."""

	format = u"%Y%m%d"
	getter = time.gmtime

	if full: format += u"%H%M%S"

	if humanreadable:
		format = format.replace(u"%Y%m%d", u"%Y/%m/%d")
		format = format.replace(u"%H%M%S", u" %H:%M:%S")

	if local: getter = time.localtime

	# according to/taken from 'runbotrun.py'
	return time.strftime(format, getter())		

## @since   ? (ADDED)
#  @remarks need to convert wiki timestamp format to python
def getTime(timestamp, localized=True):
	"""Convert wiki timestamp to (localized) python format."""
	# thanks to: http://docs.python.org/library/time.html
	# http://www.mediawiki.org/wiki/API:Data_formats
	# http://www.w3.org/TR/NOTE-datetime
	# http://pytz.sourceforge.net/
	# use only UTC for internal timestamps
	# could also be used as given by the API, but is converted here for compatibility
	timestamp = pywikibot.Timestamp.fromISOformat(timestamp)
	if localized:
		# is localized to the actual date/time settings, cannot localize timestamps that are
		#    half of a year in the past or future!
		timestamp = pywikibot.Timestamp.fromtimestamp( calendar.timegm(timestamp.timetuple()) )
	return timestamp.strftime(u'%H:%M, %d. %b. %Y').decode(pywikibot.getSite().encoding())

