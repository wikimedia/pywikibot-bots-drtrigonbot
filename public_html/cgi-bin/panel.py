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
import datetime
# http://www.ibm.com/developerworks/aix/library/au-python/
import os, re, sys, copy

#import Image,ImageDraw
import matplotlib.pyplot as plt
# http://matplotlib.sourceforge.net/api/dates_api.html?highlight=year%20out%20range#matplotlib.dates.epoch2num
from matplotlib.dates import MonthLocator, DayLocator, DateFormatter, epoch2num
import cStringIO

import numpy


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
Successfully finished bot runs: <b>%(successfull)s</b><br><br>
Current log files: %(currentlog)s<br>
<a href="%(oldlink)s">Old log</a> files: <i>%(oldlog)s</i><br><br>
See also <a href="%(logstat)s">logging statistics</a> and the important messages:
<br>
%(messages)s<br>
<br>"""

logstat_content = \
"""<small><a href="%(backlink)s">back</a></small><br>
Evaluated data period from %(start_date)s to %(end_date)s.<br>
<br>
Filter: %(filter)s<br>
<br>
<h2>Runs (started, ended, difference, history compression)</h2>
<a href="%(graphlink-ecount)s"><img src="%(graphlink-ecount)s" alt=""></a>
<a href="%(graphlink-ecount-sed)s"><img src="%(graphlink-ecount-sed)s" alt=""></a><br>
<br>
<table>
<tr><td>Total runs:</td><td>%(start_count)s</td></tr>
<tr><td>Successful runs:</td><td>%(end_count)s</td></tr>
<tr><td>Difference:</td><td>%(run_diff)s</td></tr>
<tr><td>Uptime [s]:</td><td>%(uptimes)s</td></tr>
</table>
<br>
History compressed: %(histcomp_count)s (times)<br>
<br>
<h2>Logging messages</h2>
<a href="%(graphlink-mcount)s"><img src="%(graphlink-mcount)s" alt=""></a>
<a href="%(graphlink-mcount-i)s"><img src="%(graphlink-mcount-i)s" alt=""></a><br>
<br>
Important messages (everything except INFO):<br>
<br>
%(messages)s"""

adminlogs_content = \
"""Log file count: %(logcount)s<br>
<p>%(message)s</p>
<form action="panel.py">
  <input type="hidden" name="action" value="adminlogs">
  Filter:
  <select name="filter" size="1">
    %(filter_options)s
  </select>
  <p>
    %(oldloglist)s
  </p>
  <input type="submit" value=" Delete/OK ">
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
regex   = re.compile(r'(?P<timestamp>\S+\s\S+)\s(?P<file>\S+)\s*(?P<level>\S+)\s*(?P<message>.*)')#, re.U)
timefmt = "%Y-%m-%d %H:%M:%S,%f"


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

# http://www.scipy.org/Cookbook/Matplotlib/Using_MatPlotLib_in_a_CGI_script
def show_onwebpage(plt):
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

def logging_statistics(logfile):
	f = open(logfile, "r")
	buffer = f.read(-1).strip().split("\n")
	f.close()

	# statistics (like mentioned in 'logging.statistics')
	mcount    = { 'debug': 0, 'warning': 0, 'info': 0, 'error': 0, 'critical': 0, 'unknown': 0, }
	mqueue    = { 'debug': [], 'warning': [], 'info': [], 'error': [], 'critical': [], 'unknown': [], }
	events    = { 'start':     'SCRIPT CALL:',
	              'end':       botdonemsg,
	              'histcomp':  '* Compressing of histories:',
	              'warn?':     '* Processing Warnings:',
	              'backlink?': '* Processing Template Backlink List:', }
	ecount    = { 'start': 0, 'end': 0, 'histcomp': 0, 'warn?': 0, 'backlink?': 0, }
	etiming   = { 'start': [], 'end': [], 'histcomp': [], 'warn?': [], 'backlink?': [],
	              'mainstart': None, 'mainend': None, }
	resources = { 'files': set(), }

	def process_event(event, result, log, process=None, ignore=[]):
		# match event
		if process is None:
			event = 'unknown' if event not in result else event
		else:
			noevent = True
			for e in process:
				if process[e] in event:
					event   = e
					noevent = False
					break
			if noevent:
				return
		# count matched events
		result[event] += 1
		if event not in ignore:
			log[0][event].append( log[1] )
		return

	timeepoch = lambda t: mktime(datetime.datetime.strptime(t, timefmt).timetuple())

	#How many requests are being handled per second, how much of various resources are 

	# gather statistics
	etiming['mainstart'] = [ regex.match(buffer[0]).groupdict()['timestamp'] ]
	etiming['mainend']   = [ regex.match(buffer[-1]).groupdict()['timestamp'] ]
	for line in buffer:
		if not line.strip(): continue
		try:
			info = regex.match(line).groupdict()

			process_event( info['level'].lower(), mcount, (mqueue, cgi.escape(line)), 
			               ignore='info' )
			process_event( info['message'],       ecount, (etiming, info['timestamp']), 
			               process=events )
			resources['files'].add( info['file'] )
		except AttributeError:
			pass

	# evaluate statistics
	stats = {'mcount': mcount, 'mqueue': mqueue, 'ecount': ecount, 'resources': resources}
	# (in use, how long we've been up.)
	start = datetime.datetime.strptime(etiming['mainstart'][0], timefmt)
	end   = datetime.datetime.strptime(etiming['mainend'][0], timefmt)
	stats['uptime'] = (end - start).seconds
	stats['mainstart'] = timeepoch(etiming['mainstart'][0])
	stats['mainend']   = timeepoch(etiming['mainend'][0])
	# gather messages ignoring info
	stats['messages'] = []
	for key in mqueue:
		if key == 'info': continue
		stats['messages'].append( "<i>%s</i>" % key )
		stats['messages'] += mqueue[key]
	# convert event times
	for key in etiming:
		etiming[key] = [ timeepoch(item) for item in etiming[key] ]
	stats['etiming'] = etiming
	# last message
	stats['lastmessage'] = regex.match(buffer[-1]).groupdict()['message'].strip()

	return stats


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

	stat = logging_statistics(data['loglink'])
	data['botlog']      = stat['lastmessage']
	data['messages']    = "<br>\n".join(stat['messages'])
	data['successfull'] = "%s of %s" % (stat['ecount']['end'], stat['ecount']['start'])

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

	(localdir, files, current) = oldlogfiles()

	filelist = form.getvalue('filelist', [])
	if type(filelist) == type(''): filelist = [filelist]

	current.insert(0, 'ALL')
	filt = form.getvalue('filter', current[0])
	filt = '' if filt == 'ALL' else filt
	data['filter_options'] = "<option>%s</option>" % ("</option><option>".join(current))
	data['filter_options'] = data['filter_options'].replace("<option>%s</option>" % filt,
	                                                        "<option selected>%s</option>" % filt)

	files = filter(lambda item: filt in item, files)
	files_str = map(str, files)

	data['message'] = ''

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

	#(localdir, files, log) = oldlogfiles(all=True)		# would be better - but has NO date!
	(localdir, files, log) = oldlogfiles()

	filter = 'mainbot.log'

	data = {'start_count':		0, # = run_count
		'end_count':		0, # = successful_count
		'histcomp_count':	0, 
		'messages':		"", 
		'start_date':		0.0,
		'end_date':		0.0,
		'filter':		filter + " (fix)",  }

	stat = {}
	for item in files:
		if filter not in item: continue
		last = item	# a little bit hacky but needed for plot below

		logfile = os.path.join(localdir, item)
		stat[item] = logging_statistics(logfile)

	d = {'mcount': [], 'ecount': [], 'messages': '', 'uptimes': [], 'histcomp': 0}
	keys = stat.keys()
	keys.sort()
	data['start_date'] = stat[keys[0]]['mainstart']
	data['end_date']   = stat[keys[-1]]['mainend']
	for item in keys:
		t = mktime(strptime(item.split('.')[-1], "%Y-%m-%d"))

		d['mcount'].append( [t] + stat[item]['mcount'].values() )

		d['ecount'].append( [t] + stat[item]['ecount'].values() )

		d['messages'] += "<b>%s</b><br>\n<i>used resources: %s</i><br>\n" % (item, stat[item]['resources'])
		d['messages'] += "<br>\n".join(stat[item]['messages']) + ("<br>\n"*2)

		end   = numpy.array(stat[item]['etiming']['end'])
		start = numpy.array(stat[item]['etiming']['start'])
		if end.shape == start.shape:
			d['uptimes'].append( list(end-start-3600) )	# -3600 because of time jump during 'set TZ'
		else:
			d['uptimes'].append( '-' )

		d['histcomp'] += stat[item]['ecount']['histcomp']

	d['mcount'] = numpy.array(d['mcount'])
	d['ecount'] = numpy.array(d['ecount'])

	data.update({'start_date':		str(strftime("%a %b %d %Y", localtime(data['start_date']))),
		'end_date':		str(strftime("%a %b %d %Y", localtime(data['end_date']))),
		'run_diff':		"</td><td>".join( map(str, d['ecount'][:,1]-d['ecount'][:,3]) ),
		'messages':		d['messages'],
		'start_count':		"</td><td>".join( map(str, d['ecount'][:,1]) ),
		'end_count':		"</td><td>".join( map(str, d['ecount'][:,3]) ),
		'uptimes':		"</td><td>".join( map(str, d['uptimes']) ),
		'histcomp_count':	d['histcomp'], 
		'graphlink-mcount':	sys.argv[0] + r"?action=logstat&amp;format=graph-mcount",
		'graphlink-mcount-i':	sys.argv[0] + r"?action=logstat&amp;format=graph-mcount-i",
		'graphlink-ecount':	sys.argv[0] + r"?action=logstat&amp;format=graph-ecount",
		'graphlink-ecount-sed':	sys.argv[0] + r"?action=logstat&amp;format=graph-ecount-sed",
		'backlink':		sys.argv[0],
	})

	if   (format == 'plain'):
		return "Content-Type: text/plain\n\n%s" % str(stat)
	elif (format == 'graph-mcount'):
		d = d['mcount']
		fig = plt.figure(figsize=(4,4))
		ax = fig.add_subplot(111)
		#plot1 = ax.bar(range(len(xdata)), xdata)
		#p1 = ax.plot(epoch2num(d[:,0]), d[:,1])	# 'info'
		p2 = ax.step(epoch2num(d[:,0]), d[:,2], marker='x', where='mid')
		p3 = ax.step(epoch2num(d[:,0]), d[:,3], marker='x', where='mid')
		p4 = ax.step(epoch2num(d[:,0]), d[:,4], marker='x', where='mid')
		p5 = ax.step(epoch2num(d[:,0]), d[:,5], marker='x', where='mid')
		p6 = ax.step(epoch2num(d[:,0]), d[:,6], marker='x', where='mid')
		plt.legend([p2, p3, p4, p5, p6], stat[last]['mcount'].keys()[1:], loc='center left')
		plt.grid(True, which='both')
		# format the ticks
		ax.xaxis.set_major_locator(MonthLocator())
		ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
		ax.xaxis.set_minor_locator(DayLocator())
		ax.autoscale_view()
		# format the coords message box
		ax.fmt_xdata = DateFormatter('%Y-%m-%d')
		# format axis
		fig.autofmt_xdate()
		# show plot
		return show_onwebpage(plt)
	elif (format == 'graph-mcount-i'):
		d = d['mcount']
		fig = plt.figure(figsize=(4,4))
		ax = fig.add_subplot(111)
		p1 = ax.step(epoch2num(d[:,0]), d[:,1], marker='x', where='mid')
		# legend
		plt.legend([p1], stat[last]['mcount'].keys(), loc='upper left')
		# grid
		plt.grid(True, which='both')
		# format the ticks
		ax.xaxis.set_major_locator(MonthLocator())
		ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
		ax.xaxis.set_minor_locator(DayLocator())
		ax.autoscale_view()
		# format the coords message box
		ax.fmt_xdata = DateFormatter('%Y-%m-%d')
		# format axis
		fig.autofmt_xdate()
		# show plot
		return show_onwebpage(plt)
	elif (format == 'graph-ecount'):
		d = d['ecount']
		fig = plt.figure(figsize=(4,4))
		ax = fig.add_subplot(111)
		p1 = ax.step(epoch2num(d[:,0]), d[:,1], marker='x', where='mid')
		p2 = ax.step(epoch2num(d[:,0]), d[:,2], marker='x', where='mid')
		p3 = ax.step(epoch2num(d[:,0]), d[:,3], marker='x', where='mid')
		p4 = ax.step(epoch2num(d[:,0]), d[:,4], marker='x', where='mid')
		p5 = ax.step(epoch2num(d[:,0]), d[:,5], marker='x', where='mid')
		plt.legend([p1, p2, p3, p4, p5], stat[last]['ecount'].keys(), loc='upper left')
		plt.grid(True, which='both')
		# format the ticks
		ax.xaxis.set_major_locator(MonthLocator())
		ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
		ax.xaxis.set_minor_locator(DayLocator())
		ax.autoscale_view()
		# format the coords message box
		ax.fmt_xdata = DateFormatter('%Y-%m-%d')
		# format axis
		fig.autofmt_xdate()
		# show plot
		return show_onwebpage(plt)
	elif (format == 'graph-ecount-sed'):
		d = d['ecount']
		fig = plt.figure(figsize=(4,4))
		ax = fig.add_subplot(111)
		p1 = ax.step(epoch2num(d[:,0]), (d[:,1]-d[:,3]), marker='x', where='mid')
		plt.legend([p1], ['runs failed'])
		plt.grid(True, which='both')
		# format the ticks
		ax.xaxis.set_major_locator(MonthLocator())
		ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
		ax.xaxis.set_minor_locator(DayLocator())
		ax.autoscale_view()
		# format the coords message box
		ax.fmt_xdata = DateFormatter('%Y-%m-%d')
		# format axis
		fig.autofmt_xdate()
		# show plot
		return show_onwebpage(plt)

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
