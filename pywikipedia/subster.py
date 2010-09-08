# -*- coding: utf-8  -*-
"""
This bot is used for summarize discussions spread over the whole wiki
including all namespaces. It checks several users (at request), sequential 
(currently for the german wiki [de] only).

...
"""

# ====================================================================================================
#
# ToDo-Liste (Bugs, Features, usw.):
# http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste
#
# READ THE *DOGMAS* FIRST!
# 
# ====================================================================================================

#
# (C) Dr. Trigon, 2008, 2009
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
__version__='$Id: subster.py 0.2.0001 2009-09-09 18:46:00Z drtrigon $'
#


import wikipedia, config
import dtbext
import re, sys, os, time
import math, copy


class SubsterRobot:
	'''
	Robot which will do ...
	'''
	#http://de.wikipedia.org/w/index.php?limit=50&title=Spezial:Beiträge&contribs=user&target=DrTrigon&namespace=3&year=&month=-1
	#http://de.wikipedia.org/wiki/Spezial:Beiträge/DrTrigon

	_content_maxlen = 3000
	_var_regex_str	= '<!--SUBSTER-%(var)s-->%(cont)s<!--SUBSTER-%(var)s-->'
	_tag_regex	= re.compile('<.*?>', re.S | re.I)
	# used/defined magic words, look also at 'runbotrun.py'
	# use, e.g.: '<!--SUBSTER-BOTerror--><!--SUBSTER-BOTerror-->'
	magic_words	= {}	# no magic word substitution (for empty dict)
	_param_default = {	'url': 		'',
				'regex':	'',
				'value':	'',
				'count':	'0',
				'notags':	'',
				#'postproc':	'("","")',
				'postproc':	'(\'\', \'\')',
				'wiki':		'False', }

	# -template and subst-tag handling taken from MerlBot
	# -this bot could also be runned on my local wiki with an anacron-job

	def __init__(self):
		'''
		constructor of SumDiscBot(), initialize needed vars
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 30, 17)

        	self._userListPage = dtbext.wikipedia.Page(wikipedia.getSite(), u'Benutzer:DrTrigon/Entwurf/Vorlage:Subster')

		self._tmpl_regex = re.compile('\{\{Benutzer:DrTrigon/Entwurf/Vorlage:Subster(.*?)\}\}', re.S)

	def run(self, sim=False):
		'''
		run SumDiscBot()
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 24, 38, 17)

		wikipedia.output(u'\03{lightgreen}* Processing Template Backlink List:\03{default}')

		if sim:	pagegen = ['dummy']
		#else:	pagegen = dtbext.pagegenerators.ReferringPageGenerator(self._userListPage)
		else:	pagegen = dtbext.pagegenerators.ReferringPageGenerator(self._userListPage, onlyTemplateInclusion=True)

		for page in pagegen:
			if sim:
				content = sim['content']
				params = [ sim ]
			else:
				content = self._readPage(page)
				params = self._getMode(content)				# get operating mode

			if not params: continue

			substed_content = content
			for item in params:
				# 1.) getUrl
				if eval(item['wiki']):
					external_buffer = self._readPage( dtbext.wikipedia.Page(wikipedia.getSite(), item['url']) )
				else:
					external_buffer = wikipedia.getSite().getUrl(item['url'], no_hostname = True)

				# 2.) regexp
				#regex = re.compile(item['regex'], re.S | re.I | re.M)
				#for subitem in item['regex']:
				subitem = item['regex']
				regex = re.compile(subitem, re.S | re.I)
				#var_regex = re.compile((self._var_regex_str%{'var':item['value'],'cont':'.*?'}), re.S | re.I)
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

				#if eval(item['notags']):
				if item['notags']:
					#external_data = self._tag_regex.sub('', external_data)
					#external_data = self._tag_regex.sub("'", external_data)
					external_data = self._tag_regex.sub(item['notags'], external_data)
				#print external_data

				# postprocessing
				item['postproc'] = eval(item['postproc'])
				if (item['postproc'][0] == 'list'):		# create list
					external_data = str(re.compile(item['postproc'][1], re.S | re.I).findall(external_data))
				elif (item['postproc'][0] == 'wikilist'):	# create list in wiki format
					external_data = "* " + "\n* ".join(re.compile(item['postproc'][1], re.S | re.I).findall(external_data)) + "\n"
				#print external_data

				# subst content
				substed_content = var_regex.sub((self._var_regex_str%{'var':item['value'],'cont':external_data}), substed_content, int(item['count']))

				# subst (internal) magic words
				for subitem in self.magic_words.keys():
					substed_content = self.get_var_regex(subitem).sub( (self._var_regex_str%{'var':subitem,'cont':self.magic_words[subitem]}),
											   substed_content)

			if sim:
				return substed_content
			else:
				#continue
				# 4.) if changed, write!
				if (substed_content != content):
					self._writePage(page, substed_content, u'substituting changed tags')
				else:
					wikipedia.output(u'NOTHING TO DO!')

	def _readPage(self, page, full=False):
		'''
		read wiki page

		input:  page
		returns:  page content [string (unicode)]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28)

		if full:	(mode, info) = ('full', ' using "getFull()" mode')
		else:		(mode, info) = ('default', '')

		#wikipedia.output(u'\03{lightblue}Reading Wiki at %s...\03{default}' % page.aslink())
		wikipedia.output(u'\03{lightblue}Reading Wiki%s at %s...\03{default}' % (info, page.aslink()))
		try:
			#content = page.get()
			content = page.get(mode=mode)
			#if url in content:		# durch history schon gegeben! (achtung dann bei multithreading... wobei ist ja thread per user...)
			#	wikipedia.output(u'\03{lightaqua}** Dead link seems to have already been reported on %s\03{default}' % page.aslink())
			#	continue
		except (wikipedia.NoPage, wikipedia.IsRedirectPage):
			content = u''
		return content

	def _writePage(self, page, data, comment, minorEdit = True):
		'''
		write wiki page

		input:  page
                        data [string (unicode)]
		returns:  (writes data to page on the wiki, nothing else)
		'''

		wikipedia.output(u'\03{lightblue}Writing to Wiki on %s...\03{default}' % page.aslink())

		wikipedia.setAction(comment)

		content = data
		try:
			if minorEdit:	page.put(content)
			else:		page.put(content, minorEdit = False)
		except wikipedia.SpamfilterError, error:
			wikipedia.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (page.aslink(), "error.url"))

	def _getMode(self, content):
		'''
		get operating mode from page with template by searching the template

		input:  content [text] (page content)
                        self-objects
		returns:  params [dict]
		'''
		# modified due: http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot/ToDo-Liste (id 28, 17)

		tmpl_buf = self._tmpl_regex.findall(content)
		params = []
		# enhanced: with template
		#for item in tmpl_buf.groups():
		for item in tmpl_buf:
			#tmpl_params = tmpl_buf.groups()[0]
			#default = {'count':'0', 'notags':'False'}
			#default = {'count':'0', 'notags':'', 'postproc':'("","")'}
			default = copy.deepcopy(self._param_default)
			tmpl_params = item
			#tmpl_params = re.sub('\|', "','", tmpl_params)
			#tmpl_params = re.sub('=', "':'", tmpl_params)		# wenn ein '=' verlangt ist, mit '\x3d' darstellen
			#default.update( eval( "{" + tmpl_params[2:] + "'}" ) )
			tmpl_params = re.sub('\n', '', tmpl_params)
			tmpl_params = re.sub("'", "\\'", tmpl_params)
			tmpl_params = re.split('\|', tmpl_params)
			for subitem in tmpl_params[1:]:
				subitem = re.sub('=', "':'", subitem, 1)	# nur immer erstes '=' ersetzten, das ist von wiki syntax !
				default.update( eval( "{'" + subitem + "'}" ) )
			#default['regex'] = []
			#for subitem in re.split(',', tmpl_params):
			#	if (u"\'regex\':" in subitem[:8]):
			#		default['regex'].append( eval(u"{" + subitem + u"}")['regex'] )
			params.append( default )

		return params

	def get_var_regex(self, var, cont='.*?'):
		'''
		get regex used/needed to find the tags to replace

		...
		'''
		return re.compile((self._var_regex_str%{'var':var,'cont':cont}), re.S | re.I)

def main():
	bot = SubsterRobot()	# for several user's, but what about complete automation (continous running...)
	if len(wikipedia.handleArgs()) > 0:
		for arg in wikipedia.handleArgs():
			if arg[:2] == "u'": arg = eval(arg)		# for 'runbotrun.py' and unicode compatibility
			if	(arg[:5] == "-auto") or (arg[:5] == "-cron"):
				bot.silent = True
			elif	(arg == "-all") or ("-subster" in arg):
				pass
			elif	(arg == "-no_magic_words"):
				pass
			else:
				wikipedia.showHelp()
				return
	bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

