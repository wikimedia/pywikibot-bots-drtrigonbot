import sys, os
scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))
sys.path.append(os.path.join(scriptdir, 'dtbext/_pydmtx/build/lib.linux-x86_64-%s.%s' % sys.version_info[:2]))
try:
    # try to import
    from pydmtx import DataMatrix
except ImportError:
    #import os

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, 'dtbext/_pydmtx') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("python setup.py build"):
#    if os.system("make"):
        raise ImportError("'_pydmtx.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import   - DOES NOT WORK HERE...?!?!
    from pydmtx import DataMatrix

## skip processing of DataMatrix with this dummy
#class DataMatrix(object):
#    def __init__(self, *arg, **kwd):
#        return None
#    def decode(self, *arg, **kwd):
#        return None
#    def count(self, *arg, **kwd):
#        return 0
