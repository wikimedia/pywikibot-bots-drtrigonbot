try:
    # try to import
    import BoWclassify
except ImportError:
    import os

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(os.path.abspath(os.curdir), 'dtbext/opencv') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make BoWclassify.so"):
        raise ImportError("'BoWclassify.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import BoWclassify