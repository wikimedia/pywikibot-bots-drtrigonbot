# -*- coding: utf-8  -*-
__version__ = '$Id: southernapproach_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# ZRHwiki, formerly known as SouthernApproachWiki, a wiki about Zürich Airport.

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'southernapproach'
        self.langs = {
            'de':'www.zrhwiki.ch',
        }

    def version(self, code):
        return "1.17alpha"
