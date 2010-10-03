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
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: bot_control.py 0.3.0041 2010-10-03 15:54:26Z drtrigon $'
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


# logging of framework info
infolist = [ pywikibot.__version__, pywikibot.config.__version__,	# framework
             pywikibot.query.__version__, pagegenerators.__version__,	#
             dtbext.pywikibot.__version__, dtbext.basic.__version__,	# DrTrigonBot extensions
             dtbext.date.__version__, dtbext.userlib.__version__,	#
             dtbext.botlist.__version__,				#
             __version__, clean_user_sandbox.__version__,		# bots
             sum_disc.__version__, mailer.__version__,			#
             subster.__version__, page_disc.__version__, ]		#

# bots to run and control
bot_list = { 'clean_user_sandbox': (clean_user_sandbox, u'clean userspace Sandboxes'),
             'sum_disc':           (sum_disc, u'discussion summary'),
             'compress_history':   (sum_disc, u'compressing discussion summary'),
             'replace_tmpl':       (replace_tmpl, u'replace_tmpl'),
             'mailer':             (mailer, u'"MailerBot"'),
             'subster':            (subster, u'"SubsterBot"'),
             'page_disc':          (page_disc, u'page_disc (beta test)'), }
bot_order = [ 'clean_user_sandbox', 'sum_disc', 'compress_history', 'mailer', 'subster', 'page_disc' ]


class SubBotError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


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
	def flush(self):
		self.file.flush()

class OutputLog:
	def __init__(self, addlogname=None):
		if addlogname == None:
			self.logfile = None
		else:
			self.logfile = Logger(logname % dtbext.date.getTimeStmp() + addlogname,
				              encoding=pywikibot.config.textfile_encoding,
				              mode='a+')

		(self.stdout, self.stderr) = (sys.stdout, sys.stderr)

		if self.logfile:
			(sys.stdout, sys.stderr) = (self.logfile, self.logfile)

	def close(self):
		(sys.stdout, sys.stderr) = (self.stdout, self.stderr)

		if self.logfile:
			self.logfile.close()

	def switch(self, addlogname=""):
		pywikibot.output(u'switching log to "...%s.log", please look there ...' % addlogname)

		self.close()
		self.__init__(addlogname=addlogname)


class BotController:
	def __init__(self, bot, desc, run_bot):
		self.bot = bot
		self.desc = desc
		self.run_bot = run_bot
		self.error = None

	def trigger(self):
		if self.run_bot:
			self.run()
		else:
			self.skip()

		if self.error:
			return [self.error]
		else:
			return []

	def skip(self):
		pywikibot.output(u'SKIPPING: ' + self.desc)

	def run(self):
		pywikibot.output(u'RUN BOT: ' + self.desc)

		try:
			self.bot.main()
		except:
			self.error = gettraceback(sys.exc_info())
			if self.error:
				pywikibot.output(u'\03{lightred}%s\03{default}' % self.error[2])
			else:
				raise
			#raise sys.exc_info()[0](sys.exc_info()[1])


def gettraceback(exc_info):
	output = StringIO.StringIO()
	traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)
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
	global log, error_buffer
#	global do_dict		# alle anderen NICHT noetig, warum diese hier ?!?????

	# script call
	pywikibot.output(u'\nSCRIPT CALL:')
	pywikibot.output(u'  ' + u' '.join(sys.argv))

	# logging of framework info
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

	for bot_name in bot_order:
		(bot_module, bot_desc) = bot_list[bot]

		bot = BotController(bot_module,
			            bot_desc,
			            do_dict[bot_name]) )

		#if bot.desc == u'"SubsterBot"':
		if bot_name == 'subster':
			if cron:
				# use another log (for subster because of 'panel.py')
				logname_enh = "_subster"
				log.switch(addlogname=logname_enh)
			# magic words for subster, look also at 'subster.py' (should be strings, but not needed)
			if not no_magic_words:
				bot.bot.magic_words = {'BOTerror':          str(bool(error_buffer)),
				                       'BOTerrortraceback': str([item[2] for item in error_buffer]),}
				                       #'BOTversion':        '0.2.0000, rev. ' + __revision__,
				                       #'BOTrunningsubbots': '...',}
			error_buffer += bot.trigger()
			if cron:
				# back to default log (for everything else than subster)
				logname_enh = ""
				log.switch(addlogname=logname_enh)
		else:
			error_buffer += bot.trigger()

	pywikibot.output(u'\nDone.')
	return


if __name__ == "__main__":
	arg = pywikibot.handleArgs()
	if len(arg) > 0:
		#arg = pywikibot.handleArgs()[0]
		#print sys.argv[0]	# who am I?

		cron = ("-cron" in arg)

		do_dict = { 'clean_user_sandbox': False,
		            'sum_disc':           False,
		            'compress_history':   False,
		            'replace_tmpl':       False,
		            'mailer':             False,
		            'subster':            False,
		            'page_disc':          False,
		}
		logname_enh = ""		
		if ("-all" in arg):
			do_dict.update({ 'clean_user_sandbox': True,
			                 'sum_disc':           True,
			                 #'replace_tmpl':       False,
			                 'mailer':             True,
			                 'subster':            True,
			                 'page_disc':          True,
			})
		elif ("-default" in arg):
			do_dict.update({ 'clean_user_sandbox': True,
			                 'sum_disc':           True,
			                 #'replace_tmpl':       True,
			                 'mailer':             True,
			                 #'subster':            True,
			                 'page_disc':          True,
			})
		elif ("-compress_history:[]" in arg):		# muss alleine laufen, sollte aber mit allen 
			do_dict['compress_history'] = True		# anderen kombiniert werden können (siehe 'else')...!
		elif ("-subster" in arg):
			do_dict['subster'] = True
			logname_enh = "_subster"			# use another log than usual !!!
		else:
			do_dict.update({ 'clean_user_sandbox': ("-clean_user_sandbox" in arg),
			                 'sum_disc':           ("-sum_disc" in arg),
			                 'mailer':             ("-mailer" in arg),
			                 #'subster':            ("-subster" in arg),
			                 'page_disc':          ("-page_disc" in arg),
			})

		if cron:
			log = OutputLog(addlogname=logname_enh)

		no_magic_words = ("-no_magic_words" in arg)

		error_buffer = []
	else:
		log = OutputLog()
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
			error_buffer.append( error )

		for item in error_buffer:		# if Ctrl-C/BREAK/keyb-int; the 'error_buffer' should be empty
			item = item[2]
			# if runned as CRON-job mail occuring exception and traceback to bot admin
			if cron and error_mail_fromwiki:
				pywikibot.output(u'ERROR:\n%s\n' % item)
				pywikibot.output(u'Sending mail "%s" to "%s" as notification!' % (error_mail[1], error_mail[0]))
				usr = userlib.User(pywikibot.getSite(), error_mail[0])
				if not usr.sendMail(subject=error_mail[1], text=item):		# 'item' should be unicode!
					pywikibot.output(u'!!! WARNING: mail could not be sent!')

			# https://wiki.toolserver.org/view/Cronjob#Output use CRON for error and mail handling, if
			# something should be mailed/reported just print it to 'log.stdout' or 'log.stderr'
			print >> log.stdout, item

		raise #sys.exc_info()[0](sys.exc_info()[1])
	finally:
		pywikibot.stopme()

	log.close()

