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
import subprocess

#import Image,ImageDraw
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
"""Actual state: <img src="%(botstate_daily)s" width="15" height="15" alt="Botstate: daily">
                 <img src="%(botstate_subster)s" width="15" height="15" alt="Botstate: subster">
                 <img src="%(botstate_wui)s" width="15" height="15" alt="Botstate: wui"><br><br>
Time now: %(time)s<br><br>

%(loglink)s gathered bot status message log: <b>%(botlog)s</b><br><br>
Successfully finished bot runs: <b>%(successfull)s</b><br><br>
Current log files: %(currentlog)s<br>
<a href="%(oldlink)s">Old log</a> files: <i>%(oldlog)s</i><br><br>
See also <a href="%(logstat)s">logging statistics</a> and the important messages:
<p style="white-space:pre-wrap;">%(messages)s</p>
<br>"""

logstat_content = \
"""<small><a href="%(backlink)s">back</a></small><br>
Evaluated data period from %(start_date)s to %(end_date)s.<br>
<br>
<form action="panel.py">
  <input type="hidden" name="action" value="logstat">
  Filter:
  <select name="filter" size="1">
    %(filter_options)s
  </select>
  <input type="submit" value=" OK ">
</form>
<br>
<h2>Runs (started, ended, difference, history compression)</h2>
<a href="%(graphlink-ecount)s"><img src="%(graphlink-ecount)s" alt=""></a>
<a href="%(graphlink-ecount-sed)s"><img src="%(graphlink-ecount-sed)s" alt=""></a><br>
<br>
<div style="width:100%%; overflow:scroll; border:0px solid #000000; margin:1em;">
<table class="wikitable">
<tr><td>Total runs:</td><td>%(start_count)s</td></tr>
<tr><td>Successful runs:</td><td>%(end_count)s</td></tr>
<tr><td>Difference:</td><td>%(run_diff)s</td></tr>
<tr><td>Uptime [s]:</td><td>%(uptimes)s</td></tr>
</table>
</div>
<br>
<h2>Logging messages</h2>
<a href="%(graphlink-mcount)s"><img src="%(graphlink-mcount)s" alt=""></a>
<a href="%(graphlink-mcount-i)s"><img src="%(graphlink-mcount-i)s" alt=""></a><br>
<br>
Important messages (everything except INFO):<br>
<p style="white-space:pre-wrap;">%(messages)s</p>"""

adminlogs_content = \
"""<img src="../DrTrigonBot/metrics-monthly.png"><br>
Log file count: %(logcount)s<br>
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
botcontinuous = ['trunk/bot_control.py-subster_irc.log', 'rewrite/script_wui-bot.log']

# use classic 're' since 'pyparsing' does not work with unicode
## fmt='%(asctime)s %(name)18s: %(levelname)-8s %(message)s'
#regex    = re.compile(r'(?P<timestamp>[\d-]+\s[\d:,]+)\s+(?P<file>\S+)\s+(?P<level>\S+)\s+(?P<message>.*)')#, re.U)
# fmt="%(asctime)s %(caller_file)18s, %(caller_line)4s "
# "in %(caller_name)18s: %(levelname)-8s %(message)s"
regex    = re.compile(r'(?P<timestamp>[\d-]+\s[\d:,]+)\s+(?P<caller_file>\S+),\s+(?P<caller_line>\S+)\s+in\s+(?P<file>\S+):\s+(?P<level>\S+)\s+(?P<message>.*)')#, re.U)
timefmt  = "%Y-%m-%d %H:%M:%S,%f"
timefmt2 = "%Y-%m-%d %H:%M:%S"
datefmt  = "%Y-%m-%d"

localdir = os.path.dirname(os.path.join('..','DrTrigonBot','.'))


# === functions === === ===
#
def oldlogfiles(all=False, exclude=['commands.log', 'throttle.log']):
#	files  = os.listdir( localdir )
	files  = [os.path.join('trunk', item) for item in os.listdir( os.path.join(localdir, 'trunk') )]
	files += [os.path.join('rewrite', item) for item in os.listdir( os.path.join(localdir, 'rewrite') )]
	archive, current = {}, []
	files.sort()
	for item in files:
		info = item.split('.')
		bn = os.path.basename(item)
		if (len(info) < 2) or (bn[1:] == info[-1]) or (bn in exclude):
			continue
		ext = info[-1].lower()
		if ext == 'log':
			current.append( item )
			if all:
				e = strftime(datefmt)
				archive[e] = archive.get(e, []) + [item]
		else:
			archive[ext] = archive.get(ext, []) + [item]

	# sort dict archive and list current
	keys, arch = archive.keys(), []
	keys.sort()
	for k in keys:
		arch.append( (k, archive[k]) )
	current.sort()

	return (localdir, arch, current)

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

	s=socket.socket( )
	s.connect((HOST, PORT))
	s.send("NICK %s\r\n" % NICK)
	s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
	#s.send('JOIN ' + CHAN + '\r\n') # Join the pre defined channel
	s.send('NAMES ' + CHAN + '\r\n') # Show all Nicks in channel
	sleep(.5)			 # give the server some time

	readbuffer=""
	while True:
		buf=s.recv(1024)
		readbuffer=readbuffer+buf
		if (':End of /NAMES' in readbuffer) or (len(buf) < 1024):
			break
	s.close()
	del s

	users = []
	for line in readbuffer.splitlines():
		line=string.rstrip(line)
		line=string.split(line)

		if (line[1] == "353"):  # answer to 'NAMES' request
			i = line.index(CHAN)
			users += line[(i+1):]

	return users

def logging_statistics(logfiles, exclude):
	# chronological sort
	logfiles = dict([ (os.stat(os.path.join(localdir, item)).st_mtime, item) \
                     for item in logfiles \
                     if (item not in exclude) and (os.path.splitext(item)[0] not in exclude) ])
	keys = logfiles.keys()
	keys.sort()

	buffer = []
	#for file in logfiles:
	for k in keys:
		file = logfiles[k]
# skip rewrite logs for the moment
		if 'rewrite' in file:	# cheat (since trunk and rewrite have different formats)
			continue	#  "
		#if file in exclude:
		#	continue
		f = open(os.path.join(localdir, file), "r")
		#buffer += f.read(-1).strip().split("\n")
		buffer.append( (file, f.read(-1).strip().splitlines()) )
		f.close()

	if not buffer:
		return None, None

	# statistics (like mentioned in 'logging.statistics')
	mcount    = { 'debug': 0, 'warning': 0, 'info': 0, 'error': 0, 'critical': 0, 'unknown': 0, }
	mqueue    = { 'debug': [], 'warning': [], 'info': [], 'error': [], 'critical': [], 'unknown': [], }
	events    = { 'start':     '=== Pywikipediabot framework v1.0 -- Logging header ===',
	              'end':       botdonemsg, }
	ecount    = { 'start': 0, 'end': 0, }
	etiming   = { 'start': [], 'end': [],
	              'mainstart': None, 'mainend': None, }
	fcount    = {}
	ftiming   = {}
	resources = { 'files': set(), }

	def process_event(event, result, log, process=None, ignore=[]):
		# match event
		if process is None:
			event = 'unknown' if event not in result else event
		else:
			noevent = True
			for e in process:
				#if process[e] in event:
				if (process[e] == event.strip()):
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

	timeepoch = lambda t: mktime(datetime.datetime.strptime(t, (timefmt if ',' in t else timefmt2)).timetuple())

	#How many requests are being handled per second, how much of various resources are 

	# gather statistics
	etiming['mainstart'] = [ regex.match(buffer[0][1][0]).groupdict()['timestamp'] ]
	#etiming['mainend']   = [ regex.match(buffer[-1][1][-1]).groupdict()['timestamp'] ]
	end  = regex.match(buffer[-1][1][-1])
	end  = regex.match(buffer[-1][1][-2]) if not end else end  # or strftime(timefmt2)
	etiming['mainend']   = [ end.groupdict()['timestamp'] ]
	info = {'level': 'unknown', 'message': '', 'timestamp': etiming['mainstart'][0], 'file': ''}
	for item in buffer:
		file = os.path.split(item[0])[1].split('-')[1].split('.')[0]
		for line in item[1]:
			if not line.strip(): continue

			data = regex.match(line)
			if (data is not None):
				data = data.groupdict()
			else:
				#line = ("%(level)s " % info) + line
				data = {'message': line}
			info.update( data )

			process_event( info['level'].lower(), mcount, (mqueue, cgi.escape(line)), 
		        	       process=None, ignore=['info'] )
			process_event( info['message'],       ecount, (etiming, info['timestamp']), 
			               process=events, ignore=[] )
			resources['files'].add( info['file'] )
		fcount[file]  = fcount.get(file, 0) + ecount['start']
		ftiming[file] = ftiming.get(file, []) + etiming['start']

	# evaluate statistics
	ecount.update(fcount)
	etiming.update(ftiming)
	stats = {'mcount': mcount, 'mqueue': mqueue, 'ecount': ecount, 'resources': resources}
	# (in use, how long we've been up.)
	start = datetime.datetime.strptime(etiming['mainstart'][0], (timefmt if ',' in etiming['mainstart'][0] else timefmt2))
	end   = datetime.datetime.strptime(etiming['mainend'][0], (timefmt if ',' in etiming['mainend'][0] else timefmt2))
	stats['uptime'] = (end - start).seconds
	stats['mainstart'] = timeepoch(etiming['mainstart'][0])
	stats['mainend']   = timeepoch(etiming['mainend'][0])
	# gather messages ignoring info
	stats['messages'] = []
	for key in mqueue:
		if key == 'info': continue
		stats['messages'].append( "<i>%s</i>" % key )
		stats['messages'] += mqueue[key]
	# assign and convert event times
	for key in etiming:
		etiming[key] = [ timeepoch(item) for item in etiming[key] ]
	stats['etiming'] = etiming
	# last message
	stats['lastmessage'] = regex.match(buffer[-1][1][-1]).groupdict()['message'].strip()

	return (stats, logfiles[keys[-1]])


# === SHELL/CRON interfaces === === ===
#
def maintain_stats(init=False):
    # http://supportex.net/2011/09/rrd-python/
    # (https://jira.toolserver.org/browse/DRTRIGON-74)
    global localdir    # why is this needed here? nowhere else needed...?!?!!

    import platform, numpy, rrdtool    # for statistics '-stats'

    #rrd_fn = os.path.join(localdir, "stats-01-%s.rrd" % platform.platform())
    rrd_fn = os.path.join(localdir, "stats-01-%s.rrd" % platform.system())

    if init:
        ret = rrdtool.create(rrd_fn, "--step", "86400", "--start", '0',
         "DS:sum_start:GAUGE:144000:U:U",
         "DS:sum_end:GAUGE:144000:U:U",
         "DS:sum_diff:GAUGE:144000:U:U",
         "DS:bot_sum_disc:GAUGE:144000:U:U",
         "DS:bot_subster:GAUGE:144000:U:U",
         "DS:bot_catimages:GAUGE:144000:U:U",
         "DS:bot_uptime_sum_disc:GAUGE:144000:U:U",
         "DS:bot_uptime_subster:GAUGE:144000:U:U",
         "DS:bot_uptime_catimages:GAUGE:144000:U:U",
         "DS:msg_unknown:GAUGE:144000:U:U",
         "DS:msg_info:GAUGE:144000:U:U",
         "DS:msg_warning:GAUGE:144000:U:U",
         "DS:msg_error:GAUGE:144000:U:U",
         "DS:msg_critical:GAUGE:144000:U:U",
         "DS:msg_debug:GAUGE:144000:U:U",
         "DS:metric1:GAUGE:144000:U:U",
         "DS:metric2:GAUGE:144000:U:U",
         "DS:metric3:GAUGE:144000:U:U",
         "DS:metric4:GAUGE:144000:U:U",
         "DS:metric5:GAUGE:144000:U:U",
         "DS:sum_diff_inter:COMPUTE:sum_start,sum_end,-",
	 # (number of logfiles, quota, ...)
         "RRA:AVERAGE:0.5:1:600",
         "RRA:AVERAGE:0.5:6:700",
         "RRA:AVERAGE:0.5:24:775",
         "RRA:AVERAGE:0.5:288:797",
         "RRA:MIN:0.5:1:600",
         "RRA:MIN:0.5:6:700",
         "RRA:MIN:0.5:24:775",
         "RRA:MIN:0.5:444:797",
         "RRA:MAX:0.5:1:600",
         "RRA:MAX:0.5:6:700",
         "RRA:MAX:0.5:24:775",
         "RRA:MAX:0.5:444:797",
         "RRA:LAST:0.5:1:600",
         "RRA:LAST:0.5:6:700",
         "RRA:LAST:0.5:24:775",
         "RRA:LAST:0.5:444:797")
    else:
	(localdir, files, current) = oldlogfiles()
        stat, recent = logging_statistics(current, botcontinuous)
#        for item in current:
#            stat, recent = logging_statistics([item], botcontinuous)
#            if stat is None:
#                continue
#            end, start = numpy.array(stat['etiming']['end']), numpy.array(stat['etiming']['start'])
#            shape = min(end.shape[0], start.shape[0])
#            runtime = end[:shape]-start[:shape]-7200	# -2*60*60 because of time jump during 'set TZ'
#            if runtime.any() and (runtime.min() < 0):	# DST or not; e.g. ('CET', 'CEST')
#                runtime += 3600
#            uptime = numpy.array(runtime).sum()

        (bot_uptime_sum_disc, bot_uptime_subster, bot_uptime_catimages) = (0, 0, 0)
        (metric1, metric2, metric3, metric4, metric5) = (0, 0, 0, 0, 0)
        val = (ecount['start'], ecount['end'],  (ecount['start']-ecount['end']),
               ecount['sum_disc'], ecount['subster'], ecount['catimages'],
               bot_uptime_sum_disc, bot_uptime_subster, bot_uptime_catimages,
               mcount['unknown'], mcount['info'], mcount['warning'], mcount['error'], mcount['critical'], mcount['debug'],
               metric1, metric2, metric3, metric4, metric5,)

        # update
        ret = rrdtool.update(rrd_fn, ('N' + (':%s'*22)) % val);

        # show
        #for sched in ['hourly', 'daily', 'weekly', 'monthly']:
        for sched in ['daily', 'weekly', 'monthly']:
            fn  = "/home/drtrigon/public_html/DrTrigonBot/test-%s.png" % (sched)
#            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Num",
#                 '--watermark=DrTrigonBot.TS',
#                 "-w 800",
#                 "DEF:m1_num=%s:metric1:AVERAGE" % rrd_fn,
#                 "DEF:m2_num=%s:metric2:AVERAGE" % rrd_fn,
#                 "LINE1:m1_num#0000FF:metric1\\r",
#                 "LINE2:m2_num#00FF00:metric2\\r",
#                 "GPRINT:m1_num:AVERAGE:Avg m1\: %6.0lf ",
#                 "GPRINT:m1_num:MAX:Max m1\: %6.0lf \\r",
#                 "GPRINT:m2_num:AVERAGE:Avg m2\: %6.0lf ",
#                 "GPRINT:m2_num:MAX:Max m2\: %6.0lf \\r")
            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Num",
                 '--watermark=DrTrigonBot.TS',
                 "DEF:end_num=%s:sum_end:AVERAGE" % rrd_fn,
                 "DEF:start_num=%s:sum_start:AVERAGE" % rrd_fn,
                 "DEF:subster_num=%s:bot_subster:AVERAGE" % rrd_fn,
                 "DEF:sum_disc_num=%s:bot_sum_disc:AVERAGE" % rrd_fn,
                 "DEF:catimages_num=%s:bot_catimages:AVERAGE" % rrd_fn,
                 "LINE1:end_num#0000FF:end\\r",
                 "LINE2:start_num#00FF00:start\\r",
                 "LINE4:subster_num#00FF00:subster\\r",
                 "LINE5:sum_disc_num#00FF00:sum_disc\\r",
                 "LINE6:catimages_num#00FF00:catimages\\r",
                 "GPRINT:end_num:AVERAGE:Avg end\: %6.0lf ",
                 "GPRINT:end_num:MAX:Max end\: %6.0lf \\r",
                 "GPRINT:start_num:AVERAGE:Avg start\: %6.0lf ",
                 "GPRINT:start_num:MAX:Max start\: %6.0lf \\r")
#            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Num",
#                 '--watermark=DrTrigonBot.TS',
#                 "DEF:end_num=%s:sum_end:AVERAGE" % rrd_fn,
#                 "DEF:diff_num=%s:sum_diff:AVERAGE" % rrd_fn,
#                 "DEF:diff_intern_num=%s:sum_diff_inter:AVERAGE" % rrd_fn,
#                 "LINE1:end_num#0000FF:successful\\r",
#                 "LINE2:diff_num#00FF00:runs_failed\\r",
#                 "LINE3:diff_intern_num#00FF00:runs_failed_i\\r",
#                 "GPRINT:end_num:AVERAGE:Avg end\: %6.0lf ",
#                 "GPRINT:end_num:MAX:Max end\: %6.0lf \\r")
#            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Num",
#                 '--watermark=DrTrigonBot.TS',
#                 "DEF:unknown_num=%s:msg_unknown:AVERAGE" % rrd_fn,
#                 "DEF:warning_num=%s:msg_warning:AVERAGE" % rrd_fn,
#                 "DEF:error_num=%s:msg_error:AVERAGE" % rrd_fn,
#                 "DEF:critical_num=%s:msg_critical:AVERAGE" % rrd_fn,
#                 "DEF:debug_num=%s:msg_debug:AVERAGE" % rrd_fn,
#                 "LINE1:unknown_num#0000FF:unknown\\r",
#                 "LINE2:warning_num#00FF00:warning\\r",
#                 "LINE3:error_num#00FF00:error\\r",
#                 "LINE4:critical_num#00FF00:critical\\r",
#                 "LINE5:debug_num#00FF00:debug\\r",
#                 "GPRINT:warning_num:AVERAGE:Avg warning\: %6.0lf ",
#                 "GPRINT:warning_num:MAX:Max warning\: %6.0lf \\r")
#            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Num",
#                 '--watermark=DrTrigonBot.TS',
#                 "DEF:info_num=%s:msg_info:AVERAGE" % rrd_fn,
#                 "LINE1:info_num#0000FF:info\\r",
#                 "GPRINT:info_num:AVERAGE:Avg info\: %6.0lf ",
#                 "GPRINT:info_num:MAX:Max info\: %6.0lf \\r")

#        print rrdtool.fetch(rrd_fn, 'AVERAGE')[2]

# * add rrdtool graphs for comparison to statistics page, later remove matplotlib
# * get all data on statistics page from rrdtool.fetch, thus replace text output below graphs
#   through links to mainpages but containing history (old days/logs) 
#   -> mainpage has to be capable to process and show old data
#   -> mainpage does always gather actual data and NOT use rrdtool.fetch (and thus can also 
#      process text data like messages)
# * setup cron job at midnight in order to gather and update rrdtool data and graphs


# === CGI/HTML page view user interfaces === === ===
#
def displaystate(form):
	data = {}

	(localdir, files, current) = oldlogfiles()
	files = [item for key, value in files for item in value]	# flatten

	stat, recent = logging_statistics(current, botcontinuous)
	if stat is None:
		data['botlog']      = 'n/a'
		data['messages']    = 'n/a'
		data['successfull'] = "n/a"
		data['loglink']     = 'Latest'
	else:
		data['botlog']      = stat['lastmessage']
		data['messages']    = "\n".join(stat['messages'])
		data['successfull'] = "%s of %s" % (stat['ecount']['end'], stat['ecount']['start'])
		data['loglink']     = '<a href="%s">Latest</a>' % os.path.join(localdir, recent)
	lastrun = max([os.stat(os.path.join(localdir, item)).st_mtime for item in files]+[0])
	botmsg = data['botlog'].strip()

	data['botstate_daily'] = botstate_img['red']
	color = html_color['red']
	state_text = "n/a"
	if lastrun and ((lastrun-time()) <= (bottimeout*60*60)):
		if   (botmsg == botdonemsg) and not (stat['ecount']['end'] - stat['ecount']['start']):
			data['botstate_daily'] = botstate_img['green']
			color = html_color['green']
			state_text = "OK"
		elif (botmsg.find(botdonemsg) == 0):
			data['botstate_daily'] = botstate_img['orange']
			color = html_color['orange']
			state_text = "problem"
		else:
			data['botstate_daily'] = botstate_img['orange']
			color = html_color['orange']

	users = irc_status()

	data['botstate_subster'] = botstate_img['red']
	if ("DrTrigonBot" in users) or (":DrTrigonBot" in users):
		data['botstate_subster'] = botstate_img['green']
		irc_subster_color = html_color['green']
		irc_subster_state_text = "OK"
	else:
		data['botstate_subster'] = botstate_img['orange']
		irc_subster_color = html_color['orange']
		irc_subster_state_text = "problem"

	data['botstate_wui'] = botstate_img['red']
	if ("DrTrigonBot_WUI" in users) or (":DrTrigonBot_WUI" in users):
		data['botstate_wui'] = botstate_img['green']
		irc_wui_color = html_color['green']
		irc_wui_state_text = "OK"
	else:
		data['botstate_wui'] = botstate_img['orange']
		irc_wui_color = html_color['orange']
		irc_wui_state_text = "problem"

	status  = "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': color, 'bot': 'regular:', 'state': state_text}
	status += "<tr><td></td><td></td></tr>\n"    # separator (cheap)
	status += "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': irc_subster_color, 'bot': 'subster:', 'state': irc_subster_state_text}
	status += "<tr style='background-color: %(color)s'><td>%(bot)s</td><td>%(state)s</td></tr>\n" % {'color': irc_wui_color, 'bot': 'wui:', 'state': irc_wui_state_text}

	data['currentlog'] = ", ".join([ '<a href="%s">%s</a>' % (os.path.join(localdir, item), item) for item in current ])

	data.update({	'time':		asctime(localtime(time())),
			'oldlog':	", ".join(files),
			'oldlink':	r"../DrTrigonBot/",
			'logstat':	os.path.basename(sys.argv[0]) + r"?action=logstat",
			'logstatraw':	os.path.basename(sys.argv[0]) + r"?action=logstat&amp;format=plain",
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
	files = [item for key, value in files for item in value]	# flatten
	files.sort()

	filelist = form.getvalue('filelist', [])
	if type(filelist) == type(''): filelist = [filelist]

	current.insert(0, 'ALL')
	filt = form.getvalue('filter', current[0])
	filt = ('' if filt == 'ALL' else filt)
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
		files = [item for key, value in files for item in value]	# flatten

	checkbox_tmpl = '<input type="checkbox" name="filelist" value="%(datei)s">%(datei)s<br>'

	# get directory size (but is not stable)
	du = subprocess.Popen(["du", "-hL", localdir], stdout=subprocess.PIPE)
	du = du.communicate()[0].split()
	size = du[du.index('../DrTrigonBot')-1]

	#data.update({	'oldloglist':	'\n'.join([checkbox_tmpl % {'datei':item} for item in files[:-5]]),
	data.update({	'oldloglist':	'\n'.join([checkbox_tmpl % {'datei':item} for item in files]),
			'logcount':	"%i (size: %s)" % (len(files), size),
			'refresh':	'',
			'title':	'DrTrigonBot log admin panel',
			'tsnotice': 	'',
			'content':	adminlogs_content,
			'footer': 	'',
	})

	return (style.admin_page % data) % data

def logstat(form):
	import matplotlib
	matplotlib.rc('font', size=8)
	import matplotlib.pyplot as plt
	# http://matplotlib.sourceforge.net/api/dates_api.html?highlight=year%20out%20range#matplotlib.dates.epoch2num
	from matplotlib.dates import MonthLocator, DayLocator, DateFormatter, epoch2num

#	import platform, rrdtool	# for statistics '-stats'

	import numpy

	data = {'messages':		'', }

	format = form.getvalue('format', 'html')

	# filter: '' (all), 'default', 'subster', 'subster_irc', 'catimages'
	# (similar to the one used in adminlogs)
	current = ['ALL', 'default', 'subster', 'catimages',]# 'subster_irc', 'script_wui']
	filt = form.getvalue('filter', current[0])
	filt = ('' if filt == 'ALL' else filt)
	data['filter_options'] = "<option>%s</option>" % ("</option><option>".join(current))
	data['filter_options'] = data['filter_options'].replace("<option>%s</option>" % filt,
	                                                        "<option selected>%s</option>" % filt)

	(localdir, files, log) = oldlogfiles(all=True)

	stat = {}
	for date, item in files:
		logfiles = [f for f in item if filt in f]
		#if not logfiles:
		#	continue
		s, recent = logging_statistics(logfiles, botcontinuous)
		if s is None:	# includes 'if not logfiles'
			continue
		last = date	# a little bit hacky but needed for plot below
		stat[date] = s

	d = {'mcount': [], 'ecount': [], 'uptimes': []}
	keys = stat.keys()
	keys.sort()
	data['start_date'] = str(strftime("%a %b %d %Y", localtime( stat[keys[0]]['mainstart'] )))
	data['end_date']   = str(strftime("%a %b %d %Y", localtime( stat[keys[-1]]['mainend'] )))
	dkeys = dict([ (k, i) for item in keys for i, k in enumerate(stat[item]['ecount'].keys()) ])
	d['ecount'] = numpy.zeros((len(keys),len(dkeys)+1))
	for i, item in enumerate(keys):
		t = mktime(strptime(item.split('.')[-1], datefmt))

		d['mcount'].append( [t] + stat[item]['mcount'].values() )

		d['ecount'][i,0] = t
		for kj in dkeys:
			d['ecount'][i,(dkeys[kj]+1)] = stat[item]['ecount'].get(kj, 0)

		data['messages'] += "<b>%s</b>\n<i>used resources: %s</i>\n" % (item, stat[item]['resources'])
		data['messages'] += "\n".join(stat[item]['messages']) + ("\n"*2)

		end   = numpy.array(stat[item]['etiming']['end'])
		start = numpy.array(stat[item]['etiming']['start'])
		if end.shape == start.shape:
			runtime = end-start-7200			# -2*60*60 because of time jump during 'set TZ'
			if runtime.any() and (runtime.min() < 0):	# DST or not; e.g. ('CET', 'CEST')
				runtime += 3600
			d['uptimes'].append( list(runtime) )
		else:
			d['uptimes'].append( '-' )

	d['mcount'] = numpy.array(d['mcount'])
	#d['ecount'] = numpy.array(d['ecount'])
	d['mcount'][:,0] = epoch2num(d['mcount'][:,0])
	d['ecount'][:,0] = epoch2num(d['ecount'][:,0])
	keys = dkeys.keys()
	ks, ke = keys.index('start')+1, keys.index('end')+1

        plotlink = os.path.basename(sys.argv[0]) + (r"?action=logstat&amp;filter=%s" % filt)
	data.update({
		'run_diff':		"</td><td>".join( map(str, d['ecount'][:,ks]-d['ecount'][:,ke]) ),
		'start_count':		"</td><td>".join( map(str, d['ecount'][:,ks]) ),
		'end_count':		"</td><td>".join( map(str, d['ecount'][:,ke]) ),
		'uptimes':		"</td><td>".join( map(str, d['uptimes']) ),
		'graphlink-mcount':	plotlink + r"&amp;format=graph-mcount",
		'graphlink-mcount-i':	plotlink + r"&amp;format=graph-mcount-i",
		'graphlink-ecount':	plotlink + r"&amp;format=graph-ecount",
		'graphlink-ecount-sed':	plotlink + r"&amp;format=graph-ecount-sed",
		'backlink':		os.path.basename(sys.argv[0]),
	})

	# plot graphs output
	if   (format == 'graph-mcount'):
		d = d['mcount']
		fig = plt.figure(figsize=(5,3))
		#ax = fig.add_subplot(111)
		ax_size = [0.125, 0.15, 
			1-0.1-0.05, 1-0.15-0.05]
		ax = fig.add_axes(ax_size)
		#plot1 = ax.bar(range(len(xdata)), xdata)
		#p1 = ax.plot(d[:,0], d[:,1])	# 'info'
		p2 = ax.step(d[:,0], d[:,2], marker='x', where='mid')
		p3 = ax.step(d[:,0], d[:,3], marker='x', where='mid')
		p4 = ax.step(d[:,0], d[:,4], marker='x', where='mid')
		p5 = ax.step(d[:,0], d[:,5], marker='x', where='mid')
		p6 = ax.step(d[:,0], d[:,6], marker='x', where='mid')
		plt.legend([p2, p3, p4, p5, p6], stat[last]['mcount'].keys()[1:], loc='upper left', prop={'size':8})
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
		fig = plt.figure(figsize=(5,3))
		#ax = fig.add_subplot(111)
		ax_size = [0.125, 0.15, 
			1-0.1-0.05, 1-0.15-0.05]
		ax = fig.add_axes(ax_size)
		p1 = ax.step(d[:,0], d[:,1], marker='x', where='mid')
		# legend
		plt.legend([p1], stat[last]['mcount'].keys(), loc='upper left', prop={'size':8})
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
		fig = plt.figure(figsize=(5,3))
		#ax = fig.add_subplot(111)
		ax_size = [0.125, 0.15, 
			1-0.1-0.05, 1-0.15-0.05]
		ax = fig.add_axes(ax_size)
		pa = []
		for i in range(1, d.shape[1]):
			pa.append( ax.step(d[:,0], d[:,i], where='mid') )#, marker='x') )
		plt.legend(pa, stat[last]['ecount'].keys(), loc='upper left', bbox_to_anchor=[-0.15, 1.0], ncol=2, prop={'size':8})
		plt.grid(True, which='both')
		#plt.ylim(ymax=10)
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
		fig = plt.figure(figsize=(5,3))
		#ax = fig.add_subplot(111)
		ax_size = [0.125, 0.15, 
			1-0.1-0.05, 1-0.15-0.05]
		ax = fig.add_axes(ax_size)
		p1 = ax.step(d[:,0], (d[:,ks]-d[:,ke]), marker='x', where='mid')
		p2 = ax.step(d[:,0], d[:,ke], marker='x', where='mid')
		plt.legend([p1, p2], ['runs failed', 'successful'], prop={'size':8})
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

	# default output
	return style.page % data


# === Main procedure entry point === === ===
#
if __name__ == '__main__':
    if   '-init_stats' in sys.argv:
        maintain_stats(init=True)
    elif '-stats' in sys.argv:
        maintain_stats()
    else:
        form = cgi.FieldStorage()

        # operational mode
        action = form.getvalue('action', 'displaystate')
        #print locals()[action](form)
        print style.change_logo(locals()[action](form), os.environ)    # labs patch
