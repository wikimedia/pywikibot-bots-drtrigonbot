# -*- coding: utf-8  -*-

__version__ = '$Id: commons_family.py 11163 2013-03-02 20:04:53Z legoktm $'

from pywikibot import family

# The Wikimedia Commons family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
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

    def ssl_pathprefix(self, code):
        return "/wikipedia/commons"

