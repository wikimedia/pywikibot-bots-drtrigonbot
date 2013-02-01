# -*- coding: utf-8  -*-

__version__ = '$Id: strategy_family.py 10993 2013-01-27 12:38:06Z xqt $'

from pywikibot import family

# The Wikimedia Strategy family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'strategy'
        self.langs = {
            'strategy': 'strategy.wikimedia.org',
        }
        self.interwiki_forward = 'wikipedia'

    def dbName(self, code):
        return 'strategywiki_p'

    def ssl_pathprefix(self, code):
        return "/wikipedia/strategy"
