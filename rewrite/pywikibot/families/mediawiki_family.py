# -*- coding: utf-8  -*-

__version__ = '$Id: mediawiki_family.py 10993 2013-01-27 12:38:06Z xqt $'

from pywikibot import family

# The MediaWiki family
# user-config.py: usernames['mediawiki']['mediawiki'] = 'User name'

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'mediawiki'

        self.langs = {
            'mediawiki': 'www.mediawiki.org',
        }

    def ssl_pathprefix(self, code):
        return "/wikipedia/mediawiki"
