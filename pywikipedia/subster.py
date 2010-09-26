# -*- coding: utf-8  -*-
"""
Robot which will does substitutions of tags within wiki page content with external or
other wiki text data. Like dynamic text updating.
"""
#
# (C) Dr. Trigon, 2009-2010
#
# DrTrigonBot: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
# Distributed under the terms of the MIT license.
#
__version__='$Id: subster.py 0.2.0034 2009-11-26 18:53 drtrigon $'
#


import re
import difflib

import pagegenerators
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


bot_config = {	# unicode values
		'TemplateName':		u'Benutzer:DrTrigon/Entwurf/Vorlage:Subster',

		# regex values
		'tag_regex':		re.compile('<.*?>', re.S | re.I),

		'var_regex_str':	u'<!--SUBSTER-%(var)s-->%(cont)s<!--SUBSTER-%(var)s-->',

		# bot paramater/options
		'param_default':	{ 'url': 		'',
					'regex':	'',
					'value':	'',
					'count':	'0',
					'notags':	'',
					#'postproc':	'("","")',
					'postproc':	'(\'\', \'\')',
					'wiki':		'False',
					}
}

debug = True


class SubsterBot(dtbext.basic.BasicBot):
	'''
	Robot which will does substitutions of tags within wiki page content with external or
	other wiki text data. Like dynamic text updating.
	'''

	# used/defined magic words, look also at 'runbotrun.py'
	# use, e.g.: '<!--SUBSTER-BOTerror--><!--SUBSTER-BOTerror-->'
	magic_words	= {}	# no magic word substitution (for empty dict)

	_param_default  = bot_config['param_default']

	_tag_regex	= bot_config['tag_regex']
	_var_regex_str	= bot_config['var_regex_str']

	# -template and subst-tag handling taken from MerlBot
	# -this bot could also be runned on my local wiki with an anacron-job

	def __init__(self):
		'''Constructor of SubsterBot(), initialize needed vars.'''

		pywikibot.output(u'\03{lightgreen}* Initialization of bot:\03{default}')

		dtbext.basic.BasicBot.__init__(self, bot_config)

		# init constants
        	self._userListPage = pywikibot.Page(self.site, bot_config['TemplateName'])

	def run(self, sim=False):
		'''Run SubsterBot().'''

		pywikibot.output(u'\03{lightgreen}* Processing Template Backlink List:\03{default}')

		if sim:	pagegen = ['dummy']
		else:	pagegen = pagegenerators.ReferringPageGenerator(self._userListPage, onlyTemplateInclusion=True)

		for page in pagegen:
			# setup source to get data from
			if sim:
				content = sim['content']
				params = [ sim ]
			else:
				# get page content and operating mode
				content = self.load(page)
				params = self.loadTemplates(page, default=self._param_default)

			if not params: continue

			substed_content = self.subContent(content, params)

			# output result to page or return directly
			if sim:
				return substed_content
			else:
				if debug:
					pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
					continue

				# if changed, write!
				if (substed_content != content):
					self.outputContentDiff(content, substed_content)

					self.save(page, substed_content, u'Bot: substituting changed tags.')
				else:
					pywikibot.output(u'NOTHING TO DO!')

	def subContent(self, content, params):
		"""Substitute the tags in content according to params.

		   @param content: Content with tags to substitute.
		   @type  content: string
		   @param params: Params with data how to substitute tags.
		   @type  params: dict

		   Returns the new content with tags substituted.
		"""

		substed_content = content
		for item in params:
			# 1.) getUrl or wiki text
			if eval(item['wiki']):
				external_buffer = self.load( dtbext.pywikibot.Page(self.site, item['url']) )
			else:
				external_buffer = self.site.getUrl(item['url'], no_hostname = True)

			# 2.) regexp
			#for subitem in item['regex']:
			subitem = item['regex']
			regex = re.compile(subitem, re.S | re.I)
			var_regex = self.get_var_regex(item['value'])

			# 3.) subst in content
			external_data = regex.search(external_buffer)

			if external_data:
				external_data = external_data.groups()
				if (len(external_data) == 1):
					external_data = external_data[0]
				else:
					external_data = str(external_data)
			#print external_data

			if item['notags']:
				external_data = self._tag_regex.sub(item['notags'], external_data)
			#print external_data

			# 4.) postprocessing
			item['postproc'] = eval(item['postproc'])
			if (item['postproc'][0] == 'list'):		# create list
				external_data = str(re.compile(item['postproc'][1], re.S | re.I).findall(external_data))
			elif (item['postproc'][0] == 'wikilist'):	# create list in wiki format
				external_data = "* " + "\n* ".join(re.compile(item['postproc'][1], re.S | re.I).findall(external_data)) + "\n"
			#print external_data

			# 5.) subst content
			substed_content = var_regex.sub((self._var_regex_str%{'var':item['value'],'cont':external_data}), substed_content, int(item['count']))

			# 6.) subst (internal) magic words
			for subitem in self.magic_words.keys():
				substed_content = self.get_var_regex(subitem).sub( (self._var_regex_str%{'var':subitem,'cont':self.magic_words[subitem]}),
										   substed_content)

		return substed_content

	def outputContentDiff(self, content, substed_content):
		"""Outputs the diff between the original and the new content.

		   @param content: Original content.
		   @type  content: string
		   @param substed_content: New content.
		   @type  substed_content: string

		   Returns nothing, but outputs/prints the diff.
		"""
		diff = difflib.Differ().compare(content.splitlines(1), substed_content.splitlines(1))
		diff = [ line for line in diff if line[0].strip() ]
		pywikibot.output(u'Diff:')
		pywikibot.output(u'--- ' * 10)
		pywikibot.output(u''.join(diff))
		pywikibot.output(u'--- ' * 10)

	def get_var_regex(self, var, cont='.*?'):
		"""Get regex used/needed to find the tags to replace.

		   @param var: The tag/variable name.
		   @type  var: string
		   @param cont: The content/value of the variable.
		   @type  cont: string

		   Return the according (and compiled) regex object.
		"""
		return re.compile((self._var_regex_str%{'var':var,'cont':cont}), re.S | re.I)


def main():
	bot = SubsterBot()	# for several user's, but what about complete automation (continous running...)
	if len(pywikibot.handleArgs()) > 0:
		for arg in pywikibot.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
				bot.silent = True
			elif	(arg == "-all") or ("-subster" in arg):
				pass
			elif	(arg == "-no_magic_words"):
				pass
			else:
				pywikibot.showHelp()
				return
	bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()

