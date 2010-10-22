#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test CGI python script

to make it usable from server, use: 'chmod 755 test.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

#
# (C) Dr. Trigon, 2008, 2009
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', ... (and others)
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id$'
#


# debug
import cgitb
cgitb.enable()


import cgi
from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import commands, os, errno
#import subprocess
import re
import httplib, StringIO, hashlib, urllib
from xml.sax import saxutils, make_parser, ContentHandler
from xml.sax.handler import feature_namespaces


displaystate_content = """Content-Type: text/html
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>Global Wiki API Version</title>
</head>
<body>
<p><span style="font-family:sans-serif">
Global Wiki API Version<br><br><br>
%(output)s<br>
<small>Global Wiki API Version, written by <a href="https://wiki.toolserver.org/view/User:DrTrigon">DrTrigon</a>. 
<!-- <img src="https://wiki.toolserver.org/w/images/e/e1/Wikimedia_Community_Logo-Toolserver.png" 
width="16" height="16" alt="Toolserver"> -->
<a href="http://tools.wikimedia.de/"><img 
src="https://wiki.toolserver.org/favicon.ico" border="0" 
alt="Toolserver"> Powered by Wikimedia Toolserver</a>.
<a href="http://de.selfhtml.org/index.htm"><img 
src="http://de.selfhtml.org/src/favicon.ico" border="0" width="16" 
height="16" alt="SELFHTML"> Thanks to SELFHTML</a>.
<!--<a href="http://validator.w3.org/check?uri=referer"><img 
src="http://www.w3.org/Icons/valid-html401-blue" 
alt="Valid HTML 4.01 Transitional" height="16" width="44" 
border="0"></a>--></small>
</span></p>
</body>
</html>
"""

textfile_encoding = 'utf-8'

wikis = ["translatewiki.net", "test.wikipedia.org", "de.wikipedia.org", "en.wikipedia.org"]
REQUEST_getHelp			= ("/w/api.php?action=help&format=xml")
REQUEST_getVersion		= ("/w/api.php?action=paraminfo&modules=%s&format=xml")


# thanks to: http://pyxml.sourceforge.net/topics/howto/xml-howto.html
#class GetData(saxutils.DefaultHandler):
class GetData(ContentHandler):
	"""
	Parse XML output of wiki API interface
	"""
	def __init__(self, parent, content, values = []):
		self.get_parent, self.get_content, self.get_values = parent, content, values
		self._parent, self._content = "", ""
		self.chars = ""

	def startElement(self, name, attrs):
		self._content = name
		if not ((self._parent == self.get_parent) and (self._content == self.get_content)):
			self._content = ""
			self._parent = name

	def characters(self, content):
		if not (self._content == self.get_content): return
		self.chars += content

# thanks to: http://pyxml.sourceforge.net/topics/howto/xml-howto.html
#class _GetData(saxutils.DefaultHandler):
class _GetData(ContentHandler):
	"""
	Parse XML output of wiki API interface
	"""
	def __init__(self, content, values = []):
		self.get_content, self.get_values = content, values
		self._content = ""
		self.data = []
		self.chars = ""

	def startElement(self, name, attrs):
		self._content = name
		if not (self._content == self.get_content):
			self._content = ""
			return
		data = []
		for item in self.get_values:
			#data.append( attrs.get(item, "") )
			try:	(val, default) = item
			except:	(val, default) = (item, "")
			data.append( attrs.get(val, default) )
		self.data.append( tuple(data) )

	def characters(self, content):
		if not (self._content == self.get_content): return
		self.chars += content


def _apiread(request, content, values):
	# look also at wikipedia.site.getUrl() and config.textfile_encoding
	conn = httplib.HTTPConnection(request[0])
	conn.request("GET", request[1])
	r1 = conn.getresponse()
	#print r1.status, r1.reason
	APIdata = r1.read()
	text = unicode(APIdata, textfile_encoding, errors = 'strict')

	APIdata = StringIO.StringIO(text.encode(textfile_encoding))
	parser = make_parser()				# Create a XML parser
	parser.setFeature(feature_namespaces, 0)	# Tell the parser we are not interested in XML namespaces
	dh = _GetData(content, values)			# Create the handler
	parser.setContentHandler(dh)			# Tell the parser to use our handler
	parser.parse(APIdata)				# Parse the input

	del parser
	APIdata.close()

	if (values == []): 
		return dh.chars
	return dh.data


def displayhtmlpage(form):
	result = ""

	for wiki in wikis:
		result += "<b>%s</b><br>\n" % wiki

		request = REQUEST_getHelp
		test = _apiread((wiki, request), 'error', [])
		test = re.split('\n', test)[29]
		actions = re.split('[:,]\s', test)[1:]

		request = REQUEST_getVersion % urllib.quote( "|".join(actions) )
		#print request
		test = _apiread((wiki, request), 'module', ['name', 'version'])
		#test = ["%s: %s" % item for item in test]
		a = lambda x: ( item[0], re.search('\.php (\d*?) ', item[1]).groups()[0], item[1] )
		#test = ["<tr>\n<td>%s</td><td>%s</td>\n</tr>\n" % item for item in test]
		test = ["<tr>\n<td>%s</td><td>%s</td><td>%s</td>\n</tr>\n" % a(item) for item in test]
		test = "".join(test)
	
		result += "<table>\n"
		result += test
		result += "</table>\n"

		result += "<br>"

	data = {'output':	result,
	}

	return displaystate_content % data



form = cgi.FieldStorage()

# operational mode
#action = form.getvalue('action', '')
#if action == 'adminlogs':
#	pass
#else:
html = displayhtmlpage(form)

print html
