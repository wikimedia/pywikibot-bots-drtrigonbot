#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""XSaLT: XSL/XSLT Simple and Lightweight Tool (CGI) for toolserver

to make it usable from server, use: 'chmod 755 xsalt.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

## @package xsalt.py
#  @brief   XSaLT: XSL/XSLT Simple and Lightweight Tool
#
#  @copyright Dr. Trigon, 2011
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


# === python CGI script === === ===
#
import cgitb    # debug
cgitb.enable()  #

import cgi


# === module imports === === ===
#


# === CGI/HTML page view user interfaces === === ===
#


# === Main procedure entry point === === ===
#
form = cgi.FieldStorage()

# operational mode
url  = form.getvalue('url', '')
xslt = form.getvalue('xslt', '')

content_type = "Content-Type: text/html; charset=UTF-8"
print content_type

if url and xslt:
    # http://docs.python.org/library/urllib.html#examples
    import urllib
    f = urllib.urlopen(url)
    #print f.read()

    # http://lxml.de/xpathxslt.html
    from lxml import etree
    doc = etree.parse(f)
    xslt_root = etree.XML( open(xslt).read() )
    transform = etree.XSLT(xslt_root)
    result = transform(doc)
    #print str(result)
    #print result.getroot().text
    print result
else:
    print \
"""
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>XSaLT: XSL/XSLT Simple and Lightweight Tool</title>
</head>
<body>
<h3>XSaLT: XSL/XSLT Simple and Lightweight Tool</h3>
<p><small><img src="https://wiki.toolserver.org/favicon.ico" border="0" 
alt="Toolserver"> <a href="http://tools.wikimedia.de/">Powered by Wikimedia Toolserver</a>
-
<img src="http://de.selfhtml.org/src/favicon.ico" border="0" width="16" 
height="16" alt="SELFHTML"> <a href="http://de.selfhtml.org/xml/darstellung/xslgrundlagen.htm">Thanks to SELFHTML</a>
-
<a href="http://validator.w3.org/check?uri=referer"><img 
src="http://www.w3.org/Icons/valid-html401-blue" 
alt="Valid HTML 4.01 Transitional" height="16" width="44" 
border="0"></a>
</small></p>
<form action="xsalt.py" name="">
  <table>
  <tr>
    <td>url:</td>
    <td><input name="url" type="text" size="60" maxlength="200" value="%(url)s"></td>
    <td>(e.g. "http://blog.wikimedia.de/feed/")</td>
  </tr>
  <tr>
    <td>xslt:</td>
    <td><input name="xslt" type="text" size="60" maxlength="200" value="%(xslt)s"></td>
    <td>(e.g. "rss2html.xslt")</td>
  </tr>
  </table>

  <input type="submit" value=" OK ">
</form>
</body>
</html>""" % {'url': url, 'xslt': xslt}
