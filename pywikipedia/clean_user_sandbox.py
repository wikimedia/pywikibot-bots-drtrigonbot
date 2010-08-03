# -*- coding: utf-8 -*-
"""
This bot cleans a sandbox by replacing the current contents with predefined
text.

This script understands the following command-line arguments:

    -hours:#       Use this parameter if to make the script repeat itself
                   after # hours. Hours can be defined as a decimal. 0.001
                   hours is one second.

"""
#
# (C) Leogregianin, 2006
# (C) Wikipedian, 2006-2007
# (C) Andre Engels, 2007
# (C) Siebrand Mazeland, 2007
# (C) DrTrigon, 2008
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
__version__ = '$Id: clean_user_sandbox.py 0.2.0000/3968 2009-06-06 15:01:00Z drtrigon $'
#

import wikipedia
import time
import re, sets
import dtbext

content = {
    'ar': u'{{من فضلك اترك هذا السطر ولا تعدله (عنوان ساحة اللعب)}}\n <!-- مرحبا! خذ راحتك في تجربة مهارتك في التنسيق والتحرير أسفل هذا السطر. هذه الصفحة لتجارب التعديل ، سيتم تفريغ هذه الصفحة كل 6 ساعات. -->',
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\r\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'nl': u'{{subst:Wikipedia:Zandbak/schoon zand}}',
    'pl': u'{{Prosimy - NIE ZMIENIAJ, NIE KASUJ, NIE PRZENOŚ tej linijki - pisz niżej}}',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\r\n',
    'commons': u'{{Sandbox}}\n<!-- Please edit only below this line. -->'
    }

msg = {
    'ar': u'روبوت: هذه الصفحة سيتم تفريغها تلقائياً',
    'de': u'Bot: Setze Seite zurück.',
    'en': u'Robot: This page will automatically be cleaned.',
    'nl': u'Robot: Automatisch voorzien van schoon zand.',
    'pl': u'Robot czyści brudnopis',
    'pt': u'Bot: Limpeza da página de testes',
    }

sandboxTitle = {
    'ar': u'ويكيبيديا:ساحة اللعب',
    'de': u'Wikipedia:Spielwiese',
    'en': u'Wikipedia:Sandbox',
    'nl': u'Wikipedia:Zandbak',
    'pl': u'Wikipedia:Brudnopis',
    'pt': u'Wikipedia:Página de testes',
    'commons': u'Commons:Sandbox'
    }

userlist = u'Benutzer:DrTrigonBot/Diene_Mir!'

class SandboxBot:
    def __init__(self, hours, no_repeat, userListPage):
        self.hours = hours
        self.no_repeat = no_repeat
        self.userListPage = wikipedia.Page(wikipedia.getSite(), userListPage)

    def run(self):
        wikipedia.setAction(u'RESET (Spielwiese gemäht)')

        wikipedia.output(u'\03{lightgreen}* Processing User List (wishes): %s\03{default}' % self.userListPage)

        for user in dtbext.config.getUsersConfig(self.userListPage):
        #for user in [u'DrTrigon',]:
            user = user[0]
            wikipedia.output(u'\03{lightgreen}** Processing User: %s\03{default}' % user)

            mySite = wikipedia.getSite()
            while True:
                now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
                #localSandboxTitle = wikipedia.translate(mySite, sandboxTitle)
                #sandboxPage = wikipedia.Page(mySite, localSandboxTitle)
                sandboxPage = wikipedia.Page(mySite, u'Benutzer:%s/Spielwiese' % user)
                if not sandboxPage.exists():
                    wikipedia.output(u'The sandbox [[%s]] is not existent, skipping.' % sandboxPage.title())
                    break
                try:
                    text = sandboxPage.get(get_redirect=True)
                    #content = re.search(u'(.*?{{Bitte erst NACH dieser Zeile schreiben\! \(Begrüßungskasten\)}}\n)(.*)', text, re.S)
                    content = re.search(u'(.*?{{Benutzer\:DrTrigon\/Entwurf\/Vorlage\:Spielwiese}}\n)(.*)', text, re.S)
                    #translatedContent = wikipedia.translate(mySite, content)
                    #if text.strip() == translatedContent.strip():
                    if content == None:
                        wikipedia.output(u'The sandbox [[%s]] is still clean (or not set up), no change necessary.' % sandboxPage.title())
                    else:
                        #translatedMsg = wikipedia.translate(mySite, msg)
                        #sandboxPage.put(translatedContent, translatedMsg)
                        wikipedia.output(u'The sandbox [[%s]] is cleaned up.' % sandboxPage.title())
                        sandboxPage.put(content.group(1))
                except wikipedia.EditConflict:
                    wikipedia.output(u'*** Loading again because of edit conflict.')
                if self.no_repeat:
                    #wikipedia.output(u'Done.')
                    wikipedia.stopme()
                    #return
                    break
                else:
                    wikipedia.output(u'\nSleeping %s hours, now %s' % (self.hours, now))
                    time.sleep(self.hours * 60 * 60)

def main():
    hours = 1
    no_repeat = True
    for arg in wikipedia.handleArgs():
        if	arg.startswith('-hours:'):
            hours = float(arg[7:])
            no_repeat = False
        elif	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
            pass
        elif	(arg == "-skip_clean_user_sandbox"):
            pass
        else:
            wikipedia.showHelp('clean_sandbox')
            wikipedia.stopme()
            return

    bot = SandboxBot(hours, no_repeat, userlist)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
