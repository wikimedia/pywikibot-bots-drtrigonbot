# -*- coding: utf-8 -*-
"""
This bot cleans a user sandbox by replacing the current contents with predefined
text.

This script understands the following command-line arguments:

    -hours:#       Use this parameter if to make the script repeat itself
                   after # hours. Hours can be defined as a decimal. 0.01
                   hours are 36 seconds; 0.1 are 6 minutes.

    -delay:#       Use this parameter for a wait time after the last edit
                   was made. If no parameter is given it takes it from
                   hours and limits it between 5 and 15 minutes.
                   The minimum delay time is 5 minutes.

"""
## @package clean_user_sandbox
#  @brief   Clean User Sandbox Robot (like clean_sandbox)
#
#  @copyright Dr. Trigon, 2008-2010
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

clean_sandbox.content = {
	'de': u'{{Benutzer:DrTrigon/Entwurf/Vorlage:Spielwiese}}',
	}

clean_sandbox.sandboxTitle = {
	'de': u'Benutzer:%s/Spielwiese',
	}

bot_config = {	# unicode values
		'userlist':		u'Benutzer:DrTrigonBot/Diene_Mir!',
		'TemplateName':		u'',
# 'TemplateName' is just a dummy for 'dtbext.basic.BasicBot'
}


class UserSandboxBot(clean_sandbox.SandboxBot, dtbext.basic.BasicBot):
	'''
	Robot which will clean per user sandbox pages.
	'''

	def __init__(self, hours, no_repeat, delay, userListPage):
		'''Constructor of UserSandboxBot(); setup environment, initialize needed consts and objects.'''

		pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

		dtbext.basic.BasicBot.__init__(self, bot_config)
		clean_sandbox.SandboxBot.__init__(self, hours, no_repeat, delay)

		# init constants
		self._userListPage = pywikibot.Page(self.site, userListPage)

		pywikibot.output(u'\03{lightred}** Receiving User List (wishes): %s\03{default}' % self._userListPage)
		self._user_list = self.loadUsersConfig(self._userListPage)

		# init variable/dynamic objects

def main():
    hours = 1
    delay = None
    no_repeat = True
    for arg in pywikibot.handleArgs():
        if arg.startswith('-hours:'):
            hours = float(arg[7:])
            no_repeat = False
        elif (arg[:5] == "-auto") \
          or (arg[:5] == "-cron"):
            pass
        elif (arg == "-all") \
          or (arg == "-default") \
          or ("-clean_user_sandbox" in arg):
            pass
        elif arg.startswith('-delay:'):
            delay = int(arg[7:])
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
