# -*- coding: utf-8  -*-

__version__ = '$Id: wikitech_family.py 10993 2013-01-27 12:38:06Z xqt $'

from pywikibot import family

# The Wikitech family

class Family(family.Family):

    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikitech'
        self.langs = {
            'en': 'wikitech.wikimedia.org',
        }

    def version(self, code):
        return '1.19wmf2'

    def scriptpath(self, code):
        return ''
