# -*- coding: utf-8  -*-
"""
Robot which runs python framework scripts as (sub-)bot and provides a
WikiUserInterface (WUI) with Lua support for bot operators.

The following parameters are supported:

&params;

All other parameters will be ignored.

Syntax example:
    python script_wui.py -dir:.
        Default operating mode.
"""
## @package script_wui
#  @brief   Script WikiUserInterface (WUI) Robot
#
#  @copyright Dr. Trigon, 2012
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
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#  @todo rewrite zusammen mit diesem script auf dem TS installieren (commit to
#        svn repo) und aktivieren (in crontab setzen wie subsetr_irc). Dann
#        user sandbox cleaner von trunk nach rewrite wechseln durch script_wui.py
#        (somit ist bot_control.py in rewrite ev. gar nicht nötig...!?! ;)
#
#  @todo Simulationen werden ausgeführt und das Resultat mit eindeutiger
#        Id (rev-id) auf Ausgabeseite geschrieben, damit kann der Befehl
#        (durch Angabe der Sim-Id) ausgeführt werden -> crontab (!)
#        [ shell (rev-id) -> output mit shell rev-id ]
#        [ shell rev-id (als eindeutige job/task-config bzw. script) -> crontab ]
#  @todo Bei jeder Botbearbeitung wird der Name des Auftraggebers vermerkt
#  @todo (may be queue_security needed later in order to allow other 'super-users' too...)
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
__version__ = '$Id: script_wui.py 427 2012-12-10 20:01:27Z drtrigon $'
#


import datetime
import thread, threading

# http://labix.org/lunatic-python
#import lua    # install f15 packages: 'lua', 'lunatic-python'
import dtbext.crontab

import pywikibot
import pywikibot.botirc

bot_config = {    'BotName':    pywikibot.config.usernames[pywikibot.config.family][pywikibot.config.mylang],

            # protected !!! ('CSS' or other semi-protected page is essential here)
            'ConfCSSshell':     u'User:DrTrigon/DrTrigonBot/script_wui-shell.css',    # u'User:DrTrigonBot/Simon sagt' ?
            'ConfCSScrontab':   u'User:DrTrigon/DrTrigonBot/script_wui-crontab.css',

            # (may be protected but not that important... 'CSS' is not needed here !!!)
            'ConfCSSoutput':    u'User:DrTrigonBot/Simulation',

            'CRONMaxDelay':     5*60.0,       # check all ~5 minutes

#        'queue_security':       ([u'DrTrigon', u'DrTrigonBot'], u'Bot: exec'),
#        'queue_security':       ([u'DrTrigon'], u'Bot: exec'),

        # supported and allowed bot scripts
        # (at the moment all)

        # forbidden parameters
        # (at the moment none, but consider e.g. '-always' or allow it with '-simulate' only!)
}

## debug tools
## (look at 'bot_control.py' and 'subster.py' for more info)
#debug = []


class ScriptWUIBot(pywikibot.botirc.IRCBot):
    def __init__(self, *arg):
        pywikibot.output(u'\03{lightgreen}* Initialization of bot\03{default}')

        pywikibot.botirc.IRCBot.__init__(self, *arg)

        self.templ = pywikibot.Page(self.site, bot_config['ConfCSSshell'])
        self.cron  = pywikibot.Page(self.site, bot_config['ConfCSScrontab'])

        self.refs  = {}
        self.refs[self.templ.title()] = self.templ

        self.on_timer()

#        # init constants
#        self._ConfCSSconfigPage = pywikibot.Page(self.site, bot_config['ConfCSSconfig'])
#        self._difflink = []
#        if self._ConfCSSconfigPage.exists():
#            exec(self._ConfCSSconfigPage.get())    # with variable: bot_config_wiki
#            self._difflink = bot_config_wiki['difflink']

    def on_pubmsg(self, c, e):
        match = self.re_edit.match(e.arguments()[0])
        if not match:
            return
#        print match.groups(), match.group('page'), match.group('user')
        user = match.group('user').decode(self.site.encoding())
        if user == bot_config['BotName']:
            return
        # test actual page against (template incl.) list
        page = match.group('page').decode(self.site.encoding())
        if page in self.refs:
            pywikibot.output(u"SHELL: %s" % page)
            self.do_check(page)

    def on_timer(self):
        self.t = threading.Timer(bot_config['CRONMaxDelay'], self.on_timer)
        self.t.start()

        self.do_check_CronJobs()

    def do_check_CronJobs(self):
        # check cron/date
        page    = self.templ
        # (track changes of self.cron in on_pubmsg and re-load after changes only...)
        crontab = self.cron.get(force=True)
        # extract 'rev' and 'timestmp' from 'crontab' page text ...
        for line in crontab.splitlines():   # hacky/ugly/cheap; already better done in trunk dtbext
            (rev, timestmp) = [item.strip() for item in line[1:].split(',')]

            # [min] [hour] [day of month] [month] [day of week]
            # (date supported only, thus [min] and [hour] dropped)
            entry = dtbext.crontab.CronTab(timestmp)
            # find the delay from current minute (does not return 0.0 - but next)
            delay = entry.next(datetime.datetime.now().replace(second=0,microsecond=0)-datetime.timedelta(microseconds=1))
            #pywikibot.output(u'CRON delay for execution: %.3f (<= %i)' % (delay, bot_config['CRONMaxDelay']))
    
            if (delay <= bot_config['CRONMaxDelay']):
                pywikibot.output(u"CRONTAB: %s / %s / %s" % (page, rev, timestmp))
                self.do_check(page.title(), int(rev))

    def do_check(self, page_title, rev=None, params=None):
        # Create two threads as follows
        # (simple 'thread' for more sophisticated code use 'threading')
        try:
            thread.start_new_thread( main_script, (self.refs[page_title], rev, params) )
        except:
            pywikibot.output(u"WARNING: unable to start thread")

            # has to be done according to subster in trunk with 'get_traceback' (!)
            traceback = u"[ERROR OCCURRED; here you should see here a python traceback giving more information]\n"
            wiki_logger(traceback, self.refs[page_title], rev)

# Define a function for the thread
def main_script(page, rev=None, params=None):
    # http://opensourcehacker.com/2011/02/23/temporarily-capturing-python-logging-output-to-a-string-buffer/
    # http://docs.python.org/release/2.6/library/logging.html
    from StringIO import StringIO
    import logging, sys

    pywikibot.output(u'--- ' * 20)

    buffer = StringIO()
    rootLogger = logging.getLogger()

    logHandler = logging.StreamHandler(buffer)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(formatter)
    rootLogger.addHandler(logHandler)

    sys.stdout = buffer
    sys.stderr = buffer

    # all output to logging and stdout/stderr is catched BUT NOT lua output (!)
    if rev is None:
        code = page.get(force=True)     # shell; "on demand"
    else:
        code = page.getOldVersion(rev)  # crontab; scheduled
    exec( code )

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    # Remove our handler
    rootLogger.removeHandler(logHandler)

    logHandler.flush()
    buffer.flush()

    pywikibot.output(u'--- ' * 20)

    # append result to output page
    if rev is None:
        wiki_logger(buffer.getvalue(), page, rev)

def wiki_logger(buffer, page, rev=None):
# (might be a problem here for TS and SGE, output string has another encoding)
#    buffer  = buffer.decode(config.console_encoding)
    if rev is None:
        rev = page.latestRevision()
    # append to page
    outpage = pywikibot.Page(pywikibot.getSite(), bot_config['ConfCSSoutput'])
    text = outpage.get()
    # vvv permalink is VERY CHEAP/UGLY/HACKY and has to be done better !!!!!!!! vvv
    outpage.put(text + u"\n== Simulation vom %s mit [http://de.wikipedia.org/w/index.php?title=%s&oldid=%s code:%s] ==\n<pre>\n%s</pre>\n\n" % (pywikibot.Timestamp.now().isoformat(' '), bot_config['ConfCSSshell'], rev, rev, buffer))
#                comment = pywikibot.translate(self.site.lang, bot_config['msg']))

def main():
    for arg in pywikibot.handleArgs():
        pywikibot.showHelp('script_wui')
        return
        
    site = pywikibot.getSite()
    site.login()
    chan = '#' + site.language() + '.' + site.family.name
    bot = ScriptWUIBot(site, chan, site.user() + "_WUI", "irc.wikimedia.org")
    try:
        bot.start()
    except:
        bot.t.cancel()
        raise

if __name__ == "__main__":
    main()


comment = """
...

builtin_raw_input = __builtin__.raw_input
__builtin__.raw_input = lambda: 'n'     # overwrite 'raw_input' to run bot non-blocking and simulation mode
def block(*args, **kwargs):
    pywikibot.output(u'=== ! SIMULATION MODE; WIKI WRITE ATTEMPT BLOCKED ! ===')
    return (None, None, None)
pywikibot_Page_put = pywikibot.Page.put
pywikibot.Page.put = block              # overwrite 'pywikibot.Page.put'

sys_argv = copy.deepcopy( sys.argv )
#print sys.argv
sys_stdout = sys.stdout
sys_stderr = sys.stderr
out = u""
for command in self._commandlist:  # may be try with PreloadingGenerator?!
    command = command.encode(config.console_encoding)
    cmd = command.split(' ')

    if cmd[0] not in bot_config['bot_list']: continue

    pywikibot.output('\03{lightred}** Processing Command: %s\03{default}' % command)

    out += u"== %s ==\n" % command

...

sys.argv = sys_argv
pywikibot.Page.put = pywikibot_Page_put
"""

