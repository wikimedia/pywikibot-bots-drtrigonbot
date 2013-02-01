# -*- coding: utf-8  -*-

__version__ = '$Id: meta_family.py 10996 2013-01-27 12:51:44Z xqt $'

from pywikibot import family

# The meta wikimedia family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'meta'
        self.langs = {
            'meta': 'meta.wikimedia.org',
        }
        self.interwiki_forward = 'wikipedia'
        self.cross_allowed = ['meta',]

    def ssl_pathprefix(self, code):
        return "/wikipedia/meta"
