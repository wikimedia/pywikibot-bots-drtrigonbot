#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DrTrigon Bot status panel (CGI) for toolserver

to make it usable from server, use: 'chmod 755 panel.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

## @package panel.py
#  @brief   DrTrigon Bot status panel for toolserver
#
#  @copyright Dr. Trigon, 2008-2011
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
from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import os, re, sys, copy

#import Image,ImageDraw
import matplotlib.pyplot as plt
import cStringIO


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
"""Actual state: <img src="%(botstate_daily)s" width="15" height="15" alt="Botstate">
                 <img src="%(botstate_cont)s" width="15" height="15" alt="Botstate"><br><br>
Time now: %(time)s<br><br>

<a href="%(loglink)s">Latest</a> bot status message log: <b>%(botlog)s</b><br><br>
Current log files: %(currentlog)s<br><br>
<a href="%(oldlink)s">Old log</a> files: <i>%(oldlog)s</i><br><br>
See also <a href="%(logstat)s">log statistics</a> <small>(also available in <a href="%(logstatraw)s">raw/plain format</a>)</small>.<br><br>"""

logstat_content = \
"""Evaluated data period from %(start_date)s to %(end_date)s.<br>
<br>
<table>
<tr><td>Total runs:</td><td>%(run_count)s</td></tr>
<tr><td>Successful runs:</td><td>%(successful_count)s</td></tr>
<tr><td>Difference:</td><td>%(run_diff)s</td></tr>
</table>
<br>
History compressed: %(histcomp_count)s (times)<br>
<br>
Problem rate (in %%):<br>
%(reliability)s<br>
<!--<a href="%(graphlink)s"><img src="%(graphlink)s"></a><br>
<br>
Warnings (%(warn_total)s distilled to %(warn_dist)s):<br>
%(warnings)s<br>
<br>-->"""

adminlogs_content = \
"""Log file count: %(logcount)s<br>
<p>%(message)s</p>
<form action="panel.py">
  <input type="hidden" name="action" value="adminlogs">
  <p>
    %(oldloglist)s
  </p>
  <input type="submit" value=" Delete ">
  <input type="reset" value=" Reset ">
</form>"""


# === external (wiki) status links === === ===
#
botstate_img = {#'green':	'http://upload.wikimedia.org/wikipedia/commons/3/3c/ButtonGreen.svg',
		'green':	'http://upload.wikimedia.org/wikipedia/commons/6/65/ButtonGreen.png',
		#'orange':	'http://upload.wikimedia.org/wikipedia/commons/b/b0/ButtonYellow.svg',
		#'red':		'http://upload.wikimedia.org/wikipedia/commons/9/97/ButtonRed.svg',
		'orange':	'http://upload.wikimedia.org/wikipedia/commons/b/bf/ButtonYellow.png',
		'red':		'http://upload.wikimedia.org/wikipedia/commons/6/65/ButtonRed.png',
		}

html_color = {	'green':	'#00ff00',
		'orange':	'#ffff00',
		'red':		'#ff0000',
		}


# === bot status surveillance === === ===
#
bottimeout = 24
botdonemsg = 'DONE'

# use classic 're' since 'pyparsing' does not work with unicode
regex = re.compile(r'(?P<timestamp>\S+\s\S+)\s(?P<file>\S+)\s*(?P<level>\S+)\s*(?P<message>.*)')#, re.U)


# === functions === === ===
#
def oldlogfiles(all=False):
	localdir = os.path.dirname(os.path.join('..','DrTrigonBot','.'))
	files = os.listdir( localdir )
	archive, current = [], []
	for item in files:
		info = item.split('.')
		if   (len(info) == 2):
			current.append( item )
			if all: archive.append( item )
		elif (len(info) == 3):
			archive.append( item )

	archive.sort()
	current.sort()

	return (localdir, archive, current)

#def graph(xdata, xscale=1, xticks=10, xmajor=5, yscale=1, yticks=10, ymajor=1):
#	X,Y = 500, 275			# image width and height
#
#	img = Image.new("RGB", (X,Y), "#FFFFFF")
#	draw = ImageDraw.Draw(img)
#
#	#draw some axes and markers
#	for i in range(X/10):
#		draw.line((i*10+30, Y-15, i*10+30, 20), fill="#DDD")
#		if i % xmajor == 0:
#			draw.text((xscale*(i*xticks)+15, Y-15), `i*xticks`, fill="#000")
#	for j in range(1,Y/10-2):
#		if i % ymajor == 0:
#			#draw.text((xscale*(0),Y-15-yscale*(j*yticks)), `j*yticks`, fill="#000")
#			draw.text((xscale*(0),Y-15-yscale*(2*j*yticks)), `j*yticks`, fill="#000")	# cheap patch
#	draw.line((20,Y-19,X,Y-19), fill="#000")
#	draw.line((19,20,19,Y-18), fill="#000")
#
#	#graph data (file)
#	#log = file(r"c:\python\random_img\%s" % filename)
#	#log = file(filename)
#	for (i, value) in enumerate(xdata):
#		#value = int(value.strip())
#		draw.line((xscale*(i)+20,Y-20,xscale*(i)+20,Y-20-yscale*(value)), fill="#55d")
#
#	#write to file object
#	f = cStringIO.StringIO()
#	img.save(f, "PNG")
#	f.seek(0)
#
#	#output to browser
#	return "Content-type: image/png\n\n" + f.read()

# http://www.scipy.org/Cookbook/Matplotlib/Using_MatPlotLib_in_a_CGI_script
def graph(xdata, *args, **kwargs):
	fig = plt.figure(figsize=(10,4))
	ax = fig.add_subplot(111)
	plot1 = ax.bar(range(len(xdata)), xdata)

	ax.grid(True)

	#plt.show()

	#write to file object
	f = cStringIO.StringIO()
	plt.savefig(f, format="PNG")
	f.seek(0)

	#output to browser
	return "Content-type: image/png\n\n" + f.read()

# http://oreilly.com/pub/h/1968
# http://forum.codecall.net/python-tutorials/33361-developing-basic-irc-bot-python.html
def irc_status():
	import socket
	import string

	HOST     = "irc.wikimedia.org"
	PORT     = 6667
	NICK     = "DrTrigonBot_panel"
	IDENT    = NICK.lower()
	REALNAME = NICK
	CHAN     = "#de.wikipedia"
	readbuffer=""

	s=socket.socket( )
	s.connect((HOST, PORT))
	s.send("NICK %s\r\n" % NICK)
	s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
	#s.send('JOIN ' + CHAN + '\r\n') # Join the pre defined channel
	s.send('NAMES ' + CHAN + '\r\n') # Show all Nicks in channel

	users = []
	while (not users):
		readbuffer=readbuffer+s.recv(1024)
		temp=string.split(readbuffer, "\n")
		readbuffer=temp.pop( )

		for line in temp:
			line=string.rstrip(line)
			line=string.split(line)

			if (line[1] == "353"):  # answer to 'NAMES' request
				i = line.index(CHAN)
				users = line[(i+1):]

	del s

	botname = "DrTrigonBot"
	return ((botname in users) or
		(":"+botname in users), users)


# === CGI/HTML page view user interfaces === === ===
#
def displaystate(form):
	data = {}

	(localdir, files, current) = oldlogfiles()
	data['loglink'] = os.path.join(localdir, 'mainbot.log')

	b = file(data['loglink'], "r")
	d = b.readlines()
	b.close()

	d.reverse()

	data['botlog'] = ""
	# or use 'regex' here...
	for item in d:
	    try:    data['botlog'] = re.split('\s+', item, maxsplit=4)[-1].strip()
	    except: pass
	    if data['botlog']: break

	lastrun = (time() - os.stat(data['loglink']).st_mtime)
	botmsg = data['botlog'].strip()

	data['botstate_daily'] = botstate_img['red']
	color = html_color['red']
	state_text = "n/a"
	if (lastrun <= (bottimeout*60*60)):
		if   (botmsg == botdonemsg):
			data['botstate_daily'] = botstate_img['green']
			color = html_color['green']
			state_text = "OK"
		elif (botmsg.find(botdonemsg) == 0):
			data['botstate_daily'] = botstate_img['orange']
			color = html_color['orange']
			state_text = "problem"
		elif (lastrun <= 5*60):  # during run is also green (thus: lastrun <= 5*60)
			data['botstate_daily'] = botstate_img['green']
			color = html_color['green']
			state_text = "running"
		else:
			data['botstate'] = botstate_img['orange']
			color = html_color['orange']

	data['botstate_cont'] = botstate_img['red']
	if irc_status()[0]:
		data['botstate_cont'] = botstate_img['green']
		irc_color = html_color['green']
		irc_state_text = "OK"
	else:
		data['botstate_cont'] = botstate_img['orange']
		irc_color = html_color['orange']
		irc_state_text = "problem"

	status  = "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': color, 'bot': 'daily:', 'state': state_text}
	status += "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': irc_color, 'bot': 'cont.:', 'state': irc_state_text}

	data['currentlog'] = ", ".join([ '<a href="%s">%s</a>' % (os.path.join(localdir, item), item) for item in current ])

	data.update({	'time':		asctime(localtime(time())),
			'oldlog':	", ".join(files),
			'oldlink':	r"http://toolserver.org/~drtrigon/DrTrigonBot/",
			'logstat':	sys.argv[0] + r"?action=logstat",
			'logstatraw':	sys.argv[0] + r"?action=logstat&amp;format=plain",
			'refresh':	'15',
			'title':	'DrTrigonBot status panel',
			'tsnotice': 	style.print_tsnotice(),
			'p-status':	status,
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data

def adminlogs(form):
	data = {}

	filelist = form.getvalue('filelist', [])
	if type(filelist) == type(''): filelist = [filelist]

	data['message'] = ''

	(localdir, files, current) = oldlogfiles()
	files_str = map(str, files)

	if (len(filelist) > 0):
		data['message'] = []
		for item in filelist:
			if (item in files_str):
				os.remove( os.path.join(localdir, item) )
			else:
				data['message'].append( 'Warning: "%s" is NOT a log file! Nothing done.' % item )
		data['message'].append( '%i log file(s) deleted.' % (len(filelist)-len(data['message'])) )
		data['message'] = '<br>\n'.join(data['message'])
		(localdir, files, current) = oldlogfiles()

	checkbox_tmpl = '<input type="checkbox" name="filelist" value="%(datei)s">%(datei)s<br>'

	#data.update({	'oldloglist':	'\n'.join([checkbox_tmpl % {'datei':item} for item in files[:-5]]),
	data.update({	'oldloglist':	'\n'.join([checkbox_tmpl % {'datei':item} for item in files]),
			'logcount':	len(files),
			'refresh':	'',
			'title':	'DrTrigonBot log admin panel',
			'tsnotice': 	'',
			'content':	adminlogs_content,
			'footer': 	'',
	})

	return (style.admin_page % data) % data

def logstat(form):
	format = form.getvalue('format', 'html')

#	(localdir, files, log) = oldlogfiles(all=True)
	(localdir, files, log) = oldlogfiles()

	stat = {'run_count':		0, 
		'histcomp_count':	0, 
		'successful_count':	0, 
		'warn_list':		[], 
		'reliability_list':	[], 
#		'start_date':		strptime(os.path.splitext(files[0])[1], "%Y-%m-%d"),
#		'end_date':		strptime(os.path.splitext(files[-1])[1], "%Y-%m-%d"),
		'start_date':		strptime("2011-12-25", "%Y-%m-%d"),
		'end_date':		strptime("2011-12-28", "%Y-%m-%d"),
		'warn_total':		0, 
		'warn_dist':		0,  }

#	for item in files:
#		logfile = os.path.join(localdir, item)
#		f = open(logfile, "r")
#		buffer = re.split('\n', f.read(-1))
#		f.close()

	logfile = os.path.join(localdir, files[0])
	f = open(logfile, "r")
	buffer = f.read(-1).strip().split("\n")
	f.close()

	# statistics (like mentioned in 'logging.statistics')
	count     = { 'debug': 0, 'warn': 0, 'info': 0, 'error': 0, 'critical': 0, 'unknown': 0, }
	events    = { 'start':     'SCRIPT CALL:',
	              'end':       botdonemsg,
	              'histcomp':  '* Compressing of histories:',
	              'warn?':     '* Processing Warnings:',
	              'backlink?': '* Processing Template Backlink List:', }
	etiming   = { 'start': [], 'end': [], 'histcomp': [], 'warn?': [], 'backlink?': [],
	              'mainstart': None, 'mainend': None, }
	resources = { 'files': set(), }

	#How many requests are being handled per second, how much of various resources are 

	# gather statistics
	etiming['mainstart'] = regex.match(buffer[0]).groupdict()['timestamp']
	etiming['mainend']   = regex.match(buffer[-1]).groupdict()['timestamp']
	for line in buffer:
		if not line.strip(): continue
		try:
			info = regex.match(line).groupdict()

			lvl = info['level'].lower()
			count[ 'unknown' if lvl not in count else lvl ] += 1

			for e in events:
				if events[e] in info['message']:
					etiming[e].append( info['timestamp'] )

			resources['files'].add( info['file'] )
		except AttributeError:
			pass

	# evaluate statistics
	#in use, how long we've been up. 


	#stat['warn_total'] = len(stat['warn_list'])
	stat['warn_total'] = None
	stat['warn_list'] = list(set(stat['warn_list']))
	#stat['warn_dist'] = len(stat['warn_list'])
	stat['warn_dist'] = None
	stat['warn_list'].sort()

	data = copy.deepcopy(stat)
	data.update({'start_date':		str(strftime("%a %b %d %Y", stat['start_date'])),
		'end_date':		str(strftime("%a %b %d %Y", stat['end_date'])),
		'run_diff':		(int(stat['run_count']) - int(stat['successful_count'])),
		#'reliability':		[ "%.2f" % (100*item[1]) for item in stat['reliability_list'] ],
		'reliability':		str(count) + str(etiming) + str(resources),
		#'warnings':		"<br>".join(stat['warn_list']),
		'warnings':		None,
		#'graphlink':		sys.argv[0] + r"?action=logstat&format=graph",
		'graphlink':		None,
	})


	if (format == 'plain'): return "Content-Type: text/plain\n\n%s" % str(stat)
	if (format == 'graph'):
		xdata = [ item[1]*100 for item in stat['reliability_list'] ]
		return graph(xdata, xscale=3, xticks=10, xmajor=1, yscale=4, yticks=10, ymajor=1)

	data.update({	'refresh':	'',
			'title':	'DrTrigonBot log statistics',
			'tsnotice': 	style.print_tsnotice(),
			#'content':	logstat_content,
			'p-status':	'<tr><td></td></tr>',
			'footer': 	style.footer + style.footer_w3c,
	})
	data['content'] = logstat_content % data

	return style.page % data


# === Main procedure entry point === === ===
#
form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', 'displaystate')
print locals()[action](form)
