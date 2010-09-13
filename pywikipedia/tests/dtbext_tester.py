# -*- coding: utf-8 -*-

import time

import test_utils

#import wikipedia, wikipediaAPI
import wikipedia, pagegenerators
import dtbext
import userlib


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

TESTPAGES = [	u'Hilfe Diskussion:Weiterleitung',
		u'Benutzer Diskussion:BitH',
		u'Benutzer Diskussion:DrTrigonBot',
		u'Benutzer Diskussion:DrTrigonBo', ]

TESTPAGE = u'...'
TESTPAGE = u'Wikipedia:Löschkandidaten/20. Juli 2009'
TESTPAGE = u'Benutzer Diskussion:Karsten11'
TESTPAGE = u'Benutzer Diskussion:GregorHelms'
TESTPAGE = u'Wikipedia:WikiProjekt Vorlagen/Werkstatt'
#TESTPAGE = u'Benutzer_Diskussion:DrTrigonBot'
TESTPAGE = u'Benutzer_Diskussion:DrTrigon'


def TEST_getSections():
	#print "\nTest of 'dtbext.wikipedia.Page.getSections()' on page '%s'..." % TESTPAGE
	#
	##site = wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	site = dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	buf = site.get()
	#buf = site.get(mode='full')
	##buf = site.getFullB()[:1000]
	#print buf

	print "\nTest of 'dtbext.wikipedia.Pages.getSections()' on page '%s'..." % TESTPAGE

	#site = dtbext.wikipedia.Pages(wikipedia.getSite(), [TESTPAGE])
	##buf = site.get()
	#buf = [data for (site, data) in site.get(mode='full')][0]
	##buf = [data for (site, data) in site.get()][0]

	#siteAPI = dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	#(sections, test) = siteAPI.getSections(minLevel=1)
	#(sections, test) = site.getSections(minLevel=1, getter=site.get)
	#(sections, test) = site.getSections(minLevel=1, getter=site._getFullContent)
	sections = site.getSections(minLevel=1, pagewikitext=buf)
	#(sections, test) = site.getSections()

	#print "*"
	#for item in sections:
	#	print buf[item[0]]
	#	print "*"

	#head = []
	#body = []
	#body_part = []
	#actual_head = sections.pop(0)
	#for i in range(len(buf)):
	#	item = buf[i]
	#	if (i == actual_head[0]):
	#		body.append( u'\n'.join(body_part) )
	#		body_part = []
	#		head.append( item )
	#		try:	actual_head = sections.pop(0)
	#		except:	actual_head = (len(buf)+1,)
	#	else:
	#		body_part.append( item )
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
	#site = dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	#print site.getSections()
	##sites = dtbext.wikipedia.Pages(wikipedia.getSite(), TESTPAGES*5)
	##a = sites.getSections()
	##print len(TESTPAGES*5), len(a), a

def TEST_getParsedContent():
	print "\nTest of 'dtbext.wikipedia.Page.getParsedContent()' on page '%s'..." % TESTPAGE

	#print dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE).get(mode='parse')
	#print dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE).get(mode='parse', plaintext=True)

	site = wikipedia.getSite()
	dtbext.wikipedia.addAttributes( site )
	print "*", site.getParsedString(u'Erweiterung für [[Wikipedia:Bots/Bot-Info]]', keeptags = []), "*"

def TEST_purgeCache():
	print "\nTest of 'dtbext.wikipedia.Page.purgeCache()' on page '%s'..." % TESTPAGE
	
	print dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE).purgeCache()

def TEST_GlobalWikiNotificationsGen():
	print "\nTest of 'dtbext.wikipedia.GlobalWikiNotificationsGen()' on page '%s'..." % TESTPAGE

	for item in dtbext.wikipedia.GlobalWikiNotificationsGen(u'DrTrigon'):
		print item[0]

def TEST_getVersionHistory():
	#print "\nTest of 'wikipedia.Page.getVersionHistory()' on page '%s'..." % TESTPAGE
	#
	#for item in TESTPAGES:	
	#	site = wikipedia.Page(wikipedia.getSite(), item)
	#	print site.getVersionHistory(revCount=1)
	#
	#print "\nTest of 'dtbext.wikipedia.Page.getVersionHistory()' on page '%s'..." % TESTPAGE

	#for item in TESTPAGES:	
	#	site = dtbext.wikipedia.Page(wikipedia.getSite(), item)
	#	print site.getVersionHistory(revCount=1)
	site = dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	print site.getVersionHistory(revCount=1)
	print site.isRedirectPage()

def TEST_VersionHistoryGenerator():
	print "\nTest of 'dtbext.pagegenerators.VersionHistoryGenerator()' on '%i' page(s)..." % len(TESTPAGES)

	gen = dtbext.pagegenerators.VersionHistoryGenerator(TESTPAGES)
	for item in gen:	
		print item[1:]
		#print item, a[item], ('redirect' in a[item][0])

def TEST_get():
	#print "\nTest of 'dtbext.wikipedia.Pages.get()' on '%i' page(s)..." % len(TESTPAGES)
	print "\nTest of sequence:"
	print "   PagesFromTitlesGenerator ->"
	print "   (PageTitleFilterPageGenerator) ->"
	print "   PreloadingGenerator ->"
	print "   [output]"
	print

	ignore_list = { wikipedia.getSite().family.name: { wikipedia.getSite().lang: [u'Benutzer Diskussion:DrTrigonBo'] }}
	#ignore_list = { wikipedia.getSite().family.name: { wikipedia.getSite().lang: [] }}

	wikipedia.debug = True		# to enable the use of the API here
	gen        = pagegenerators.PagesFromTitlesGenerator(TESTPAGES)
	filter_gen = pagegenerators.PageTitleFilterPageGenerator(gen, ignore_list)	# or RegexFilterPageGenerator
	prload_gen = pagegenerators.PreloadingGenerator(filter_gen)			# ThreadedGenerator would be nice!
	for page in prload_gen:
		print page

		start = time.time()
		u = page.get()
		stop = time.time()
		buffd = stop-start

		start = time.time()
		u = page.getVersionHistory()
		stop = time.time()
		buffd2 = stop-start

		start = time.time()
		u = page.get(force=True)
		stop = time.time()
		unbuffd = stop-start

		start = time.time()
		u = page.getVersionHistory(forceReload=True)
		stop = time.time()
		unbuffd2 = stop-start

		print "GET; buffered:", buffd, "\t", "unbuffered:", unbuffd
		print "GETVERSIONHISTORY; buffered:", buffd2, "\t", "unbuffered:", unbuffd2
	wikipedia.debug = False

def TEST_addAttributes():
	page = wikipedia.Page(wikipedia.getSite(), TESTPAGE)
	#print page.getSections()
	dtbext.wikipedia.addAttributes( page )
	print page.getSections()

	page2 = wikipedia.Page(wikipedia.getSite(), u'Benutzer Diskussion:Karsten11')
	#print page.getSections()
	dtbext.wikipedia.addAttributes( page2 )
	print page2.getSections()
	print page.getSections()


# wikipedia.py
TEST_getVersionHistory()
#TEST_getSections()
#TEST_purgeCache()
#TEST_get()
#TEST_getParsedContent()
#print wikipedia.getSite().getUrl('/w/api.php?action=query&meta=userinfo&uiprop=blockinfo|hasmsg|groups|rights|options|preferencestoken|editcount|ratelimits|email&formal=xml')
#TEST_GlobalWikiNotificationsGen()

#TEST_addAttributes()

TEST_VersionHistoryGenerator()


#a_str = r'<strong class="error">Referenz-Fehler: Einzelnachweisfehler: <code>&lt;ref&gt;</code>-Tags existieren, jedoch wurde kein <code>&lt;references&#160;/&gt;</code>-Tag gefunden.</strong>'
#site = dtbext.wikipedia.Page(wikipedia.getSite(), TESTPAGE)
#buf = site.get(mode='parse')
#import re
#if re.search(a_str, buf): print "<references />-Tag Fehler"


#page = wikipedia.Page(wikipedia.getSite(), TESTPAGE)
#page.extradata = "hallo"
#print page.title(), page.extradata

#dtbext.wikipedia.Pages(None, None)


print "done."

