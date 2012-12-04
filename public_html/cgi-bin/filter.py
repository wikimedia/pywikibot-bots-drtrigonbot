#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""filter: Versatile/Generic (text) Page Filter Tool (CGI) for toolserver
(description)

to make it usable from server, use: 'chmod 755 filter.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""

## @package filter.py
#  @brief   filter: Versatile/Generic (text) Page Filter Tool (CGI) for toolserver
#
#  @copyright Dr. Trigon, 2012
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


# *other options additional to 'unshort' can an may be should
#  be implemented...
# *PROBLEMS with 'Content-Type ... utf-8' ... !!!!


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
  <title>filter: Versatile/Generic (text) Page Filter Tool</title>
</head>
<body>
<h3>filter: Versatile/Generic (text) Page Filter Tool</h3>
<p>%(footer)s</p>
<form action="filter.py" name="">
  <table>
  <tr>
    <td>url:</td>
    <td><input name="url" type="text" size="60" maxlength="200" value="%(url)s"></td>
    <td>(e.g. "http://blog.wikimedia.de/feed/")</td>
  </tr>
  <tr>
    <td>unshorten urls:</td>
    <td><input type="checkbox" name="unshort" value="1" %(unshort)s></td>
    <td>(this is VERY slow - be patient)</td>
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
param = {    'url': form.getvalue('url', ''),
         'unshort': form.getvalue('unshort', ''),
        }
url   = param['url']

secure = style.secure_url(url)    # security
content_type = style.content_type


if secure and url:
    import urllib, re, BeautifulSoup, time

    # external unshortener API from ...
    #unshort   = "http://realurl.org/api/v1/getrealurl.php?url=%s"
    #unshort   = "http://www.unshorten.it/api1.0.php?responseFormat=xml&shortURL=%s"    # needs API-key (free) now
    unshort   = "http://api.unshort.me/?t=xml&r=%s"
    skip_list = ['://identi.ca',
                 '.wikimedia.org',
                 '://wikimediafoundation.org',
                ]

    info = []

    tot_tic = time.time()

    # http://docs.python.org/library/urllib.html
    # http://docs.python.org/library/mimetools.html#mimetools.Message
    #url = urllib.unquote(url)
    f = urllib.urlopen(url)
    page_buf  = f.read()
    page_info = f.info()
    #print page_buf

    # prevent '502 bad gateway' errors
#    content_type = '; '.join(['Content-Type: %s' % page_info.gettype()] + page_info.getplist())
    content_type = "Content-Type: text/html;\n"

    toc = time.time()
    info += [ 'Page served by %s in %.3f secs.' % (url.split('/')[2], toc-tot_tic) ]

    if param['unshort']:
        tic = time.time()

        r = re.compile(r'(http(s?)://[^ "<\']+)')
        url_list = r.findall(page_buf)
        for (url, other) in set(url_list):
            skip = False
            for skip_url in skip_list:
                 if skip_url in url:
                     skip = True
                     break
            if skip: continue

            unshort_buf = urllib.urlopen(unshort % url).read()
            bs          = BeautifulSoup.BeautifulSoup(unshort_buf)
            #if (bs.status.contents[0] == "1"):
            #    longurl  = str(bs.real.contents[0])
            #if not bs.findAll('error'):
            #    longurl  = str(bs.fullurl.contents[0])
            if (bs.success.contents[0] == "true"):
                longurl  = str(bs.resolvedurl.contents[0])
                page_buf = page_buf.replace(url, longurl)

        toc = time.time()
        info += [ 'UnShortened by %s in %.3f secs.' % (unshort.split('/')[2], toc-tic) ]

    tot_toc = time.time()
    info = [ 'Served by toolserver.org in %.3f secs.' % (tot_toc-tot_tic) ] + info

    #page_buf += '\n<!-- %s -->' % '\n'.join(info)
    page_buf += '\n<!-- \n%s\n -->' % '\n'.join(info)

else:
    sel_dict = {'': '', '1': 'checked'}

    # disable XSS cross site scripting (code injection vulnerability)
    # http://amix.dk/blog/post/19432
    url = cgi.escape(url, quote=True)

    param.update({'footer': style.footer + style.footer_w3c, 'unshort': sel_dict[param['unshort']], 'url': url})
    page_buf = default_content % param


# send page to browser/receiver
print content_type
print page_buf
