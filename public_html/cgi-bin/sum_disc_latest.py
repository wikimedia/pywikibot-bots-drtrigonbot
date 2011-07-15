#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DrTrigonBot Discussion Summary MOST RECENT / LATEST [alpha] (CGI) for toolserver

to make it usable from server, use: 'chmod 755 sum_disc_latest.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

## @package sum_disc_latest.py
#  @brief   DrTrigonBot Discussion Summary MOST RECENT / LATEST [alpha]
#
#  @copyright Dr. Trigon, 2008-2011
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


# === python CGI script === === ===
#
import cgitb    # debug
cgitb.enable()  #

import cgi


# === module imports === === ===
#
# http://www.ibm.com/developerworks/aix/library/au-python/
import os, re, sys, copy


# === panel HTML stylesheets === === ===
# MAY BE USING Cheetah (http://www.cheetahtemplate.org/) WOULD BE BETTER (or needed at any point...)
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


# === page HTML contents === === ===
#
displaystate_content = \
"""<br>
%(output)s<br>"""


# === functions === === ===
#
def oldlogfiles(all=False):
	#localdir = os.path.dirname('../DrTrigonBot/')
	localdir = os.path.dirname(os.path.join('..','DrTrigonBot','.'))
	files = os.listdir( localdir )
	#files = [int(item[:-4]) for item in files]
	buffer = files
	files = []
	for item in buffer:
		if item[:-4].isdigit(): files.append( int(item[:-4]) )
	a = max(files)
	if not all: files.remove(a)
	log = os.path.join(localdir, str(a) + ".log")

	return (localdir, files, log)


# === CGI/HTML page view user interfaces === === ===
#
def displaystate(form):
	usr = form.getvalue('user', '')

	data = {}

	(localdir, files, data['loglink']) = oldlogfiles()

	c = {'': ''}
	if usr:
		a = open(data['loglink'], 'r')
		b = a.read()
		a.close()

		b = re.sub("\n(.*?):: ", "\n", b)
		b = re.split("\*\* Processing User: wikipedia:de:(.*?)\n", b)[1:]

		user_list = b[::2]
		data_list = b[1::2]
		for i, user in enumerate(user_list):
			d = re.split("(=+?)\n", data_list[i])
			if (len(d) > 1):
				c[user] = d[2]

	data['output'] = '(no data...)'
	if usr in c:
		# replace by 'getParsedString' from 'dtbext.wikipedia'
		import urllib
		params = urllib.urlencode({'action': 'parse', 'format': 'json', 'text': c[usr]})
		f = urllib.urlopen(u"http://de.wikipedia.org/w/api.php?%s" % params)
		data['output'] = eval(f.read())['parse']['text']['*']
		data['output'] = re.sub("\\\/", "/", data['output'])		# CHEAP UGLY WORK-A-ROUND
		data['output'] = re.sub("/wiki", "http://de.wikipedia.org/wiki", data['output'])


	data.update({	'refresh':	'',
			'title':	'DrTrigonBot Discussion Summary MOST RECENT / LATEST [alpha]',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	"?",
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data


# === Main procedure entry point === === ===
#
form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', 'displaystate')
print locals()[action](form)
