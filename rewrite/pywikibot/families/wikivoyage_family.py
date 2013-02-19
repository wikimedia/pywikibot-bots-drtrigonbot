# -*- coding: utf-8 -*-

__version__ = '$Id: wikivoyage_family.py 11067 2013-02-10 15:41:55Z xqt $'

# The new wikivoyage family that is hosted at wikimedia

from pywikibot import family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikivoyage'
        self.languages_by_size = [
            'en', 'de', 'pt', 'nl', 'fr', 'it', 'ru', 'sv', 'es', 'ro', 'pl',
        ]

        self.langs = dict([(lang, '%s.wikivoyage.org' % lang)
                           for lang in self.languages_by_size])
        # Global bot allowed languages on http://meta.wikimedia.org/wiki/Bot_policy/Implementation#Current_implementation
        self.cross_allowed = ['es', 'ru', ]
