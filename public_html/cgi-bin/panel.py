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
"""Actual state: <img src="%(botstate)s" width="15" height="15" alt="Botstate"><br><br>
Time now: %(time)s<br><br>

<a href="%(loglink)s">Latest</a> bot status message log: <b>%(botlog)s</b><br><br>
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
<!--Problem rate (in %%):<br>
%(reliability)s<br>
<a href="%(graphlink)s"><img src="%(graphlink)s"></a><br>
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


# === functions === === ===
#
def oldlogfiles(all=False):
	#localdir = os.path.dirname('../DrTrigonBot/')
	localdir = os.path.dirname(os.path.join('..','DrTrigonBot','.'))
	files = os.listdir( localdir )
	#files = [int(item[:-4]) for item in files]
	buffer = files
	files = []
	for item in buffer:
		if item[:-4].isdigit(): files.append( int(item[:-4]) )
	a = max(files)
	if not all: files.remove(a)
	log = os.path.join(localdir, str(a) + ".log")

	return (localdir, files, log)

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

	(localdir, files, data['loglink']) = oldlogfiles()

	b = file(data['loglink'], "r")
	d = b.readlines()
	b.close()

	#buffer = os.path.join(localdir, data['loglink']) + str(b.readlines())

	d.reverse()

	data['botlog'] = ""
	for item in d:
	    try:    data['botlog'] = re.split(':: ', item)[-1].strip()
	    except: pass
	    if data['botlog']: break

	#buffer = data['botlog'] +"\n"+ str(files)

	files = [str(item)+".log" for item in files]
	files.sort()
	buf = ", "

	lastrun = (time() - os.stat(data['loglink']).st_mtime)
	botmsg = data['botlog'].strip()

	data['botstate'] = botstate_img['red']
	color = html_color['red']
	state_text = "n/a"
	if (lastrun <= (bottimeout*60*60)):
		if   (botmsg == botdonemsg):
			data['botstate'] = botstate_img['green']
			color = html_color['green']
			state_text = "OK"
		elif (botmsg.find(botdonemsg) == 0):
			data['botstate'] = botstate_img['orange']
			color = html_color['orange']
			state_text = "problem"
		elif (lastrun <= 5*60):  # during run is also green (thus: lastrun <= 5*60)
			data['botstate'] = botstate_img['green']
			color = html_color['green']
			state_text = "running"
		else:
			data['botstate'] = botstate_img['orange']
			color = html_color['orange']

	if irc_status()[0]:
		irc_color = html_color['green']
		irc_state_text = "OK"
	else:
		irc_color = html_color['orange']
		irc_state_text = "problem"

	status  = "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': color, 'bot': 'all:', 'state': state_text}
	status += "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': irc_color, 'bot': 'irc:', 'state': irc_state_text}

	data.update({	'time':		asctime(localtime(time())),
			'oldlog':	buf.join(files),
			'oldlink':	r"http://toolserver.org/~drtrigon/DrTrigonBot/",
			'logstat':	sys.argv[0] + r"?action=logstat",
			'logstatraw':	sys.argv[0] + r"?action=logstat&amp;format=plain",
			'refresh':	'15',
			'title':	'DrTrigonBot status panel',
			'tsnotice': 	style.print_tsnotice(),
			#'content':	displaystate_content,
			'p-status':	status,
			#'footer': 	style.footer + style.footer_w3c + style.footer_w3c_css,
			'footer': 	style.footer + style.footer_w3c, # wiki (new) not CSS 2.1 compilant
	})
	data['content'] = displaystate_content % data

	return style.page % data

def adminlogs(form):
	data = {}

	filelist = form.getvalue('filelist', [])
	if type(filelist) == type(''): filelist = [filelist]

	data['message'] = ''

	(localdir, files, log) = oldlogfiles()
	files_str = map(str, files)

	if (len(filelist) > 0):
		data['message'] = []
		for item in filelist:
			if (item in files_str): os.remove( os.path.join(localdir, str(item)+".log") )
			else: data['message'].append( 'Warning: "%s" is NOT a log file! Nothing done.' % item )
			#pass
		data['message'].append( '%i log file(s) deleted.' % (len(filelist)-len(data['message'])) )
		data['message'] = '<br>\n'.join(data['message'])
		(localdir, files, log) = oldlogfiles()

	checkbox_tmpl = '<input type="checkbox" name="filelist" value="%(datei)s">%(datei)s<br>'

	buf = '\n'
	files.sort()
	data.update({	'oldloglist':	buf.join([checkbox_tmpl % {'datei':item} for item in files[:-5]]),
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

	(localdir, files, log) = oldlogfiles(all=True)
	files = [str(item)+".log" for item in files]
	files.sort()
	buf = ", "

	stat = {'run_count':		0, 
		'histcomp_count':	0, 
		'successful_count':	0, 
		'warn_list':		[], 
		'reliability_list':	[], 
		'start_date':		strptime(files[0], "%Y%m%d.log"),
		'end_date':		strptime(files[-1], "%Y%m%d.log"),
		'warn_total':		0, 
		'warn_dist':		0,  }

	for item in files:
		logfile = os.path.join(localdir, item)
		f = open(logfile, "r")
		buffer = re.split('\n', f.read(-1))
		f.close()
		status = 0
		request_total = 0
		request_failed = 0
		for line in buffer:
			#line.append(None)
			if ('SCRIPT CALL:' in line): stat['run_count'] += 1
			elif ('* Compressing of histories:' in line): stat['histcomp_count'] += 1
			elif ('Done.' in line): stat['successful_count'] += 1
			elif ('progress: 0.0% (0 of ' in line):
				try:	request_total += int(re.split('\s|\)', line)[6])
				except: request_total += int(re.split('\s|\)', line)[4])	# work-a-round for old format
			elif ('* Processing Warnings:' in line): status += 1
			elif (status == 1) and ('*Bot warning message:' in line):
				request_failed += 1
				try:	(timestmp, data) = re.split('::', line)
				except:	data = line						# work-a-round for old format
				stat['warn_list'].append( data )
			elif ('* Processing Template Backlink List:' in line): status += 1
			#elif ('SCRIPT CALL:' in line): stat['run_count'] += 1
		if request_total != 0: stat['reliability_list'].append( (item, float(request_failed)/float(request_total)) )

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
		'reliability':		None,
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
