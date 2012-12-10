# -*- coding: utf-8  -*-
__version__ = '$Id: lyricwiki_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# The LyricWiki family

# user_config.py:
# usernames['lyricwiki']['en'] = 'user'

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'lyricwiki'
        self.langs = {
            'en': 'lyrics.wikia.com',
           }

    def version(self, code):
        return "1.16.2"

    def scriptpath(self, code):
        return ''

    def apipath(self, code):
        return '/api.php'
