# -*- coding: utf-8  -*-
"""
Robot which runs framework scripts as (sub-)bot and provides a WikiUserInterface
(WUI) for users.

The following parameters are supported:

&params;

All other parameters will be ignored.

Syntax example:
    python script_wui.py
        Default operating mode.
"""
## @package script_wui
#  @brief   Script WikiUserInterface (WUI) Robot
#
#  @copyright Dr. Trigon, 2011
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
__version__ = '$Id$'
#


import sys, os
import copy
import StringIO
import re
import __builtin__

import config
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


bot_config = {    # unicode values
        'commandlist':        u'Benutzer:DrTrigonBot/Simon sagt',
        'sim_output':        u'Benutzer:DrTrigonBot/Simulation',

#        'queue_security':    ([u'DrTrigon', u'DrTrigonBot'], u'Bot: exec'),
        'queue_security':    ([u'DrTrigon'], u'Bot: exec'),

        # supported and allowed bot scripts
        'bot_list':            [u'replace', u'template', u'templatecount',
                                 u'weblinkchecker', #u'copyright',                  # UNTESTED
                                 u'cosmetic_changes'], #u'spellcheck',              # UNTESTED
                                 #u'add_text', u'table2wiki',                       # UNTESTED
                                 #u'standardize_notes', u'redirect',                # UNTESTED
                                 #u'image', u'imagecopy', u'imagetransfer',         # UNTESTED
                                 #u'category', u'category_redirect', u'commonscat', # UNTESTED
                                 #u'articlenos', u'wikilogbot', ]                   # UNTESTED
        # forbidden parameters
        'bot_params_forbidden':    [u'-always'],

        'msg': {
            'de':    ( u'Bot: ',
                u'Simulation vom %s',
                ),
            'en':    ( u'robot ',
                u'Simulation from %s',
                ),
        },
}

# debug tools
# (look at 'bot_control.py' for more info)
debug = []                      # no write
#debug.append( 'write2wiki' )    # write to wiki (operational mode)

docuReplacements = {
#    '&params;': pagegenerators.parameterHelp
    '&params;': u''
}


class ScriptWUIBot(dtbext.basic.BasicBot):
    '''
    Robot which will run framework scripts as (sub-)bot and provides a
    WikiUserInterface (WUI) for users.
    '''
    #http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
    #http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

    def __init__(self):
        '''Constructor of ScriptWUIBot(); setup environment, initialize needed consts and objects.'''

        pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

        dtbext.basic.BasicBot.__init__(self)
        self.site = pywikibot.getSite()

        # init constants
        pywikibot.output(u'\03{lightred}** Receiving Job Queue\03{default}')
        page = pywikibot.Page(self.site, bot_config['commandlist'])
        self._commandlist = self.loadJobQueue(page, bot_config['queue_security'], debug = ('write2wiki' in debug))
#        print self._commandlist

        # code debugging
        dtbext.pywikibot.debug = ('code' in debug)

    def run(self):
        '''Run ScriptWUIBot().'''

        pywikibot.output(u'\03{lightgreen}* Processing Job List:\03{default}')

        __builtin__.raw_input = lambda: 'n'    # overwrite 'raw_input' to run bot non-blocking and simulation mode
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

            imp  = __import__(cmd[0])
            argv = [ os.path.join(os.path.split(sys_argv[0])[0], cmd[0])+'.py' ] + cmd[1:]
            for item in bot_config['bot_params_forbidden']:
                if item in argv:
                    argv.remove(item)
            sys.argv = argv
            #print sys.argv

            sys.stderr = sys.stdout = stdout = StringIO.StringIO()
            imp.main()
            sys.stdout = sys_stdout
            sys.stderr = sys_stderr

            sys.argv = sys_argv
            out += stdout.getvalue().decode(config.console_encoding)
#            out += stdout.getvalue()
# problem here for TS and SGE, output string has another encoding, printing below does not work also!
            out += u"\n"

        sys.argv = sys_argv
        if not out:
            return

        if 'write2wiki' in debug:
            head, msg = pywikibot.translate(self.site.lang, bot_config['msg'])
            comment = head + msg % dtbext.date.getTimeStmpNow(full=True, humanreadable=True, local=True)
            page = pywikibot.Page(self.site, bot_config['sim_output'])
            self.append(page, self.terminal2wiki(out), comment=comment)
        else:
            print self.terminal2wiki(out)
            pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')

    def terminal2wiki(self, text):
        # https://fisheye.toolserver.org/browse/~raw,r=19/drtrigon/pywikipedia/replace_tmpl.py

        # \n respective <br>
#        text = re.sub('\n(\x1b\[0m)?', '<br>\n', text)
        text = re.sub('\n(\x1b\[0m)?', '\n\n', text)
#        text = re.sub('\n{2,}', '', text)   # more than one '\n' -> ''
        # color; <span style=...>
        color = {'35': 'magenta', '91': 'red', '92': 'green'}
        replfunc = lambda matchobj: '<span style="color:%s">%s</span>' % \
                                    (color[matchobj.group(1)], matchobj.group(2))
        text = re.sub('\x1b\[(.*?);1m(.*?)\x1b\[0m', replfunc, text)
        # {{...}}
        replfunc = lambda matchobj: '<tt><nowiki>{{</nowiki></tt>%s<tt><nowiki>}}</nowiki></tt>' % \
                                    matchobj.group(1)
        text = re.sub('\{\{(.*?)\}\}', replfunc, text)
        # heading to link
        replfunc = lambda matchobj: '>>> [[%s]] <<<' % \
                                    matchobj.group(1)
        text = re.sub('>>> <span style="color:magenta">(.*?)</span> <<<', replfunc, text)

        return text


def main():
    bot = ScriptWUIBot()
    if len(pywikibot.handleArgs()) > 0:
        for arg in pywikibot.handleArgs():
            if arg[:2] == "u'": arg = eval(arg)        # for 'runbotrun.py' and unicode compatibility
            if   arg[:17] == "-compress_history":
                bot.compressHistory( eval(arg[18:]) )
                return
            elif (arg[:17] == "-rollback_history"):
                bot.rollback = int( arg[18:] )
            elif (arg[:5] == "-auto") \
                 or (arg[:5] == "-cron"):
                pass
            elif (arg == "-all") \
                 or (arg == "-default") \
                 or ("-script_wui" in arg):
                pass
            else:
                pywikibot.showHelp()
                return
    try:
        bot.run()
    except KeyboardInterrupt:
        pywikibot.output('\nQuitting program...')

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

