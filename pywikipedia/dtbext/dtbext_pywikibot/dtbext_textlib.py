# -*- coding: utf-8  -*-
"""
This is a part of pywikipedia framework, it is a deviation of pywikibot/textlib.py.

...
"""
## @package dtbext.dtbext_pywikibot.dtbext_textlib
#  @brief   Deviation of pywikibot.textlib
#
#  @copyright Dr. Trigon, 2010
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


#--------------------------------------------
# Functions dealing with interwiki links
#--------------------------------------------

## @since   r165 (ADDED)
#  @remarks needed by various bots
def dblink2wikilink(site, dblink):
    """Return interwiki link to page.

    You can use DB links like used on the toolserver and convert
    them to valid interwiki links.
    """

    link = dblink
    for family in site.fam().get_known_families(site).values():
        title = link.replace(u'%s:' % family.decode('unicode_escape'), u':')    # e.g. 'dewiki:...' --> 'de:...'
        if not (title == link):
            dblink = u'%s:%s' % (family, title)
            # [ 'wiki' in framework/interwiki is not the same as in TS DB / JIRA: DRTRIGON-60 ]
            dblink = dblink.replace(u'wiki:', u'')  # may be better to use u'wikipedia:' or u'w:'

    return dblink
