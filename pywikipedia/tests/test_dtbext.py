# -*- coding: utf-8 -*-

# This test script is intended to be used with mature unittest code.
#
# This script contains important unittests in order to ensure the function
# and stability of core dtbext (DrTrigonBot framework) code and methods.
# You should not change code here except you want to add a new test case
# for a function, mechanism or else.

import unittest
import sys


import time


import test_utils

import dtbext

import pagegenerators, catlib
import userlib
import botlist
# Splitting the bot into library parts
import wikipedia as pywikibot


site = pywikibot.getSite()


# http://docs.python.org/library/unittest.html
class TestModuleImports(unittest.TestCase):
  def test_MI_framework(self):
    self.assertTrue( "pagegenerators" in sys.modules )
    self.assertTrue( "catlib" in sys.modules )
    self.assertTrue( "userlib" in sys.modules )
    self.assertTrue( "pywikibot" in sys.modules )
    self.assertTrue( "botlist" in sys.modules )
    # ... (e.g. sub modules, ...)

  def test_MI_dtbext(self):
    self.assertTrue( "dtbext" in sys.modules )
    # ...

  def test_MI_botlist(self):
    bots = botlist.get()
    self.assertTrue( len(bots) > 0 )    # check if there is at least one bot in list
    print "Number of bots total:", len(bots)

  def test_MI_addAttributes(self):
    site = pywikibot.getSite()
    self.assertTrue( hasattr(site, "getParsedString") )  # how to check if callable???
    site.getParsedString(TESTBUFFER)                     #


class TestWorkerFunction(unittest.TestCase):
  def test_WF_getSections(self):
    #print "\nTest of 'dtbext.pywikibot.Page.getSections()' on page '%s'..." % TESTPAGE
    #
    ##page = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    page = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    dtbext.pywikibot.addAttributes(page)
    buf = page.get()
    #buf = page.get(mode='full')
    ##buf = page.getFullB()[:1000]
    #print buf

    print "\nTest of 'dtbext.pywikibot.Pages.getSections()' on page '%s'..." % TESTPAGE

    #page = dtbext.pywikibot.Pages(pywikibot.getSite(), [TESTPAGE])
    ##buf = page.get()
    #buf = [data for (page, data) in page.get(mode='full')][0]
    ##buf = [data for (page, data) in page.get()][0]

    #pageAPI = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #(sections, test) = pageAPI.getSections(minLevel=1)
    #(sections, test) = page.getSections(minLevel=1, getter=page.get)
    #(sections, test) = page.getSections(minLevel=1, getter=page._getFullContent)
    sections = page.getSections(minLevel=1)
    #sections = page.getSections(minLevel=1, force=True)
    #(sections, test) = page.getSections()

    #print "*"
    #for item in sections:
    #  print buf[item[0]]
    #  print "*"

    #head = []
    #body = []
    #body_part = []
    #actual_head = sections.pop(0)
    #for i in range(len(buf)):
    #  item = buf[i]
    #  if (i == actual_head[0]):
    #    body.append( u'\n'.join(body_part) )
    #    body_part = []
    #    head.append( item )
    #    try:	actual_head = sections.pop(0)
    #    except:	actual_head = (len(buf)+1,)
    #  else:
    #    body_part.append( item )
    #body.append( u'\n'.join(body_part) )
    #body.pop(0)
    #print head
    #print body[0]

    for item in sections:
      #print item[2:4]
      print item
    #print sections[-3], len(sections[-3][2]),len(sections[-3][3])

    #print "\n'Pages.getSections()' self-test: %s" % test
    #
    #page = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #print page.getSections()
    ##pages = dtbext.pywikibot.Pages(pywikibot.getSite(), TESTPAGES*5)
    ##a = pages.getSections()
    ##print len(TESTPAGES*5), len(a), a

  def test_WF_getParsedContent(self):
    print "\nTest of 'dtbext.pywikibot.Page.getParsedContent()' on page '%s'..." % TESTPAGE

    #print dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE).get(mode='parse')
    #print dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE).get(mode='parse', plaintext=True)

    site = pywikibot.getSite()
    print "*", site.getParsedString(u'Erweiterung für [[Wikipedia:Bots/Bot-Info]]', keeptags = []), "*"

  def test_WF_purgeCache(self):
    print "\nTest of 'dtbext.pywikibot.Page.purgeCache()' on page '%s'..." % TESTPAGE
    
    res = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE).purgeCache()
    self.assertEqual( res, True )
    print res

  def test_WF_globalnotifications(self):
    print "\nTest of 'dtbext.userlib.globalnotifications()' on page '%s'..." % TESTPAGE

    user = userlib.User(pywikibot.getSite(), u'DrTrigon')
    dtbext.userlib.addAttributes(user)
    for (page, data) in user.globalnotifications():
      print page
      print data
      #print item.globalwikinotify
      print

  def test_WF_getVersionHistory(self):
    #print "\nTest of 'pywikibot.Page.getVersionHistory()' on page '%s'..." % TESTPAGE
    #
    #for item in TESTPAGES:
    #  site = pywikibot.Page(pywikibot.getSite(), item)
    #  print site.getVersionHistory(revCount=1)
    #
    #print "\nTest of 'dtbext.pywikibot.Page.getVersionHistory()' on page '%s'..." % TESTPAGE

    #for item in TESTPAGES:
    #  site = dtbext.pywikibot.Page(pywikibot.getSite(), item)
    #  print site.getVersionHistory(revCount=1)
    site = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    print site.getVersionHistory(revCount=1)
    print site.isRedirectPage()

  def test_WF_PreloadingGenerator(self):
    #print "\nTest of 'dtbext.pywikibot.Pages.get()' on '%i' page(s)..." % len(TESTPAGES)
    print "\nTest of sequence:"
    print "   PagesFromTitlesGenerator ->"
    print "   (PageTitleFilterPageGenerator) ->"
    print "   PreloadingGenerator ->"
    print "   [output]"
    print

    TESTPAGES.append( TESTPAGE )

    ignore_list = { pywikibot.getSite().family.name: { pywikibot.getSite().lang: [u'Benutzer Diskussion:DrTrigonBo'] }}
    #ignore_list = { pywikibot.getSite().family.name: { pywikibot.getSite().lang: [] }}

    # !!! ATTENTION PROBLEM HERE: xqt says API call can loose pages !!!
    gen        = pagegenerators.PagesFromTitlesGenerator(TESTPAGES)
    filter_gen = pagegenerators.PageTitleFilterPageGenerator(gen, ignore_list)	# or RegexFilterPageGenerator
    prload_gen = pagegenerators.PreloadingGenerator(filter_gen)			# ThreadedGenerator would be nice!
    #pywikibot.debug = debug		# to enable the use of the API here (seams to be slower... ?!?)
    for page in prload_gen:
      print page

      start = time.time()
      u = page.get()
      stop = time.time()
      buffd = stop-start
      self.assertAlmostEqual( buffd, 0., places=3 )

      start = time.time()
      u = page.getVersionHistory(revCount=1)
      stop = time.time()
      buffd2 = stop-start
      self.assertAlmostEqual( buffd2, 0., places=4 )

      dtbext.pywikibot.addAttributes(page)
      start = time.time()
      u = page.getSections(minLevel=1)
      stop = time.time()
      unbuffd3 = stop-start

      start = time.time()
      u = page.getSections(minLevel=1)
      stop = time.time()
      buffd3 = stop-start
      self.assertAlmostEqual( buffd3, 0., places=4 )

      start = time.time()
      u = page.get(force=True)  # triggers reload of 'getSections' also
      stop = time.time()
      unbuffd = stop-start

      start = time.time()
      u = page.getVersionHistory(revCount=1, forceReload=True)
      #print u
      stop = time.time()
      unbuffd2 = stop-start

      print "GET; buffered:", buffd, "\t", "unbuffered:", unbuffd
      print "GETVERSIONHISTORY; buffered:", buffd2, "\t", "unbuffered:", unbuffd2
      print "GETSECTIONS; buffered:", buffd3, "\t", "unbuffered:", unbuffd3
    pywikibot.debug = False

  def test_WF_get(self):
    print "\nTest of 'dtbext.pywikibot.Page.get()' on [[%s]]..." % TESTPAGE

    page = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #page.getVersionHistory()

    page.extradata = "hallo"
    print page.title()
    print page.extradata
    self.assertEqual( page.extradata, "hallo" )
    #page.get()
    #page.getVersionHistory(revCount=1)
    #page.isRedirectPage()


#TESTPAGE = u'Benutzer:DrTrigonBot/ToDo-Liste'
TESTPAGE = u'Benutzer:DrTrigon'
#TESTPAGE = u'Wikipedia:Verbesserungsvorschläge'
#TESTPAGE = u'Wikipedia:Fragen zur Wikipedia'
#TESTPAGE = u'Benutzer Diskussion:Meisterkoch'
#TESTPAGE = u'Benutzer Diskussion:Drdoht'
#TESTPAGE = u'Benutzer Diskussion:Borusse86'
#TESTPAGE = u'Diskussion:Legendresche Vermutung'
#TESTPAGE = u'Diskussion:Entziehung Minderjähriger'
#TESTPAGE = u'Wikipedia Diskussion:Namenskonventionen'
#TESTPAGE = u'Wikipedia:Redaktion Medizin/Liste bedeutender Mediziner und Ärzte'
#TESTPAGE = u'Wikipedia:Qualitätssicherung/28. November 2008'
#TESTPAGE = u'Hilfe_Diskussion:Weiterleitung'
#TESTPAGE = u'Benutzer Diskussion:BitH'
#TESTPAGE = u'Diskussion:Amoklauf in Winnenden'
#TESTPAGE = u'Wikipedia:Löschkandidaten/20. Juni 2009'
#TESTPAGE = u'Diskussion:C++/Archiv/2008'
#TESTPAGE = u'Benutzer Diskussion:Andre Kaiser'
#TESTPAGE = u'Benutzer_Diskussion:Raymond'
#TESTPAGE = u'Wikipedia:WikiProjekt Begriffsklärungsseiten/Arbeitslisten/Botomatic'
#TESTPAGE = u'Diskussion:Arbeitnehmerüberlassung'
#TESTPAGE = u'Benutzer Diskussion:DrTrigonBot'
#TESTPAGE = u'Benutzer Diskussion:FalkOberdorf'
#TESTPAGE = u'Vorlage Diskussion:Infobox Gemeinde in Deutschland'
#TESTPAGE = u'Wikipedia:WikiProjekt Begriffsklärungsseiten/Arbeitslisten/NeueVerlinkteBKS'
#TESTPAGE = u'Wikipedia:WikiProjekt Marxismus/Kandidaturen und Reviews'
#TESTPAGE = u'Wikipedia:WikiProjekt Schweiz/Wartung/Worklists'
TESTPAGE = u'Wikipedia:Testseite'

TESTPAGE = u'Wikipedia:Löschkandidaten/20. Juli 2009'
TESTPAGE = u'Benutzer Diskussion:Karsten11'
TESTPAGE = u'Benutzer Diskussion:GregorHelms'
TESTPAGE = u'Wikipedia:WikiProjekt Vorlagen/Werkstatt'
#TESTPAGE = u'Benutzer_Diskussion:DrTrigonBot'
TESTPAGE = u'Benutzer_Diskussion:DrTrigon'
TESTPAGE = u'Wikipedia Diskussion:WikiProjekt Portale/Baustelle/Portal:Biochemie'
TESTPAGE = u'Portal:Serbien/Artikelwunsch'
TESTPAGE = u'Wikipedia:Auskunft'
TESTPAGE = u'Benutzer Diskussion:MerlBot/Vermutlich verstorben'

TESTPAGES = [	u'Hilfe Diskussion:Weiterleitung',
		u'Benutzer Diskussion:BitH',
		u'Benutzer Diskussion:DrTrigonBot',
		u'Benutzer Diskussion:DrTrigonBo', ]

TESTBUFFER = u"""
{{Archiv|Wikipedia Diskussion:WikiProjekt Einsatzorganisationen}}

== {{Vorlage|BW-EO}} ==

Auf [[Wikipedia:Redaktion Bilder/Arbeitsliste]] gibt es eine sehr lange Liste von so markieren Bildern. Aber auf [[Wikipedia:WikiProjekt Einsatzorganisationen/Bilderwerkstatt]] findet sich die Bilder nicht wieder. Zudem scheint die Seite inaktiv. Sollte man den Baustein nicht besser löschen, da er nicht mehr genutzt wird? [[Benutzer:Merlissimo/Sig|Merl]][[Benutzer Diskussion:Merlissimo/Sig|issimo]] 14:53, 17. Jan. 2010 (CET)
:Ja, Bapperl kann weg - zusammen mit der Werkstatt-Seite. Kümmert sich ja keiner drum. [[Benutzer:Jiver|Jiver]] 00:22, 18. Jan. 2010 (CET)
:: Da würde ich mich anschließen, da sie sowieso nicht genutzt wird. -- [[Benutzer:Apfel3748|Apfel3748]] <sup>[[Benutzer Diskussion:Apfel3748|Diskussion]]</sup> 16:29, 18. Jan. 2010 (CET)
:::jepp --[[Benutzer:Schmendrik881|Schmendi]] [[Benutzer_Diskussion:Schmendrik881|sprich]] 16:31, 18. Jan. 2010 (CET)
::::Ok, ich markiere die Vorlage als veraltet und kümmere mich morgen um die Entlinkung. Ist ja ein eindeutiges Portalvortum. [[Benutzer:Merlissimo/Sig|Merl]][[Benutzer Diskussion:Merlissimo/Sig|issimo]] 16:47, 18. Jan. 2010 (CET)
:::::{{erl.}} entlinkt, WL {{Vorlage|Projekt BEO}} ebenfalls --&nbsp;<small>[[Benutzer Diskussion:Xqt|@]]</small>[[Benutzer:Xqt|xqt]] 06:39, 19. Jan. 2010 (CET)
== Artikel [[Einsatzorganisation]] ==

fällt mir auf, dass es diesen artikel noch gar nicht gibt und dennoch schmeisst ihr bereits ein ganzes projekt ;-) -- [[Benutzer:Saltose|Saltose]] 18:34, 4. Feb. 2010 (CET)
:Das ist eine lange Geschichte.... :-) Gruß --[[Benutzer:Schmendrik881|Schmendi]] [[Benutzer_Diskussion:Schmendrik881|sprich]] 18:37, 4. Feb. 2010 (CET)
"""


if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestModuleImports)
  unittest.TextTestRunner(verbosity=2).run(suite)

  #suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkerFunction)
  suite = unittest.TestSuite()
  # wikipedia.py
  dtbext.pywikibot.debug = True
  #suite.addTest(TestWorkerFunction('test_WF_getVersionHistory'))
  #suite.addTest(TestWorkerFunction('test_WF_getSections'))
  #suite.addTest(TestWorkerFunction('test_WF_purgeCache'))
  #suite.addTest(TestWorkerFunction('test_WF_get'))
  #suite.addTest(TestWorkerFunction('test_WF_getParsedContent'))
  #print pywikibot.getSite().getUrl('/w/api.php?action=query&meta=userinfo&uiprop=blockinfo|hasmsg|groups|rights|options|preferencestoken|editcount|ratelimits|email&formal=xml')
  #suite.addTest(TestWorkerFunction('test_WF_globalnotifications'))
  #pywikibot.debug = True
  #suite.addTest(TestWorkerFunction('test_WF_PreloadingGenerator'))
  #suite.addTest(TestWorkerFunction('test_WF_VersionHistoryGenerator'))
  unittest.TextTestRunner(verbosity=2).run(suite)
