# -*- coding: utf-8  -*-

__version__ = '$Id: wikia_family.py 10503 2012-08-23 10:23:04Z xqt $'

from pywikibot import family

# The Wikia Search family
# user-config.py: usernames['wikia']['wikia'] = 'User name'

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = u'wikia'

        self.langs = {
            u'wikia': None,
        }

    def hostname(self, code):
        return u'www.wikia.com'

    def version(self, code):
        return "1.16.5"

    def scriptpath(self, code):
        return ''

    def apipath(self, code):
        return '/api.php'
