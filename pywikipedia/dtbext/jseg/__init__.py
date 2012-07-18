try:
    # try to import
    import segdist_cpp
except ImportError:
    import os

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(os.path.abspath(os.curdir), 'dtbext/jseg') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make segdist_cpp.so"):
        raise ImportError("'segdist_cpp.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import segdist_cpp
