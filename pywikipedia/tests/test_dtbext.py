# -*- coding: utf-8 -*-

# This test script is intended to be used with mature unittest code.
#
# This script contains important unittests in order to ensure the function
# and stability of core dtbext (DrTrigonBot framework) code and methods.
# You should not change code here except you want to add a new test case
# for a function, mechanism or else.

import unittest
import __main__


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
    self.assertTrue( "pagegenerators" in __main__.__dict__ )
    self.assertTrue( "catlib" in __main__.__dict__ )
    self.assertTrue( "userlib" in __main__.__dict__ )
    self.assertTrue( "pywikibot" in __main__.__dict__ )
    self.assertTrue( "botlist" in __main__.__dict__ )
    # ... (e.g. sub modules, ...)

  def test_MI_dtbext(self):
    self.assertTrue( "dtbext" in __main__.__dict__ )
    # ...

  def test_MI_botlist(self):
    bots = botlist.get()
    self.assertTrue( len(bots) > 0 )    # check if there is at least one bot in list
    print "Number of bots total:", len(bots)

  def test_WF_addAttributes(self):
    site = pywikibot.getSite()
    dtbext.pywikibot.addAttributes( site )
    self.assertTrue( hasattr(site, "getParsedString") )  # how to check if callable???
    site.getParsedString(TESTBUFFER)                     #

    page = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #print page.getSections()
    dtbext.pywikibot.addAttributes( page )
    self.assertTrue( hasattr(page, "getSections") )
    page.getSections()

    page2 = pywikibot.Page(pywikibot.getSite(), u'Benutzer Diskussion:Karsten11')
    #print page.getSections()
    dtbext.pywikibot.addAttributes( page2 )
    self.assertTrue( hasattr(page, "getSections") )
    page2.getSections()


class TestFunctionStability(unittest.TestCase):
  def test_FS_getSections(self):
    self.assertEqual( len(PAGE_SET_test_FS_getSections), 137 )
    count = 0
    problems = []
    for i, TESTPAGE in enumerate(PAGE_SET_test_FS_getSections):
      page = pywikibot.Page(site, TESTPAGE)
      dtbext.pywikibot.addAttributes(page)
      try:
        sections = page.getSections(minLevel=1)
      except pywikibot.exceptions.Error:
        count += 1
        problems.append( (i, page) )
    print "Number of pages total:", len(PAGE_SET_test_FS_getSections)
    print "Number of problematic pages:", count
    #print "Problematic pages:", problems
    print "Problematic pages:\n", "\n".join( map(str, problems) )
    #self.assertLessEqual( count, 4 )
    self.assertTrue( count <= 4 )

    return

class TestWorkerFunction(unittest.TestCase):
  def test_WF_getSections(self):
    #print "\nTest of 'dtbext.pywikibot.Page.getSections()' on page '%s'..." % TESTPAGE
    #
    ##site = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    site = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    dtbext.pywikibot.addAttributes(site)
    buf = site.get()
    #buf = site.get(mode='full')
    ##buf = site.getFullB()[:1000]
    #print buf

    print "\nTest of 'dtbext.pywikibot.Pages.getSections()' on page '%s'..." % TESTPAGE

    #site = dtbext.pywikibot.Pages(pywikibot.getSite(), [TESTPAGE])
    ##buf = site.get()
    #buf = [data for (site, data) in site.get(mode='full')][0]
    ##buf = [data for (site, data) in site.get()][0]

    #siteAPI = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #(sections, test) = siteAPI.getSections(minLevel=1)
    #(sections, test) = site.getSections(minLevel=1, getter=site.get)
    #(sections, test) = site.getSections(minLevel=1, getter=site._getFullContent)
    sections = site.getSections(minLevel=1)
    #sections = site.getSections(minLevel=1, force=True)
    #(sections, test) = site.getSections()

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
    #site = dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE)
    #print site.getSections()
    ##sites = dtbext.pywikibot.Pages(pywikibot.getSite(), TESTPAGES*5)
    ##a = sites.getSections()
    ##print len(TESTPAGES*5), len(a), a

  def test_WF_getParsedContent(self):
    print "\nTest of 'dtbext.pywikibot.Page.getParsedContent()' on page '%s'..." % TESTPAGE

    #print dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE).get(mode='parse')
    #print dtbext.pywikibot.Page(pywikibot.getSite(), TESTPAGE).get(mode='parse', plaintext=True)

    site = pywikibot.getSite()
    dtbext.pywikibot.addAttributes( site )
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
    for item in user.globalnotifications():
      print item
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

  def test_WF_VersionHistoryGenerator(self):
    print "\nTest of 'dtbext.pagegenerators.VersionHistoryGenerator()' on '%i' page(s)..." % len(TESTPAGES)

    gen = dtbext.pagegenerators.VersionHistoryGenerator(TESTPAGES)
    for item in gen:
      print item[1:]
      #print item, a[item], ('redirect' in a[item][0])

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
      self.assertAlmostEqual( buffd, 0. )

      start = time.time()
      u = page.getVersionHistory(revCount=1)
      dtbext.pywikibot.addAttributes(page)
      print page.getSections(minLevel=1)
      #print u
      stop = time.time()
      buffd2 = stop-start
      self.assertAlmostEqual( buffd2, 0. )

      start = time.time()
      u = page.get(force=True)
      stop = time.time()
      unbuffd = stop-start

      start = time.time()
      u = page.getVersionHistory(revCount=1, forceReload=True)
      #print u
      stop = time.time()
      unbuffd2 = stop-start

      print "GET; buffered:", buffd, "\t", "unbuffered:", unbuffd
      print "GETVERSIONHISTORY; buffered:", buffd2, "\t", "unbuffered:", unbuffd2
    pywikibot.debug = False

#  def test_WF_addAttributes(self):
#    site = pywikibot.getSite()
#    dtbext.pywikibot.addAttributes( site )
#    print site.getParsedString(TESTBUFFER)
#
#    page = pywikibot.Page(pywikibot.getSite(), TESTPAGE)
#    #print page.getSections()
#    dtbext.pywikibot.addAttributes( page )
#    print page.getSections()
#
#    page2 = pywikibot.Page(pywikibot.getSite(), u'Benutzer Diskussion:Karsten11')
#    #print page.getSections()
#    dtbext.pywikibot.addAttributes( page2 )
#    print page2.getSections()
#    print page.getSections()

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


PAGE_SET_test_FS_getSections = [
u'Benutzer Diskussion:Reiner Stoppok/Dachboden',
u'Wikipedia:Löschkandidaten/12. Dezember 2009',
u'Wikipedia:Löschkandidaten/28. Juli 2006',
u'Wikipedia Diskussion:Persönliche Bekanntschaften/Archiv/2008',
u'Wikipedia:WikiProjekt München',
u'Wikipedia Diskussion:Hauptseite',
u'Diskussion:Selbstkühlendes Bierfass',
u'Benutzer Diskussion:P.Copp',
u'Benutzer Diskussion:David Ludwig',
u'Diskussion:Zufall',
u'Benutzer Diskussion:Dekator',
u'Benutzer Diskussion:Bautsch',
u'Benutzer Diskussion:Henbeu',
u'Benutzer Diskussion:Olaf Studt',
u'Diskussion:K.-o.-Tropfen',
u'Portal Diskussion:Fußball/Archiv6',
u'Benutzer Diskussion:Roland.M/Archiv2006-2007',
u'Benutzer Diskussion:Tigerente/Archiv2006',
u'Wikipedia:WikiProjekt Bremen/Beobachtungsliste',
u'Diskussion:Wirtschaft Chiles',
u'Benutzer Diskussion:Ausgangskontrolle',
u'Benutzer Diskussion:Amnesty.tina',
u'Diskussion:Chicagoer Schule',
#u'Wikipedia Diskussion:Hausaufgabenhilfe',         # [ DELETED ]
u'Benutzer Diskussion:Niemot',
u'Benutzer Diskussion:Computer356',
u'Benutzer Diskussion:Bautsch',
u'Benutzer Diskussion:Infinite Monkey',
u'Benutzer Diskussion:Lsjm',
u'Benutzer Diskussion:Eduardo79',
u'Benutzer Diskussion:Rigidmc',
u'Benutzer Diskussion:Gilgamesch2010',
u'Benutzer Diskussion:Paulusschinew',
u'Benutzer Diskussion:Hollister71',
u'Benutzer Diskussion:Schott-PR',
u'Benutzer Diskussion:RoBoVsKi',
#u'Benutzer Diskussion:Tjaraaa',                    # [ REDIRECTED ]
u'Benutzer Diskussion:Jason Hits',
u'Benutzer Diskussion:Fit-Fabrik',
u'Benutzer Diskussion:SpaceRazor',
u'Benutzer Diskussion:Fachversicherer',
u'Benutzer Diskussion:Qniemiec',
u'Benutzer Diskussion:Ilikeriri',
u'Benutzer Diskussion:Casinoroyal',
u'Benutzer Diskussion:Havanabua',
u'Benutzer Diskussion:Euku/2010/II. Quartal',
u'Benutzer Diskussion:Mo4jolo/Archiv/2008',
u'Benutzer Diskussion:Eschweiler',
u'Benutzer Diskussion:Marilyn.hanson',
u'Benutzer Diskussion:A.Savin',
u'Benutzer Diskussion:W!B:/Knacknüsse',
u'Benutzer Diskussion:Euku/2009/II. Halbjahr',
u'Benutzer Diskussion:Gamma',
u'Hilfe Diskussion:Captcha',
u'Benutzer Diskussion:Zacke/Kokytos',
u'Benutzer Diskussion:Wolfgang1018',
u'Benutzer Diskussion:El bes',
u'Benutzer Diskussion:Janneman/Orkus',
u'Wikipedia Diskussion:Shortcuts',
u'Benutzer Diskussion:PDD',
u'Wikipedia:WikiProjekt Vorlagen/Werkstatt',
u'Wikipedia Diskussion:WikiProjekt Wuppertal/2008',
u'Benutzer Diskussion:SchirmerPower',
u'Benutzer Diskussion:Stefan Kühn/Check Wikipedia',
u'Benutzer Diskussion:Elian',
u'Wikipedia:Fragen zur Wikipedia',
u'Benutzer Diskussion:Michael Kühntopf',
u'Benutzer Diskussion:Drahreg01',
u'Wikipedia:Vandalismusmeldung',
u'Benutzer Diskussion:Jesusfreund',
u'Benutzer Diskussion:Velipp28',
u'Benutzer Diskussion:Jotge',
u'Benutzer Diskussion:DAJ',
u'Benutzer Diskussion:Karl-G. Walther',
u'Benutzer Diskussion:Pincerno',
u'Benutzer Diskussion:Polluks',
u'Portal:Serbien/Nachrichtenarchiv',
u'Benutzer Diskussion:Elly200253',
u'Benutzer Diskussion:Yak',
u'Wikipedia:Auskunft',
u'Benutzer Diskussion:Toolittle',
u'Benutzer Diskussion:He3nry',
u'Benutzer Diskussion:Euku/2009/I. Halbjahr',
u'Benutzer Diskussion:Elchbauer' ,
u'Benutzer Diskussion:Matthiasb',
u'Benutzer Diskussion:Gripweed',
u'Wikipedia:Löschkandidaten/10. Februar 2011',
u'Benutzer Diskussion:Funkruf',
u'Benutzer Diskussion:Vux',
u'Benutzer Diskussion:Zollernalb/Archiv/2008' ,
u'Benutzer Diskussion:Geiserich77/Archiv2009',
u'Benutzer Diskussion:Markus Mueller/Archiv' ,
u'Benutzer Diskussion:Capaci34/Archiv/2009',
u'Wikipedia Diskussion:Persönliche Bekanntschaften/Archiv/2010',
u'Benutzer Diskussion:Leithian/Archiv/2009/Aug',
u'Benutzer Diskussion:Lady Whistler/Archiv/2010',
u'Benutzer Diskussion:Jens Liebenau/Archiv1',
u'Benutzer Diskussion:Tilla/Archiv/2009/Juli',
u'Benutzer Diskussion:Xqt',
u'Vorlage Diskussion:Benutzerdiskussionsseite',
u'Wikipedia Diskussion:Meinungsbilder/Gestaltung von Signaturen',
u'Benutzer Diskussion:JvB1953',
u'Benutzer Diskussion:J.-H. Janßen',
u'Benutzer Diskussion:Xqt/Archiv/2009-1',
u'Hilfe Diskussion:Weiterleitung/Archiv/001',
u'Benutzer Diskussion:Raymond/Archiv 2006-2',
u'Wikipedia Diskussion:Projektneuheiten/Archiv/2009',
u'Vorlage Diskussion:Erledigt',
u'Wikipedia:Bots/Anfragen/Archiv/2008-2',
u'Diskussion:Golfschläger/Archiv',
u'Wikipedia:Löschkandidaten/9. Januar 2006',
u'Benutzer Diskussion:Church of emacs/Archiv5',
u'Wikipedia:WikiProjekt Vorlagen/Werkstatt/Archiv 2006',
u'Wikipedia Diskussion:Löschkandidaten/Archiv7',
u'Benutzer Diskussion:Physikr',
u'Benutzer Diskussion:Haring/Archiv, Dez. 2005',
u'Benutzer Diskussion:Seewolf/Archiv 7',
u'Benutzer Diskussion:Mipago/Archiv',
u'Wikipedia Diskussion:WikiProjekt Syntaxkorrektur/Archiv/2009',
u'Benutzer Diskussion:PDD/monobook.js',
u'Wikipedia:Löschkandidaten/9. April 2010',
u'Benutzer Diskussion:Augiasstallputzer/Archiv',
u'Hilfe Diskussion:Variablen',
u'Benutzer Diskussion:Merlissimo/Archiv/2009',
u'Benutzer Diskussion:Elya/Archiv 2007-01',
u'Benutzer Diskussion:Merlissimo/Archiv/2010',
u'Benutzer Diskussion:Jonathan Groß/Archiv 2006',
u'Benutzer Diskussion:Erendissss',
u'Diskussion:Ilse Elsner',
u'Diskussion:Pedro Muñoz',
u'Diskussion:Stimmkreis Nürnberg-Süd',
u'Diskussion:Geschichte der Sozialversicherung in Deutschland',
u'Diskussion:Josef Kappius',
u'Diskussion:Bibra (Adelsgeschlecht)',
u'Diskussion:Stimmkreis Regensburg-Land-Ost',
u'Diskussion:Volkmar Kretkowski',
u'Diskussion:KS Cracovia',
u'Diskussion:Livingston (Izabal)',
u'Wikipedia Diskussion:WikiProjekt Gesprochene Wikipedia/Howto',
]


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

  suite = unittest.TestLoader().loadTestsFromTestCase(TestFunctionStability)
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
  #suite.addTest(TestWorkerFunction('test_WF_addAttributes'))
  #pywikibot.debug = True
  #suite.addTest(TestWorkerFunction('test_WF_PreloadingGenerator'))
  #suite.addTest(TestWorkerFunction('test_WF_VersionHistoryGenerator'))
  unittest.TextTestRunner(verbosity=2).run(suite)
