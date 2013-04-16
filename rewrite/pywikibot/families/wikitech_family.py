# -*- coding: utf-8  -*-

__version__ = '$Id: wikitech_family.py 11164 2013-03-02 20:12:47Z xqt $'

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
        return '1.21wmf8'

    def scriptpath(self, code):
        return ''
