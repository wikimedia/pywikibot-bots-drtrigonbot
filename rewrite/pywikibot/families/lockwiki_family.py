# -*- coding: utf-8  -*-

__version__ = '$Id: lockwiki_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# The locksmithwiki family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'lockwiki'
        self.langs = {
            'en': 'www.locksmithwiki.com',
        }

    def scriptpath(self, code):
        return '/lockwiki'

    def version(self, code):
        return '1.15.1'

    def nicepath(self, code):
        return "%s/" % self.path(self, code)
