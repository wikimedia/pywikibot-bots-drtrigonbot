# -*- coding: utf-8  -*-

__version__ = '$Id: wikitech_family.py 8789 2010-12-22 22:51:50Z xqt $'

from pywikibot import family

# The Wikitech family

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikitech'
        self.langs = {
            'en': 'wikitech.wikimedia.org',
        }

    def version(self, code):
        return '1.16wmf4'

    def scriptpath(self, code):
        return ''
