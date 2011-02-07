#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Global Wiki API Version (CGI) for toolserver

(for mor info look at 'panel.py' also!)
"""

## @package g_api_ver.py
#  @brief   Global Wiki API Version (CGI) for toolserver
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


bot_path = os.path.realpath("../../pywikipedia/")
sys.path.append( bot_path )				# bot import form other path (!)
import query						#
import wikipedia as pywikibot				#


# === panel HTML stylesheets === === ===
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


displaystate_content = \
"""%(output)s"""


wikilist = ["translatewiki.net", "test.wikipedia.org", "de.wikipedia.org", "en.wikipedia.org"]

blacklist = [u'userrights']


def displayhtmlpage(form):
	site = pywikibot.getSite()
	data = {'output': ''}

	wikis = wikilist
	param_wiki = form.getvalue('wiki', None)
	if param_wiki:
		wikis = param_wiki.split("|")

	for wiki in wikis:
		data['output'] += "<b>%s</b><br>\n" % wiki

		# .../w/api.php?action=help&format=xml
		params = {
			u'action'	: u'help',
		}
		test = query.GetData(params, site)[u'error'][u'*']
		test = re.split('\n', test)[29]
		full_actions = re.split('[:,]\s', test)[1:]
		actions = [item for item in full_actions if item not in blacklist]

		# .../w/api.php?action=paraminfo&modules=%s&format=xml
		params = {
			u'action'	: u'paraminfo',
			u'modules'	: u'|'.join(actions),
		}
		test = query.GetData(params, site)[u'paraminfo'][u'modules']
		test = [t.get(u'version', u'> PROBLEM <') for t in test]
		#test = str(test)
		#test = "<br>\n".join(test)
		#test = str(re.search('\.php (\d*?) ', test[0]).groups())
		test = ["<tr>\n  <td>%s</td>\n</tr>\n" % item for item in test]
		test = "".join(test)

		data['output'] += "<table>\n"
		data['output'] += "<tr>\n  <td>"
		data['output'] += "actions:"
		data['output'] += "</td>\n  <td>"
		data['output'] += str(full_actions)
		data['output'] += "</td>\n</tr>\n"
		data['output'] += "<tr>\n  <td>"
		data['output'] += "blacklist:"
		data['output'] += "</td>\n  <td>"
		data['output'] += str(blacklist)
		data['output'] += "</td>\n</tr>\n"
		data['output'] += "</table>\n"

		data['output'] += "<br>\n"

		data['output'] += "<table>\n"
		data['output'] += test
		data['output'] += "</table>\n"

		data['output'] += "<br>\n"

	data.update({	'title':	'Global Wiki API Version',
			'refresh':	'',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	'<tr><td></td></tr>',
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data


form = cgi.FieldStorage()

# operational mode
print displayhtmlpage(form)
