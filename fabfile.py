# -*- coding: utf-8 -*-
"""
HOW TO INSTALL DrTrigonBot TO TOOLSERVER AND/OR LABS-TOOLS

1.) download and install fabric
2.) download the fabfile:
    $ wget https://git.wikimedia.org/raw/pywikibot%2Fbots%2Fdrtrigonbot/HEAD/fabfile.py
3.) run the fabfile:
    $ fab -H localhost install

It will automatically clone the needed repos and setup the server home
directory in order to be able to run DrTrigonBot.

Created on Sat Sep 14 18:22:30 2013
@author: drtrigon
"""
# http://yuji.wordpress.com/2011/04/09/django-python-fabric-deployment-script-and-example/
# http://artymiak.com/quick-backups-with-fabric-and-python/

from fabric.api import *


def __host_info():
    #run('uname -s')
    result = local('uname -a', capture=True)
    print result
    return result

LABS = ('tools-login' in __host_info())


def _get_git_path(repo, dest, path):
    #local('wget --content-disposition https://git.wikimedia.org/zip/?r=pywikibot/bots/drtrigonbot\&p=public_html\&h=HEAD\&format=gz')
    local('wget -O temp.tar.gz https://git.wikimedia.org/zip/?r=%s\&p=%s\&h=HEAD\&format=gz' % (repo, path))
    local('tar -zxvf temp.tar.gz')
    local('rm temp.tar.gz')

# (simpler) alternative to '_clone_git' & '_clean_git'
def _get_git(repo):
    #local('wget --content-disposition https://git.wikimedia.org/zip/?r=pywikibot/bots/drtrigonbot\&p=public_html\&h=HEAD\&format=gz')
    local('wget -O temp.tar.gz https://git.wikimedia.org/zip/?r=%s\&h=HEAD\&format=gz' % (repo,))
    local('tar -zxvf temp.tar.gz')
    local('rm temp.tar.gz')

def _clone_git_devel(repo='pywikibot/compat', dest='pywikipedia-git', username='drtrigon'):
    local('git clone --recursive ssh://%s@gerrit.wikimedia.org:29418/%s.git %s' % (username, repo, dest))

def _clone_git_user(repo='pywikibot/compat', dest='pywikipedia-git'):
    local('git clone --recursive https://gerrit.wikimedia.org/r/%s.git %s' % (repo, dest))

def _clone_git(repo, dest):
    _clone_git_user(repo=repo, dest=dest)

def _clone_git_path(repo, dest, paths=[]):
    # http://vmiklos.hu/blog/sparse-checkout-example-in-git-1-7
    _clone_git_user(repo=repo, dest=dest)
    local('cd %s; git config core.sparsecheckout true' % dest)
    for item in paths:
        local('cd %s; echo %s > .git/info/sparse-checkout' % (dest, item))
    local('cd %s; git read-tree -m -u HEAD' % dest)

def _clean_git(repos=[]):
    for path in repos:
        local('cd %s; git gc --aggressive --prune' % path)


def setup():
    """ 1.) setup home directory structure and .htaccess files """
    local('mkdir BAK_DIR')
    local('mkdir data')
    local('mkdir data/subster')
    local('mkdir data/sum_disc')
    if LABS:    # labs-tools
        local('echo Options +Indexes > public_html/.htaccess')
        local('mkdir public_html/logs')         # contains symlinks
        local('echo AddType text/plain .log > public_html/logs/.htaccess')
    else:       # toolserver
        local('mkdir public_html/doc')          # contains symlinks
        local('mkdir public_html/DrTrigonBot')  # contains symlinks
        local('mkdir public_html/source')
# create redirect to svn and git repo browser in 'public_html/source'
        local('mkdir public_html/test')

def dl_webstuff():
    if LABS:    # labs-tools
        _get_git_path(repo='pywikibot/bots/drtrigonbot', dest=None, path='public_html/cgi-bin')
        _clone_git_path(repo='pywikibot/bots/drtrigonbot', dest='pywikibot-web/', paths=['public_html/'])
    else:       # toolserver
        _get_git_path(repo='pywikibot/bots/drtrigonbot', dest=None, path='public_html')
        _clone_git_path(repo='pywikibot/bots/drtrigonbot', dest='pywikibot-web/', paths=['public_html/'])

def dl_compat():
    # https://www.mediawiki.org/wiki/Manual:Pywikipediabot/Installation#Setup_on_Wikimedia_Labs.2FTool_Labs_server
    _clone_git(repo='pywikibot/compat', dest='pywikibot-compat')
    _clean_git(repos=['pywikibot-compat/i18n/',
                      'pywikibot-compat/externals/opencv/',
                      'pywikibot-compat/externals/pycolorname/',
                      'pywikibot-compat/externals/spelling/',])
    # or: _get_git(repo='pywikibot/compat')

def dl_core():
    # https://www.mediawiki.org/wiki/Manual:Pywikipediabot/Installation#Setup_on_Wikimedia_Labs.2FTool_Labs_server
    _clone_git(repo='pywikibot/core', dest='pywikibot-core')
    _clean_git(repos=['pywikibot-core/',                        # needed?
                      'pywikibot-core/scripts/i18n/',
                      'pywikibot-core/externals/httplib2/',])
    # or: _get_git(repo='pywikibot/core')

def download():
    """ 2.) download (dl) all code """
    dl_webstuff()
    dl_compat()
    dl_core()

#def sl_webstuff(): pass

def sl_compat():
    if LABS:    # labs-tools
        # docs ?
        # logs
        local('cd public_html/logs/; ln -s /data/project/drtrigonbot/pywikibot-compat/logs compat')
    else:       # toolserver
        # docs
        local('cd public_html/doc/; ln -s /home/drtrigon/pywikipedia/docs DrTrigonBot')
        # logs
        local('cd public_html/DrTrigonBot/; ln -s /home/drtrigon/pywikipedia/logs trunk')

def sl_core():
    if LABS:    # labs-tools
        # docs ?
        # logs
        local('cd public_html/logs/; ln -s /data/project/drtrigonbot/pywikibot-core/logs core')
    else:       # toolserver
        # docs
# create symlink to core (rewrite) docs here
        # logs
        local('cd public_html/DrTrigonBot/; ln -s /home/drtrigon/rewrite/logs rewrite')

def symlink():
    """ 3.) symlink (sl) all directories and files """
    #sl_webstuff()
    sl_compat()
    sl_core()

def install():
    """ install all bot code to the server (ALL steps) """
    # setup home directory structure
    setup()    
    # download all
    download()
    # symlink all
    symlink()
    # setup server config files ...
    # set file permissions ...
    # ...
