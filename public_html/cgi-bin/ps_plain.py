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
