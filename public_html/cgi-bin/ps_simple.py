# -*- coding: utf-8 -*-
"""
panel-stylesheet 'simple' (module for panel.py)
"""

## @package ps_simple
#  @brief   panel-stylesheet 'simple'
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


from ps_plain import *

tsnotice = """<div class="tsnotice" id="tsnotice">%(text)s</div>"""

page = content_type + """
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>%(title)s</title>
  <!-- Idea to use Sphinx stylesheet from: http://toolserver.org/~pywikipedia/nightly/
  and http://toolserver.org/~valhallasw/.style/main.css -->
  <link rel="stylesheet" href="http://sphinx.pocoo.org/_static/default.css">
  <link rel="stylesheet" href="http://sphinx.pocoo.org/_static/pygments.css">
  <link rel="stylesheet" href="../tsnotice.css">
  <meta http-equiv="refresh" content="%(refresh)s">
</head>
<body>
%(tsnotice)s
<div class="body">
<h1>%(title)s</h1>

%(content)s

%(footer)s

</div>
</body>
</html>
"""
