# -*- coding: utf-8  -*-

__version__ = '$Id: incubator_family.py 9589 2011-10-06 07:28:32Z xqt $'

from pywikibot import family

# The Wikimedia Incubator family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'incubator'
        self.langs = {
            'incubator': 'incubator.wikimedia.org',
        }

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def ssl_pathprefix(self, code):
        return "/wikipedia/incubator"

