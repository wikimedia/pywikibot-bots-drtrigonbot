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


#content_type = "Content-Type: text/html"
content_type = "Content-Type: text/html; charset=UTF-8\n"

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

debug_page = content_type + _minimal_page % { 'title': 'DEBUG PAGE',
                                              'refresh': '',
                                              'tsnotice': '',
                                              'content': '%s',
                                              'footer': '', }


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


# === functions === === ===
#
# https://wiki.toolserver.org/view/Toolserver_notice
# http://toolserver.org/sitenotice
# http://www.mail-archive.com/toolserver-l@lists.wikimedia.org/msg01679.html
def print_tsnotice():
    try:
        notice = open('/var/www/sitenotice', 'r').read()
        if notice:
            return tsnotice % { 'text': notice }
    except IOError:
        pass
    return ''

# security
# http://lists.wikimedia.org/pipermail/toolserver-l/2011-September/004403.html
# check url not to point to a local file on the server, e.g. 'file://'
# (same code as used in subster.py)
def secure_url(url):
    # check no.1
    s1 = False
    for item in ['http://', 'https://']:
        s1 = s1 or (url[:len(item)] == item)
    secure = s1

    return secure


# === labs conversion patch: functions === === ===
#
def change_logo(content, environ):
    # labs patch: adopt logo for labs server instead of TS (default)
    TS   = 'http://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Wikimedia_Community_Logo-Toolserver.svg/135px-Wikimedia_Community_Logo-Toolserver.svg.png'
    labs = 'http://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Wikimedia_labs_logo.svg/135px-Wikimedia_labs_logo.svg.png'
    if ('HTTP_HOST' in environ) and (not (environ['HTTP_HOST'] == 'toolserver.org')):
        content = content.replace(TS, labs)
    return content

def host(environ):
    if ('HTTP_HOST' in environ) and (not (environ['HTTP_HOST'] == 'toolserver.org')):
        return 'labs'
    else:
        return 'ts'


# === labs conversion patch: variables === === ===
#
from config import *
