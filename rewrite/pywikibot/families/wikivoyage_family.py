# -*- coding: utf-8 -*-

__version__ = '$Id: wikivoyage_family.py 11006 2013-01-27 14:20:10Z xqt $'

# The new wikivoyage family that is hosted at wikimedia

from pywikibot import family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikivoyage'
        self.languages_by_size = [
            'de', 'en', 'fr', 'it', 'nl', 'ru', 'sv', 'pt', 'es',
        ]

        self.langs = dict([(lang, '%s.wikivoyage.org' % lang)
                           for lang in self.languages_by_size])
