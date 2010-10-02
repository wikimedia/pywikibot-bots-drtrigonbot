# -*- coding: utf-8  -*-
"""
This bot is the general DrTrigonBot caller. It runs all the different sub tasks,
that DrTrigonBot does. That are:
	-sandbox cleaner
	-sum disc (sum disc hisory compression)
	-mailer
	-subster
	-page disc		[experimental]
...

Options/parameters:
	-cron	run as CRON job, no output to stdout and stderr except error output
		that should be sent by mail, all other output goes to a log file


Run all bots (output to stdout):
	python bot_control.py
NEW:	python bot_control.py -all
(do user_sandbox, sum_disc, mailer, subster)

# Run all bots as CRON job (output to log on server, and another one for subster):
# NEW:	python bot_control.py -all -cron
# (do user_sandbox, sum_disc, mailer, subster, page_disc / ATTENTION: this mode uses 2 log files !!!)
# CRON (toolserver):
# # m h  dom mon dow   command
# 0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -all -cron
# FUNKTIONIERT LEIDER NOCH NICHT, DA ZUM ZEITPUNKT DER AUSFUEHRUNG VON SUBSTER IM LOG 'Done.'
# NOCH NICHT GESCHRIEBEN WURDE, ALSO EIN FEHLER GEMELDET WIRD!!! Waere cool, da es magic_words
# liefern wuerde.

Run default bot set as CRON job (output to log on server):
	python bot_control.py -cron
NEW:	python bot_control.py -default -cron
(do user_sandbox, sum_disc, mailer, page_disc / skip subster)
CRON (toolserver):
# m h  dom mon dow   command
0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -default -cron

Run sum_disc.py history compression as CRON job (output to log on server):
	python bot_control.py -skip_clean_user_sandbox -compress_history:[] -cron
NEW:	python bot_control.py -compress_history:[] -cron
(do sum_disc history compression only / skip user_sandbox, sum_disc, mailer, subster)
CRON (toolserver):
# m h  dom mon dow   command
0 0 */14 * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -compress_history:[] -cron

Run subster bot only as CRON job (output to own log not to disturb the output of 'panel.py'
and run stand-alone to catch failed other runs...):
	python bot_control.py -subster -no_magic_words -cron
(do subster / skip user_sandbox, sum_disc, mailer / ATTENTION: this mode uses another log than usual !!!)
CRON (toolserver):
# m h  dom mon dow   command
0 */12 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -no_magic_words -cron
0 14 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -no_magic_words -cron


others:
Run all bots in never-ending loop (output to log):
	python bot_control.py -all -auto

Run the bot 'clean_user_sandbox.py' only:
	python bot_control.py -clean_user_sandbox

Run the bot 'sum_disc.py' only:
	python bot_control.py -sum_disc

Run the bot 'mailer.py' only:
	python bot_control.py -mailer


For tests its sometimes better to use:
	python clean_user_sandbox.py
	python sum_disc.py
	python mailer.py
"""

# ====================================================================================================
#
# ToDo-Liste (Bugs, Features, usw.):
# http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste
#
# READ THE *DOGMAS* FIRST!
# 
# CHANGES on pywikipedia framework:
#  - after 0.1.0012
#	wikipedia.py: line 725-728  "make more stable" (+some more...)
#	IMPORTANT: to merge with most recent pywikipedia trunk and take the
#			   newest wikipedia.py from there
#
# ====================================================================================================

#
# (C) Dr. Trigon, 2009
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: bot_control.py 0.3.0040 2010-10-03 00:06 drtrigon $'
__revision__='8601'
#

# wikipedia-bot imports
import pagegenerators, userlib
import sys, os, re, time, codecs
import clean_user_sandbox, sum_disc, mailer, subster, page_disc
#import clean_user_sandbox, sum_disc, replace_tmpl
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot

import traceback, StringIO


logname = pywikibot.config.datafilepath('../public_html/DrTrigonBot', '%s.log')
#os.chdir("/home/drtrigon/pywikipedia")
logger_tmsp = sum_disc.bot_config['logger_tmsp']

error_mail_fromwiki = True				# send error mail from wiki too!
error_mail          = (u'DrTrigon', u'Bot ERROR')	# error mail via wiki mail interface instead of CRON job


class Logger:
	def __init__(self, filename, **param):
		self.file = codecs.open(filename, **param)
		self._filename = filename
		self._param = param
	def write(self, string):
		self.file.flush()
		string = re.sub('\x1B\[.*?m', '', string)	# make more readable
		string = re.sub('\x03\{.*?\}', '', string)	#
		if logger_tmsp: string = re.sub('\n', '\n' + dtbext.date.getTimeStmp(full = True, humanreadable = True, local = True) + ':: ', string)
		result = self.file.write( str(string).decode('latin-1') )
		self.file.flush()
		return result
	def close(self):
		self.file.close()
		#del self.file
		self.file = None
		return
	def flush(self):
		self.file.flush()
		#pass
	def slow_write(self, string):
		try:
			if self.file: return
			self.__init__(self._filename, **self._param)
			self.write(string)
			self.file.close()
		except:
			print "DEBUG: slow_write error"
		return

class SubBotError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class BotController:
	def __init__(self, bot, desc):
		self.bot = bot
		self.desc = desc

	def run(self):
		pywikibot.output(u'RUN BOT: ' + self.desc)

		try:
			self.bot.main()
		except:
			error = gettraceback(sys.exc_info())
			if error:
				pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
				error_buffer.append( error )
			else:
				raise
			#raise sys.exc_info()[0](sys.exc_info()[1])


def setlogfile(addlogname = ""):
	#logfile = Logger(logname % time.strftime("%Y%m%d", time.gmtime()), encoding=config.textfile_encoding, mode='a+')
	logfile = Logger(logname % dtbext.date.getTimeStmp() + addlogname, encoding=pywikibot.config.textfile_encoding, mode='a+')
	(out_stream, err_stream) = (sys.stdout, sys.stderr)
	(sys.stdout, sys.stderr) = (logfile, logfile)
	return (logfile, out_stream, err_stream)

def gettraceback(exc_info):
	output = StringIO.StringIO()
	traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)
	#if not ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
	#	result = output.getvalue()
	if ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
		return None
	result = output.getvalue()
	output.close()
	#exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
	return (exc_info[0], exc_info[1], result)

def getversion_svn():
	# framework revision?
	pywikibot.output(u'LATEST FRAMEWORK REVISION:')
	buf = pywikibot.getSite().getUrl( 'http://svn.wikimedia.org/viewvc/pywikipedia/trunk/pywikipedia/', no_hostname = True, retry = False )
	match = re.search('<td>Directory revision:</td>\n<td><a (.*?)>(.*?)</a> \(of <a (.*?)>(.*?)</a>\)</td>', buf)
	if match and (len(match.groups()) > 0):
		info = {True: '=', False: '>'}		
		pywikibot.output(u'  Directory revision: %s (%s %s)' % (match.groups()[-1], info[(match.groups()[-1]==__revision__)], __revision__))
	else:
		pywikibot.output(u'  WARNING: could not retrieve information!')


def main():
	global logfile, out_stream, err_stream, error_buffer
	global do_subster		# alle anderen NICHT noetig, warum diese hier ?!?????

	# script call
	#pywikibot.output(u'SCRIPT CALL:')
	pywikibot.output(u'\nSCRIPT CALL:')
	pywikibot.output(u'  ' + u' '.join(sys.argv))

	# logging of framework info
	infolist = [ pywikibot.__version__, pywikibot.config.__version__,		# framework
		pywikibot.query.__version__, pagegenerators.__version__,	#
		dtbext.pywikibot.__version__, dtbext.basic.__version__,		# DrTrigonBot extensions
		dtbext.date.__version__, dtbext.userlib.__version__,		#
		dtbext.botlist.__version__,					#
		__version__, clean_user_sandbox.__version__,			# bots
		sum_disc.__version__, mailer.__version__,			#
		subster.__version__, page_disc.__version__ ]			#
	pywikibot.output(u'FRAMEWORK VERSION:')
	for item in infolist: pywikibot.output(u'  %s' % item)

	# new framework revision?
	getversion_svn()

	# processing of messages on bot discussion page
	if pywikibot.getSite().messages():
		pywikibot.output(u'====== new messages on bot discussion page =======')
		messagesforbot = pywikibot.Page(pywikibot.getSite(), u'Benutzer Diskussion:DrTrigonBot').get(get_redirect=True)
		pywikibot.output(messagesforbot)
		pywikibot.output(u'==================================================')

	while True:
		if do_clean_user_sandbox:
			bot = BotController(clean_user_sandbox, u'clean userspace Sandboxes')
			bot.run()
		else:
			pywikibot.output(u'SKIPPING: clean userspace Sandboxes')

		if do_sum_disc or do_compress_history:
			if do_sum_disc:		pywikibot.output(u'RUN SUB-BOT: discussion summary')
			elif do_compress_history:	pywikibot.output(u'RUN SUB-BOT: compressing discussion summary')
			try:
				sum_disc.main()
			except:
				error = gettraceback(sys.exc_info())
				if error:
					pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
					error_buffer.append( error )
				else:
					raise
		else:
			pywikibot.output(u'SKIPPING: discussion summary or compressing discussion summary')

		#if do_replace_tmpl:
		#	pywikibot.output(u'RUN SUB-BOT: replace_tmpl')
		#	try:
		#		replace_tmpl.main()
		#	except:
		#		error = gettraceback(sys.exc_info())
		#		if error:
		#			pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
		#			error_buffer.append( error )
		#		else:
		#			raise
		#else:
		#	pywikibot.output(u'SKIPPING: replace_tmpl')

		if do_mailer:
			bot = BotController(clean_user_sandbox, u'"MailerBot"')
			bot.run()
		else:
			pywikibot.output(u'SKIPPING: "MailerBot"')

		if do_subster:
			pywikibot.output(u'RUN SUB-BOT: "SubsterBot"')

			if cron:
				# use another log (for subster because of 'panel.py')
				logname_enh = "_subster"
				pywikibot.output(u'switching log to "...%s.log", please look there ...' % logname_enh)
				(sys.stdout, sys.stderr) = (out_stream, err_stream)
				logfile.close()
				(logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)

			try:
				# magic words for subster, look also at 'subster.py' (should be strings, but not needed)
				if not no_magic_words:
					subster.magic_words = {'BOTerror':		  str(bool(error_buffer)),
										   'BOTerrortraceback': str([item[2] for item in error_buffer]),}
										   #'BOTversion':		'0.2.0000, rev. ' + __revision__,
										   #'BOTrunningsubbots': '...',}
				subster.main()
			except:
				error = gettraceback(sys.exc_info())
				if error:
					pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
					error_buffer.append( error )
				else:
					raise

			if cron:
				# back to default log (for everything else than subster)
				logname_enh = ""
				pywikibot.output(u'switching log to "...%s.log", please look there ...' % logname_enh)
				(sys.stdout, sys.stderr) = (out_stream, err_stream)
				logfile.close()
				(logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)
		else:
			pywikibot.output(u'SKIPPING: "SubsterBot"')

		if do_page_disc:
			pywikibot.output(u'RUN SUB-BOT: page_disc')
			try:
				page_disc.main()
			except:
				error = gettraceback(sys.exc_info())
				if error:
					pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
					error_buffer.append( error )
				else:
					raise
		else:
			pywikibot.output(u'SKIPPING: page_disc')

		if no_repeat:
			pywikibot.output(u'\nDone.')
			return
		else:
			now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
			pywikibot.output(u'\nSleeping %s hours, now %s' % (hours, now))
			(sys.stdout, sys.stderr) = (out_stream, err_stream)
			logfile.close()
			time.sleep(hours * 60 * 60)
			#time.sleep(5)
			(logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)


if __name__ == "__main__":
	hours = 48
	no_repeat = True
	arg = pywikibot.handleArgs()
	if len(arg) > 0:
		#arg = pywikibot.handleArgs()[0]
		#print sys.argv[0]	# who am I?
		#if (arg[:5] == "-auto") or (arg[:5] == "-cron"):

		cron			= ("-cron" in arg)

		do_clean_user_sandbox	= False
		do_sum_disc		= False
		do_compress_history 	= False
		do_replace_tmpl		= False
		do_mailer		= False
		do_subster		= False
		do_page_disc	= False
		logname_enh = ""		
		if ("-all" in arg):
			do_clean_user_sandbox	= True
			do_sum_disc			= True
			#do_replace_tmpl		= True
			do_mailer			= True
			do_subster			= True
			do_page_disc		= True
		elif ("-default" in arg):
			do_clean_user_sandbox	= True
			do_sum_disc			= True
			#do_replace_tmpl		= True
			do_mailer			= True
			#do_subster			= True
			do_page_disc		= True
		elif ("-compress_history:[]" in arg):		# muss alleine laufen, sollte aber mit allen 
			do_compress_history 	= True		# anderen kombiniert werden können (siehe 'else')...!
		elif ("-subster" in arg):
			do_subster			= True
			logname_enh = "_subster"			# use another log than usual !!!
		else:
			do_clean_user_sandbox	= ("-clean_user_sandbox" in arg)
			do_sum_disc		= ("-sum_disc" in arg)
			do_mailer		= ("-mailer" in arg)
			#do_subster		= ("-subster" in arg)
			do_page_disc	= ("-page_disc" in arg)

		if ("-auto" in arg) or cron:
			#logfile = file(logname, "w")
			#(out_stream, err_stream) = (sys.stdout, sys.stderr)
			#(sys.stdout, sys.stderr) = (logfile, logfile)
			(logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)
			#no_repeat = False
			#no_repeat = not (arg[:5] == "-auto")
			no_repeat = not ("-auto" in arg)

		no_magic_words = ("-no_magic_words" in arg)

		error_buffer = []
	else:
		(out_stream, err_stream) = (sys.stdout, sys.stderr)
		choice = pywikibot.inputChoice('Do you want to compress the histories?', ['Yes', 'No'], ['y', 'n'])
		if choice == 'y':
			logs = os.listdir(u'logs')
			for item in logs:
				if item[-4:] == u'.dat':
					user = re.findall(u'sum_disc-%s-%s-(.*?).dat' % (u'wikipedia', u'de'), item)[0]

					sys.argv.append( repr(u'-compress_history:%s' % user) )
					sum_disc.main()
					del sys.argv[1]

	try:
		main()
		if error_buffer:	# SubBot error
			raise SubBotError('exception(s) occured in SubBot')
	except:
		error = gettraceback(sys.exc_info())
		if error:				# sub-bot error OR other/unexpected error
			#pywikibot.output(u'\03{lightred}%s\03{default}' % error[2])
			error_buffer.append( error )
		#else:					# Ctrl-C/BREAK/keyb-int
		#	raise

		if cron:	# if runned as CRON-job mail occuring exception and traceback to bot admin
			for item in error_buffer:		# if Ctrl-C/BREAK/keyb-int; the 'error_buffer' should be empty
				item = item[2]
				if error_mail_fromwiki:
					pywikibot.output(u'ERROR:\n%s\n' % item)
					pywikibot.output(u'Sending mail "%s" to "%s" as notification!' % (error_mail[1], error_mail[0]))
					usr = userlib.User(pywikibot.getSite(), error_mail[0])
					if not usr.sendMail(subject=error_mail[1], text=item):		# 'item' should be unicode!
						pywikibot.output(u'!!! WARNING: mail could not be sent!')

				# https://wiki.toolserver.org/view/Cronjob#Output use CRON for error and mail handling, if
				# something should be mailed/reported just print it to 'out_stream' or 'err_stream'
				print >> out_stream, item
		raise
		#raise sys.exc_info()[0](sys.exc_info()[1])
	finally:
		pywikibot.stopme()

	if not no_repeat:
		(sys.stdout, sys.stderr) = (out_stream, err_stream)
		logfile.close()

