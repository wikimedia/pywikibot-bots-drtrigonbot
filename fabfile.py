# -*- coding: utf-8 -*-
"""
HOW TO INSTALL DrTrigonBot TO TOOLSERVER AND/OR LABS-TOOLS

1.) download and install git (and fabric)
2.) download the fabfile, e.g.:
    $ wget https://git.wikimedia.org/raw/pywikibot%2Fbots%2Fdrtrigonbot/HEAD/fabfile.py
3.) run the fabfile:
    $ fab -H localhost install
4.) setup you config files by generating new or copying existing ones
5.) run the finalization:
    $ fab -H localhost backup

It will automatically clone the needed repos and setup the server home
directory in order to be able to run DrTrigonBot.

To update the repos on the server run:
$ fab -H localhost update

To backup the config data on the server run:
$ fab -H localhost backup

To get an overview of the available commands run:
$ fab -H localhost help

If you did not install fabric or it is not available because you do not have
permissions, you can use the following syntax alternatively:
$ python fabfile.py -H localhost cmd1[,cmd2,...]
instead of
$ fab -H localhost cmd1[,cmd2,...]


Created on Sat Sep 14 18:22:30 2013
@author: drtrigon
"""
# http://yuji.wordpress.com/2011/04/09/django-python-fabric-deployment-script-and-example/

try:
    from fabric.api import *
except ImportError:
    # setup a simple local replacement, for alternative syntax
    import sys, os, subprocess
    def local(cmd, capture=False, *args, **kwargs):
        print "[%s] local-simple: %s" % (sys.argv[2], cmd)
        kwargs = {  'cwd': os.path.dirname(os.path.abspath(__file__)),
                  'shell': True,}
        if capture:
            kwargs['stdout'] = subprocess.PIPE
        res = subprocess.Popen(cmd, **kwargs)
        res.wait()
        if res.returncode:
            raise IOError('returncode %s' % res.returncode)
        return res.stdout.read().strip() if res.stdout else ""


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
        local('cd %s; echo %s >> .git/info/sparse-checkout' % (dest, item))
    local('cd %s; git read-tree -m -u HEAD' % dest)

def _clean_git(repos=[]):
    for path in repos:
        local('cd %s; git gc --aggressive --prune' % path)

def _update_git(dest):
    #local('cd %s; git checkout master' % (dest,))  # should always be on 'master'
    local('cd %s; git pull' % (dest,))
    #local('cd %s; git submodule update --force' % (dest,))


def setup():
    """ I.1) setup home directory structure and .htaccess files """
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

def dl_drtrigonbot():
#    if LABS:    # labs-tools
#        _get_git_path(repo='pywikibot/bots/drtrigonbot', dest=None, path='public_html/cgi-bin')
#    else:       # toolserver
#        _get_git_path(repo='pywikibot/bots/drtrigonbot', dest=None, path='public_html')
    _clone_git_path(repo='pywikibot/bots/drtrigonbot', dest='pywikibot-drtrigonbot/',
                    paths=['public_html/',
                           '/README',       # exclude 'externals/README'
                           'backup',
                           'fabfile.py',
                           'warnuserquota.py',
                           'crontab',
                           'literature',])
    _clean_git(repos=['pywikibot-drtrigonbot/',])
    if LABS:    # labs-tools
#        local('cp -r pywikibot-drtrigonbot/public_html/cgi-bin/* cgi-bin/')
        local('ln -s ~/pywikibot-drtrigonbot/public_html/cgi-bin/* cgi-bin/')
    else:       # toolserver
#        local('cp -r pywikibot-drtrigonbot/public_html/* public_html/')
        local('ln -s ~/pywikibot-drtrigonbot/public_html/* public_html/')

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
    """ I.2) download (dl) all code """
    dl_drtrigonbot()
    dl_compat()
    dl_core()

def sl_drtrigonbot():
    local('ln -s pywikibot-drtrigonbot/README README')
    local('ln -s pywikibot-drtrigonbot/backup backup')
    local('ln -s pywikibot-drtrigonbot/warnuserquota.py warnuserquota.py')

def sl_compat():
    if LABS:    # labs-tools
        # docs ?
        # logs
#        local('cd public_html/logs/; ln -s /data/project/drtrigonbot/pywikibot-compat/logs compat')
        local('ln -s ~/pywikibot-compat/logs public_html/logs/compat')
    else:       # toolserver
        # docs
#        local('cd public_html/doc/; ln -s /home/drtrigon/pywikipedia/docs DrTrigonBot')
        local('ln -s ~/pywikipedia/docs public_html/doc/DrTrigonBot')
        # logs
#        local('cd public_html/DrTrigonBot/; ln -s /home/drtrigon/pywikipedia/logs trunk')
        local('ln -s ~/pywikipedia/logs public_html/DrTrigonBot/trunk')

def sl_core():
    if LABS:    # labs-tools
        # docs ?
        # logs
#        local('cd public_html/logs/; ln -s /data/project/drtrigonbot/pywikibot-core/logs core')
        local('ln -s ~/pywikibot-core/logs public_html/logs/core')
    else:       # toolserver
        # docs
# create symlink to core (rewrite) docs here
        # logs
#        local('cd public_html/DrTrigonBot/; ln -s /home/drtrigon/rewrite/logs rewrite')
        local('ln -s ~/rewrite/logs public_html/DrTrigonBot/rewrite')

def symlink():
    """ I.3) symlink (sl) all directories and files """
    sl_drtrigonbot()
    sl_compat()
    sl_core()

def install():
    """ I.A) Install all bot code to the server   (all I.# steps) """
    # setup home directory structure
    setup()    
    # download all
    download()
    # symlink all
    symlink()
    # replace fabfile.py by a symlink to the one in the repo
    # done here at the very end instead of in 'sl_drtrigonbot'
    local('rm fabfile.py')
    local('ln -s pywikibot-drtrigonbot/fabfile.py fabfile.py')
    # setup server config files
    print ("\nPlease generate or copy the needed config files now:\n"
           "* user-config.py\n"
           "* login-data/* and *.lwp\n"
           "* data (subster mailbox, sum_disc history)\n"
           "* may be others (devel/, public_html/, quota-SunOS.rrd, ...)\n"
           "\nThen finish the installation by running:\n"
           "$ fab -H localhost backup")

def up_drtrigonbot():
    _update_git(dest='pywikibot-drtrigonbot/')
#    if LABS:    # labs-tools
#        local('cp -r pywikibot-drtrigonbot/public_html/cgi-bin/* cgi-bin/')
#    else:       # toolserver
#        local('cp -r pywikibot-drtrigonbot/public_html/* public_html/')

def up_compat():
    _update_git(dest='pywikibot-compat')

def up_core():
    _update_git(dest='pywikibot-core')

def update():
    """ U.A) Update (up) all code on the server   (all U.# steps) """
    up_drtrigonbot()
    up_compat()
    up_core()

def backup():
    """ B.A) Backup all bot code on the server    (all B.# steps) """
    # see also 'backup' sh script ...
    # http://artymiak.com/quick-backups-with-fabric-and-python/
    # * set file permissions ...
    # * run backup ...
    raise NotImplementedError

def list_large_files():
    """ L.A) List all files exceeding 5 and 10MB  (all L.# steps) """
    # List all files exceeding an size of 10MB. Use this to find e.g.
    # core dump files.
    # list files >5MB
    print "files larger than 5MB"
    local("""find . -type f -size +5000k -exec ls -lh {} \; | awk '{ print $9 ": " $5 }'""")
    print
    # list files >10MB
    print "files larger than 10MB"
    local("""find . -type f -size +10000k -exec ls -lh {} \; | awk '{ print $9 ": " $5 }'""")
    print


if (__name__ == '__main__') and ('sys' in locals()):
    if sys.argv[3] in locals():
        locals()[sys.argv[3]]()
    else:
        print dir()
