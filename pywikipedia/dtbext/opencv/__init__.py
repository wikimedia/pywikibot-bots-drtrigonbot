import sys, os
scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))

try:
    # try to import
    import BoWclassify
except ImportError:
    #import os

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, 'dtbext/opencv') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make BoWclassify.so"):
        raise ImportError("'BoWclassify.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import BoWclassify
