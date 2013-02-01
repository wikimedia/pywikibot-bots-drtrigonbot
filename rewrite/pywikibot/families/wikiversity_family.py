# -*- coding: utf-8  -*-
from pywikibot import family

__version__ = '$Id: wikiversity_family.py 11006 2013-01-27 14:20:10Z xqt $'

# The Wikimedia family that is known as Wikiversity

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikiversity'

        self.languages_by_size = [
            'en', 'fr', 'de', 'beta', 'cs', 'ru', 'it', 'es', 'pt', 'ar', 'fi',
            'el', 'sv', 'sl', 'ja',
        ]

        self.langs = dict([(lang, '%s.wikiversity.org' % lang)
                           for lang in self.languages_by_size])


        # Global bot allowed languages on http://meta.wikimedia.org/wiki/Bot_policy/Implementation#Current_implementation
        self.cross_allowed = ['ja',]
