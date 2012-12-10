# -*- coding: utf-8  -*-
__version__ = '$Id: fon_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# The official Beta Wiki.
class Family(family.Family):

    def __init__(self):

        family.Family.__init__(self)
        self.name = 'fon'

        self.langs = {
            'en': None,
        }

    def hostname(self, code):
        return 'wiki.fon.com'

    def scriptpath(self, code):
        return '/mediawiki'

    def version(self, code):
        return "1.15.1"
