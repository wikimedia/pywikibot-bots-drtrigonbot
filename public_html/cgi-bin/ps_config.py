# -*- coding: utf-8 -*-
"""
Configuration variables (config for cgi-bin scripts)
"""

## @package ps_config
#  @brief   configuration variables
#
#  @copyright Dr. Trigon, 2008-2013
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


# === labs conversion patch: variables === === ===
#
ver_desc = {  'ts': ['trunk', 'rewrite'],
            'labs': ['compat', 'core'], }

localdir = {  'ts': ['..', 'DrTrigonBot', '.'],
            'labs': ['..', 'public_html', 'logs', '.'], }

bot_path = {  'ts': ["../../pywikipedia/", "../../rewrite/"],
            'labs': ["../pywikibot-compat/", "../pywikibot-core/"], }

db_conf  = {  'ts': ['u_%(user)s', "wiki-p.userdb.toolserver.org"],
            'labs': ['%(user)s__%(dbname)s', "wiki.labsdb"], }
