#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
This bot is the general DrTrigonBot caller. It runs all the different sub tasks,
that DrTrigonBot does. That are:
	-sandbox cleaner
	-sum disc (sum disc hisory compression)
	-subster
	-page disc		[experimental]
...

Options/parameters:
	-cron	run as CRON job, no output to stdout and stderr except error output
		that should be sent by mail, all other output goes to a log file
"""
## @package bot_control
#  @brief   General DrTrigonBot Robot(s) Caller
#
#  @copyright Dr. Trigon, 2008-2010
#
#  @todo      look also at and learn from daemonize.py (@ref daemonize)
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
#  @section Usage
#  @li Run all bots (according to bot_control.bot_order) with output to stdout:
#  @verbatim python bot_control.py -all @endverbatim
#
#  @li Run all bots (according to bot_control.bot_order) as CRON job with output to log on server,
#  and another one for subster.SubsterBot:
#  @verbatim python bot_control.py -all -cron @endverbatim
#  CRON (toolserver):
#  @verbatim # m h  dom mon dow   command
#  0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -all -cron @endverbatim
#  @attention
#  Zum Zeitpunkt der Ausführung von subster ist im log 'DONE.' noch nicht geschrieben, aber es
#  sind subster.magic_words vorhanden. Um ALLES zu prüfen ist ein separater @ref subster Lauf nötig.
#  \n(this mode uses 2 log files !!!)
#
#  @li Run default bot set (clean_user_sandbox, sum_disc, @ref subster, page_disc) as CRON job with output
#  to log on server:
#  @verbatim python bot_control.py -default -cron @endverbatim
#  CRON (toolserver):
#  @verbatim # m h  dom mon dow   command
#  0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -default -cron @endverbatim
#
#  @li Run sum_disc history compression as CRON job with output to log on server:
#  @verbatim python bot_control.py -compress_history:[] -cron @endverbatim
#  CRON (toolserver):
#  @verbatim # m h  dom mon dow   command
#  0 0 */14 * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -compress_history:[] -cron @endverbatim
#
#  @li Run @ref subster bot only as CRON job with output to own log not to disturb the output of 
#  'panel.py' (run stand-alone to catch failed other runs):
#  @verbatim python bot_control.py -subster -no_magic_words -cron @endverbatim
#  CRON (toolserver):
#  @verbatim # m h  dom mon dow   command
#  0 */12 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -no_magic_words -cron
#  0 14 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -no_magic_words -cron @endverbatim
#  @attention
#  (this mode uses another log than usual !!!)
#
#  @li Run the bot clean_user_sandbox only:
#  @verbatim python bot_control.py -clean_user_sandbox @endverbatim
#
#  @li Run the bot sum_disc only:
#  @verbatim python bot_control.py -sum_disc @endverbatim
#
#  @li For tests its sometimes better to invoke the bot scripts separately:
#  @verbatim python clean_user_sandbox.py @endverbatim
#  @verbatim python sum_disc.py @endverbatim
#
__version__  = '$Id$'
__revision__ = '8881'
#

# wikipedia-bot imports
import pagegenerators, userlib, botlist
import sys, os, re, time, codecs
import clean_user_sandbox, sum_disc, subster, page_disc
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
             botlist.__version__,					#
             dtbext.pywikibot.__version__, dtbext.basic.__version__,	# DrTrigonBot extensions
             dtbext.date.__version__, dtbext.userlib.__version__,	#
             __version__, clean_user_sandbox.__version__,		# bots
             sum_disc.__version__, subster.__version__,			#
             page_disc.__version__, ]					#

# bots to run and control
bot_list = { 'clean_user_sandbox': (clean_user_sandbox, u'clean userspace Sandboxes'),
             'sum_disc':           (sum_disc, u'discussion summary'),
             'compress_history':   (sum_disc, u'compressing discussion summary'),
             #'replace_tmpl':       (replace_tmpl, u'replace_tmpl'),
             'subster':            (subster, u'"SubsterBot"'),
             'page_disc':          (page_disc, u'page_disc (beta test)'), }
#bot_order = [ 'clean_user_sandbox', 'sum_disc', 'compress_history', 'subster', 'page_disc' ]
bot_order = [ 'clean_user_sandbox', 'sum_disc', 'subster' ] # debug


# Bot Error Handling; to prevent bot errors to stop execution of other bots
class BotError(pywikibot.Error):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class BotErrorHandler:
	def __init__(self):
		self.error_buffer = []

	def raise_exceptions(self):
		if self.error_buffer:
			#raise BotError('Exception(s) occured in Bot')
			pywikibot.output( u'BotError: ' + str(BotError('Exception(s) occured in Bot')) )

	def handle_exceptions(self, log):
		self.gettraceback(sys.exc_info())

		for item in self.error_buffer:		# if Ctrl-C/BREAK/keyb-int; the 'error_buffer' should be empty
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

	def gettraceback(self, exc_info):
		output = StringIO.StringIO()
		traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)
		if ('KeyboardInterrupt\n' not in traceback.format_exception_only(exc_info[0], exc_info[1])):
			result = output.getvalue()
			output.close()
			#exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			#return (exc_info[0], exc_info[1], result)
			error = (exc_info[0], exc_info[1], result)
			self.error_buffer.append( error )

			pywikibot.output(u'\n\03{lightred}%s\03{default}' % error[2])

## BotController (or WatchDog) class.
#
class BotController:
	def __init__(self, bot, desc, run_bot, ErrorHandler):
		self.bot          = bot
		self.desc         = desc
		self.run_bot      = run_bot
		self.ErrorHandler = ErrorHandler

	def trigger(self):
		if self.run_bot:
			self.run()
		else:
			self.skip()

	def skip(self):
		pywikibot.output(u'\nSKIPPING: ' + self.desc)

	def run(self):
		pywikibot.output(u'\nRUN BOT: ' + self.desc)

		try:
			self.bot.main()
		except:
			self.ErrorHandler.gettraceback(sys.exc_info())


# Bot Output Redirecting And Logging; to assure all output is logged into file
class Logger:
	def __init__(self, filename, **param):
		self.file = codecs.open(filename, **param)
		self._filename = filename
		self._param = param
	def write(self, string):
		self.file.flush()
		string = re.sub('\x1B\[.*?m', '', string)	# make more readable
		string = re.sub('\x03\{.*?\}', '', string)	#
		if logger_tmsp: string = re.sub('\n', '\n' + dtbext.date.getTimeStmpNow(full = True, humanreadable = True, local = True) + ':: ', string)
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
			self.logfile = Logger(logname % dtbext.date.getTimeStmpNow() + addlogname,
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


# Retrieve revision number of pywikibedia framework
def getversion_svn():
	# framework revision?
	buf = pywikibot.getSite().getUrl( 'http://svn.wikimedia.org/viewvc/pywikipedia/trunk/pywikipedia/', no_hostname = True, retry = False )
	match = re.search('<td>Directory revision:</td>\n<td><a (.*?)>(.*?)</a> \(of <a (.*?)>(.*?)</a>\)</td>', buf)
	if match and (len(match.groups()) > 0):
		info = {True: '=', False: '>'}		
		pywikibot.output(u'  Directory revision: %s (%s %s)' % (match.groups()[-1], info[(match.groups()[-1]==__revision__)], __revision__))
	else:
		pywikibot.output(u'  WARNING: could not retrieve information!')


# main procedure
def main():
#	global log, error
#	global do_dict		# alle anderen NICHT noetig, warum diese hier ?!?????

	# script call
	pywikibot.output(u'SCRIPT CALL:')
	pywikibot.output(u'  ' + u' '.join(sys.argv))

	# logging of framework info
	pywikibot.output(u'\nFRAMEWORK VERSION:')
	for item in infolist: pywikibot.output(u'  %s' % item)

	# new framework revision?
	pywikibot.output(u'\nLATEST FRAMEWORK REVISION:')
	getversion_svn()

	# processing of messages on bot discussion page
	if pywikibot.getSite().messages():
		pywikibot.output(u'====== new messages on bot discussion page =======')
		messagesforbot = pywikibot.Page(pywikibot.getSite(), u'Benutzer Diskussion:DrTrigonBot').get(get_redirect=True)
		pywikibot.output(messagesforbot)
		pywikibot.output(u'==================================================')

	for bot_name in bot_order:
		(bot_module, bot_desc) = bot_list[bot_name]

		bot = BotController(bot_module,
			            bot_desc,
			            do_dict[bot_name],
		                    error )

		#if bot.desc == u'"SubsterBot"':
		if bot_name == 'subster':
			if cron:
				# use another log (for subster because of 'panel.py')
				logname_enh = "_subster"
				log.switch(addlogname=logname_enh)
			# magic words for subster, look also at 'subster.py' (should be strings, but not needed)
			if not no_magic_words:
				bot.bot.magic_words = {'BOTerror':          str(bool(error.error_buffer)),
				                       'BOTerrortraceback': str([item[2] for item in error.error_buffer]),}
				                       #'BOTversion':        '0.2.0000, rev. ' + __revision__,
				                       #'BOTrunningsubbots': bot_order,}
			bot.trigger()
			if cron:
				# back to default log (for everything else than subster)
				logname_enh = ""
				log.switch(addlogname=logname_enh)
		else:
			bot.trigger()

	pywikibot.output(u'\nDONE.')
	return


if __name__ == "__main__":
	arg = pywikibot.handleArgs()
	log = None
	if len(arg) > 0:
		#arg = pywikibot.handleArgs()[0]
		#print sys.argv[0]	# who am I?

		cron = ("-cron" in arg)

		do_dict = { 'clean_user_sandbox': False,
		            'sum_disc':           False,
		            'compress_history':   False,
		            'replace_tmpl':       False,
		            'subster':            False,
		            'page_disc':          False,
		}
		logname_enh = ""		
		if ("-all" in arg):
			do_dict.update({ 'clean_user_sandbox': True,
			                 'sum_disc':           True,
			                 #'replace_tmpl':       False,
			                 'subster':            True,
			                 'page_disc':          True,
			})
		elif ("-default" in arg):
			do_dict.update({ 'clean_user_sandbox': True,
			                 'sum_disc':           True,
			                 #'replace_tmpl':       True,
			                 'subster':            True,
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
			                 #'subster':            ("-subster" in arg),
			                 'page_disc':          ("-page_disc" in arg),
			})

		if cron:
			log = OutputLog(addlogname=logname_enh)

		no_magic_words = ("-no_magic_words" in arg)

		error = BotErrorHandler()
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
		error.raise_exceptions()
	except:
		if log:
			error.handle_exceptions(log)
		raise #sys.exc_info()[0](sys.exc_info()[1])
	finally:
		pywikibot.stopme()

	if log:
		log.close()

