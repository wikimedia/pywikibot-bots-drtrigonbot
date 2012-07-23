import sys, os

scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))

try:
    # try to import
    import segdist_cpp
except ImportError, e:
    print "(re-)compilation triggered because of: '%s'" % e

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, 'dtbext/jseg') )

    # remove/reset if existing already
    if os.path.exists('segdist_cpp.so'):
        os.remove('segdist_cpp.so')

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make segdist_cpp.so"):
        raise ImportError("'segdist_cpp.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import segdist_cpp
