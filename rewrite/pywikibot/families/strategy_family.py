# -*- coding: utf-8  -*-

__version__ = '$Id: strategy_family.py 9577 2011-10-03 14:53:28Z xqt $'

from pywikibot import family

# The Wikimedia Strategy family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'strategy'
        self.langs = {
            'strategy': 'strategy.wikimedia.org',
        }
        self.interwiki_forward = 'wikipedia'

    def dbName(self, code):
        return 'strategywiki_p'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def ssl_pathprefix(self, code):
        return "/wikipedia/strategy"
