# -*- coding: utf-8  -*-
"""
This bot is the general DrTrigonBot caller. It runs all the different sub tasks,
that DrTrigonBot does.

...
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
__version__='$Id: runbotrun.py 0.2.0000 2009-06-05 14:56:00Z drtrigon $'
__revision__='8072'
#

# wikipedia-bot imports
import wikipedia, config, query, pagegenerators
import sys, os, re, time, codecs
import clean_user_sandbox, sum_disc, mailer, page_disc
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

error_mail = ('DrTrigon', 'Bot ERROR')


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

def setlogfile():
    #logfile = Logger(logname % time.strftime("%Y%m%d", time.gmtime()), encoding=config.textfile_encoding, mode='a+')
    logfile = Logger(logname % dtbext.date.getTimeStmp(), encoding=config.textfile_encoding, mode='a+')
    (out_stream, err_stream) = (sys.stdout, sys.stderr)
    (sys.stdout, sys.stderr) = (logfile, logfile)
    return (logfile, out_stream, err_stream)

def main():
    global logfile, out_stream, err_stream

    # script call
    #wikipedia.output(u'SCRIPT CALL:')
    wikipedia.output(u'\nSCRIPT CALL:')
    wikipedia.output(u'  ' + u' '.join(sys.argv))

    # logging of framework info
    infolist = [ config.__version__, pagegenerators.__version__, query.__version__, wikipedia.__version__,	# framework
		dtbext.pagegenerators.__version__, dtbext.query.__version__, dtbext.wikipedia.__version__,	# DrTrigonBot extensions
		dtbext.date.__version__, dtbext.config.__version__,						#
		__version__, clean_user_sandbox.__version__, sum_disc.__version__, mailer.__version__, page_disc.__version__ ]		# bots
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
        if skip_clean_user_sandbox: wikipedia.output(u'SKIPPING: clean userspace Sandboxes')
        else: clean_user_sandbox.main()

        sum_disc.main()

        #replace_tmpl.main()

        if skip_clean_user_sandbox: wikipedia.output(u'SKIPPING: MailerBot')
        else: mailer.main()

        if skip_clean_user_sandbox: wikipedia.output(u'SKIPPING: page_disc bot')
        else: page_disc.main()

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
            (logfile, out_stream, err_stream) = setlogfile()


if __name__ == "__main__":
    hours = 48
    no_repeat = True
    arg = wikipedia.handleArgs()
    skip_clean_sanbox2 = False
    if len(arg) > 0:
        #arg = wikipedia.handleArgs()[0]
        #print sys.argv[0]	# who am I?
        #if (arg[:5] == "-auto") or (arg[:5] == "-cron"):
        if ("-auto" in arg) or ("-cron" in arg):
            #logfile = file(logname, "w")
            #(out_stream, err_stream) = (sys.stdout, sys.stderr)
            #(sys.stdout, sys.stderr) = (logfile, logfile)
            (logfile, out_stream, err_stream) = setlogfile()
            #no_repeat = False
            #no_repeat = not (arg[:5] == "-auto")
            no_repeat = not ("-auto" in arg)
        skip_clean_user_sandbox = ("-skip_clean_user_sandbox" in arg)
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
    #except KeyboardInterrupt:	# faengt nich alles ab (da viele try vorhanden), vorallem sleep...
    #    #wikipedia.output(u'\nSleeping %s hours, now %s' % (hours, now))
    #    logfile.slow_write( '\nShutting down, now %s' % time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )	# for write to last log during sleep
    #    print '\nShutting down, now %s' % time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
    # or with predefined clean-up action
    #with open("myfile.txt") as f:
    #    for line in f:
    #        print line
    except:
        output = StringIO.StringIO()
        traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], file=output)
        if not ('KeyboardInterrupt\n' in traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])):
		print error_mail[0], error_mail[1], '\n', output.getvalue()
		if not dtbext.wikipedia.SendMail(error_mail[0], error_mail[1], output.getvalue()):
		    wikipedia.output(u'!!! WARNING: mail could not be sent!')
        output.close()
        raise
    finally:
        wikipedia.stopme()

    if not no_repeat:
        (sys.stdout, sys.stderr) = (out_stream, err_stream)
        logfile.close()

