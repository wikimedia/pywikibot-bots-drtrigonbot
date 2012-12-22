# -*- coding: utf-8  -*-
from pywikibot import family

__version__ = '$Id: wikiversity_family.py 10771 2012-12-08 13:45:00Z xqt $'

# The Wikimedia family that is known as Wikiversity

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikiversity'

        self.languages_by_size = [
            'en', 'fr', 'de', 'beta', 'cs', 'ru', 'it', 'es', 'pt', 'ar', 'fi',
            'el', 'sv', 'sl', 'ja',
        ]

        self.langs = dict([(lang, '%s.wikiversity.org' % lang) for lang in self.languages_by_size])


        # CentralAuth cross avaliable projects.
        self.cross_projects = [
            'wiktionary', 'wikibooks', 'wikiquote', 'wikisource', 'wikinews',
            'wikiversity', 'meta', 'mediawiki', 'test', 'incubator', 'commons',
            'species',
        ]

        # Global bot allowed languages on http://meta.wikimedia.org/wiki/Bot_policy/Implementation#Current_implementation
        self.cross_allowed = ['ja',]

    def shared_image_repository(self, code):
        return ('commons', 'commons')