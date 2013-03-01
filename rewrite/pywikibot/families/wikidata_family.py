# -*- coding: utf-8  -*-

__version__ = '$Id: wikidata_family.py 11106 2013-02-23 22:23:33Z valhallasw $'

from pywikibot import family

# The wikidata family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikidata'
        self.langs = {
            'wikidata': 'www.wikidata.org',
            'repo': 'wikidata-test-repo.wikimedia.de',
            'client': 'wikidata-test-client.wikimedia.de',
        }

    def shared_data_repository(self, code, transcluded=False):
        """Always return a repository tupe. This enables testing whether
        the site opject is the repository itself, see Site.is_data_repository()

        """
        if transcluded:
            return(None, None)
        else:
            return ('wikidata',
                    'wikidata') if code == 'wikidata' else ('repo', 'wikidata')
