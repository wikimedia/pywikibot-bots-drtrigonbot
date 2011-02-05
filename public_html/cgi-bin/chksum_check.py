#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DrTrigonBot checksum checker (CGI) for toolserver

(for mor info look at 'panel.py' also!)
"""

## @package chksum_check.py
#  @brief   DrTrigonBot checksum checker (CGI) for toolserver
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


# debug
import cgitb
cgitb.enable()

import cgi


from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import os, re, sys
import hashlib


bot_path = os.path.realpath("../../pywikipedia/")
sys.path.append( bot_path )                             # bot import form other path (!)
import query                                            #
import wikipedia as pywikibot                           #


# === panel HTML stylesheets === === ===
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


displaystate_content = \
"""%(output)s<br>"""

textfile_encoding = 'utf-8'


def displayhtmlpage(form):
	titles   = re.split('\|', form.getvalue('title', ''))
	sections = re.split('\|', form.getvalue('section', ''))
	chksum   = re.split('\|', form.getvalue('chksum', ''))

        site = pywikibot.getSite()
        data = {'output': ''}

	#data['output'] += str(titles)
	#data['output'] += "<br>"
	#data['output'] += str(chksum)
	#data['output'] += "<br>"

	for i, title in enumerate(titles):
		try:	section = sections[i]
		except:	section = '0'

		# .../w/api.php?action=parse&page=%s&prop=sections&format=xml
		params = {
			u'action'       : u'parse',
			u'page'		: title,
			u'prop'		: u'sections',
		}
		try:
			test = query.GetData(params, site)[u'parse'][u'sections']
		except:
			# e.g. wrong params for page call ...
			data['output'] += str(query.GetData(params, site))
			data['output'] += "<br>"
			break
		test = dict( [(item[u'line'], item[u'number']) for item in test] )
		if section in test: section = test[section]

		# .../w/api.php?action=query&prop=revisions&titles=%s&rvprop=timestamp|user|comment|content&rvsection=%s&format=xml
		params = {
			u'action'       : u'query',
			u'prop'		: u'revisions',
			u'titles'	: title,
			u'rvprop'	: u'timestamp|user|comment|content',
			u'rvsection'	: section,
		}
		try:
			test = query.GetData(params, site)[u'query'][u'pages']
		except:
			# e.g. wrong params for page call ...
			data['output'] += str(query.GetData(params, site))
			data['output'] += "<br>"
			break
		test = test[test.keys()[0]][u'revisions'][0]
		dh_chars = test[u'*']
		m = re.search('^(=+)(.*?)(=+)(?=\s)', dh_chars, re.M)
		if m:	section_name = m.groups()[1].strip()
		else:	section_name = "?"

		data['output'] += "Page: <i>%s</i> / Section: <i>%s (%s)</i>" % (title, section_name.encode(textfile_encoding), section)
		data['output'] += "<br>"
		data['output'] += "Old checksum: %s" % chksum[i]
		data['output'] += "<br>"

		new_chksum = hashlib.md5(dh_chars.encode('utf8').strip()).hexdigest()
		data['output'] += "New checksum: %s" % new_chksum
		data['output'] += "<br>"
		data['output'] += "<b>Section changed: %s</b>" % (not (chksum[i] == new_chksum))

		#data['output'] += "<br>"
		#data['output'] += "<div style=\"padding:20px; border:thin solid gray; margin:25px\">"
		#data['output'] += "<small>"
		##data['output'] += re.sub('\n','<br>',text).encode('utf8')
		#data['output'] += text.encode('utf8')
		#data['output'] += "</small>"
		#data['output'] += "</div>"

		data['output'] += "<br>"

        data.update({   'title':        'DrTrigonBot checksum checker',
                        'refresh':      '',
                        'tsnotice':     '',
                        'p-status':     '<tr><td></td></tr>',
                        'footer':       style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
        })
        data['content'] = displaystate_content % data

        return style.page % data


form = cgi.FieldStorage()

# operational mode
print displayhtmlpage(form)
