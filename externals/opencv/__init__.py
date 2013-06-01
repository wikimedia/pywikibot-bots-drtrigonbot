import sys, os

scriptdir = os.path.dirname(sys.argv[0])
if not os.path.isabs(scriptdir):
    scriptdir = os.path.abspath(os.path.join(os.curdir, scriptdir))
#sys.path.append("/home/ursin/data/toolserver/pywikipedia/dtbext/opencv")
    
libdir = os.path.join(scriptdir, 'dtbext/opencv')
if not os.path.exists(libdir):
    os.makedirs(libdir)
# path has to exist BEFORE appending, otherwise the re-import fails
sys.path.append(libdir)

import numpy

try:
    # try to import
    import BoWclassify
except ImportError, e:
    print "(re-)compilation triggered because of: '%s'" % e

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, 'dtbext/opencv') )

    # remove/reset if existing already
    if os.path.exists(os.path.join(libdir, 'BoWclassify.so')):
        os.remove( os.path.join(libdir, 'BoWclassify.so') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make BoWclassify.so"):
        raise ImportError("'BoWclassify.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import BoWclassify

try:
    # try to import
    import posit as _posit
except ImportError, e:
    print "(re-)compilation triggered because of: '%s'" % e

    cur = os.path.abspath(os.curdir)
    os.chdir( os.path.join(scriptdir, 'dtbext/opencv') )

    # remove/reset if existing already
    if os.path.exists(os.path.join(libdir, 'posit.so')):
        os.remove( os.path.join(libdir, 'posit.so') )

    # compile python module (may be use 'distutil' instead of 'make' here)
    if os.system("make posit.so"):
        raise ImportError("'posit.so' could not be compiled!")

    os.chdir( cur )

    # re-try to import
    import posit as _posit

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def posit(model, image, crit):
    _model = [ tuple(item) for item in model.astype(float) ]
    _image = [ tuple(item) for item in image.astype(float) ]
    #_crit  = tuple(crit.astype(float))
    _crit  = (long(crit[0]), float(crit[1]))

    try:
        (_rmat, _tvec) = _posit.main(_model, _image, _crit)
    except Exception, e:
        raise e.__class__("Error in 'cvPOSIT' wrapper 'posit.so' (%s)" % e)

    rmat = numpy.reshape(numpy.array(_rmat), (3,3))
    tvec = numpy.array(_tvec)
    return (rmat, tvec)
