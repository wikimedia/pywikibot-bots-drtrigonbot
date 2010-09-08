# -*- coding: utf-8  -*-
"""
This bot is used for summarize discussions spread over the whole wiki
including all namespaces. It checks several users (at request), sequential 
(currently for the german wiki [de] only).

!!! MAILER BOT HAS TO BE RUN DAILY TO WORK CORRECT AT CURRENT STATE !!!

...
"""

# ====================================================================================================
#
# ToDo-Liste (Bugs, Features, usw.):
# http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste
#
# READ THE *DOGMAS* FIRST!
# 
# ====================================================================================================

#
# (C) Dr. Trigon, 2008, 2009
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_user_sandbox.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', 'sum_disc-conf.py', ...
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id: mailer.py 0.2.0001 2009-08-29 10:12:00Z drtrigon $'
#


import wikipedia, config
import dtbext
import re, sys, os, time
import math
import copy
#import StringIO, pickle


# ====================================================================================================
#
# read external config vars
#from sum_disc_conf import *
tmpl_Mailer = '\{\{Benutzer:DrTrigon/Entwurf/Vorlage:AutoMail(.*?)\}\}'

conf = {	# unicode values
		'userlist':	u'Benutzer:DrTrigon/Entwurf/Vorlage:AutoMail',
		'default':	{ 'expandtemplates':'False', 'clearpage':'False' },
#		'maildb':	'/home/ursin/toolserver/mailerreg.pkl',			# LOCAL
		'maildb':	'/home/drtrigon/mailerreg.pkl',					# TOOLSERVER
}

# debug tools
debug = { 'sendmail': True, 'write2wiki': True, 'forcesend': False }	# operational mode (default)
#debug = { 'sendmail': False, 'write2wiki': False, 'forcesend': False }	# debug mode
#debug = { 'sendmail': False, 'write2wiki': False, 'forcesend': True }	# debug mode
#debug = { 'sendmail': True, 'write2wiki': False, 'forcesend': True }	# debug mode
#debug = { 'sendmail': False, 'write2wiki': True, 'forcesend': False }	# debug mode
#
# ====================================================================================================


class MailerRobot:
	'''
	Robot which will check ...
	'''
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	#_content_maxlen = 3000
	#_content_maxlen = 2900
	_content_maxlen = 100000				# huge, to DEACTIVATE splitting

	_tmpl_regex = re.compile(tmpl_Mailer, re.S)

	def __init__(self):
		'''
		constructor of SumDiscBot(), initialize needed vars
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 30, 17)

        	self._userListPage = dtbext.wikipedia.Page(wikipedia.getSite(), conf['userlist'])

		self._today = int(time.time() / (60*60*24))

		#wikipedia.output(u'\03{lightgreen}* Reading list of users registered for long mail delivery.\03{default}')
		#
		#
		# this function has also to be used in mailer-bot and thus should be put into the dtbext package
		# (it comes from 'mailerreg.py')
		#
		#self._user_longmail = loaduserdb(conf['maildb'])
		self._user_longmail = []			# DEACTIVATE long mail support

	def run(self):
		'''
		run SumDiscBot()
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24, 38, 17)

		wikipedia.output(u'\03{lightgreen}* Processing Template Backlink List:\03{default}')

		#for page in dtbext.pagegenerators.ReferringPageGenerator(self._userListPage):
		for page in dtbext.pagegenerators.ReferringPageGenerator(self._userListPage, onlyTemplateInclusion=True):
			content = self._readPage(page)

			(params, clearedcontent) = self._getMode(content)	# get operating mode

			if not params: continue

			for item in params:
				days = self._today % int(item['Frequenz'])
				if debug['forcesend']:
					days = 0
					wikipedia.output(u'\03{lightred}=== ! DEBUG MODE FORCING MAIL DELIVERY ! ===\03{default}')
				if not (days == 0):
					wikipedia.output(u'INFO: mail to %s will be sent in %i day(s)' % (item['Benutzer'], (int(item['Frequenz'])-days)))
					continue

				wikipedia.output(u'\03{lightblue}** Sending page %s as mail to user %s...\03{default}' % (page.aslink(), item['Benutzer']))

				mail_content = content
				if ( ('expandtemplates' in item) and eval(item['expandtemplates']) ): mail_content = self._readPage(page, full=True)
				mail_content = mail_content.encode(config.textfile_encoding)

				url = "http://" + page.site().hostname() + page.site().nice_get_address(page.title(underscore = True))
				mail_content = url + "\n\n" + mail_content

				#if not dtbext.wikipedia.SendMail(item['Benutzer'], page.title().encode(config.textfile_encoding), mail_content.encode(config.textfile_encoding)):
				success = True
				#item['Benutzer'] = u"DrTrigon"
				if item['Benutzer'] in self._user_longmail:
					wikipedia.output(u"\03{lightblue}*** Sending mail through toolserver (long-mail) ... \03{default}")

					p = {	'email':   self._user_longmail[item['Benutzer']],
						'subject': page.title().encode(config.textfile_encoding),
						'content': mail_content,  }
					success = local_sendmail(p)
					wikipedia.output(u"\03{lightblue}*** Mail '%s' sent. \03{default}" % page.title())
				else:
					wikipedia.output(u"\03{lightblue}*** Sending mail through Wikipedia server (default) ... \03{default}")

					j = 1
					content_maxlen = self._content_maxlen - len(page.title()) - 6	# calc. max len -6 is for the numbers in subject: ' ##/##'
					j_max = math.ceil(float(len(mail_content)) / content_maxlen)
					for i in range(0, len(mail_content), content_maxlen):
						text = mail_content[i:(i+content_maxlen)]
						title = page.title() + (u' %i/%i' % (j, j_max))
						if not debug['sendmail']:
							wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NO MAILS SENT ! ===\03{default}')
							continue
						success = success and dtbext.wikipedia.SendMail(item['Benutzer'], title.encode(config.textfile_encoding), text)
						#success = success and dtbext.wikipedia.SendMail(u"DrTrigon", title.encode(config.textfile_encoding), text)
						j += 1
						wikipedia.output(u"\03{lightblue}*** Mail '%s' sent. \03{default}" % title)

				if not success: wikipedia.output(u'!!! WARNING: mail could not be sent!')

				if success and eval(item['clearpage']):
					if debug['write2wiki']:		# debug mode
						self._writePage(page, clearedcontent + u'\n', u'clearing page after mail has been sent')
					else:
						wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

	def _readPage(self, page, full=False):
		'''
		read wiki page

		input:  page
		returns:  page content [string (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28)

		if full:	(mode, info, plaintext) = ('full', ' using "getFull()" mode', True)
		else:		(mode, info, plaintext) = ('default', '', False)

		#wikipedia.output(u'\03{lightblue}Reading Wiki at %s...\03{default}' % page.aslink())
		wikipedia.output(u'\03{lightblue}Reading Wiki%s at %s...\03{default}' % (info, page.aslink()))
		try:
			#content = page.get()
			content = page.get(mode=mode, plaintext=plaintext)
			#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
			#	wikipedia.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.aslink())
			#	continue
		except (wikipedia.NoPage, wikipedia.IsRedirectPage):
			content = u''
		return content

	def _writePage(self, page, data, comment, minorEdit = True):
		'''
		write wiki page

		input:  page
                        data [string (unicode)]
		returns:  (writes data to page on the wiki, nothing else)
		'''

		wikipedia.output(u'\03{lightblue}Writing to Wiki on %s...\03{default}' % page.aslink())

		wikipedia.setAction(comment)

		content = data
		try:
			if minorEdit:	page.put(content)
			else:		page.put(content, minorEdit = False)
		except wikipedia.SpamfilterError, error:
			wikipedia.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (page.aslink(), "error.url"))

	def _getMode(self, content):
		'''
		get operating mode from page with template by searching the template

		input:  content [text] (page content)
                        self-objects
		returns:  params [dict]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 17)

		#tmpl_buf = self._tmpl_regex.search(content)
		#print "C:", content
		tmpl_buf = self._tmpl_regex.findall(content)
		params = []
		#if tmpl_buf:
		# enhanced: with template
		#for item in tmpl_buf.groups():
		for item in tmpl_buf:
			#tmpl_params = tmpl_buf.groups()[0]
			default = copy.deepcopy(conf['default'])
			tmpl_params = item
			tmpl_params = re.sub('\n', '', tmpl_params)
			tmpl_params = re.sub('\|', "','", tmpl_params)
			tmpl_params = re.sub('=', "':'", tmpl_params)
			#params.append( eval( "{" + tmpl_params[2:] + "'}" ) )
			default.update( eval( "{" + tmpl_params[2:] + "'}" ) )
			params.append( default )

		try:	pos = self._tmpl_regex.search(content).span()
		except:	pos = (0, 0)
		clearedcontent = content[:pos[1]]

		return (params, clearedcontent)

#
# this function has also to be used in mailer-bot and thus should be put into the dtbext package
# (it comes from 'mailerreg.py')
# (from 'mailerreg.py'; ev. besser wenn es in 'dtbext.config' käme und dann von
# 'mailerreg.py' laden wie 'subster.py' von 'substersim.py' geladen wird...)
#
def loaduserdb(path):
	if os.path.exists(path):
		# http://docs.python.org/library/pickle.html
		pkl_file = open(path, 'rb')
		data1 = pickle.load(pkl_file)
		#buf = pkl_file.read()
		#pprint.pprint(data1)
		#data2 = pickle.load(pkl_file)
		#pprint.pprint(data2)
		pkl_file.close()
		return data1
	else:
		return {}

#
# this function has also to be used in mailer-bot and thus should be put into the dtbext package
# (it comes from 'mailerreg.py')
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

def main():
	bot = MailerRobot()	# for several user's, but what about complete automation (continous running...)
	if len(wikipedia.handleArgs()) > 0:
		for arg in wikipedia.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
				bot.silent = True
			elif	(arg == "-all") or ("-mailer" in arg):
				pass
			else:
				wikipedia.showHelp()
				return
	bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

