# -*- coding: utf-8  -*-

__version__ = '$Id: incubator_family.py 10996 2013-01-27 12:51:44Z xqt $'

from pywikibot import family

# The Wikimedia Incubator family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'incubator'
        self.langs = {
            'incubator': 'incubator.wikimedia.org',
        }

    def ssl_pathprefix(self, code):
        return "/wikipedia/incubator"
