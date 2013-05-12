#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Externals modules automatic setup checker and installer for various OS.
"""

#
# (C) DrTrigon, 2013
# (C) Pywikipedia team, 2013
#
# Distributed under the terms of the MIT license.
#
# Strongly inspired by files beeing part of VisTrails distribution
#   utils/installbundle.py
#   utils/requirements.py
# Copyright (C) 2006-2010 University of Utah. All rights reserved.
# GNU General Public License version 2.0 by the Free Software Foundation
#
__version__ = '$Id$'
#


# supports: 1. package management system (yum, apt-get, ...)
#           2. download from url (or svn, git repo)
#          (?. checkout from svn/mercurial repo)
#           3. svn:externals
modules_needed = {
# TODO: vvv (future; enable for and use in 'catimages.py')
#              '_mlpy': ({},
#                        {  'url': 'http://downloads.sourceforge.net/project/mlpy/mlpy%203.5.0/mlpy-3.5.0.tar.gz',
#                          'path': 'mlpy-3.5.0/mlpy',}),                    # OK
# TODO: vvv (future; enable for and use in 'catimages.py')
# mercurial: $ hg clone -r ocropus-0.6pre3 https://code.google.com/p/ocropus
#           '_ocropus': ({},
#                        {}),                                               # OPEN
# TODO: vvv (further clean-up and unlink - check with 'svn list')
#             'opencv': $ svn propedit svn:externals .
#                         bagofwords_classification.cpp https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/bagofwords_classification.cpp
#                         bagofwords_classification_python.cpp https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/bagofwords_classification_python.cpp
#                         camera_virtual_default https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/camera_virtual_default
#                         facetest.pl https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/facetest.pl
#                         __init.py__ https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/__init__.py
#                         makefile https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/makefile
#                         peopledetect.py https://svn.toolserver.org/svnroot/drtrigon/externals/opencv/peopledetect.py
#                       $ svn propedit svn:externals haarcascades/haartraining/
#                         HaarTraining https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/HaarTraining
#                         HaarTraining.tar.gz https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/HaarTraining.tar.gz
#                         convert_cascade.c https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/convert_cascade.c
#                         create_pos_neg.py https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/create_pos_neg.py
#                         createtestsamples.pl https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/createtestsamples.pl
#                         createtrainsamples.pl https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/createtrainsamples.pl
'opencv/haarcascades': ({},
                        {  'url': 'https://svn.toolserver.org/svnroot/drtrigon/externals/haarcascades-full.tar.gz',
                          'path': 'haarcascades',}),                       # OK
# TODO: vvv (include)
#               'TEST_slic': ({},
#                        {  'url': 'https://github.com/amueller/slic-python/archive/master.zip',
#                          'path': 'slic-python-master',}),                 # OPEN
#               'TEST_slic': ({},
#                        {  'url': 'http://ivrg.epfl.ch/files/content/sites/ivrg/files/supplementary_material/RK_SLICsuperpixels/SLICSuperpixelsAndSupervoxelsCode.zip',
#                          'path': 'SLICSuperpixelsAndSupervoxelsCode/SLICSuperpixels',}),# OPEN
# (2 download sources to same dir) + patch (at least for '__init__.py') needed
# TODO: vvv (include)
#               'TEST__bob': ({},
#                        { 'url': 'https://www.idiap.ch/software/bob/packages/bob-1.1.2.zip',
#                         'path': 'bob-1.1.2',}),                           # OPEN
# (complex compilation) + patch (at least for '__init__.py') needed
#     'TEST_xbob_flandmark': ({},
#                        { 'url': 'https://pypi.python.org/packages/source/x/xbob.flandmark/xbob.flandmark-1.0.9.zip',
#                         'path': 'xbob.flandmark-1.0.9',}),                # OPEN
# (complex compilation, dependent on '_bob') + patch (at least for '__init__.py') needed
}

#modules_order = ['_mlpy', '_ocropus', 'opencv', 'opencv/haarcascades', 'slic',
#                 '_bob', 'xbob_flandmark',]
modules_order = ['opencv/haarcascades',]


import os

import wikipedia as pywikibot


### BEGIN of VisTrails inspired and copied code ### ### ### ### ### ### ### ###

def guess_system():
    import platform
    return ("%s-%s" % (platform.system(), platform.dist()[0])).lower()

def show_question(which_files):
    pywikibot.output("Required package missing")
    pywikibot.output("A required package is missing, but externals can"
                     " automatically install it."
                     " If you say Yes, externals will need administrator"
                     " privileges, and you might be asked for the administrator"
                     " password.")
    pywikibot.output("Give externals permission to try to install package?"
                     " (y/N)")
    v = raw_input().upper()
    return v == 'Y' or v == 'YES'


def linux_ubuntu_install(package_name):
    cmd = 'apt-get install -y'

    if type(package_name) == str:
        cmd += ' ' + package_name
    elif type(package_name) == list:
        for package in package_name:
            if type(package) != str:
                raise TypeError("Expected string or list of strings")
            cmd += ' ' + package

    pywikibot.warning("externals wants to install package(s) '%s'" %
                      package_name)
    sucmd = "sudo %s" % cmd

    result = os.system(sucmd)

    return (result == 0) # 0 indicates success

def linux_fedora_install(package_name):
    cmd = 'yum -y install'

    if type(package_name) == str:
        cmd += ' ' + package_name
    elif type(package_name) == list:
        for package in package_name:
            if type(package) != str:
                raise TypeError("Expected string or list of strings")
            cmd += ' ' + package

    pywikibot.warning("externals wants to install package(s) '%s'" %
                      package_name)
    sucmd = "su -c'%s'" % cmd

    result = os.system(sucmd)

    return (result == 0)

def linux_install(dependency_dictionary):
    """Tries to import a python module. If unsuccessful, tries to install
the appropriate bundle and then reimport. py_import tries to be smart
about which system it runs on."""

    # Ugly fix to avoid circular import
    distro = guess_system()
    if not dependency_dictionary.has_key(distro):
        return False
    else:
        files = dependency_dictionary[distro]
        if files and show_question(files):
            callable_ = globals()[distro.replace('-', '_') + '_install']
            return callable_(files)
        else:
            return False

### END of VisTrails inspired and copied code   ### ### ### ### ### ### ### ###


def download_install(package, module, path):
    if package:
        pywikibot.warning(u'Download package "%s" from %s'
                          % (module, package['url']))
        import urllib2, mimetypes
        response = urllib2.urlopen(package['url'])
        pywikibot.warning(u'Size of download: %s byte(s)'
                          % response.headers['Content-Length'])
        #mime = response.headers['Content-Type'].lower().split('/')
        mime = mimetypes.guess_type(package['url'], strict=True)[0].lower().split('/')
        pywikibot.warning(u'MIME type: %s' % mime)

        pywikibot.warning(u'Extract package "%s" to %s'
                          % (module, os.path.join(path, module)))
        if len(mime) > 1:
            if   mime[1] == 'zip':
                import zipfile, StringIO
                arch = zipfile.ZipFile(StringIO.StringIO(response.read()))
            elif mime[1] == 'x-tar':
                import tarfile, StringIO
                arch = tarfile.open(fileobj=StringIO.StringIO(response.read()))
            arch.extractall(os.path.join(path, '__setup_tmp/'))
            arch.close()
            import shutil
            shutil.move(os.path.join(path, '__setup_tmp/', package['path']),
                        os.path.join(path, module))
            shutil.rmtree(os.path.join(path, '__setup_tmp/'))

            result = 0
            if 'patch' in package:
                pywikibot.warning(u'Install package "%s" by applying patch to %s.'
                                  % (module, os.path.join(path, module)))
                cmd = 'patch -p0 -d %s < %s' % (path, os.path.join(path, package['patch']))
                result = os.system(cmd)

            pywikibot.warning(u'Package "%s" installed to %s.'
                              % (module, os.path.join(path, module)))
            return (result == 0)

    return False


def check_setup(m):
    path = os.path.dirname(os.path.abspath(os.path.join(os.curdir, __file__)))
    mf = os.path.join(path, m)

    #__import__(mf)
    if not os.path.exists(mf):
        # install the missing module
        if linux_install(modules_needed[m][0]):
            return
        if download_install(modules_needed[m][1], m, path):
            return
#        if svn_repo_install(modules_needed[m][2]):
#            return
        pywikibot.error(u'Package "%s" could not be found nor installed!'
                            % m) 

def check_setup_all():
    #for m in modules_needed:
    for m in modules_order:
        check_setup(m)


#check_setup_all()
