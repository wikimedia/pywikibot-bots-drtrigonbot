# -*- coding: utf-8 -*-
"""
panel-stylesheet 'wiki (monobook)' (module for panel.py)
"""

## @package ps_wiki
#  @brief   panel-stylesheet 'wiki (monobook)'
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

tsnotice = """<br><div class="tsnotice" id="tsnotice">%(text)s</div>"""

page = content_type + """
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>%(title)s</title>
  <!-- Idea to use Wiki stylesheet from: http://toolserver.org/~vvv/sulutil.php -->
  <link rel="stylesheet" href="http://en.wikipedia.org/skins-1.5/monobook/main.css">
  <link rel="stylesheet" href="http://bits.wikimedia.org/skins-1.5/common/shared.css">
  <link rel="stylesheet" href="../tsnotice.css">
  <!--<link rel="stylesheet" media="all" type="text/css" href="http://tools.wikimedia.de/~vvv/inc/ts.css" />-->
  <meta http-equiv="refresh" content="%(refresh)s">
</head>
<body class="mediawiki">
<div id="globalWrapper"><div id="column-content"><div id="content">
%(tsnotice)s
<h1>%(title)s</h1>

%(content)s

%(footer)s

</div></div>

<div id="column-one">
<div class="portlet" id="p-logo"><a style="background-image: 
url(http://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Wikimedia_Community_Logo-Toolserver.svg/135px-Wikimedia_Community_Logo-Toolserver.svg.png);" 
href="http://toolserver.org/~vvv/" title="Home"></a></div>
<div class='portlet' id='p-navigation'><h5>navigation</h5><div class='pBody'>
<ul>
<li><a href="http://tools.wikimedia.de/~vvv/">Main Page</a></li>
<li><a href="http://jira.ts.wikimedia.org/browse/VVV">Bug tracker</a></li>
<li><a href="http://fisheye.ts.wikimedia.org/browse/vvv">SVN repository</a></li>
</ul>
</div></div>
<div class='portlet' id='p-status'><h5>status</h5><div class='pBody'>
<table style="width: 100%%; border-collapse: collapse;">
<tr style='background-color: #a5ffbb'><td style='width: 25%%; padding-left: 1em;'>c_u_s</td><td>OK</td></tr>
<tr style='background-color: #a5ffbb'><td style='width: 25%%; padding-left: 1em;'>sum_disc</td><td>OK</td></tr>
<tr style='background-color: #a5ffbb'><td style='width: 25%%; padding-left: 1em;'>subster</td><td>OK</td></tr>
<tr style='background-color: #e7ffbb'><td style='width: 25%%; padding-left: 1em;'>other</td><td>Warning</td></tr>
</table>
</div></div>
</div>

<table id="footer" style="text-align: left; clear:both;" width="100%%"><tr><td><a href="http://tools.wikimedia.de/"><img 
src="http://tools.wikimedia.de/images/wikimedia-toolserver-button.png" alt="Toolserver project"></a>
 <a href="http://validator.w3.org/check?uri=referer"><img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Strict" height="31" width="88"></a> <a 
href="http://wikimediafoundation.org/wiki/Fundraising?s=cl-Wikipedia-free-mini-button.png"><img src="http://upload.wikimedia.org/wikipedia/meta/6/66/Wikipedia-free-mini-button.png" 
alt="Wikipedia...keep it free."></a>
</td></tr></table>

</div>
</body>
</html>
"""
