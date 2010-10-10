# -*- coding: utf-8 -*-
"""
This bot cleans a sandbox by replacing the current contents with predefined
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
#
# @copyright Dr. Trigon, 2008-2010
#
# @todo      ...
#
# @section FRAMEWORK
#
# Python wikipedia robot framework, DrTrigonBot.
# @see http://pywikipediabot.sourceforge.net/
# @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# @section LICENSE
#
# Distributed under the terms of the MIT license.
# @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
__version__ = '$Id$'
#

import re
import clean_sandbox
import dtbext
import wikipedia as pywikibot

clean_sandbox.content = {
	'de': u'{{Benutzer:DrTrigon/Entwurf/Vorlage:Spielwiese}}\n',
	}

#clean_sandbox.msg = {
#	'de': u'RESET (Spielwiese gemäht)',
#	}

clean_sandbox.sandboxTitle = {
	'de': u'Benutzer:%s/Spielwiese',
	}

bot_config = {	# unicode values
		'userlist':		u'Benutzer:DrTrigonBot/Diene_Mir!',
		'TemplateName':		u'',
# 'TemplateName' is just a dummy for 'dtbext.basic.BasicBot'
}

class UserSandboxBot(dtbext.basic.BasicBot, clean_sandbox.SandboxBot):
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

	def run(self):
		'''Run UserSandboxBot().'''

		#for user in self._user_list:
		import userlib
		for user in [userlib.User(self.site, u'DrTrigon')]:
			pywikibot.output(u'\03{lightgreen}** Processing User: %s\03{default}' % user)

			clean_sandbox.sandboxTitle['de'] = clean_sandbox.sandboxTitle['de'] % user.name()

			sandboxPage = pywikibot.Page(self.site, clean_sandbox.sandboxTitle['de'])
			if not sandboxPage.exists():
				pywikibot.output(u'The sandbox %s is not existent, skipping.' % sandboxPage.title(asLink=True))
				break

# try to implement this also with 'clean_sandbox.SandboxBot'  vvv
# [ should be done in framework / JIRA: ticket? ]
			#try:
			#	text = sandboxPage.get(get_redirect=True)
			#	content = re.search(u'(.*?{{Benutzer\:DrTrigon\/Entwurf\/Vorlage\:Spielwiese}}\n)(.*)', text, re.S)
			#	if content == None:
			#		pywikibot.output(u'The sandbox [[%s]] is still clean (or not set up), no change necessary.' % sandboxPage.title())
			#	else:
			#		pywikibot.output(u'The sandbox [[%s]] is cleaned up.' % sandboxPage.title())
			#		sandboxPage.put(content.group(1))
			#except pywikibot.EditConflict:
			#	pywikibot.output(u'*** Loading again because of edit conflict.')

			clean_sandbox.SandboxBot.run(self)

def main():
    hours = 1
    delay = None
    no_repeat = True
    for arg in pywikibot.handleArgs():
        if arg.startswith('-hours:'):
            hours = float(arg[7:])
            no_repeat = False
        elif	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
            pass
        elif	(arg == "-all") or ("-clean_user_sandbox" in arg):
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
