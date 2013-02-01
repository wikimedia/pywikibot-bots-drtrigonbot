# -*- coding: utf-8  -*-

__version__ = '$Id: test_family.py 10993 2013-01-27 12:38:06Z xqt $'

from pywikibot import family

# The test wikipedia family
class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'test'
        self.langs = {
            'test': 'test.wikipedia.org',
        }

    def ssl_pathprefix(self, code):
        return "/wikipedia/test"
