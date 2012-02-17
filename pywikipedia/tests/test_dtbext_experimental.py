# -*- coding: utf-8 -*-

# This test script is intended to be used with EXPERIMENTAL code.
#
# You can add, remove or modify the code in here more or less freely
# to test what ever you need to test... enjoy!

import test_utils

from test_dtbext import *

import dtbext

import pagegenerators, catlib
import userlib
# Splitting the bot into library parts
import wikipedia as pywikibot


# 'TESTPAGE', 'TESTPAGES', ... imported from 'test_dtbext.py'


if __name__ == '__main__':
    site = pywikibot.getSite()

    #a_str = r'<strong class="error">Referenz-Fehler: Einzelnachweisfehler: <code>&lt;ref&gt;</code>-Tags existieren, jedoch wurde kein <code>&lt;references&#160;/&gt;</code>-Tag gefunden.</strong>'
    #site = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #buf = site.get(mode='parse')
    #import re
    #if re.search(a_str, buf): print "<references />-Tag Fehler"

    #print userlib.User(pywikibot.getSite(), u'º_the_Bench_º')

#    # test_MI_botlist - further investigation on: botlist.get #
#    bots = botlist.get()
#    print bots
#    print len(bots)

#    # test_FS_getSections - further investigation on: getSections #
#    TESTPAGE = PAGE_SET_test_FS_getSections[1]
#    page = pywikibot.Page(site, TESTPAGE)
#    dtbext.pywikibot.addAttributes(page)
#    sections = page.getSections(minLevel=1)
#    for s in sections:
#        print s

#    #print site.cookies()
#    print 'loggedInAs: %s' % site.loggedInAs()
#    external_buffer = site.getUrl(u'http://aniki.info/Special:Statistics', no_hostname = True)
#    print 'loggedInAs: %s' % site.loggedInAs()
#    if site.loggedInAs() is None:
#        site._load(force=True)
#    print 'loggedInAs: %s' % site.loggedInAs()
#
#    print '-' * 20
#
#    from pywikibot.comms import http
#    print 'loggedInAs: %s' % site.loggedInAs()
#    external_buffer = http.request(site, u'http://aniki.info/Special:Statistics', no_hostname = True)
#    print 'loggedInAs: %s' % site.loggedInAs()

    print site.getParsedString("{{CURRENTTIMESTAMP}}")
    print site.getExpandedString("{{CURRENTTIMESTAMP}}")
