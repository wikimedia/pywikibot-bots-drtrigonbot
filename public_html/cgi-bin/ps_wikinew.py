# -*- coding: utf-8 -*-
"""
panel-stylesheet 'wiki (new)' (module for panel.py)
"""

## @package ps_wikinew
#  @brief   panel-stylesheet 'wiki (new)'
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

tsnotice = """<div id="tsnotice">%(text)s</div><br>"""

page = content_type + """
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>%(title)s</title>
  <link rel="copyright" href="//creativecommons.org/licenses/by-sa/3.0/" >
  <!-- Idea to use Wiki stylesheet from: http://toolserver.org/~vvv/sulutil.php 
  BUT this is the new!! (done by myself) -->
  <!--<link rel="stylesheet" href="http://bits.wikimedia.org/de.wikipedia.org/load.php?debug=false&amp;lang=de&amp;modules=ext%%21wikihiero%%7Cmediawiki%%21legacy%%21commonPrint%%7Cmediawiki%%21legacy%%21shared%%7Cskins%%21vector&amp;only=styles&amp;skin=vector" type="text/css" media="all">-->
  <!--<link rel="stylesheet" href="//bits.wikimedia.org/de.wikipedia.org/load.php?debug=false&amp;lang=de&amp;modules=ext.gadget.CommonsDirekt%%2CExtra-Editbuttons%%2CVorlagenmeister%%2Cold-movepage%%7Cext.rtlcite%%2Cwikihiero%%7Cext.uls.nojs%%7Cext.visualEditor.viewPageTarget.noscript%%7Cmediawiki.legacy.commonPrint%%2Cshared%%7Cmw.PopUpMediaTransform%%7Cskins.vector&amp;only=styles&amp;skin=vector&amp;*" >-->
  <link rel="stylesheet" href="//bits.wikimedia.org/de.wikipedia.org/load.php?debug=false&amp;lang=de&amp;modules=ext.echo.badge%%7Cext.gadget.CommonsDirekt%%2CExtra-Editbuttons%%2CVorlagenmeister%%2Cold-movepage%%7Cext.visualEditor.viewPageTarget.noscript%%7Cext.wikihiero%%7Cmediawiki.legacy.commonPrint%%2Cshared%%7Cskins.common.interface%%7Cskins.vector.styles&amp;only=styles&amp;skin=vector&amp;*" >
  <link rel="stylesheet" href="../tsnotice.css">
  <meta http-equiv="refresh" content="%(refresh)s">
</head>
<body class="mediawiki">
<div id="mw-page-base" class="noprint"></div><div id="mw-head-base" class="noprint"></div><div id="content">
%(tsnotice)s
<h1 id="firstHeading" class="firstHeading">%(title)s</h1>
<div id="bodyContent">

%(content)s

%(footer)s

</div></div>

<div id="mw-panel" class="noprint">
<div id="p-logo"><a style="background-image: 
url(http://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Wikimedia_Community_Logo-Toolserver.svg/135px-Wikimedia_Community_Logo-Toolserver.svg.png);" 
href="/" title="Home"></a></div>
<div class="portal" id='p-navigation'><h5>navigation</h5><div class="body">
<ul>
<li><a href="https://wiki.toolserver.org/view/User:DrTrigon">TS</a> / <a href="https://labsconsole.wikimedia.org/wiki/DrTrigonBot">labs</a> Main Page</li>
<li><a href="https://bugzilla.wikimedia.org/describecomponents.cgi?product=Tool%%20Labs%%20tools">Bugzilla</a> tracker</li>
<li><a href="https://fisheye.toolserver.org/browse/drtrigon">SVN</a> / <a href="https://gerrit.wikimedia.org/r/#/admin/projects/?filter=pywikibot">GIT</a> repository</li>
<li><a href="info.py">Info</a></li>
</ul>
</div></div>
<div class="portal" id='p-status'><h5>status</h5><div class="body">
<table style="border-collapse: collapse; font-size: 11pt;">
%(p-status)s
</table>
</div></div>
</div>

<div id="footer">
<ul id="footer-places">
	<li><!--<a href="/wiki/Wikipedia:Datenschutz">...</a>--></li>
</ul>
<ul id="footer-icons" class="noprint">
	<li><a href="http://www.mediawiki.org/"><img src="http://bits.wikimedia.org/skins-1.5/common/images/poweredby_mediawiki_88x31.png" height="31" width="88" alt="Powered by MediaWiki" 
></a></li>
	<li><a href="http://wikimediafoundation.org/"><img src="http://de.wikipedia.org/images/wikimedia-button.png" width="88" height="31" alt="Wikimedia Foundation"></a></li>

	<li><a href="http://tools.wikimedia.de/"><img src="http://tools.wikimedia.de/images/wikimedia-toolserver-button.png" alt="Toolserver project"></a></li>
	<!--<li><a href="http://validator.w3.org/check?uri=referer"><img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Strict" height="31" width="88"></a></li>
	<li><a href="http://wikimediafoundation.org/wiki/Fundraising?s=cl-Wikipedia-free-mini-button.png"><img 
src="http://upload.wikimedia.org/wikipedia/meta/6/66/Wikipedia-free-mini-button.png" alt="Wikipedia...keep it free."></a></li>-->
</ul>

</div>
</body>
</html>
"""
