# -*- coding: utf-8  -*-

__version__ = '$Id: test_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# The test wikipedia family
class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'test'
        self.langs = {
            'test': 'test.wikipedia.org',
        }

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def ssl_pathprefix(self, code):
        return "/wikipedia/test"
