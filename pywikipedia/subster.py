# -*- coding: utf-8  -*-
"""
Robot which will does substitutions of tags within wiki page content with external or
other wiki text data. Like dynamic text updating.
"""
## @package subster
#  @brief   Dynamic Text Substitutions Robot
#
#  @copyright Dr. Trigon, 2009-2010
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


import re, sys
import difflib

import pagegenerators
import dtbext
# Splitting the bot into library parts
import wikipedia as pywikibot


bot_config = {	# unicode values
		'TemplateName':		u'Benutzer:DrTrigon/Entwurf/Vorlage:Subster',
		'ErrorTemplate':		u'\n----\n;SubsterBot Exception\n%s\n',

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
					'magicwords_only':	'False',
					}
}

## used/defined magic words, look also at bot_control
#  use, for example: '\<!--SUBSTER-BOTerror--\>\<!--SUBSTER-BOTerror--\>'
magic_words = {} # no magic word substitution (for empty dict)

# debug tools
# (look at 'bot_control.py' for more info)
debug = []				# no write, all users
#debug.append( 'write2wiki' )		# write to wiki (operational mode)


class SubsterBot(dtbext.basic.BasicBot):
	'''
	Robot which will does substitutions of tags within wiki page content with external or
	other wiki text data. Like dynamic text updating.
	'''

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
			pywikibot.output(u'Getting page "%s" via API from %s...'
			                 % (page, self.site))

			# setup source to get data from
			if sim:
				content = sim['content']
				params = [ sim ]
			else:
				# get page content and operating mode
				content = self.load(page)
				params = self.loadTemplates(page, default=self._param_default)

			if not params: continue

			(substed_content, substed_tags) = self.subContent(content, params)

			# output result to page or return directly
			if sim:
				return substed_content
			else:
				# if changed, write!
				if (substed_content != content):
				#if substed_tags:
					self.outputContentDiff(content, substed_content)

					if 'write2wiki' not in debug:
						pywikibot.output(u'\03{lightyellow}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
						continue

					self.save(page, substed_content, u'Bot: substituting %s tags.' % (", ".join(substed_tags)))
				else:
					pywikibot.output(u'NOTHING TO DO!')

	def subContent(self, content, params):
		"""Substitute the tags in content according to params.

		   @param content: Content with tags to substitute.
		   @type  content: string
		   @param params: Params with data how to substitute tags.
		   @type  params: dict

		   Returns a tuple containig the new content with tags
		   substituted and a list of those tags.
		"""

		substed_content = content
		substed_tags = []  # DRTRIGON-73

		# 0.) subst (internal) magic words
		try:
			(substed_content, tags) = self.subBotMagicWords(substed_content)
			substed_tags += tags
		except:
			exc_info = sys.exc_info()
			(exception_only, result) = dtbext.pywikibot.gettraceback(exc_info)
			substed_content += bot_config['ErrorTemplate'] % (u' ' + result.replace(u'\n', u'\n '))
			substed_tags.append( u'>error:BotMagicWords<' )

		if (len(params) == 1) and eval(params[0]['magicwords_only']):
			return (substed_content, substed_tags)

		for item in params:
			# 1.) - 5.) subst templates
			try:
				(substed_content, tags) = self.subTemplate(substed_content, item)
				substed_tags += tags
			except:
				exc_info = sys.exc_info()
				(exception_only, result) = dtbext.pywikibot.gettraceback(exc_info)
				substed_content += bot_config['ErrorTemplate'] % (u' ' + result.replace(u'\n', u'\n '))
				substed_tags.append( u'>error:Template<' )

		return (substed_content, substed_tags)

	def subBotMagicWords(self, content):
		"""Substitute the DrTrigonBot Magic Word (tag)s in content.

		   @param content: Content with tags to substitute.
		   @type  content: string

		   Returns a tuple containig the new content with tags
		   substituted and a list of those tags.
		"""

		substed_tags = []  # DRTRIGON-73

		# 0.) subst (internal) magic words
		for subitem in magic_words.keys():
			prev_content = content
			content = self.get_var_regex(subitem).sub( (self._var_regex_str%{'var':subitem,'cont':magic_words[subitem]}),
									   content, 1)  # subst. once
			if (content != prev_content):
				substed_tags.append(subitem)

		return (content, substed_tags)

	def subTemplate(self, content, param):
		"""Substitute the template tags in content according to param.

		   @param content: Content with tags to substitute.
		   @type  content: string
		   @param param: Param with data how to substitute tags.
		   @type  param: dict

		   Returns a tuple containig the new content with tags
		   substituted and a list of those tags.
		"""

		substed_tags = []  # DRTRIGON-73

		# 1.) getUrl or wiki text
		if eval(param['wiki']):
			external_buffer = self.load( dtbext.pywikibot.Page(self.site, param['url']) )
		else:
			external_buffer = self.site.getUrl(param['url'], no_hostname = True)

		# 2.) regexp
		#for subitem in param['regex']:
		subitem = param['regex']
		regex = re.compile(subitem, re.S | re.I)
		var_regex = self.get_var_regex(param['value'])

		# 3.) subst in content
		external_data = regex.search(external_buffer)

		if external_data:
			external_data = external_data.groups()
			if (len(external_data) == 1):
				external_data = external_data[0]
			else:
				external_data = str(external_data)
		#print external_data

		if param['notags']:
			external_data = self._tag_regex.sub(param['notags'], external_data)
		#print external_data

		# 4.) postprocessing
		param['postproc'] = eval(param['postproc'])
		if (param['postproc'][0] == 'list'):		# create list
			external_data = str(re.compile(param['postproc'][1], re.S | re.I).findall(external_data))
		elif (param['postproc'][0] == 'wikilist'):	# create list in wiki format
			external_data = "* " + "\n* ".join(re.compile(param['postproc'][1], re.S | re.I).findall(external_data)) + "\n"
		#print external_data

		# 5.) subst content
		prev_content = content
		content = var_regex.sub((self._var_regex_str%{'var':param['value'],'cont':external_data}), content, int(param['count']))
		if (content != prev_content):
			substed_tags.append(param['value'])

		return (content, substed_tags)

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
		pywikibot.output(u'--- ' * 15)
		pywikibot.output(u''.join(diff))
		pywikibot.output(u'--- ' * 15)

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
			if arg[:2] == "u'": arg = eval(arg)		# for 'bot_control.py' and unicode compatibility
			if   (arg[:5] == "-auto") \
			     or (arg[:5] == "-cron"):
				bot.silent = True
			elif (arg == "-all") \
			     or (arg == "-default") \
			     or ("-subster" in arg):
				pass
			elif (arg == "-no_magic_words"):
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

