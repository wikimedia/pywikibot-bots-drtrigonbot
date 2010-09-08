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
	python runbotrun.py
NEW:	python runbotrun.py -all
(do user_sandbox, sum_disc, mailer, subster)

# Run all bots as CRON job (output to log on server, and another one for subster):
# NEW:	python runbotrun.py -all -cron
# (do user_sandbox, sum_disc, mailer, subster, page_disc / ATTENTION: this mode uses 2 log files !!!)
# CRON (toolserver):
# # m h  dom mon dow   command
# 0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/runbotrun.py -all -cron
# FUNKTIONIERT LEIDER NOCH NICHT, DA ZUM ZEITPUNKT DER AUSFUEHRUNG VON SUBSTER IM LOG 'Done.'
# NOCH NICHT GESCHRIEBEN WURDE, ALSO EIN FEHLER GEMELDET WIRD!!! Waere cool, da es magic_words
# liefern wuerde.

Run default bot set as CRON job (output to log on server):
	python runbotrun.py -cron
NEW:	python runbotrun.py -default -cron
(do user_sandbox, sum_disc, mailer, page_disc / skip subster)
CRON (toolserver):
# m h  dom mon dow   command
0 2 * * * nice -n +15 python /home/drtrigon/pywikipedia/runbotrun.py -default -cron

Run sum_disc.py history compression as CRON job (output to log on server):
	python runbotrun.py -skip_clean_user_sandbox -compress_history:[] -cron
NEW:	python runbotrun.py -compress_history:[] -cron
(do sum_disc history compression only / skip user_sandbox, sum_disc, mailer, subster)
CRON (toolserver):
# m h  dom mon dow   command
0 0 */14 * * nice -n +15 python /home/drtrigon/pywikipedia/runbotrun.py -compress_history:[] -cron

Run subster bot only as CRON job (output to own log not to disturb the output of 'panel.py'
and run stand-alone to catch failed other runs...):
	python runbotrun.py -subster -no_magic_words -cron
(do subster / skip user_sandbox, sum_disc, mailer / ATTENTION: this mode uses another log than usual !!!)
CRON (toolserver):
# m h  dom mon dow   command
0 */12 * * * nice -n +15 python /home/drtrigon/pywikipedia/runbotrun.py -subster -no_magic_words -cron
0 14 * * * nice -n +15 python /home/drtrigon/pywikipedia/runbotrun.py -subster -no_magic_words -cron


others:
Run all bots in never-ending loop (output to log):
	python runbotrun.py -all -auto

Run the bot 'clean_user_sandbox.py' only:
	python runbotrun.py -clean_user_sandbox

Run the bot 'sum_disc.py' only:
	python runbotrun.py -sum_disc

Run the bot 'mailer.py' only:
	python runbotrun.py -mailer


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
#    wikipedia.py: line 725-728  "make more stable" (+some more...)
#    IMPORTANT: to merge with most recent pywikipedia trunk and take the
#               newest wikipedia.py from there
#
# ====================================================================================================

#
# (C) Dr. Trigon, 2009
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
__version__='$Id: runbotrun.py 0.2.0001 2009-06-05 14:56:00Z drtrigon $'
__revision__='8072'
#

# wikipedia-bot imports
import wikipedia, config, query, pagegenerators
import sys, os, re, time, codecs
import clean_user_sandbox, sum_disc, mailer, subster, page_disc
#import clean_user_sandbox, sum_disc, replace_tmpl
import dtbext

import traceback, StringIO


# ====================================================================================================
#
# read external config vars
#exec(open("sum_disc-conf.py","r").read(-1))
from sum_disc_conf import *
#
# ====================================================================================================

#logname = "../public_html/DrTrigonBot/%s.log"
#logname = "/home/drtrigon/public_html/DrTrigonBot/%s.log"
logname = conf['logger_path']
#os.chdir("/home/drtrigon/pywikipedia")
logger_tmsp = conf['logger_tmsp']

error_mail_fromwiki	= True					# send error mail from wiki too!
error_mail		= ('DrTrigon', 'Bot ERROR')	# error mail via wiki mail interface instead of CRON job


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

def setlogfile(addlogname = ""):
    #logfile = Logger(logname % time.strftime("%Y%m%d", time.gmtime()), encoding=config.textfile_encoding, mode='a+')
    logfile = Logger(logname % dtbext.date.getTimeStmp() + addlogname, encoding=config.textfile_encoding, mode='a+')
    (out_stream, err_stream) = (sys.stdout, sys.stderr)
    (sys.stdout, sys.stderr) = (logfile, logfile)
    return (logfile, out_stream, err_stream)

def gettraceback(exc_info):
    output = StringIO.StringIO()
    traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], file=output)
    #if not ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
    #    result = output.getvalue()
    if ('KeyboardInterrupt\n' in traceback.format_exception_only(exc_info[0], exc_info[1])):
        return None
    result = output.getvalue()
    output.close()
    #exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    return (exc_info[0], exc_info[1], result)

def main():
    global logfile, out_stream, err_stream, error_buffer
    global do_subster		# alle anderen NICHT noetig, warum diese hier ?!?????

    # script call
    #wikipedia.output(u'SCRIPT CALL:')
    wikipedia.output(u'\nSCRIPT CALL:')
    wikipedia.output(u'  ' + u' '.join(sys.argv))

    # logging of framework info
    infolist = [ config.__version__, pagegenerators.__version__, query.__version__, wikipedia.__version__,	# framework
		dtbext.pagegenerators.__version__, dtbext.query.__version__, dtbext.wikipedia.__version__,	# DrTrigonBot extensions
		dtbext.date.__version__, dtbext.config.__version__,						#
		__version__, clean_user_sandbox.__version__, sum_disc.__version__, mailer.__version__,		# bots
		subster.__version__, page_disc.__version__ ]												#
    wikipedia.output(u'FRAMEWORK VERSION:')
    for item in infolist: wikipedia.output(u'  %s' % item)

    # new framework revision?
    wikipedia.output(u'LATEST FRAMEWORK REVISION:')
    #buf = wikipedia.getSite().getUrl( 'http://svn.wikimedia.org/viewvc/pywikipedia/trunk/pywikipedia/', no_hostname = True )
    buf = wikipedia.getSite().getUrl( 'http://svn.wikimedia.org/viewvc/pywikipedia/trunk/pywikipedia/', no_hostname = True, retry = False )
    match = re.search('<td>Directory revision:</td>\n<td><a (.*?)>(.*?)</a> \(of <a (.*?)>(.*?)</a>\)</td>', buf)
    if match and (len(match.groups()) > 0):
        info = {True: '=', False: '>'}        
        wikipedia.output(u'  Directory revision: %s (%s %s)' % (match.groups()[-1], info[(match.groups()[-1]==__revision__)], __revision__))
    else:
        wikipedia.output(u'  WARNING: could not retrieve information!')

    # processing of messages on bot discussion page
    if wikipedia.getSite().messages():
        wikipedia.output(u'====== new messages on bot discussion page =======')
        messagesforbot = wikipedia.Page(wikipedia.getSite(), u'Benutzer Diskussion:DrTrigonBot').get(get_redirect=True)
        wikipedia.output(messagesforbot)
        wikipedia.output(u'==================================================')

    while True:
        if do_clean_user_sandbox:
            wikipedia.output(u'RUN SUB-BOT: clean userspace Sandboxes')
            try:
                clean_user_sandbox.main()
            except:
                error = gettraceback(sys.exc_info())
                if error:
                    wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
                    error_buffer.append( error )
                else:
                    raise
                #raise sys.exc_info()[0](sys.exc_info()[1])
        else:
			wikipedia.output(u'SKIPPING: clean userspace Sandboxes')

        if do_sum_disc or do_compress_history:
            if do_sum_disc:		wikipedia.output(u'RUN SUB-BOT: discussion summary')
            elif do_compress_history:	wikipedia.output(u'RUN SUB-BOT: compressing discussion summary')
            try:
                sum_disc.main()
            except:
                error = gettraceback(sys.exc_info())
                if error:
                    wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
                    error_buffer.append( error )
                else:
                    raise
        else:
			wikipedia.output(u'SKIPPING: discussion summary or compressing discussion summary')

        #if do_replace_tmpl:
        #    wikipedia.output(u'RUN SUB-BOT: replace_tmpl')
        #    try:
        #        replace_tmpl.main()
        #    except:
        #        error = gettraceback(sys.exc_info())
        #        if error:
        #            wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
        #            error_buffer.append( error )
        #        else:
        #            raise
        #else:
		#	wikipedia.output(u'SKIPPING: replace_tmpl')

        if do_mailer:
            wikipedia.output(u'RUN SUB-BOT: "MailerBot"')
            try:
                mailer.main()
            except:
                error = gettraceback(sys.exc_info())
                if error:
                    wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
                    error_buffer.append( error )
                else:
                    raise
        else:
			wikipedia.output(u'SKIPPING: "MailerBot"')

        if do_subster:
            wikipedia.output(u'RUN SUB-BOT: "SubsterBot"')

            if cron:
                # use another log (for subster because of 'panel.py')
                logname_enh = "_subster"
                wikipedia.output(u'switching log to "...%s.log", please look there ...' % logname_enh)
                (sys.stdout, sys.stderr) = (out_stream, err_stream)
                logfile.close()
                (logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)

            try:
                # magic words for subster, look also at 'subster.py' (should be strings, but not needed)
                if not no_magic_words:
                    subster.magic_words = {'BOTerror':          str(bool(error_buffer)),
                                           'BOTerrortraceback': str([item[2] for item in error_buffer]),}
                                           #'BOTversion':        '0.2.0000, rev. ' + __revision__,
                                           #'BOTrunningsubbots': '...',}
                subster.main()
            except:
                error = gettraceback(sys.exc_info())
                if error:
                    wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
                    error_buffer.append( error )
                else:
                    raise

            if cron:
                # back to default log (for everything else than subster)
                logname_enh = ""
                wikipedia.output(u'switching log to "...%s.log", please look there ...' % logname_enh)
                (sys.stdout, sys.stderr) = (out_stream, err_stream)
                logfile.close()
                (logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)
        else:
			wikipedia.output(u'SKIPPING: "SubsterBot"')

        if do_page_disc:
            wikipedia.output(u'RUN SUB-BOT: page_disc')
            try:
                page_disc.main()
            except:
                error = gettraceback(sys.exc_info())
                if error:
                    wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
                    error_buffer.append( error )
                else:
                    raise
        else:
			wikipedia.output(u'SKIPPING: page_disc')

        if no_repeat:
            wikipedia.output(u'\nDone.')
            return
        else:
            now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
            wikipedia.output(u'\nSleeping %s hours, now %s' % (hours, now))
            (sys.stdout, sys.stderr) = (out_stream, err_stream)
            logfile.close()
            time.sleep(hours * 60 * 60)
            #time.sleep(5)
            (logfile, out_stream, err_stream) = setlogfile(addlogname=logname_enh)


if __name__ == "__main__":
    hours = 48
    no_repeat = True
    arg = wikipedia.handleArgs()
    if len(arg) > 0:
        #arg = wikipedia.handleArgs()[0]
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
        choice = wikipedia.inputChoice('Do you want to compress the histories?', ['Yes', 'No'], ['y', 'n'])
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
            #wikipedia.output(u'\03{lightred}%s\03{default}' % error[2])
            error_buffer.append( error )
        #else:					# Ctrl-C/BREAK/keyb-int
        #    raise

        if cron:	# if runned as CRON-job mail occuring exception and traceback to bot admin
            for item in error_buffer:		# if Ctrl-C/BREAK/keyb-int; the 'error_buffer' should be empty
                item = item[2]
                if error_mail_fromwiki:
                    wikipedia.output(u'ERROR:\n%s\n' % item)
                    wikipedia.output(u'Sending mail "%s" to "%s" as notification!' % (error_mail[1], error_mail[0]))
                    if not dtbext.wikipedia.SendMail(error_mail[0], error_mail[1], item):
                        wikipedia.output(u'!!! WARNING: mail could not be sent!')

                # https://wiki.toolserver.org/view/Cronjob#Output use CRON for error and mail handling, if
                # something should be mailed/reported just print it to 'out_stream' or 'err_stream'
                print >> out_stream, item
        raise
        #raise sys.exc_info()[0](sys.exc_info()[1])
    finally:
        wikipedia.stopme()

    if not no_repeat:
        (sys.stdout, sys.stderr) = (out_stream, err_stream)
        logfile.close()

