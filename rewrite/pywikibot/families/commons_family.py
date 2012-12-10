# -*- coding: utf-8  -*-

__version__ = '$Id: commons_family.py 10673 2012-11-08 07:57:03Z xqt $'

from pywikibot import family

# The Wikimedia Commons family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'commons'
        self.langs = {
            'commons': 'commons.wikimedia.org',
        }

        self.interwiki_forward = 'wikipedia'

        self.category_redirect_templates = {
            'commons': (u'Category redirect',
                        u'Categoryredirect',
                        u'Synonym taxon category redirect',
                        u'Invalid taxon category redirect',
                        u'Monotypic taxon category redirect',
                        u'See cat',
                        u'Seecat',
                        u'See category',
                        u'Catredirect',
                        u'Cat redirect',
                        u'Cat-red',
                        u'Catredir',
                        u'Redirect category'),
        }

        self.disambcatname = {
            'commons':  u'Disambiguation'
        }
        self.cross_projects = [
            'wikipedia', 'wiktionary', 'wikibooks', 'wikiquote', 'wikisource', 'wikinews', 'wikiversity',
            'meta', 'mediawiki', 'test', 'incubator', 'species',
        ]

    def dbName(self, code):
        return 'commonswiki_p'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def ssl_pathprefix(self, code):
        return "/wikipedia/commons"

