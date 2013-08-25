#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DrTrigon Bot status panel (CGI) for toolserver

to make it usable from server, use: 'chmod 755 panel.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

## @package subster_mail_queue.py
#  @brief   DrTrigonBot subster mail queue
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
# http://www.ibm.com/developerworks/aix/library/au-python/
import os

import mailbox


# === panel HTML stylesheets === === ===
# MAY BE USING Cheetah (http://www.cheetahtemplate.org/) WOULD BE BETTER (or needed at any point...)
#
#import ps_plain as style   # panel-stylesheet 'plain'
#import ps_simple as style  # panel-stylesheet 'simple'
#import ps_wiki as style    # panel-stylesheet 'wiki (monobook)'
import ps_wikinew as style # panel-stylesheet 'wiki (new)' not CSS 2.1 compilant


# === page HTML contents === === ===
#
displaystate_content = \
"""<br>%(oldlog)s<br>"""

a = """<tr>
<td>%i</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>"""
b = "<a href='/~drtrigon/cgi-bin/subster_mail_queue.py?action=content&amp;no=%s'>%s</a>"


# === functions === === ===
#


# === CGI/HTML page view user interfaces === === ===
#
def displaystate(form):
	data = {}

        mbox = mailbox.mbox('../../data/subster/mail_inbox')

        buf = []
        buf.append( '\n<table>' )
        buf.append( 
"""<tr>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
</tr>""" % ('no.', 'sender', 'subject', 'timestmp') )

        for i, message in enumerate(mbox):
            sender   = message['from']          # Could possibly be None.
            subject  = message['subject']       # Could possibly be None.
            timestmp = message['date']       # Could possibly be None.

            if sender:
                # data found
                buf.append( a % (i, (b % (i, cgi.escape(sender))), subject, timestmp) )
        buf.append( '</table>\n\n' )

	data.update({   'oldlog':	"\n".join(buf),
			'refresh':	'',
			'title':	'DrTrigonBot subster mail queue',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	"<tr><td><td></tr>",
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data

def content(form):
	data = {}

        no = int(form.getvalue('no', '-1'))
        if no < 0: return displaystate(form)

        mbox = mailbox.mbox('../../data/subster/mail_inbox')

        buf = []

        for i, message in enumerate(mbox):
            if (i != no): continue
            text = cgi.escape(message.as_string(True))
            text = text.replace("\n", "<br>\n")
            buf.append( text )
        buf.append( '\n' )

	data.update({   'oldlog':	"\n".join(buf),
			'refresh':	'',
			'title':	'DrTrigonBot subster mail queue',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	"<tr><td><td></tr>",
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data


# === Main procedure entry point === === ===
#
form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', 'displaystate')
print locals()[action](form)
