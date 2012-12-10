# -*- coding: utf-8  -*-

__version__ = '$Id: i18n_family.py 10212 2012-05-13 14:55:14Z xqt $'

from pywikibot import family

# The Wikimedia i18n family

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'i18n'
        self.langs = {
            'i18n': 'translatewiki.net',
        }

    def version(self, code):
        return "1.20alpha"
