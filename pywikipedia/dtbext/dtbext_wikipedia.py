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
        obj.__dict__['purgeCache']            = lambda *args, **kwds: Page.__dict__['purgeCache'](obj, *args, **kwds)
        obj.__dict__['userNameHuman']         = lambda *args, **kwds: Page.__dict__['userNameHuman'](obj, *args, **kwds)
        obj.__dict__['append']                = lambda *args, **kwds: Page.__dict__['append'](obj, *args, **kwds)


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

    ## @since   ? (ADDED; non-api purge can be done with wikipedia.Page.purge_address())
    #  @remarks needed by various bots
    def purgeCache(self):
        """Purges the page cache with API.
           ADDED METHOD: needed by various bots
        """

        # Make sure we re-raise an exception we got on an earlier attempt
        if hasattr(self, '_getexception'):
            return self._getexception

        # call the wiki to execute the request
        params = {
            u'action'    : u'purge',
            u'titles'    : self.title(),
        }

        pywikibot.get_throttle()
        pywikibot.output(u"Purging page cache for %s." % self.title(asLink=True))

        result = query.GetData(params, self.site())
        r = result[u'purge'][0]

        # store and return info
        if (u'missing' in r):
                self._getexception = pywikibot.NoPage
                raise pywikibot.NoPage(self.site(), self.title(asLink=True),"Page does not exist. Was not able to purge cache!" )

        return (u'purged' in r)

    ## @since   r24 (ADDED)
    #  @remarks needed by various bots
    def userNameHuman(self):
        """Return name or IP address of last human/non-bot user to edit page.
           ADDED METHOD: needed by various bots

           Returns the most recent human editor out of the last revisions
           (optimal used with getAll()). If it was not able to retrieve a
           human user returns None.
        """

        # was there already a call? already some info available?
        if hasattr(self, '_userNameHuman'):
            return self._userNameHuman

        # get history (use preloaded if available)
        (revid, timestmp, username, comment) = self.getVersionHistory(revCount=1)[0][:4]

        # is the last/actual editor already a human?
        import botlist # like watchlist
        if not botlist.isBot(username):
            self._userNameHuman = username
            return username

        # search the last human
        self._userNameHuman = None
        for vh in self.getVersionHistory()[1:]:
            (revid, timestmp, username, comment) = vh[:4]

            if username and (not botlist.isBot(username)):
                # user is a human (not a bot)
                self._userNameHuman = username
                break

        # store and return info
        return self._userNameHuman

    ## @since   r49 (ADDED)
    #  @remarks to support appending to single sections
    #
    #  @todo    submit upstream and include into framework, maybe in wikipedia.Page.put()
    #           (this function is very simple and not mature/worked out yet, has to be completed)
    #           \n[ JIRA: ticket? ]
    def append(self, newtext, comment=None, minorEdit=True, section=0):
        """Append the wiki-text to the page.
           ADDED METHOD: to support appending to single sections

           Returns the result of text append to page section number 'section'.
           0 for the top section, 'new' for a new section.
        """

        # If no comment is given for the change, use the default
        comment = comment or pywikibot.action

        # send mail by POST request
        params = {
            'action'     : 'edit',
            #'title'      : self.title().encode(self.site().encoding()),
            'title'      : self.title(),
            'section'    : '%i' % section,
            'appendtext' : self._encodeArg(newtext, 'text'),
            'token'      : self.site().getToken(),
            'summary'    : self._encodeArg(comment, 'summary'),
            'bot'        : 1,
            }

        if minorEdit:
            params['minor'] = 1
        else:
            params['notminor'] = 1

        response, data = query.GetData(params, self.site(), back_response = True)

        if not (data['edit']['result'] == u"Success"):
            raise PageNotSaved('Bad result returned: %s' % data['edit']['result'])

        return response.code, response.msg, data
