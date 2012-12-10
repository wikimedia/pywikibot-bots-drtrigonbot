#
# (C) Pywikipedia bot team, 2008
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: cgi_interface.py 9065 2011-03-13 14:33:42Z xqt $'

import sys

class UI:
    def __init__(self):
        pass

    def output(self, text, colors = None, newline = True, toStdout = False):
        if not toStdout:
            return
        sys.stdout.write(text.encode('UTF-8', 'replace'))

    def input(self, question, colors = None):
        self.output(question + ' ', newline = False, showcgi = True)
