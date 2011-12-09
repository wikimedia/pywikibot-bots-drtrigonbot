# -*- coding: utf-8 -*-
"""
This bot cleans a user sandbox by replacing the current contents with predefined
text.

"""
## @package clean_user_sandbox
#  @brief   Clean User Sandbox Robot (like clean_sandbox)
#
#  @copyright Dr. Trigon, 2008-2011
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

import clean_sandbox
import dtbext
import wikipedia as pywikibot

# overwrite bot default
clean_sandbox.content = {
                'de':       u'{{Benutzer:DrTrigon/Entwurf/Vorlage:Spielwiese}}',
}

bot_config = {  # unicode values
                'userlist': u'Benutzer:DrTrigonBot/Diene_Mir!',
}


class UserSandboxBot(clean_sandbox.SandboxBot, dtbext.basic.BasicBot):
    '''
    Robot which will clean per user sandbox pages.
    '''

    def __init__(self, hours, no_repeat, delay, userListPage):
        '''Constructor of UserSandboxBot(); setup environment, initialize needed
           consts and objects.
        '''

        pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

        dtbext.basic.BasicBot.__init__(self)  # setting TZ

        pywikibot.output(u'\03{lightred}** Receiving User List (wishes): [[%s]]\03{default}' \
                            % userListPage)

        clean_sandbox.SandboxBot.__init__(self,
                                          hours, no_repeat, delay, userListPage)


def main():
    hours = 1
    delay = None
    no_repeat = True
    for arg in pywikibot.handleArgs():
        if (arg[:5] == "-auto") \
          or (arg[:5] == "-cron"):
            pass
        elif (arg == "-all") \
          or (arg == "-default") \
          or ("-clean_user_sandbox" in arg):
            pass
        else:
            pywikibot.showHelp('clean_sandbox')
            return

    bot = UserSandboxBot(hours, no_repeat, delay, bot_config['userlist'])
    try:
        bot.run()
    except KeyboardInterrupt:
        pywikibot.output('\nQuitting program...')

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
