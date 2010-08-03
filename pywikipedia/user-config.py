# -*- coding: utf-8  -*-

# This is an automatically generated file. You can find more configuration parameters in 'config.py' file.

# The family of sites we are working on. wikipedia.py will import
# families/xxx_family.py so if you want to change this variable,
# you need to write such a file.
family = 'wikipedia'

# The language code of the site we're working on.
mylang = 'de'

# The dictionary usernames should contain a username for each site where you
# have a bot account.
usernames['wikipedia']['de'] = u'DrTrigonBot'


############## LOGFILE SETTINGS ##############

# Defines for which scripts a logfile should be enabled. Logfiles will be
# saved in the 'logs' subdirectory.
# Example:
#     log = ['interwiki', 'weblinkchecker', 'table2wiki']
# It is also possible to enable logging for all scripts, using this line:
#     log = ['*']
# To disable all logging, use this:
#     log = []
# Per default, logging of interwiki.py is enabled because its logfiles can
# be used to generate so-called warnfiles.
# This setting can be overridden by the -log or -nolog command-line arguments.
log = ['interwiki']


############## INTERWIKI SETTINGS ##############

# Should interwiki.py report warnings for missing links between foreign
# languages?
interwiki_backlink = True

# Should interwiki.py display every new link it discovers?
interwiki_shownew = True

# Should interwiki.py output a graph PNG file on conflicts?
# You need pydot for this: http://dkbza.org/pydot.html
interwiki_graph = False

# Specifies that the robot should process that amount of subjects at a time,
# only starting to load new pages in the original language when the total
# falls below that number. Default is to process (at least) 100 subjects at
# once.
interwiki_min_subjects = 100

# If interwiki graphs are enabled, which format(s) should be used?
# Supported formats include png, jpg, ps, and svg. See:
# http://www.graphviz.org/doc/info/output.html
# If you want to also dump the dot files, you can use this in your
# user-config.py:
# interwiki_graph_formats = ['dot', 'png']
# If you need a PNG image with an HTML image map, use this:
# interwiki_graph_formats = ['png', 'cmap']
# If you only need SVG images, use:
# interwiki_graph_formats = ['svg']
interwiki_graph_formats = ['png']

# You can post the contents of your autonomous_problems.dat to the wiki,
# e.g. to http://de.wikipedia.org/wiki/Wikipedia:Interwiki-Konflikte .
# This allows others to assist you in resolving interwiki problems.
# To help these people, you can upload the interwiki graphs to your
# webspace somewhere. Set the base URL here, e.g.:
# 'http://www.example.org/~yourname/interwiki-graphs/'
interwiki_graph_url = None

# Save file with local articles without interwikis.
without_interwiki = False

# Experimental feature:
# Store the page contents on disk (/cache/ directory) instead of loading
# them in RAM.
interwiki_contents_on_disk = False


############## SOLVE_DISAMBIGUATION SETTINGS ############
#
# Set disambiguation_comment[FAMILY][LANG] to a non-empty string to override
# the default edit comment for the solve_disambiguation bot.
# Use %s to represent the name of the disambiguation page being treated.
# Example:
#
# disambiguation_comment['wikipedia']['en'] = \
#    "Robot-assisted disambiguation ([[WP:DPL|you can help!]]): %s"

sort_ignore_case = False


############## IMAGE RELATED SETTINGS ##############
# If you set this to True, images will be uploaded to Wikimedia
# Commons by default.
upload_to_commons = False


############## TABLE CONVERSION BOT SETTINGS ##############

# will split long paragraphs for better reading the source.
# only table2wiki.py use it by now
splitLongParagraphs = False
# sometimes HTML-tables are indented for better reading.
# That can do very ugly results.
deIndentTables = True
# table2wiki.py works quite stable, so you might switch to True
table2wikiAskOnlyWarnings = True
table2wikiSkipWarnings = False


############## WEBLINK CHECKER SETTINGS ##############

# How many external links should weblinkchecker.py check at the same time?
# If you have a fast connection, you might want to increase this number so
# that slow servers won't slow you down.
max_external_links = 50

report_dead_links_on_talk = False


############## DATABASE SETTINGS ##############
db_hostname = 'localhost'
db_username = 'wikiuser'
db_password = ''


############## SEARCH ENGINE SETTINGS ##############

# Some scripts allow querying Google via the Google Web API. To use this feature,
# you must install the pyGoogle module from http://pygoogle.sf.net/ and have a
# Google Web API license key. Note that Google doesn't give out license keys
# anymore.
google_key = ''

# Some scripts allow using the Yahoo! Search Web Services. To use this feature,
# you must install the pYsearch module from http://pysearch.sourceforge.net/
# and get a Yahoo AppID from http://developer.yahoo.com
yahoo_appid = ''

# To use Windows Live Search web service you must get an AppID from
# http://search.msn.com/developer
msn_appid = ''


############## COPYRIGHT SETTINGS ##############

# Enable/disable search engine in copyright.py script
copyright_google = True
copyright_yahoo = True
copyright_msn = False

# Perform a deep check, loading URLs to search if 'Wikipedia' is present.
# This may be useful to improve number of correct results. If you haven't
# a fast connection, you might want to keep they disabled.
copyright_check_in_source_google = False
copyright_check_in_source_yahoo = False
copyright_check_in_source_msn = False

# Web pages may content a Wikipedia text without 'Wikipedia' word but with
# typical '[edit]' tag result of copy & paste procedure. You can want no
# report for this kind of URLs, even if they are copyright violation.
# However, when enabled these URLs are logged in a file.

copyright_check_in_source_section_names = False

# Limit number of queries for page.
copyright_max_query_for_page = 25

# Skip a specified number of queries
copyright_skip_query = 0

# Number of attempts on connection error.
copyright_connection_tries = 10

# Behavior if an exceeded error occur.
#
# Possibilities:
#
#    0 = None
#    1 = Disable search engine
#    2 = Sleep (default)
#    3 = Stop

copyright_exceeded_in_queries = 2
copyright_exceeded_in_queries_sleep_hours = 6

# Append last modified date of URL to script result
copyright_show_date = True

# Append length of URL to script result
copyright_show_length = True

# By default the script try to identify and skip text that contents a wide
# comma separated list or only numbers. But sometimes that might be the
# only part unmodified of a slightly edited and not otherwise reported
# copyright violation. You can disable this feature to try to increase
# number of results.

copyright_economize_query = True


############## FURTHER SETTINGS ##############

# The bot can make some additional changes to each page it edits, e.g. fix
# whitespace or positioning of interwiki and category links.

# This is an experimental feature; handle with care and consider re-checking
# each bot edit if enabling this!
cosmetic_changes = False

# If cosmetic changes are switched on, and you also have several accounts at
# projects where you're not familiar with the local conventions, you probably
# only want the bot to do cosmetic changes on your "home" wiki which you
# specified in config.mylang and config.family.
# If you want the bot to also do cosmetic changes when editing a page on a
# foreign wiki, set cosmetic_changes_mylang_only to False, but be careful!
cosmetic_changes_mylang_only = True

# Use the experimental disk cache to prevent huge memory usage
use_diskcache = False

# Retry loading a page on failure (back off 1 minute, 2 minutes, 4 minutes
# up to 30 minutes)
retry_on_fail = True

# End of configuration section
