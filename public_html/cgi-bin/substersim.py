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
__version__='$Id: substersim.py 0.2.0000 2009-12-29 20:49:00Z drtrigon $'
#


# debug
import cgitb
cgitb.enable()


## import any path or dir (not only subdirs of current script)
## http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
## http://docs.python.org/library/imp.html
## http://www.faqs.org/docs/diveintopython/dialect_locals.html
## http://www.koders.com/python/fidEAB56F6AFEF3116A6B06ACE7BFA65AB902D31866.aspx?s=md5
#def importglobal(name, path):
#    if (type(name) == type("")): name = [name]
#    for item in name:
#        fp, pathname, description = imp.find_module(item, [path])
#        try:
#            globals()[item] = imp.load_module(item, fp, pathname, description)
#        finally:
#            # Since we may exit via an exception, close fp explicitly.
#            if fp: fp.close()
#    return

import cgi
from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
#import commands, os, errno, imp, sys
import os, sys, re
import StringIO, traceback, signal
bot_path = os.path.realpath("../../pywikipedia/")
#importglobal("subster_beta", bot_path)
#importglobal(["wikipedia", "xmlreader", "config", "dtbext", "subster_beta"], bot_path)
# http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
from xml.sax import saxutils, make_parser		# dummy import (by adapting 'suber.py' they should be supressable)
from xml.sax.handler import feature_namespaces		# (the whole 'xml' directory !)
import xml.utils.iso8601				#
sys.path.append( bot_path )				# bot import form other path (!)
import subster_beta					#
import config


footer = """<small>DrTrigonBot subster simulation panel, written by <a href="https://wiki.toolserver.org/view/User:DrTrigon">DrTrigon</a>. 
<!-- <img src="https://wiki.toolserver.org/w/images/e/e1/Wikimedia_Community_Logo-Toolserver.png" 
width="16" height="16" alt="Toolserver"> -->
<a href="http://tools.wikimedia.de/"><img 
src="https://wiki.toolserver.org/favicon.ico" border="0" 
alt="Toolserver"> Powered by Wikimedia Toolserver</a>.
<a href="http://de.selfhtml.org/index.htm"><img 
src="http://de.selfhtml.org/src/favicon.ico" border="0" width="16" 
height="16" alt="SELFHTML"> Thanks to SELFHTML</a>.
"""
footer_w3c = """<!--<a href="http://validator.w3.org/check?uri=referer"><img 
src="http://www.w3.org/Icons/valid-html401-blue" 
alt="Valid HTML 4.01 Transitional" height="16" width="44" 
border="0"></a>--></small>
</span></p>
"""

maindisplay_content = """Content-Type: text/html
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>DrTrigonBot subster simulation panel</title>
</head>
<body>
<p><span style="font-family:sans-serif">
DrTrigonBot subster simulation panel<br>
<small>(analog to <a href="http://meta.wikimedia.org/wiki/Special:ExpandTemplates">Special:ExpandTemplates</a>)</small><br><br><br>
Version:<br>
panel: %(panel_ver)s<br>
bot: %(subster_bot_ver)s<br><br>
Simulation:
<form action="substersim.py">
  <p>
    <input type="hidden" name="action" value="runsim">
    url=<input name="url" type="text" size="60" maxlength="200" value="%(url)s"><br>
    regex=<input name="regex" type="text" size="60" maxlength="200" value="%(regex)s"><br>
    value=<input name="value" type="text" size="60" maxlength="200" value="%(value)s"><br>
    count=<input name="count" type="text" size="60" maxlength="200" value="%(count)s"><br>
    notags=<input name="notags" type="text" size="60" maxlength="200" value="%(notags)s"><br>
    postproc=<input name="postproc" type="text" size="60" maxlength="200" value="%(postproc)s"><br>
    wiki=<input name="wiki" type="text" size="60" maxlength="200" value="%(wiki)s"><br>
    (add. params) <input name="add_params" type="text" size="60" maxlength="200" value="%(add_params)s"><br>
  <p>
  </p>
    content: <textarea name="content" cols="60" rows="10">%(content)s</textarea>
  </p>
  <input type="submit" value=" Simulate ">
  <input type="reset" value=" Reset ">
  <small><a href="substersim.py">new simulation</a></small>
</form><br><br>
Bot output:
<p style="border-color:#888888; border-width:1px; border-style:solid; padding:4px"><small>%(bot_output)s</small></p>
<br>
%(footer)s
</body>
</html>
"""

sim_param_default = {	'value': 	'val',
			'action':	'',
			'content':	'<!--SUBSTER-val--><!--SUBSTER-val-->',
			'add_params':	'{}', }
timeout = 10		# 10-sec. max. delay for url request


# from 'runbotrun.py'
def gettraceback(exc_info):
	output = StringIO.StringIO()
	traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)
	##if not ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
	##    result = output.getvalue()
	#if ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
	#	return None
	result = output.getvalue()
	output.close()
	#exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
	return (exc_info[0], exc_info[1], result)

# http://docs.python.org/library/signal.html
# http://code.activestate.com/recipes/307871/ (timeout function with signals)
# http://code.activestate.com/recipes/473878/ (timeout function using threading)
def timeout_handler(signum, frame):
	print '\nTimeout: Signal handler called with signal', signum
	#raise IOError("Couldn't open device!")
	raise IOError("Couldn't open/get url, request timed out!")


def maindisplay():
	param_default = subster_beta.SubsterRobot._param_default
	param_default['postproc'] = re.sub('"', '\'', param_default['postproc'])	# hack: wegen unsauberer def. in 'subster_beta.py'
	param_default.update(sim_param_default)
	params = {}
	for key in param_default.keys():
		params[key] = form.getvalue(key, param_default[key])
		params[key] = re.sub('"', '\\x22', params[key])			# hack: wegen problem zw. " und html form 'maindisplay_content' (probl. mit 'postproc')

	# enhance with add. params
	try:	params.update( eval(params['add_params']) )
	except:	pass

	bot_output = ["(no simulation runned yet...)"]		# index 0 is bot_output, all other are errors
	if (params['action'] == 'runsim'):
		# redirect stdout and stderr
		stdlog = StringIO.StringIO()
		(out_stream, err_stream) = (sys.stdout, sys.stderr)
		(sys.stdout, sys.stderr) = (stdlog, stdlog)

		# Set the signal handler and a ?-second alarm (request max. timeout)
		signal.signal(signal.SIGALRM, timeout_handler)
		signal.alarm(timeout)

		try:
			params['content'] = subster_beta.SubsterRobot().run(sim=params)
		except:
			#params['content'] = "ERROR OCCURRED DURING BOT SIMULATION"
			bot_output.append(gettraceback(sys.exc_info())[2])

		# Cancel the signal handler alarm
		signal.alarm(0)

		# restore stdout and stderr
		(sys.stdout, sys.stderr) = (out_stream, err_stream)
		bot_output[0] = stdlog.getvalue()
		stdlog.close()

	bot_output = re.sub("\n", "<br>\n", "\n".join(bot_output))

	data = {'panel_ver':		__version__,
		'subster_bot_ver':	subster_beta.__version__,
		'bot_output':		bot_output,
		'footer':		footer + footer_w3c,
	}

	if type(params['content']) == type(u""):
		params['content'] = params['content'].encode(config.textfile_encoding)
		#params['content'] = params['content'].encode(config.textfile_encoding).decode("ISO-8859-1")

	data.update( params )

	return maindisplay_content % data


form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', '')
#if action == 'logstat':
#	html = logstat(form)
#else:
#	html = maindisplay()

html = maindisplay()

print html
