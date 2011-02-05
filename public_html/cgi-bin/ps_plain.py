# -*- coding: utf-8 -*-
"""
panel-stylesheet 'plain' (module for panel.py)
"""

## @package ps_plain
#  @brief   panel-stylesheet 'plain'
#
#  @copyright Dr. Trigon, 2008-2010
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


content_type = "Content-Type: text/html"

tsnotice = "<b>%(text)s</b><br>"


# === page HTML codes === === ===
#
_minimal_page = """
<html>
<head>
  <title>%(title)s</title>
  <meta http-equiv="refresh" content="%(refresh)s">
</head>
<body>
<p><span style="font-family:sans-serif">
%(tsnotice)s
%(title)s<br><br><br>
%(content)s
%(footer)s
</span></p>
</body>
</html>
"""

page = content_type + """
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">""" + _minimal_page

admin_page = content_type + _minimal_page


# === footer HTML codes === === ===
#
footer = \
"""<small>DrTrigonBot web-interface, written by <a href="https://wiki.toolserver.org/view/User:DrTrigon">DrTrigon</a> 
(<a href="http://toolserver.org/~daniel/stats/">stat</a> /
<a href="http://toolserver.org/~daniel/stats/url_201007.html">url</a> /
<a href="http://munin.toolserver.org/index.html">info</a>).
<img src="https://wiki.toolserver.org/favicon.ico" border="0" 
alt="Toolserver"> <a href="http://tools.wikimedia.de/">Powered by Wikimedia Toolserver</a>.
<img src="http://de.selfhtml.org/src/favicon.ico" border="0" width="16" 
height="16" alt="SELFHTML"> <a href="http://de.selfhtml.org/index.htm">Thanks to SELFHTML</a>.</small>
"""
# with preprocessed (by daniel) statistics from '/mnt/user-store/stats/'

footer_w3c = \
"""<small>
<a href="http://validator.w3.org/check?uri=referer"><img 
src="http://www.w3.org/Icons/valid-html401-blue" 
alt="Valid HTML 4.01 Transitional" height="16" width="44" 
border="0"></a>
</small>"""

footer_w3c_css = \
"""<small>
<a href="http://jigsaw.w3.org/css-validator/check/referer">
    <img style="border:0;width:44px;height:16px"
        src="http://jigsaw.w3.org/css-validator/images/vcss-blue"
        alt="CSS ist valide!">
</a>
</small>"""
