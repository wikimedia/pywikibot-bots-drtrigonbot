# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of pywikibot/exceptions.py.

...
"""
## @package dtbext.dtbext_pywikibot.dtbext_exceptions
#  @brief   Exception and traceback handling
#
#  @copyright Dr. Trigon, 2009-2011
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

## Standard library imports
import traceback, StringIO

# Application specific imports
#import config
import wikipedia as pywikibot


## @since   r95 (ADDED)
#  @remarks need for Bot Error Handling; to prevent bot errors to stop
#           execution of other bots
class BotError(pywikibot.Error):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


## @since   r95 (ADDED)
#  @remarks need for Bot Error Handling; get the error tracebacks without
#           raising the error
def gettraceback(exc_info):
	output = StringIO.StringIO()
	traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)

	exception_only = traceback.format_exception_only(exc_info[0], exc_info[1])

	result = output.getvalue()
	output.close()

	return (exception_only, result)

