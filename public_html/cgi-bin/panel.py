#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test CGI python script

to make it usable from server, use: 'chmod 755 test.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.gpcom.de/support/python

#
# (C) Dr. Trigon, 2008, 2009
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', ... (and others)
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id: panel.py 0.1.0013 2009-06-04 23:15:00Z drtrigon $'
#


# debug
import cgitb
cgitb.enable()


import cgi
from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import commands, os, errno
#import subprocess
import re


footer = """<small>DrTrigonBot status panel, written by <a href="https://wiki.toolserver.org/view/User:DrTrigon">DrTrigon</a>. 
<!-- <img src="https://wiki.toolserver.org/w/images/e/e1/Wikimedia_Community_Logo-Toolserver.png" 
width="16" height="16" alt="Toolserver"> -->
<a href="http://tools.wikimedia.de/"><img 
src="https://wiki.toolserver.org/favicon.ico" border="0" 
alt="Toolserver"> Powered by Wikimedia Toolserver</a>.
<a href="http://de.selfhtml.org/index.htm"><img 
src="http://de.selfhtml.org/src/favicon.ico" border="0" width="16" 
height="16" alt="SELFHTML"> Thanks to SELFHTML</a>.
"""
footer_w3c = """<a href="http://validator.w3.org/check?uri=referer"><img 
src="http://www.w3.org/Icons/valid-html401-blue" 
alt="Valid HTML 4.01 Transitional" height="16" width="44" 
border="0"></a></small>
</span></p>
"""

displaystate_content = """Content-Type: text/html
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>DrTrigonBot status panel</title>
  <meta http-equiv="refresh" content="15">
</head>
<body>
<p><span style="font-family:sans-serif">
DrTrigonBot status panel<br><br><br>
Actual state: <img src="%(botstate)s" width="15" height="15" alt="Botstate"><br><br>
Time now: %(time)s<br><br>
<a href="%(loglink)s">Latest</a> bot status message log: <b>%(botlog)s</b><br><br>
<a href="%(oldlink)s">Old log</a> files: <i>%(oldlog)s</i><br><br>
See also <a href="%(logstat)s">log statistics</a> <small>(also available in <a href="%(logstatraw)s">raw/plain format</a>)</small>.<br><br>
%(footer)s
</body>
</html>
"""

adminlogs_content = """Content-Type: text/html
<html>
<head>
  <title>DrTrigonBot log admin panel</title>
</head>
<body>
<p><span style="font-family:sans-serif">
DrTrigonBot log admin panel<br><br><br>
Log file count: %(logcount)s<br>
<p>%(message)s</p>
<form action="panel.py">
  <input type="hidden" name="action" value="adminlogs">
  <p>
    %(oldloglist)s
  </p>
  <input type="submit" value=" Delete ">
  <input type="reset" value=" Reset ">
</form>
</span></p>
</body>
</html>
"""

adminhist_content = """Content-Type: text/html
<html>
<head>
  <title>DrTrigonBot history admin panel</title>
</head>
<body>
<p><span style="font-family:sans-serif">
DrTrigonBot history admin panel<br><br><br>
History file count: %(histcount)s<br>
History file size: %(histsize)s<br>
<p>%(message)s</p>
<form action="panel.py">
  <input type="hidden" name="action" value="adminhist">
  <p>
    <input type="checkbox" name="compresshistory" value="True">compress history<br>
  </p>
  <input type="submit" value=" Delete ">
  <input type="reset" value=" Reset ">
</form>
</span></p>
</body>
</html>
"""

logstat_content = """Content-Type: text/html
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>DrTrigonBot log statistics</title>
</head>
<body>
<p><span style="font-family:sans-serif">
DrTrigonBot log statistics<br><br>
<br>
Evaluated data period from %(start_date)s to %(end_date)s.<br>
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
<br>
Warnings (%(warn_total)s distilled to %(warn_dist)s):<br>
%(warnings)s<br>
<br>
%(footer)s
</body>
</html>
"""

botstate_img = {#'green':	'http://upload.wikimedia.org/wikipedia/commons/3/3c/ButtonGreen.svg',
		'green':	'http://upload.wikimedia.org/wikipedia/commons/6/65/ButtonGreen.png',
		#'orange':	'http://upload.wikimedia.org/wikipedia/commons/b/b0/ButtonYellow.svg',
		#'red':		'http://upload.wikimedia.org/wikipedia/commons/9/97/ButtonRed.svg',
		'orange':	'http://upload.wikimedia.org/wikipedia/commons/b/bf/ButtonYellow.png',
		'red':		'http://upload.wikimedia.org/wikipedia/commons/6/65/ButtonRed.png',
		}

bottimeout = 24

botdonemsg = 'Done.'


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


def displaystate():
	#print("Content-Type: text/html\n")
	#
	#print("<html>\n")
	#print("<head><title>Test-Seite</title></head>\n")
	#print("<body>\n")
	#print("Willkommen<br><br>\n")
	#print("Jetzt: " + asctime(localtime(time())) + "<br>\n")
	##print( commands.getoutput("ls -l") )
	#print( commands.getoutput("ps aux | grep python") )
	##print( subprocess.call(["ls", "-l"]) )		# oder auch 'os.system(...)'
	#print("</body>\n")
	#print("</html>\n")

	#buffer = commands.getoutput("ps aux | grep python")
	##buffer = commands.getoutput("ps --pid 25801")
	#buffer = re.sub('\n','<br>\n',buffer)

	(localdir, files, log) = oldlogfiles()

	b = file(log, "r")
	d = b.readlines()
	b.close()

	#buffer = os.path.join(localdir, log) + str(b.readlines())

	d.reverse()

	c = ""
	for item in d:
	    try:    c = re.split(':: ', item)[-1].strip()
	    except: pass
	    if c: break

	#buffer = c +"\n"+ str(files)

	files = [str(item)+".log" for item in files]
	files.sort()
	buf = ", "

	lastrun = (time() - os.stat(log).st_mtime)/(60*60)
	if (lastrun > ((bottimeout*5)/4)):
		botstate = botstate_img['red']
	elif (lastrun > bottimeout) or (not (c[-len(botdonemsg):] == botdonemsg)):
		botstate = botstate_img['orange']
	else:
		botstate = botstate_img['green']

	data = {'time':		asctime(localtime(time())),
		'botlog':	c,
		'oldlog':	buf.join(files),
		'loglink':	log,
		'oldlink':	r"http://toolserver.org/~drtrigon/DrTrigonBot/",
		'botstate':	botstate,
		'logstat':	r"panel.py?action=logstat",
		'logstatraw':	r"panel.py?action=logstat&amp;format=plain",
		'footer':	footer + footer_w3c,
	}

	return displaystate_content % data

def adminlogs(form):
	filelist = form.getvalue('filelist', [])
	if type(filelist) == type(''): filelist = [filelist]

	msg = ''

	(localdir, files, log) = oldlogfiles()
	files_str = map(str, files)

	if (len(filelist) > 0):
		msg = []
		for item in filelist:
			if (item in files_str): os.remove( os.path.join(localdir, str(item)+".log") )
			else: msg.append( 'Warning: "%s" is NOT a log file! Nothing done.' % item )
			#pass
		msg.append( '%i log file(s) deleted.' % (len(filelist)-len(msg)) )
		msg = '<br>\n'.join(msg)
		(localdir, files, log) = oldlogfiles()

	checkbox_tmpl = '<input type="checkbox" name="filelist" value="%(datei)s">%(datei)s<br>'

	buf = '\n'
	files.sort()
	data = {'oldloglist':	buf.join([checkbox_tmpl % {'datei':item} for item in files[:-5]]),
		'logcount':	len(files),
		#'message':	filelist,
		'message':	msg,
	}

	return adminlogs_content % data

def adminhist(form):
	compresshistory = form.getvalue('compresshistory', False)

	# %(histcount)s<br>
	# %(histsize)s<br>
	# %(message)s</p>
	# <input type="checkbox" name="compresshistory" value="True">compress history<br>

	#return adminhist_content % data
	return ''

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

	stat['warn_total'] = len(stat['warn_list'])
	stat['warn_list'] = list(set(stat['warn_list']))
	stat['warn_dist'] = len(stat['warn_list'])
	stat['warn_list'].sort()

	#data = {'start_date':		str(asctime(strptime(files[0], "%Y%m%d.log"))),
	#	'end_date':		str(asctime(strptime(files[-1], "%Y%m%d.log") )),
	data = {'start_date':		str(strftime("%a %b %d %Y", stat['start_date'])),
		'end_date':		str(strftime("%a %b %d %Y", stat['end_date'])),
		'successful_count':	stat['successful_count'],
		'run_count':		stat['run_count'],
		'run_diff':		(int(stat['run_count']) - int(stat['successful_count'])),
		'histcomp_count':	stat['histcomp_count'],
		'reliability':		[ "%.2f" % (100*item[1]) for item in stat['reliability_list'] ],
		'warn_total':		stat['warn_total'],
		'warn_dist':		stat['warn_dist'],
		'warnings':		"<br>".join(stat['warn_list']),
		'footer':		footer,
	}


	# http://www.scipy.org/Cookbook/Matplotlib/Using_MatPlotLib_in_a_CGI_script

	if (format == 'plain'): return "Content-Type: text/plain\n\n%s" % str(stat)

	return logstat_content % data


form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', '')
if action == 'logstat':
	html = logstat(form)
elif action == 'adminlogs':
	html = adminlogs(form)
#elif action == 'adminhist':
#	html = adminhist(form)
else:
	html = displaystate()

print html
