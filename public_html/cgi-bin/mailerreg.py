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
__version__='$Id: mailerreg.py 0.2.0000 2009-12-29 20:49:00Z drtrigon $'
#


# debug
import cgitb
cgitb.enable()


import cgi
from time import *
# http://www.ibm.com/developerworks/aix/library/au-python/
import os, sys, re
import StringIO, pickle
#import traceback, signal, pprint


footer = """<small>DrTrigonBot mailer registration panel, written by <a href="https://wiki.toolserver.org/view/User:DrTrigon">DrTrigon</a>. 
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

maindisplay_content = """Content-Type: text/html
<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>DrTrigonBot mailer registration panel</title>
  <style type="text/css">
    div.c2 {border-color:#888888; border-width:1px; border-style:solid; padding:4px}
    span.c1 {font-family:sans-serif}
  </style>
</head>

<body>
<p><span class="c1">
DrTrigonBot mailer registration panel<br>
<br><br>
Version:<br>
panel: %(panel_ver)s
<br><br><br>
Registration:
</span></p>
<form action="mailerreg.py">
  <p><span class="c1">
    <input type="hidden" name="action" value="adduser">
    user: <input name="user" type="text" size="60" maxlength="200"><br>
    email: <input name="email" type="text" size="60" maxlength="200"><br>
  </span></p>
  <input type="submit" value=" Add ">
</form>

<p><span class="c1">
<br><br>
Send test mail to registred user:
</span></p>
<form action="mailerreg.py">
  <p><span class="c1">
    <input type="hidden" name="action" value="testmail">
    user: <input name="user" type="text" size="60" maxlength="200"><br>
  </span></p>
  <input type="submit" value=" Send ">
</form>

<p><span class="c1">
<br><br>
Result message:
</span></p>
<p style="border-color:#888888; border-width:1px; border-style:solid; padding:4px"><span class="c1"><small>%(result)s</small></span></p>
<p><span class="c1">
<br>
%(footer)s
</body>
</html>
"""

data_path = '/home/drtrigon/mailerreg.pkl'
#data_path = os.path.join(os.environ['HOME'], 'mailerreg.pkl')


#
# this function has also to be used in mailer-bot and thus should be put into the dtbext package
#
def loaduserdb(path):
	if os.path.exists(path):
		# http://docs.python.org/library/pickle.html
		pkl_file = open(path, 'rb')
		data1 = pickle.load(pkl_file)
		buf = pkl_file.read()
		#pprint.pprint(data1)
		#data2 = pickle.load(pkl_file)
		#pprint.pprint(data2)
		pkl_file.close()

		return data1
	else:
		return {}

def saveuserdb(path, data1):
	#data1 = {'a': [1, 2.0, 3, 4+6j],
	#         'b': ('string', u'Unicode string'),
	#         'c': None}
	#selfref_list = [1, 2, 3]
	#selfref_list.append(selfref_list)
	output = open(path, 'wb')
	# Pickle dictionary using protocol 0.
	pickle.dump(data1, output)
	## Pickle the list using the highest protocol available.
	#pickle.dump(selfref_list, output, -1)
	output.close()

	return

#
# this function has also to be used in mailer-bot and thus should be put into the dtbext package
#
def local_sendmail(mail_params):
	# http://www.daniweb.com/forums/thread15280.html
	# http://bytes.com/topic/python/answers/21352-os-system-stdout-redirection
	# http://stackoverflow.com/questions/73781/sending-mail-via-sendmail-from-python
	#print "mail %s %s" % (data[params['user']], 'abc')

	#os.system("echo abc")
	#prog = os.popen("echo hello")
	#os.system('echo "%(content)s" | mail -s "%(subject)s" %(email)s' % mail_params)

	#prog = os.popen('echo "%(content)s" | mail -s "%(subject)s" %(email)s' % mail_params)
	#prog_buf = prog.read()
	#prog.close()
	#if prog_buf:
	#	print prog_buf
	#	return False

	sendmail_location = "/usr/sbin/sendmail"
	prog = os.popen("%s -t" % sendmail_location, "w")
	prog.write("To: %(email)s\n" % mail_params)
	prog.write("Subject: %(subject)s\n" % mail_params)
	prog.write("\n") # blank line separating headers from body
	prog.write("%(content)s" % mail_params)
	status = prog.close()
	if status and (status != 0):
		print "Sendmail exit status %i" % status
		return False

	return True

def maindisplay():
	params = {}
	params['action'] = form.getvalue('action', '')
	params['user'] = form.getvalue('user', '')
	params['email'] = form.getvalue('email', '')

	bot_output = ['']

	# redirect stdout and stderr
	stdlog = StringIO.StringIO()
	(out_stream, err_stream) = (sys.stdout, sys.stderr)
	(sys.stdout, sys.stderr) = (stdlog, stdlog)

	data1, buf = {}, ''
	if (params['action'] == 'adduser') and params['user'] and params['email']:
		if (not params['email']): return maindisplay_content % data

		data = loaduserdb(data_path)
		if not data:
			print "not db existing (no users registred at all), creating a new one..."

		access = True
		if params['user'] in data:
			print "user already registred, overwriting it..."

			p = {	'email':data[params['user']],
				'subject':'DrTrigonBot mailer config modification',
				'content':'This is a notification mail for DrTrigonBot mailer long mail support registration.\nPlease take note about the fact that your old email %s was replaced/overwritten with the new %s.\nIF this was NOT DONE by you, this is most probably a hijack attempt and you may want to conact the admin of this tool. - DrTrigonBot' % (data[params['user']], params['email'])}
			access = local_sendmail(p)

		if access:
			data[params['user']] = params['email']

			saveuserdb(data_path, data)

			print "email '%s', registred for user '%s'." % (params['email'], params['user'])
		else:
			print "email '%s', could not be registred for user '%s', because of an error." % (params['email'], params['user'])
	elif (params['action'] == 'testmail') and params['user']:
		data = loaduserdb(data_path)
		if not data:
			print "not db existing (no users registred at all), test mail not sent."
		else:
			if params['user'] in data:
				p = {	'email':data[params['user']],
					'subject':'DrTrigonBot mailer test mail',
					'content':'This is a test mail for DrTrigonBot mailer long mail support registration.\nThe fact that you can read this mail is a good sign for everything to work correct.\n\nEnjoy this service - DrTrigonBot'}
				local_sendmail(p)

				print "test mail sent to user '%s'." % (params['user'],)
			else:
				print "user not registred, test mail not sent."
	else:
		print "nothing done (may be you have forgotten to fill all necessary fields)"

	# restore stdout and stderr
	(sys.stdout, sys.stderr) = (out_stream, err_stream)
	bot_output[0] = stdlog.getvalue()
	stdlog.close()

	#bot_output.append( str(data1) )

	bot_output = re.sub("\n", "<br>\n", "\n".join(bot_output))
	if not bot_output: bot_output = "(nothing done yet...)"		# index 0 is bot_output, all other are errors
			
	data = {'panel_ver':		__version__,
		'subster_bot_ver':	'',
		'result':		bot_output,
		'footer':		footer + footer_w3c,
	}

	data.update( params )

	return maindisplay_content % data

#def testdisplay():
#	pass


form = cgi.FieldStorage()

# operational mode
action = form.getvalue('action', '')
#if action == 'testdisplay':
#	html = testdisplay(form)
#else:
#	html = maindisplay()

html = maindisplay()

print html
