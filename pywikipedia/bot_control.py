#!/usr/bin/env python
# -*- coding: utf-8  -*-
#$ -m as
#$ -j y
#$ -b y
# SGE integration/interaction: https://wiki.toolserver.org/view/Job_scheduling
# Tip from Merlissimo: use (a=reschedule or abort, s= suspended) to send mail
# by SGE and exitcode 99 to restart the job and 100 to stop it in error state.
"""
This bot is the general DrTrigonBot caller. It runs all the different sub tasks,
that DrTrigonBot does. That are:
    -sandbox cleaner
    -sum disc (sum disc hisory compression)
    -subster
...

Options/parameters:
    -cron    run as CRON job, no output to stdout and stderr except error output
        that should be sent by mail, all other output goes to a log file
"""
## @package bot_control
#  @brief   General DrTrigonBot Robot(s) Caller
#
#  @copyright Dr. Trigon, 2008-2012
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
#  @li Run default bot set (sum_disc, @ref subster) as CRON job with output
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
#  @verbatim python bot_control.py -subster -cron @endverbatim
#  CRON (toolserver):
#  @verbatim # m h  dom mon dow   command
#  0 */12 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -cron
#  0 14 * * * nice -n +15 python /home/drtrigon/pywikipedia/bot_control.py -subster -cron @endverbatim
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
__version__       = '$Id$'
__framework_rev__ = '11196' # check: http://de.wikipedia.org/wiki/Hilfe:MediaWiki/Versionen
__release_ver__   = '1.5'   # increase minor (1.x) at re-merges with framework
__release_rev__   = '%i'
#

import sys, os, re, time, traceback, shelve
import logging, logging.handlers

# wikipedia-bot imports
import userlib
# Splitting the bot into library parts
from pywikibot import version   # JIRA: DRTRIGON-131
import wikipedia as pywikibot


logname = pywikibot.config.datafilepath('logs', '%s.log')

error_mail_fromwiki = True                # send error mail from wiki too!
error_mail          = (u'DrTrigon', u'Bot ERROR')    # error mail via wiki mail interface instead of CRON job


# logging of framework info
infolist = [ 'wikipedia.py', 'config.py', 'query.py',       # framework
             'pagegenerators.py', 'botlist.py',             #
             'clean_sandbox.py', 'basic.py',                #
             'dtbext/dtbext_wikipedia.py',                  # DrTrigonBot ext.
             __version__, 'sum_disc.py', 'subster.py',      # bots
             'subster_irc.py', 'catimages.py', ]            #

# bots to run and control
bot_list = { 'clean_user_sandbox': ( 'clean_sandbox', ['-user'], 
                                     u'Clean Userspace Sandboxes' ),
             'sum_disc':           ( 'sum_disc', [], 
                                     u'Discussion Summary'),
             'compress_history':   ( 'sum_disc', ['-compress_history:[]'], 
                                     u'Compressing Discussion Summary'),
             'subster':            ( 'subster', [], 
                                     u'"SubsterBot"'),
             'catimages':          ( 'catimages', ['-cat'],#, '-limit:1'], 
                                     u'Categorize Images (by content)'),
             'subster_irc':        ( 'subster_irc', [], 
                                     u'"SubsterBot" IRC surveillance (beta)'),
           }
bot_order = [ 'clean_user_sandbox', 'sum_disc', 'compress_history',
              'catimages', 'subster', 'subster_irc' ]

# SGE: exit errorlevel
error_SGE_ok      = 0    # successful termination, nothing more to do
error_SGE_restart = 99   # restart the job
#error_SGE_stop    = 100  # stop in error state (prevents re-starts)
error_SGE_stop    = 1    # error, but not for SGE


# debug tools
# 'write2hist'                 # operational mode (default)
# 'user'                       # skip users
# 'write2hist', 'toolserver'   # write history (for code changes and smooth update), toolserver down
debug = []                    # all users
#debug.append( 'user' )        # skip users
debug.append( 'write2hist' )  # write history (operational mode)
#debug.append( 'toolserver' )  # toolserver down
# write to wiki;  use -simulate instead of debug.append( 'write2wiki' )
# code debugging; use -debug    instead of debug.append( 'code' )
#                 (consider using -verbose also)


## @since   r95/r454 (MOVED from dtbext_exceptions.py)
#  @remarks need for Bot Error Handling; to prevent bot errors to stop
#           execution of other bots
class BotError(pywikibot.Error):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


## Bot Error Handling; to prevent bot errors to stop execution of other bots
#
class BotErrorHandler:
    def __init__(self, error_ec):
        self.error_buffer = []
        self.error_ec     = error_ec

    # minor error; in a sub-bot script
    def raise_exceptions(self, log=None):
        self.list_exceptions(log=log)
        if self.error_buffer:
            #raise BotError('Exception(s) occured in Bot')
            pywikibot.output( u'\nDONE with BotError: ' + str(BotError('Exception(s) occured in Bot')) )
            exitcode = self.error_ec
        else:
            pywikibot.output( u'\nDONE' )
            exitcode = error_SGE_ok
        return exitcode

    # major (critical) error; in this controller script
    def handle_exceptions(self, log=None):
        if log:
            self.gettraceback(sys.exc_info())
            self.list_exceptions(log=log)
        exitcode = error_SGE_stop
        return exitcode

    def list_exceptions(self, log=None):
        # if Ctrl-C/BREAK/keyb-int; the 'error_buffer' should be empty
        if not self.error_buffer:
            return

        pywikibot.output(u'\nEXCEPTIONS/ERRORS:')

        item = u'\n'.join([u'%s:\n%s' % (str(item[0]), item[2]) for item in self.error_buffer])
        logging.getLogger('bot_control').error(item)

        # if runned as CRON-job mail occuring exception and traceback to bot admin
        if cron and error_mail_fromwiki:
            self.send_mailnotification(item)

        if log:
            # https://wiki.toolserver.org/view/Cronjob#Output use CRON for error and mail handling, if
            # something should be mailed/reported just print it to 'log.stdout' or 'log.stderr'
            print >> log.stdout, item

    def send_mailnotification(self, item):
        pywikibot.output(u'Sending mail "%s" to "%s" as notification!' % (error_mail[1], error_mail[0]))
        # JIRA: DRTRIGON-87; output even more debug info (tip by: valhallasw@arctus.nl)
        site = pywikibot.getSite()
        pywikibot.output(u'Bot allowed to send email: %r' % (site.isAllowed('sendemail'),))
        pywikibot.output(u'Permissions: %r' % (site._rights,))
        if not site.isAllowed('sendemail'):
            pywikibot.output(u'Try getting new token: %r' % (site.getToken(getagain=True),))
        usr = userlib.User(site, error_mail[0])
        try:
            if usr.sendMail(subject=error_mail[1], text=item):    # 'item' should be unicode!
                return
        except:  # break exception handling recursion
            pass
        logging.getLogger('bot_control').warning(u'mail could not be sent!')
        pywikibot.output(u'May be not logged in - try to send emergency email')
        try:
            import smtplib
            from email.mime.text import MIMEText
            # sender's and recipient's email addresses
            FROM = "drtrigon@toolserver.org"
            TO   = ["dr.trigon@surfeu.ch"]    # must be a list
            # Create a text/plain message
            msg = MIMEText(item)
            msg['Subject'] = "!EMERGENCY! " + error_mail[1]
            msg['From']    = FROM
            msg['To']      = ", ".join(TO)
            # Send the mail
            server = smtplib.SMTP("localhost")
            server.sendmail(FROM, TO, msg.as_string())
            server.quit()
            return
        except:  # break exception handling recursion
            pass
        logging.getLogger('bot_control').warning(u'emergency mail could not be sent!')

    def gettraceback(self, exc_info):
        exception_only = traceback.format_exception_only(exc_info[0], exc_info[1])
        result = u''.join(traceback.format_exception(exc_info[0], exc_info[1], exc_info[2]))
        if ('KeyboardInterrupt\n' not in exception_only):
            error = (exc_info[0], exc_info[1], result)
            self.error_buffer.append( error )

            pywikibot.output(u'\n\03{lightred}%s\03{default}' % error[2])

## BotController (or WatchDog) class.
#
class BotController:
    def __init__(self, bot, argv, desc, run_bot, ErrorHandler):
        self.bot          = bot
        self.argv         = argv
        self.desc         = desc
        self.run_bot      = run_bot
        self.ErrorHandler = ErrorHandler

    def trigger(self):
        if self.run_bot:
            self.bot = __import__(self.bot)     # import if runned only (!)
            self.run()
        else:
            self.skip()
        return self.run_bot

    def skip(self):
        pywikibot.output(u'\nSKIPPING: ' + self.desc)

    def run(self):
        pywikibot.output(u'\nRUN BOT: ' + self.desc)

        try:
            sys.argv[1:]   = self.argv
            self.bot.debug = debug
            self.bot.main()
        except:
            self.ErrorHandler.gettraceback(sys.exc_info())


## Bot Output Redirecting And Logging; to assure all output is logged into file
#
#  @todo consider using 'rrdtool' to improve logging (and logging_statistics as
#        well as creating graphs in panel.py - may be with 'bottle' as webserver)
#  @see  http://segfault.in/2010/03/python-rrdtool-tutorial/
class BotLogger:
    def __init__(self, console=True):
        logger = logging.getLogger('bot_control')
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        #ch.setFormatter( logging.getLogger().handlers[0].formatter )
        if console:
            logger.addHandler(ch)

        self.stdlog = BotLoggerObject(logger, color=False)
        self.errlog = BotLoggerObject(logger, color=False, err=False)

        (self.stdout, self.stderr) = (sys.stdout, sys.stderr)
        (sys.stdout, sys.stderr)   = (self.stdlog, self.errlog)

    def close(self):
        (sys.stdout, sys.stderr)   = (self.stdout, self.stderr)

        logging.shutdown()

# regarding the "patch" with "still strange behaviour" below, consider:
# http://lists.wikimedia.org/pipermail/toolserver-l/2012-June/005029.html
# "That looks like line buffering in stdio. You can try prepending the
# python command with: stderr -e0"
class BotLoggerObject:
    _REGEX_boc = re.compile('\x1B\[.*?m')   # BeginOfColor
    _REGEX_eoc = re.compile('\x03\{.*?\}')  # EndOfColor
    _REGEX_eol = re.compile('\n')           # EndOfLine
    def __init__(self, logger, color=False, err=False):
        self._logger = logger
        self._color  = color
        self._last   = ''
        self._err    = err
    def write(self, string):
        if (string == '\n') and (self._last != '\n'): # patch for direct \n flush and
            self._last = string                       # r10043 upstream
            return                                    # (behaviour is still strange)
        self._last = string                           #
        if not self._color:
            string = self._REGEX_boc.sub('', string)  # make more readable
            string = self._REGEX_eoc.sub('', string)  #
        for string in self._REGEX_eol.split(string.rstrip()):
            if self._err:
                self._logger.critical('[stderr] ' + string)
            else:
                self._logger.critical('[stdout] ' + string)
    def close(self):
        pass
    def flush(self):
        pass


## Retrieve revision number of pywikibedia framework
#
def getSVN_framework_ver(site):
    __framework_rev = int(__framework_rev__)
    match = version.getversion_onlinerepo()
    if match:
        framework_rev = int(match)
        info = version.cmp_ver(framework_rev, __framework_rev, 100)
        pywikibot.output(u'  Directory revision - framework: %s (%s %s)' % (framework_rev, info, __framework_rev__))
    else:
        pywikibot.output(u'  WARNING: could not retrieve framework information!')

## Retrieve revision number of pywikibedia framework
#
def getSVN_release_ver(site):
    global __release_rev__
    __release_rev__ %= int(version.getversion_svn(pywikibot.config.datafilepath('..'))[1])
    match = version.getversion_onlinerepo('http://svn.toolserver.org/svnroot/drtrigon/')
    if match:
        release_rev = int(match)
        info = version.cmp_ver(release_rev, int(__release_rev__))
        pywikibot.output(u'  Directory revision - release:   %s (%s %s)' % (release_rev, info, __release_rev__))
    else:
        pywikibot.output(u'  WARNING: could not retrieve release information!')


## main procedure
#
def main():
#    global log, error
#    global do_dict        # alle anderen NICHT noetig, warum diese hier ?!?????

    # script call
    pywikibot.output(u'SCRIPT CALL:')
    pywikibot.output(u'  ' + u' '.join(sys.argv))

    # logging of release/framework info
    pywikibot.output(u'\nRELEASE/FRAMEWORK VERSION:')
    for item in infolist:
        ver = version.getfileversion(item)
        pywikibot.output(u'  %s' % (item if ver is None else ver))

    # new release/framework revision?
    pywikibot.output(u'\nLATEST RELEASE/FRAMEWORK REVISION:')
    site = pywikibot.getSite()
    getSVN_release_ver(site)
    getSVN_framework_ver(site)

    # mediawiki software version?
    pywikibot.output(u'\nMEDIAWIKI VERSION:')
    pywikibot.output(u'  Actual revision: %s' % str(site.live_version()))

    # processing of messages on bot discussion page
    if site.messages():
        pywikibot.output(u'====== new messages on bot discussion page (last few lines) ======')
        messages_page  = pywikibot.Page(site, u'User:DrTrigonBot').toggleTalkPage()
        messagesforbot = messages_page.get(get_redirect=True)
        pywikibot.output( u'\n'.join(messagesforbot.splitlines()[-10:]) )
        pywikibot.output(u'==================================================================')
        # purge/reset messages (remove this message from queue) by "viewing" it
        site.getUrl( os.path.join('/wiki', messages_page.urlname()) )

    # modification of timezone to be in sync with wiki
    os.environ['TZ'] = 'Europe/Amsterdam'
    time.tzset()
    pywikibot.output(u'\nSetting process TimeZone (TZ): %s' % str(time.tzname))    # ('CET', 'CEST')

    d = shelve.open(pywikibot.config.datafilepath('cache', 'state_bots'))
    d['bot_control'] = {'release_ver':      __release_ver__ + '.' + __release_rev__,
                        'framework_ver':    __framework_rev__,
                        '(runningsubbots)': bot_order,
                       }
    d.close()

    for bot_name in bot_order:
        (bot_module, bot_argv, bot_desc) = bot_list[bot_name]

        bot = BotController( bot_module,
                             bot_argv,
                             bot_desc,
                             do_dict[bot_name],
                             error )

        if bot.trigger():
            name = str('%s-%s-%s' % (bot_name, site.family.name, site.lang))
            # "magic words"/status_bots for subster, look also at 'subster.py'
            # (should be strings, but not needed)
            d = shelve.open(pywikibot.config.datafilepath('cache', 'state_bots'))
            d[name] = {'error':     str(bool(error.error_buffer)),
                       'traceback': str([item[2] for item in error.error_buffer]),
                       'timestamp': str(pywikibot.Timestamp.now().isoformat(' ')),
                      }
            d.close()

    return


if __name__ == "__main__":
    arg = pywikibot.handleArgs()
    if pywikibot.debug:
        debug.append( 'code' ) # code debugging

    log = None
    logfile = logname % ''.join([os.path.basename(sys.argv[0])]+sys.argv[1:])
    if len(arg) > 0:
        #arg = pywikibot.handleArgs()[0]
        #print sys.argv[0]    # who am I?

        cron = ("-cron" in arg)

        do_dict = { 'clean_user_sandbox': False,
                    'sum_disc':           False,
                    'compress_history':   False,
                    'subster':            False,
                    'subster_irc':        False,
                    'catimages':          False,
        }
        error_ec    = error_SGE_stop
        #error_ec    = error_SGE_restart

        if ("-all" in arg):
            do_dict.update({ 'clean_user_sandbox': True,
                             'sum_disc':           True,
                             'subster':            True,
            })
        elif ("-default" in arg):
            do_dict.update({ 'clean_user_sandbox': False,
                             'sum_disc':           True,
                             'subster':            True,
            })
        elif ("-compress_history:[]" in arg):          # muss alleine laufen, sollte aber mit allen 
            do_dict['compress_history'] = True         # anderen kombiniert werden können (siehe 'else')...!
        #elif ("-subster_irc" in arg):                  # muss alleine laufen...
        #    do_dict['subster_irc'] = True
        #    logfile = logname % "subster_irc"          # use another log than usual !!!
        #    #error_ec = error_SGE_restart
        else:
            do_dict.update({ 'clean_user_sandbox': ("-clean_user_sandbox" in arg),
                             'sum_disc':           ("-sum_disc" in arg),
                             'subster_irc':        ("-subster_irc" in arg),
                             'subster':            ("-subster" in arg),
                             'catimages':          ("-catimages" in arg),
            })

        # may be use "log = ['*']" in 'user-config.py' instead
        pywikibot.setLogfileStatus(True, logfile)   # set '-log' to catch all
        #logging.captureWarnings(True)              # (introduced in py2.7)
        log = BotLogger(not cron)                   # handle stdout and stderr
        if cron:
            # suppress console output
            pywikibot.ui.stdout = open(os.devnull, 'w')
            pywikibot.ui.stderr = open(os.devnull, 'w')

        error = BotErrorHandler(error_ec)
    else:
        pywikibot.setLogfileStatus(True, logfile)   # set '-log' to catch all
        #logging.captureWarnings(True)              # (introduced in py2.7)
        log = BotLogger()                           # handle stdout and stderr

        choice = pywikibot.inputChoice('Do you want to compress the histories?', ['Yes', 'No'], ['y', 'n'])
        if choice == 'y':
            logs = os.listdir(u'logs')
            for item in logs:
                if item[-4:] == u'.dat':
                    user = re.findall(u'sum_disc-%s-%s-(.*?).dat' % (u'wikipedia', u'de'), item)[0]

                    sys.argv.append( repr(u'-compress_history:%s' % user) )
                    import sum_disc
                    sum_disc.main()
                    del sys.argv[1]

    try:
        main()
        # minor error; in a sub-bot script
        exitcode = error.raise_exceptions(log)
    except:
        # major (critical) error; in this controller script
        exitcode = error.handle_exceptions(log)
        if 'code' in debug:
            exitcode = error_SGE_ok    # print traceback of re-raised errors by skipping sys.exit()
            raise #sys.exc_info()[0](sys.exc_info()[1])
    finally:
        pywikibot.stopme()

        if log:
            log.close()

        # use exitcode to control SGE (restart or stop with sending mail)
        # re-raised errors occouring in 'except' clause are skipped because
        # of raised 'SystemExit' exception by sys.exit()
        if exitcode:
            sys.exit(exitcode)
