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


# === panel HTML stylesheets === === ===
# MAY BE USING Cheetah (http://www.cheetahtemplate.org/) WOULD BE BETTER (or needed at any point...)
#
import ps_plain as style   # panel-stylesheet 'plain'


# === page HTML contents === === ===
#
default_content = \
"""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>XSaLT: XSL/XSLT Simple and Lightweight Tool</title>
</head>
<body>
<h3>XSaLT: XSL/XSLT Simple and Lightweight Tool</h3>
<p>%(footer)s</p>
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
</html>"""


# === CGI/HTML page view user interfaces === === ===
#


# === Main procedure entry point === === ===
#
form = cgi.FieldStorage()

# operational mode
url  = form.getvalue('url', '')
xslt = form.getvalue('xslt', '')

s1 = style.secure_url(url)    # security
# check xslt does point to allowed local files on the server (the
# '.xslt' in same directory as script) and not any other, e.g. '../'
import os
allowed = [item for item in os.listdir('.') if '.xslt' in item]
s2 = (xslt in allowed)
secure = s1 and s2

print style.content_type

if secure and url and xslt:
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
    # disable XSS cross site scripting (code injection vulnerability)
    # http://amix.dk/blog/post/19432
    url  = cgi.escape( url, quote=True)
    xslt = cgi.escape(xslt, quote=True)

    print default_content % {'url': url, 'xslt': xslt, 'footer': style.footer + style.footer_w3c}
