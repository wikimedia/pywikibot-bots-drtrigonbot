# -*- coding: utf-8  -*-
"""
...
"""
#
# @copyright Dr. Trigon, 2010
#
# @todo      ...
#
# @section FRAMEWORK
#
# Python wikipedia robot framework, DrTrigonBot.
# @see http://pywikipediabot.sourceforge.net/
# @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# @section LICENSE
#
# Distributed under the terms of the MIT license.
# @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
__version__ = '$Id$'
#

# Standard library imports
from HTMLParser import HTMLParser


# ADDED: new (r19)
# REASON: needed by various bots
def removeHTMLParts(text, keeptags = ['tt', 'nowiki', 'small', 'sup']):
	"""
	Return text without portions where HTML markup is disabled

	Parts that can/will be removed are --
	* HTML and all wiki tags

	The exact set of parts which should NOT be removed can be passed as the
	'keeptags' parameter, which defaults to ['tt', 'nowiki', 'small', 'sup'].
	"""
	# try to replace with 'pywikibot.removeDisabledParts()' from 'textlib' !!

	# thanks to http://www.hellboundhackers.org/articles/841-using-python-39;s-htmlparser-class.html
	parser = _GetDataHTML()
	parser.keeptags = keeptags
	parser.feed(text)
	parser.close()
	return parser.textdata

# thanks to http://docs.python.org/library/htmlparser.html
class _GetDataHTML(HTMLParser):
	textdata = u''
	keeptags = []

	def handle_data(self, data):
		self.textdata += data

	def handle_starttag(self, tag, attrs):
		if tag in self.keeptags: self.textdata += u"<%s>" % tag

	def handle_endtag(self, tag):
		if tag in self.keeptags: self.textdata += u"</%s>" % tag

#----------------------------------
# Functions dealing with templates
#----------------------------------

# ADDED: new (r20)
# REASON: needed by various bots
def glue_template_and_params(template_and_params):
	"""Return wiki text of template glued from params.

	You can use items from extract_templates_and_params here to get
	an equivalent template wiki text (it may happen that the order
	of the params changes).
	"""
	(template, params) = template_and_params

	text = u''
	for item in params:
		text +=  u'|%s=%s\n' % (item, params[item])

	return u'{{%s\n%s}}' % (template, text)


