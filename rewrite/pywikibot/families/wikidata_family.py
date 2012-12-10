# -*- coding: utf-8  -*-

__version__ = '$Id: wikidata_family.py 10729 2012-11-14 21:04:15Z xqt $'

from pywikibot import family

# The wikidata families

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikidata'
        self.langs = {
            'wikidata': 'wikidata.org',
            'repo': 'wikidata-test-repo.wikimedia.de',
            'client': 'wikidata-test-client.wikimedia.de',
        }

    def shared_data_repository(self, code):
        # for here an now we just use the test repo
        # for wikimedia families the method can return wikidata itself
        return ('repo', 'wikidata') if code == 'client' else (None, None)
