#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DrTrigonBot category discussion summary (CGI) for toolserver

(for mor info look at 'panel.py' also!)
"""

## @package sum_cat_disk.py
#  @brief   DrTrigonBot category discussion summary (CGI) for toolserver
#
#  @copyright Dr. Trigon, 2008-2011
#
#  @todo better/faster SQL query
#  @todo prevent DOS calls
#  @todo redirects? others...?
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
__version__='$Id$'
#


# debug
import cgitb
cgitb.enable()

import cgi


from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import datetime
import os, re, sys


import MySQLdb


bot_path = os.path.realpath("../../pywikipedia/")
sys.path.append( bot_path )				# bot import form other path (!)
import query						#
import wikipedia as pywikibot				#
import pagegenerators, catlib
#import wikipedia as pywikibot	# for 'Timestamp'
import dtbext			# for 'getTimeStmpNow'
import family

site = pywikibot.getSite()

trans_ns = family.Family().namespaces
trans_ns.update({101: {'de': u'Portal_Diskussion'}})


# === panel HTML stylesheets === === ===
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


displaystate_content = \
"""<br>
<form action="sum_cat_disk.py">
  <table>
    <tr>
      <td>wiki:</td>
      <td><input name="wiki" value="%(wiki)s"></td>
    </tr>
    <tr>
      <td>Category:</td>
      <td><input name="cat" value="%(cat)s"></td>
    </tr>
    <tr>
      <td>Start:</td>
      <td><input name="start" value="%(start)s"></td>
    </tr>
    <tr>
      <td>Period:</td>
      <td><input name="period" value="%(period)s"></td>
    </tr>
    <tr>
      <td></td>
      <td><input type="submit" value=" Check ">
          <input type="reset" value=" Reset "></td>
    </tr>
  </table>
</form><br>

<hr><br>

%(output)s"""


# http://www.mediawiki.org/wiki/Manual:Database_layout
# http://en.wikipedia.org/wiki/Wikipedia:Namespace
# http://sql.1keydata.com/de/sql-like.php

# https://wiki.toolserver.org/view/Queries#Pages_in_a_specific_category_using_a_specific_template
_SQL_query_ns_content = \
"""SELECT page_title, page_namespace
FROM page
JOIN categorylinks ON cl_from = page_id WHERE cl_to = "%s"
LIMIT %i"""

#_SQL_query_page_info = \
#"""SELECT page_title, page_namespace, page_touched
#FROM page
#WHERE page_title LIKE "%s"
#AND page_namespace IN %s
#LIMIT %i"""

_SQL_query_page_info = \
"""SELECT page_title, page_namespace, page_touched
FROM page
WHERE page_title LIKE "%s"
AND page_namespace = %i
LIMIT %i"""

#_SQL_query__ = \
#"""SELECT page_title, page_namespace, page_touched
#FROM page
#WHERE page_title IN
#(SELECT page_title
#FROM page
#JOIN categorylinks ON cl_from = page_id WHERE cl_to = "%s")
#AND page_namespace IN (1, 3, 5, 9, 11, 13, 15, 91, 93, 101, 109)
#LIMIT %i"""

# written by Merlissimo (merl) - Thanks a lot!
# http://kpaste.net/da2d, http://kpaste.net/5b2f97f
# ~/devel/experimental/diskchanges.sql
# (need db write access; e.g. not possible during 'schema changes in progress')
_SQL_query_01 = \
"""CREATE TEMPORARY TABLE cattemp (catname VARCHAR(255) PRIMARY KEY);
CREATE TEMPORARY TABLE cat (catname VARCHAR(255) PRIMARY KEY, depth INT, INDEX(depth));
INSERT IGNORE INTO cat (catname, depth) SELECT page_title, 0 FROM dewiki_p.page WHERE page_namespace=14 AND page_title='%s';"""
_SQL_query_02 = \
"""DELETE FROM cattemp;
INSERT IGNORE INTO cattemp (catname) SELECT catname FROM cat WHERE depth=%i;
INSERT IGNORE INTO cat (catname, depth) SELECT page_title, %i FROM cattemp INNER JOIN dewiki_p.categorylinks ON catname=cl_to INNER JOIN dewiki_p.page ON cl_from = page_id WHERE page_namespace=14;"""
_SQL_query_03 = \
"""SELECT rc_namespace, rc_title, rc_user_text, rc_timestamp, rc_comment
 FROM cat
  INNER JOIN dewiki_p.categorylinks ON ct = cl_to
  INNER JOIN dewiki_p.page p1 ON cl_from = page_id
  INNER JOIN dewiki_p.page p2 ON p1.page_title = p2.page_title AND p1.page_namespace+1=p2.page_namespace
  INNER JOIN dewiki_p.recentchanges ON p2.page_id = rc_cur_id
 WHERE p1.page_namespace IN (0,10,14)
  AND rc_timestamp >= DATE_SUB(CURDATE(),INTERVAL 3 DAY)
  AND rc_old_len < rc_new_len
 ORDER BY rc_timestamp DESC;"""

# https://wiki.toolserver.org/view/Database_access#wiki
_SQL_query_wiki_info = \
"""SELECT 
   lang,
   CONCAT("sql-s", server) AS dbserver,
   dbname,
   CONCAT("http://", DOMAIN, script_path, "api.php") AS url
 FROM toolserver.wiki
 WHERE family = "wikipedia"
 ORDER BY SIZE DESC LIMIT %i;"""


SQL_LIMIT_max = 1000

wikitime = "%Y%m%d%H%M%S"


def query_db(query, limit=SQL_LIMIT_max):
	db.query(query)
	r = db.store_result()

	return [row for row in r.fetch_row(limit)]

# recursive
def get_cat_tree_rec(cat, limit=SQL_LIMIT_max):
	res = set([])
	for row in query_db(_SQL_query_ns_content % (cat.replace(' ', '_'), limit)):
		# Category
		if int(row[1]) == 14:
			res = res.union( get_cat_tree_rec(row[0], limit) )
			continue

		# Page
		res.add( row )

	return res

# iterative (heavily SQL based)
def get_cat_tree_it(cat, limit=SQL_LIMIT_max):
        db.query(_SQL_query_01 % cat.replace(' ', '_'))
        r = db.store_result()
	return r

	for i in range(25):
	        db.query(_SQL_query_02 % (i, i+1))
        	r = db.store_result()

#	int [] co = stmt.executeBatch();
#	if(co[2] == 0) break;

        db.query(_SQL_query_03)
        r = db.store_result()

def checkRecentEdits_db(cat, end, limit=SQL_LIMIT_max):
	res = []
	for row in list(get_cat_tree_rec(cat, limit)):
		ns = row[1]
		ns = ns + (1 - (ns % 2))  # next bigger odd
		subrow = query_db(_SQL_query_page_info % (row[0], ns, 1))
		if subrow and (int(subrow[0][2]) >= end):
			res.append( subrow )

	return res

def checkRecentEdits_API(cat, end):
#	cat = catlib.Category(site, "%s:%s" % (site.namespace(14), u'Baden-Württemberg'))
	cat = catlib.Category(site, "%s:%s" % (site.namespace(14), u'Portal:Hund'))

	res = []
	for page in pagegenerators.CategorizedPageGenerator(cat, recurse=True):
		if not page.isTalkPage():
			page = page.toggleTalkPage()
		title  = '?'
		change = '?'
		try:
			title  = page.title()
			change = page.getVersionHistory(revCount=1)[0][1]
		except pywikibot.exceptions.NoPage:
			continue
		except:
			pass
		res.append( (title, change) )

	return res

def get_wikiinfo_db(wiki, limit=SQL_LIMIT_max):
	for item in query_db(_SQL_query_wiki_info % limit, limit):
		if item[2] == (wiki + "wiki_p"):
			return item
	return None


def displayhtmlpage(form):
	cat    = form.getvalue('cat', '')
	start  = form.getvalue('start', datetime.datetime.utcnow().strftime(wikitime))
#	start  = form.getvalue('start', dtbext.date.getTimeStmp(full=True))
	period = form.getvalue('period', '24')

	s = datetime.datetime.strptime(start, wikitime)
	p = datetime.timedelta(hours=int(period))
	end = s - p

	data = {'output': ''}

	data['output'] += "<b>Start</b>: %s (%s)<br>\n" % (start, asctime(strptime(start, wikitime)))
	data['output'] += "<b>End</b>: %s (%s)<br>\n" % (start, end.ctime())
	data['output'] += "<b>Period</b>: %sh<br>\n" % period

	end = int( end.strftime(wikitime) )

	data['output'] += "<br>\n"

#	talk_ns = (1, 3, 5, 9, 11, 13, 15, 91, 93, 101, 109)
#	res += str( query_db(_SQL_query_page_info % ('%DrTrigon',str(talk_ns),10 )) )

#	res += str( query_db(_SQL_query_02 % (cat, )) )
#	res += "<br>\n"

#	cat = 'Portal:Hund'
#	data['output'] = str( get_cat_tree_it(cat, limit=SQL_LIMIT_max) )
#	cat = ''

	if cat:
		tic = time()
#               out = checkRecentEdits_API(cat, end)
                out = checkRecentEdits_db(cat, end)
		toc = time()
		if out:
			# sort items/entries by timestamp
			# (somehow cheap algor. - use SQL directly for sorting)
			out_dict = dict( [(item[0][2]+item[0][0], item) for item in out] )
			keys = out_dict.keys()
			keys.sort()
			out = [out_dict[key] for key in keys]

			data['output'] += "<table>\n"

			for subrow in out:
				data['output'] += "<tr>\n  <td>"
				title = subrow[0][0]
				if subrow[0][1] in trans_ns:
					title = trans_ns[subrow[0][1]]['de'].encode('utf8') + ':' + title
				data['output'] += '<a href="http://de.wikipedia.org/wiki/%s" target="_blank">%s</a>' % (title, title.replace('_', ' '))
				data['output'] += "</td>\n  <td>"
#				data['output'] += str(subrow[0][1:])
				data['output'] += asctime(strptime(subrow[0][2], wikitime)) + " (UTC)"
				data['output'] += "</td>\n</tr>\n"

			data['output'] += "</table>\n"
                else:
                        data['output'] += "<i>No pages matching criteria found.</i><br>\n"
		data['output'] += "<br>\n"
                data['output'] += "Time to process: %fs\n" % (toc-tic)
	else:
		data['output'] += "<i>No category (cat) defined!</i><br>\n"

	data['output'] += "<br>\n"

	data['output'] += '<small>%s</small><br>\n' % str( get_wikiinfo_db(wiki) )

	data.update({	'title':	'DrTrigonBot category discussion summary',
			'refresh':	'',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	'<tr><td><small><a href="http://status.toolserver.org/" target="_blank">DB status</a></small></td></tr>',
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
			'wiki':		wiki,
			'cat':		cat,
			'start':	start,
			'period':	period,
	})
	data['content'] = displaystate_content % data

	return style.page % data


form = cgi.FieldStorage()
wiki = form.getvalue('wiki', 'de')

# Establich a connection
#db = MySQLdb.connect(db='enwiki_p', host="enwiki-p.rrdb.toolserver.org", read_default_file="/home/drtrigon/.my.cnf")
db = MySQLdb.connect(db=wiki+'wiki_p', host=wiki+"wiki-p.rrdb.toolserver.org", read_default_file="/home/drtrigon/.my.cnf")

# operational mode
print displayhtmlpage(form)

db.close()
