# patches applied for compatibility with lua5.1:
# https://github.com/bastibe/lunatic-python/issues/1
# http://lua-users.org/wiki/LunaticPython

import sys, os

scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))

libdir = os.path.join(scriptdir, '../dtbext/_lua/build/lib.linux-x86_64-%s.%s' % sys.version_info[:2])
sys.path.append(os.path.join(libdir))

try:
    # try to import
    from lua import *
except ImportError, e:
    print "(re-)compilation triggered because of: '%s'" % e

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, '../dtbext/_lua') )

    # remove/reset if existing already
    if os.path.exists(os.path.join(scriptdir, 'lua.so')):
        os.remove( os.path.join(scriptdir, 'lua.so') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("python setup.py build"):
#    if os.system("make"):
        raise ImportError("'lua.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import   - DOES NOT WORK HERE...?!?!
    from lua import *
