#import sys, os
#sys.path.append(os.path.join(os.path.abspath(os.curdir), 'dtbext/_pydmtx/build/lib.linux-x86_64-2.7'))
#try:
#    # try to import
#    from pydmtx import DataMatrix
#except ImportError:
#    #import os
#
#    cur = os.path.abspath(os.curdir)
#    os.chdir( os.path.join(os.path.abspath(os.curdir), 'dtbext/_pydmtx') )
#
#    # compile python module (may be use 'distutil' instead of 'make' here)
#    if os.system("python setup.py build"):
##    if os.system("make"):
#        raise ImportError("'???.so' could not be compiled!")
#
#    os.chdir( cur )
#
#    # re-try to import   - DOES NOT WORK HERE...?!?!
#    from pydmtx import DataMatrix

# skip processing of DataMatrix with this dummy
class DataMatrix(object):
    def __init__(self, *arg, **kwd):
        return None
    def decode(self, *arg, **kwd):
        return None
    def count(self, *arg, **kwd):
        return 0
