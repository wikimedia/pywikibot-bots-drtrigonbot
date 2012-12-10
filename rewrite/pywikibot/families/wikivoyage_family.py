# -*- coding: utf-8 -*-

__version__ = '$Id: wikivoyage_family.py 10728 2012-11-14 21:03:36Z xqt $'

# The new wikivoyage family that is hosted at wikimedia

from pywikibot import family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'Wikivoyage'
        self.langs = {
            'de': u'de.wikivoyage.org',
            'en': u'en.wikivoyage.org',
            'fr': u'fr.wikivoyage.org',
            'it': u'it.wikivoyage.org',
            'nl': u'nl.wikivoyage.org',
            'ru': u'ru.wikivoyage.org',
            'sv': u'sv.wikivoyage.org',
        }

    def scriptpath(self, code):
        return u'/w'

    def shared_image_repository(self, code):
        return ('commons', 'commons')
