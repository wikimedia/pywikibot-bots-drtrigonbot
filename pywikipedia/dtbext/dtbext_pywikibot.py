
"""
...
"""

#
# (C) Dr. Trigon, 2009
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', 'sum_disc-conf.py', ...
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id: dtbext/pywikibot.py 0.2.0019 2009-11-13 23:43 drtrigon $'
#

# Standard library imports
from HTMLParser import HTMLParser


# ====================================================================================================
#  textlib.py
# ====================================================================================================

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


