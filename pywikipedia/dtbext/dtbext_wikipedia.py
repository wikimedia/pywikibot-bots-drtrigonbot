# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of wikipedia.py and mainly subclasses
the page class from there.

...
"""
## @package dtbext.dtbext_wikipedia
#  @brief   Deviation of @ref wikipedia
#
#  @copyright Dr. Trigon, 2008-2010
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
pass
# Splitting the bot into library parts
from dtbext_pywikibot import *

# Application specific imports
import wikipedia as pywikibot
import query


## @since   r19 (ADDED)
#  @remarks needed to convert wikipedia.Page, Site ... objects to dtbext.dtbext_wikipedia.Page, Site, ... objects
def addAttributes(obj):
    """Add methods to various classes to convert them to the dtbext modified version."""
    # http://mousebender.wordpress.com/2007/02/17/copying-methods-in-python/
    # http://code.activestate.com/recipes/52192-add-a-method-to-a-class-instance-at-runtime/
    if "class 'wikipedia.Page'" in str(type(obj)):
        # this cannot be looped because of lambda's scope (which is important for page)
        # look also at http://www.weask.us/entry/scope-python-lambda-functions-parameters
        obj.__dict__['isRedirectPage']        = lambda *args, **kwds: Page.__dict__['isRedirectPage'](obj, *args, **kwds)


## @since   ? (MODIFIED)
#  @remarks (look below)
class Page(pywikibot.Page):
    """Page: A MediaWiki page

       look at wikipedia.py for more information!
    """

    ## @since   ? (MODIFIED)
    #  @remarks should be faster than original (look into re-write for something similar!)
    #  @remarks can be uncorrect (dangerous) according to xqt the database can contain invalid flags
    #           (http://lists.wikimedia.org/pipermail/pywikipedia-l/2011-September/006953.html)
    def isRedirectPage(self):
        """Return True if this is a redirect, False if not or not existing.
           MODIFIED METHOD: should be faster than original
        """

        # was there already a call? already some info available?
        if hasattr(self, '_getexception') and (self._getexception == pywikibot.IsRedirectPage):
            return True

        if hasattr(self, '_redir'):    # prevent multiple execute of code below,
            return self._redir         #  if page is NOT a redirect!

        # call the wiki to get info
        params = {
            u'action'  : u'query',
            u'titles'  : self.title(),
            u'prop'    : u'info',
            u'rvlimit' : 1,
        }

        pywikibot.get_throttle()
        pywikibot.output(u"Reading redirect info from %s." % self.title(asLink=True))

        result = query.GetData(params, self.site())
        r = result[u'query'][u'pages'].values()[0]

        # store and return info
        self._redir = (u'redirect' in r)
        if self._redir:
            self._getexception == pywikibot.IsRedirectPage

        return self._redir
