#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Info: Simple DrTrigonBot Information Tool

Built on Simple and Lightweight Framework which is just a combination of
flask and cgi.

to make it usable from server, use: 'chmod 755 info.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 info.py' or even better
install it through fabfile.
"""
# http://www.gpcom.de/support/python

## @package info.py
#  @brief   Info: Simple DrTrigonBot Information Tool
#
#  @copyright Dr. Trigon, 2014
#
#  @section FRAMEWORK
#
#  Python wikipedia robot framework, DrTrigonBot.
#  @see http://pywikipediabot.sourceforge.net/
#  @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
#  @section LICENSE
#
#  Distributed under the terms of the MIT license.
#  @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
__version__='$Id$'
#


# === python flask CGI script (with Cheetah support) === === ===
#
import cgitb    # debug
cgitb.enable()  #

#import cgi

# https://flask.readthedocs.org/en/0.1/api/
from flask import Flask, render_template, render_template_string, Response, request
#from flask import abort

## http://stackoverflow.com/questions/8365244/cheetah-templating-with-flask
#from Cheetah.Template import Template
#
#def render_cheetah(template, context):
#    """Helper function to make template rendering less painful."""
#    return str(Template(template, namespaces=[context]))

# (default imports)
#
import sys, os, subprocess


# === templates and style (more in ./templates/) === === ===
#
#from ps_plain import content_type    # (style-sheet old style cgi code)
contentTemplate = "Content-Type: %s; charset=%s\n\n%s"

## (Cheetah template)
#mainTemplate = """
#<html>
#    <head><title>$title</title></head>
#    <body><h1>$title</h1></body>
#</html>"""

## (flask/Jinja2 template)
#mainTemplate = """
#<!doctype html>
#<title>Flaskr</title>
#<!--<link rel=stylesheet type=text/css href="{{ url_for('static', filename='style.css') }}">-->
#<div class=page>
#  <h1>Flaskr</h1>
#<!--  {% for message in get_flashed_messages() %} -->
#<!--    <div class=flash>{{ message }}</div> -->
#<!--  {% endfor %} -->
#    <div class=test>{{ test }}</div>
#  {% block body %}{% endblock %}
#</div>"""


# === flask/cgi web app source code === === ===
#
# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
#app.debug = True
app.config.update(dict(
    DEBUG=True,
    SERVER_NAME=os.getenv("SERVER_NAME"),
    APPLICATION_ROOT=os.path.dirname(os.getenv("SCRIPT_URL").split('.py/')[0]),
))
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# (constants)
viewfunc = os.path.basename(__file__)


def info_arch():
    import ps_plain as style        # check arch (ts, or labs)
    info = style.host(os.environ)   # (temporary patch)
    desc = subprocess.Popen('uname -a',
                            shell=True,
                            stdout=subprocess.PIPE).stdout.read()
    return {'info': info, 'desc': desc.strip()}

def info_flask():
    import flask
    return {'info': '', 'desc': 'Version %s' % flask.__version__}

def info_compat():
    import ps_plain as style
    return {'hsh': open(os.path.join(style.bot_path[style.host(os.environ)][0],
                                     '.git/refs/heads/master')).read().strip()}

def info_core():
    import ps_plain as style
    return {'hsh': open(os.path.join(style.bot_path[style.host(os.environ)][1],
                                     '.git/refs/heads/master')).read().strip()}

def info_drtrigonbot():
    import ps_plain as style
    return {'hsh': open(os.path.join(style.bot_path[style.host(os.environ)][0],
                                     '../pywikibot-drtrigonbot',
                                     '.git/refs/heads/master')).read().strip()}


#@app.route('/')
# http://flask.pocoo.org/snippets/57/
#@app.route('/' + viewfunc, defaults={'action': ''})
#@app.route('/' + viewfunc + '/<action>')
#def main_route(action):
@app.route('/' + viewfunc)
def main_route():
    # http://stackoverflow.com/questions/10434599/how-to-get-whole-request-post-body-in-python-flask
    raw = request.args['raw'] if 'raw' in request.args else None

    #return render_template_string(mainTemplate, test=viewfunc+'/abc/'+a)
    #return render_cheetah(mainTemplate, {'title': 'Welcome to "/"!'})
    #return render_template('info.html', title='Info',
    res =  render_template('info.html', title       = 'Info',
                                        refresh     = '',
                                        tsnotice    = '',
                                        footer      = ['default', 'w3c'],# 'css'],
                                        p_status    = '',
                                        arch        = info_arch(),
                                        flask       = info_flask(),
                                        compat      = info_compat(),
                                        core        = info_core(),
                                        drtrigonbot = info_drtrigonbot(),)
    return res if not raw else Response(res, mimetype='text/plain')


#@app.route('/about')
@app.route('/' + viewfunc + '/about')
def action_about():
    return render_template('info.html', title  = 'Info',
                                        footer = ['default', 'w3c'],# 'css'],
                                        arch   = info_arch(),
                                        flask  = info_flask(),)


##@app.route('/<action>')
#@app.route('/' + viewfunc + '/<action>')
#def action_unknown(action):
#    abort(404)    # 404 Not Found
#    #return render_template('info.html', error='404 Not Found')


# === Main procedure entry point === === ===
#
if __name__ == '__main__':
    if   '--stand-alone' in sys.argv:
        # start flask server
        app.run()
    else:
        # run as cgi script trough test_client
        #form = cgi.FieldStorage()
        #action = form.getvalue('action', 'main_route')
        #print locals()[action](form)

        # http://flask.pocoo.org/docs/testing/#faking-resources-and-context
        # http://stackoverflow.com/questions/464040/how-are-post-and-get-variables-handled-in-python
        with app.test_client() as c:
            resp = c.get('/%s%s?%s' % (viewfunc, os.getenv("PATH_INFO", ''), os.getenv("QUERY_STRING")))
            print contentTemplate % (resp.mimetype, resp.charset, resp.data)
#            raise BaseException(contentTemplate % (resp.mimetype, resp.charset, resp.data))
