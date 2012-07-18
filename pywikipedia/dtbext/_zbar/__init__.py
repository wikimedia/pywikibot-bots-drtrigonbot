import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir), 'dtbext/_zbar/build/lib.linux-x86_64-2.7'))
try:
    # try to import
    from zbar import *
except ImportError:
    #import os

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(os.path.abspath(os.curdir), 'dtbext/_zbar') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("python setup.py build"):
        raise ImportError("'zbar.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import   - DOES NOT WORK HERE...?!?!
    from zbar import *

