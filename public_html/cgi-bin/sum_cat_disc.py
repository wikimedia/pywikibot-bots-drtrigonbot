#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DrTrigonBot category discussion summary (CGI) for toolserver

(for mor info look at 'panel.py' also!)
"""

## @package sum_cat_disc.py
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


import MySQLdb, _mysql_exceptions 


bot_path = os.path.realpath("../../pywikipedia/")
sys.path.append( bot_path )				# bot import form other path (!)
import query						#
import wikipedia as pywikibot				#
import pagegenerators, catlib
#import wikipedia as pywikibot	# for 'Timestamp'
import dtbext			# for 'getTimeStmpNow'
import family
# may be best would be to get namespace info from DB?!


# === panel HTML stylesheets === === ===
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


displaystate_content = \
"""<br>
<form action="sum_cat_disc.py">
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
JOIN categorylinks ON cl_from = page_id WHERE cl_to = %s
LIMIT %s"""

#_SQL_query_page_info = \
#"""SELECT page_title, page_namespace, page_touched
#FROM page
#WHERE page_title LIKE "%s"
#AND page_namespace IN %s
#LIMIT %s"""

_SQL_query_page_info = \
"""SELECT page_title, page_namespace, page_touched
FROM page
WHERE page_title LIKE %s
AND page_namespace = %s
LIMIT %s"""

#_SQL_query__ = \
#"""SELECT page_title, page_namespace, page_touched
#FROM page
#WHERE page_title IN
#(SELECT page_title
#FROM page
#JOIN categorylinks ON cl_from = page_id WHERE cl_to = "%s")
#AND page_namespace IN (1, 3, 5, 9, 11, 13, 15, 91, 93, 101, 109)
#LIMIT %s"""

# written by Merlissimo (merl) - Thanks a lot!
# http://kpaste.net/da2d, http://kpaste.net/5b2f97f
# ~/devel/experimental/diskchanges.sql
# need db write access; to create temporary tables (they live until the db connection
# gets closed) and is thus not possible during e.g. 'schema changes in progress'
# -----------------------------------------------------------------------------
# drtrigon@nightshade:~$ mysql -hdewiki-p.userdb u_drtrigon
# ERROR 1049 (42000): Unknown database 'u_drtrigon'
# drtrigon@nightshade:~$ mysql -hdewiki-p.userdb
# Welcome to the MySQL monitor.  Commands end with ; or \g.
# Your MySQL connection id is 22197636
# Server version: 5.1.53 Source distribution
#
# Copyright (c) 2000, 2010, Oracle and/or its affiliates. All rights reserved.
# This software comes with ABSOLUTELY NO WARRANTY. This is free software,
# and you are welcome to modify and redistribute it under the GPL v2 license
#
# Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
#
# mysql> CREATE DATABASE IF NOT EXISTS u_drtrigon
#     -> ;
# Query OK, 1 row affected (0.02 sec)
# -----------------------------------------------------------------------------
_SQL_query_cattree = [
"""CREATE TEMPORARY TABLE cattemp (catname VARCHAR(255) PRIMARY KEY);""",
"""CREATE TEMPORARY TABLE cat (catname VARCHAR(255) PRIMARY KEY, depth INT, INDEX(depth));""",
"""INSERT IGNORE INTO cat (catname, depth) SELECT page_title, 0 FROM %swiki_p.page WHERE page_namespace=14 AND page_title=%s;""",

"""DELETE FROM cattemp""",
"""INSERT IGNORE INTO cattemp (catname) SELECT catname FROM cat WHERE depth=%s""",
"""INSERT IGNORE INTO cat (catname, depth) SELECT page_title, %s FROM cattemp INNER JOIN %swiki_p.categorylinks ON catname=cl_to INNER JOIN %swiki_p.page ON cl_from = page_id WHERE page_namespace=14""",
"""SELECT ROW_COUNT()""",

"""SELECT rc_namespace, rc_title, rc_user_text, rc_timestamp, rc_comment
 FROM cat
  INNER JOIN %swiki_p.categorylinks ON catname = cl_to
  INNER JOIN %swiki_p.page p1 ON cl_from = page_id
  INNER JOIN %swiki_p.page p2 ON p1.page_title = p2.page_title AND p1.page_namespace+1=p2.page_namespace
  INNER JOIN %swiki_p.recentchanges ON p2.page_id = rc_cur_id
 WHERE p1.page_namespace IN (0,10,14)
  AND rc_timestamp >= DATE_SUB(CURDATE(),INTERVAL %s HOUR)
  AND rc_old_len < rc_new_len
 ORDER BY rc_timestamp DESC;""",

"""SELECT VERSION();""", ]

# https://wiki.toolserver.org/view/Database_access#wiki
_SQL_query_wiki_info = \
"""SELECT 
   lang,
   CONCAT("sql-s", server) AS dbserver,
   dbname,
   CONCAT("http://", DOMAIN, script_path, "api.php") AS url
 FROM toolserver.wiki
 WHERE family = "wikipedia"
 ORDER BY SIZE DESC LIMIT %s;"""


SQL_LIMIT_max = 1000

wikitime = "%Y%m%d%H%M%S"


def call_db(query, args=(), limit=SQL_LIMIT_max):
	#db.query(query % args)

	# execute SQL query using execute() method.
	# for strings " or ' has to be omitted, execute inserts them as well
	cursor.execute(query, args)

def read_db(query, args=(), limit=SQL_LIMIT_max):
	call_db(query, args, limit=limit)

	#return db.store_result().fetch_row(limit)
	return cursor.fetchmany(limit)

# recursive
def get_cat_tree_rec(cat, limit=SQL_LIMIT_max):
	res = set([])
	for row in read_db(_SQL_query_ns_content, (cat.replace(' ', '_'), limit)):
		# Category
		if int(row[1]) == 14:
			res = res.union( get_cat_tree_rec(row[0], limit) )
			continue

		# Page
		res.add( row )

	return res

# iterative (heavily SQL based)
def checkRecentEdits_db_it(cat, end, period, limit=SQL_LIMIT_max):
	res = set([])

#	db.query(("\n".join(_SQL_query_01)) % cat.replace(' ', '_'))

	c=cursor
	call_db(_SQL_query_cattree[0])
	call_db(_SQL_query_cattree[1])
	#call_db(_SQL_query_cattree[2], (cat.replace(' ', '_'),))
	_SQL_query = _SQL_query_cattree[2] % (wiki, '%s')  # BAD: SQL injection!
	call_db(_SQL_query, (cat.replace(' ', '_'),))      #

#	uu = read_db(_SQL_query_cattree[8], limit=limit)
#	res.append( uu )
#	return res

	_SQL_query = _SQL_query_cattree[5] % ('%s', wiki, wiki)  # BAD: SQL injection!
	for i in range(25):
		call_db(_SQL_query_cattree[3])
		call_db(_SQL_query_cattree[4], (i,))
		#call_db(_SQL_query_cattree[5], (i+1,))
		call_db(_SQL_query, (i+1,))                      # BAD: SQL injection!
		co = read_db(_SQL_query_cattree[6], limit=limit)

		if (co[0][0] == 0): break

	unique = {}
	_SQL_query = _SQL_query_cattree[7] % (wiki, wiki, wiki, wiki, '%s')  # BAD: SQL injection!
	for page in list(read_db(_SQL_query, (period,), limit=limit)):       #
		u = page[:2] # make list items unique, BUT YOU HAVE TO TAKE THE NEWEST ONE!!!
		date = long(page[3])
		if date > unique.get(u, end):
			res.add( ((page[1], page[0], page[3]),) )
			unique[u] = date

	return res

def checkRecentEdits_db_rec(cat, end, limit=SQL_LIMIT_max):
	res = []
	for row in list(get_cat_tree_rec(cat, limit)):
		ns = row[1]
		ns = ns + (1 - (ns % 2))  # next bigger odd
		try:
			subrow = read_db(_SQL_query_page_info, (row[0], ns, 1))
			if subrow and (long(subrow[0][2]) >= end):
				res.append( subrow )
		except _mysql_exceptions.ProgrammingError:  # are displayed later with '(!)' mark
			res.append( [(row[0], ns, '')] )

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
	for item in read_db(_SQL_query_wiki_info, (limit,), limit):
		if item[2] == (wiki + "wiki_p"):
			return item
	return None


def displayhtmlpage(form):
	cat    = form.getvalue('cat', '')
#	start  = form.getvalue('start', datetime.datetime.utcnow().strftime(wikitime))
	start  = form.getvalue('start', dtbext.date.getTimeStmpNow(full=True))
	period = form.getvalue('period', '24')

	s = datetime.datetime.strptime(start, wikitime)
	p = datetime.timedelta(hours=int(period))
	end = s - p

	data = {'output': ''}

	data['output'] += "<b>Start</b>: %s (%s)<br>\n" % (start, asctime(strptime(start, wikitime)))
	data['output'] += "<b>End</b>: %s (%s)<br>\n" % (start, end.ctime())
	data['output'] += "<b>Period</b>: %sh<br>\n" % period

	end = long( end.strftime(wikitime) )

	data['output'] += "<br>\n"

#	talk_ns = (1, 3, 5, 9, 11, 13, 15, 91, 93, 101, 109)
#	res += str( read_db(_SQL_query_page_info, ('%DrTrigon',str(talk_ns),10)) )

#	res += str( read_db(_SQL_query_02, (cat,)) )
#	res += "<br>\n"

	if cat:
		tic = time()
		#out = checkRecentEdits_API(cat, end)
		#out = checkRecentEdits_db_rec(cat, end)                    # uses 'page_touched'
		out = checkRecentEdits_db_it(cat, end, str(int(period)+1))  # uses 'rc_timestamp'
		out_size = len(out)
		toc = time()
		if out:
			# sort items/entries by timestamp
			# (somehow cheap algor. - use SQL directly for sorting)
			out_dict = dict( [(item[0][2]+item[0][0]+str(item[0][1]), item) for item in out] )
			keys = out_dict.keys()
			keys.sort()
			out = [out_dict[key] for key in keys]

			data['output'] += "<table>\n"

			for subrow in out:
				data['output'] += "<tr>\n  <td>"
				title = subrow[0][0]
				title = site.namespace(subrow[0][1]).encode('utf8') + ':' + title
				data['output'] += '<a href="http://%s.wikipedia.org/wiki/%s" target="_blank">%s</a>' % (wiki, title, title.replace('_', ' '))
				data['output'] += "</td>\n  <td>"
#				data['output'] += str(subrow[0][1:])
				try:
					tmsp = asctime(strptime(subrow[0][2], wikitime)) + " (UTC)"
				except ValueError:
					tmsp = subrow[0][2] + " (!)"
				data['output'] += tmsp
				data['output'] += "</td>\n</tr>\n"

			data['output'] += "</table>\n"
                else:
                        data['output'] += "<i>No pages matching criteria found.</i><br>\n"
		data['output'] += "<br>\n"
                data['output'] += "Time to process %i results: %fs\n" % (out_size, (toc-tic))
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
if len(wiki) > 4: wiki = 'de'  # cheap protection for SQL injection

site = pywikibot.getSite(wiki)

# Establich a connection
#db = MySQLdb.connect(db='enwiki_p', host="enwiki-p.rrdb.toolserver.org", read_default_file="/home/drtrigon/.my.cnf")
#db = MySQLdb.connect(db=wiki+'wiki_p', host=wiki+"wiki-p.rrdb.toolserver.org", read_default_file="/home/drtrigon/.my.cnf")
db = MySQLdb.connect(db='u_drtrigon', host=wiki+"wiki-p.userdb.toolserver.org", read_default_file="/home/drtrigon/.my.cnf")
# prepare a cursor object using cursor() method
cursor = db.cursor()

# operational mode
print displayhtmlpage(form)

cursor.close()
db.close()
