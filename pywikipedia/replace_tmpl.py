# -*- coding: utf-8 -*-
"""
This bot will make only template replacements. It will retrieve information on
which pages might need changes either from an XML dump or a text file, or only
change a single page.

These command line parameters can be used to specify which pages to work on:

&params;

-xml              Retrieve information from a local XML dump (pages-articles
                  or pages-meta-current, see http://download.wikimedia.org).
                  Argument can also be given as "-xml:filename".

-page             Only edit a specific page.
                  Argument can also be given as "-page:pagetitle". You can
                  give this parameter multiple times to edit multiple pages.

Furthermore, the following command line parameters are supported:

-regex            Make replacements using regular expressions. If this argument
                  isn't given, the bot will make simple text replacements.

-nocase           Use case insensitive regular expressions.

-dotall           Make the dot match any character at all, including a newline.
                  Without this flag, '.' will match anything except a newline.

-multiline        '^' and '$' will now match begin and end of each line.

-xmlstart         (Only works with -xml) Skip all articles in the XML dump
                  before the one specified (may also be given as
                  -xmlstart:Article).

-addcat:cat_name  Adds "cat_name" category to every altered page.

-excepttitle:XYZ  Skip pages with titles that contain XYZ. If the -regex
                  argument is given, XYZ will be regarded as a regular
                  expression.

-requiretitle:XYZ Only do pages with titles that contain XYZ. If the -regex
                  argument is given, XYZ will be regarded as a regular
                  expression.

-excepttext:XYZ   Skip pages which contain the text XYZ. If the -regex
                  argument is given, XYZ will be regarded as a regular
                  expression.

-exceptinside:XYZ Skip occurences of the to-be-replaced text which lie
                  within XYZ. If the -regex argument is given, XYZ will be
                  regarded as a regular expression.

-exceptinsidetag:XYZ Skip occurences of the to-be-replaced text which lie
                  within an XYZ tag.

-summary:XYZ      Set the summary message text for the edit to XYZ, bypassing
                  the predefined message texts with original and replacements
                  inserted.

-sleep:123        If you use -fix you can check multiple regex at the same time
                  in every page. This can lead to a great waste of CPU because
                  the bot will check every regex without waiting using all the
                  resources. This will slow it down between a regex and another
                  in order not to waste too much CPU.

-fix:XYZ          Perform one of the predefined replacements tasks, which are
                  given in the dictionary 'fixes' defined inside the file
                  fixes.py.
                  The -regex and -nocase argument and given replacements will
                  be ignored if you use -fix.
                  Currently available predefined fixes are:
&fixes-help;

-always           Don't prompt you for each replacement

-recursive        Recurse replacement as long as possible. Be careful, this
                  might lead to an infinite loop.

-allowoverlap     When occurences of the pattern overlap, replace all of them.
                  Be careful, this might lead to an infinite loop.

other:            First argument is the old text, second argument is the new
                  text. If the -regex argument is given, the first argument
                  will be regarded as a regular expression, and the second
                  argument might contain expressions like \\1 or \g<name>.

Examples:

If you want to change templates from the old syntax, e.g. {{msg:Stub}}, to the
new syntax, e.g. {{Stub}}, download an XML dump file (pages-articles) from
http://download.wikimedia.org, then use this command:

    python replace.py -xml -regex "{{msg:(.*?)}}" "{{\\1}}"

If you have a dump called foobar.xml and want to fix typos in articles, e.g.
Errror -> Error, use this:

    python replace.py -xml:foobar.xml "Errror" "Error" -namespace:0

If you have a page called 'John Doe' and want to fix the format of ISBNs, use:

    python replace.py -page:John_Doe -fix:isbn

This command will change 'referer' to 'referrer', but not in pages which
talk about HTTP, where the typo has become part of the standard:

    python replace.py referer referrer -file:typos.txt -excepttext:HTTP
"""

#
# TODO:
#
# OK Aufträge, also welche Vorlage durch welche ersetzt wird von wiki Seite annehmen
#    mit Sicherheit (nicht jeder darf Aufträge geben!! SEHR RESTRIKTIV SEIN!!! am
#    anfang nur aufträge von mir akzeptieren...)
#    SIEHE AUCH: http://de.wikipedia.org/wiki/Wikipedia:Tellerrand#Orgullobot
#    AKZEPTIERTE AUFTRäGE: 'DrTrigon' muss letzter Bearbeiter in History sein mit Summary
#    'Bot: exec' siehe "conf['security']"
#
# OK Aufträge "simulieren" können mit Ausgabe von Hinweis (bzw. Liste mit nötigen Aenderungen)
#    SIMULIEREN MIT: 'Bot sim' (dokumentieren in wiki!!) mit resultat in wiki seite
#
# OK ausgabe von simulation(s-daten) nicht ganz fehlerfrei
#
# OK Ausgeführe Aufträge auf der Seite markieren (auch damit sie nicht nochmals aus-
#    geführt werden) / bei sicherheit edits von 'DrTrigonBot' auch akzeptieren...
#    [in confbot beim einlesen zeilennummern speichern für spätere modifikation]
#
# OK findet jetzt immer nur den 1sten eintrag, obschon er DEN NICHT mehr finden dürfte (abgleich
#    mit ref text darunter ok?!) / security muss noch so verbessert werden, dass es eine liste
#    von usern verarbeitet
#
#  - abgleich zw. einträgen und ref text darunter ok?! glaube kaum!!!
#    MUSS DERZEIT IMMER ALLE EINTRAEGE AUF SEITE ABARBEITEN (d.h. keine (erledigt) dürfen dabei sein!)
#
#  - log von richtigem run erzeugen und ausgeben (wohin? wiki?)
#
#  - Bot automatisch und durchgehend (24h am Tag) lauffähig machen und dann auf Server
#    zu restlichen Bot Scripts packen!!
#
#  - mehr interaktivität (ausschliessen von seiten; ist ja schon vorhanden in replace.py)
#    also mehr parameter und konfigurationsmöglichkeiten / ideal wäre eben auch dass er
#    zu grosse aufträge (> 50) nur simuliert und zurückweist (wenn nicht zuvor schon sim-
#    uliert; zur sicherheit) so führt er sie erst nach sim./erneuter aufforderung aus...
#    [Aufträge zuerst "simulieren" wenn mehr als 50 Aenderungen zurückweisen, mit Hinweis
#    (und dann ev. auf 'force', bestätigung oder erneute aufforderung (vorh. sim. reicht))]
#
#  - möglichkeit/befehl um vorlagen umparametrisieren zu können
#
#  - gross-/kleinschreibung...
#
#  - problem mit summary text für vorlagen mit parameter...!!
#
#  - writeDoneMarker: nur schreiben wenn änderungen vorhanden
#

#
# (C) Daniel Herding & the Pywikipediabot Team, 2004-2008
# (C) Dr. Trigon, 2009
#
# Distributed under the terms of the MIT license.
#

from __future__ import generators
import sys, re, time
import wikipedia, pagegenerators, catlib, config
import editarticle
import webbrowser
import wikipediaAPI, cStringIO

# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'sum_disc.py'
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
#
__version__='$Id: replace_tmpl.py 0.1.0013/6374 2009-02-19 01:48:35Z drtrigon $'
#

# Imports predefined replacements tasks from fixes.py
import fixes

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
    '&fixes-help;': fixes.help,
}

#__version__='$Id: replace.py 6374 2009-02-19 01:48:35Z nicdumz $'

# Vars
#
conf = {	# unicode values
		'replacelist':		u'Benutzer:DrTrigonBot/Simon sagt',
		'sim_output':		u'Benutzer:DrTrigonBot/Simulation',

#		'security':		(u'DrTrigon', u'Bot: exec'),
		'security':		([u'DrTrigon', u'DrTrigonBot'], u'Bot: exec'),
}

# debug tools
debug = { 'write2wiki': True, 'sim2wiki': True }	# operational mode (default)
#debug = { 'write2wiki': False, 'sim2wiki': False }	# no write at all!
#debug = { 'write2wiki': False, 'sim2wiki': True }	# write only sim results

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# below.`v
msg = {
    'ar': u'%s روبوت : استبدال تلقائي للنص',
    'ca': u'Robot: Reemplaçament automàtic de text %s',
    'cs': u'Robot automaticky nahradil text: %s',
    'de': u'Bot: Automatisierte Textersetzung %s',
    'el': u'Ρομπότ: Αυτόματη αντικατάσταση κειμένου %s',
    'en': u'Robot: Automated text replacement %s',
    'es': u'Robot: Reemplazo automático de texto %s',
    'fa': u'ربات: تغییر خودکار متن %s',
    'fr': u'Bot : Remplacement de texte automatisé %s',
    'he': u'בוט: החלפת טקסט אוטומטית %s',
    'hu': u'Robot: Automatikus szövegcsere %s',
    'ia': u'Robot: Reimplaciamento automatic de texto %s',
    'id': u'Bot: Penggantian teks otomatis %s',
    'is': u'Vélmenni: breyti texta %s',
    'it': u'Bot: Sostituzione automatica %s',
    'ja': u'ロボットによる: 文字置き換え %s',
    'ka': u'რობოტი: ტექსტის ავტომატური შეცვლა %s',
    'kk': u'Бот: Мәтінді өздікті алмастырды: %s',
    'ksh': u'Bot: hät outomatesch Täx jetuusch: %s',
    'lt': u'robotas: Automatinis teksto keitimas %s',
    'nds': u'Bot: Text automaatsch utwesselt: %s',
    'nds-nl': u'Bot: autematisch tekse vervungen %s',
    'nl': u'Bot: automatisch tekst vervangen %s',
    'nn': u'robot: automatisk teksterstatning: %s',
    'no': u'robot: automatisk teksterstatning: %s',
    'pl': u'Robot automatycznie zamienia tekst %s',
    'pt': u'Bot: Mudança automática %s',
    'ru': u'Робот: Автоматизированная замена текста %s',
    'sr': u'Бот: Аутоматска замена текста %s',
    'sv': u'Bot: Automatisk textersättning: %s',
    'zh': u'機器人:執行文字代換作業 %s',
}


class XmlDumpReplacePageGenerator:
    """
    Iterator that will yield Pages that might contain text to replace.

    These pages will be retrieved from a local XML dump file.
    Arguments:
        * xmlFilename  - The dump's path, either absolute or relative
        * xmlStart     - Skip all articles in the dump before this one
        * replacements - A list of 2-tuples of original text (as a
                         compiled regular expression) and replacement
                         text (as a string).
        * exceptions   - A dictionary which defines when to ignore an
                         occurence. See docu of the ReplaceRobot
                         constructor below.

    """
    def __init__(self, xmlFilename, xmlStart, replacements, exceptions):
        self.xmlFilename = xmlFilename
        self.replacements = replacements
        self.exceptions = exceptions
        self.xmlStart = xmlStart
        self.skipping = bool(xmlStart)

        self.excsInside = []
        if self.exceptions.has_key('inside-tags'):
            self.excsInside += self.exceptions['inside-tags']
        if self.exceptions.has_key('inside'):
            self.excsInside += self.exceptions['inside']
        import xmlreader
        self.site = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlFilename)
        self.parser = dump.parse()

    def __iter__(self):
        try:
            for entry in self.parser:
                if self.skipping:
                    if entry.title != self.xmlStart:
                        continue
                    self.skipping = False
                if not self.isTitleExcepted(entry.title) \
                        and not self.isTextExcepted(entry.text):
                    new_text = entry.text
                    for old, new in self.replacements:
                        new_text = wikipedia.replaceExcept(new_text, old, new, self.excsInside, self.site)
                    if new_text != entry.text:
                        yield wikipedia.Page(self.site, entry.title)
        except KeyboardInterrupt:
            try:
                if not self.skipping:
                    wikipedia.output(
                        u'To resume, use "-xmlstart:%s" on the command line.'
                        % entry.title)
            except NameError:
                pass

    def isTitleExcepted(self, title):
        if self.exceptions.has_key('title'):
            for exc in self.exceptions['title']:
                if exc.search(title):
                    return True
        if self.exceptions.has_key('require-title'):
            for req in self.exceptions['require-title']:
                if not req.search(title): # if not all requirements are met:
                    return True

        return False

    def isTextExcepted(self, text):
        if self.exceptions.has_key('text-contains'):
            for exc in self.exceptions['text-contains']:
                if exc.search(text):
                    return True
        return False


class ReplaceRobot:
    """
    A bot that can do text replacements.
    """
    def __init__(self, generator, replacements, exceptions={},
                 acceptall=False, allowoverlap=False, recursive=False,
                 addedCat=None, sleep=None):
        """
        Arguments:
            * generator    - A generator that yields Page objects.
            * replacements - A list of 2-tuples of original text (as a
                             compiled regular expression) and replacement
                             text (as a string).
            * exceptions   - A dictionary which defines when not to change an
                             occurence. See below.
            * acceptall    - If True, the user won't be prompted before changes
                             are made.
            * allowoverlap - If True, when matches overlap, all of them are
                             replaced.
            * addedCat     - If set to a value, add this category to every page
                             touched.

        Structure of the exceptions dictionary:
        This dictionary can have these keys:

            title
                A list of regular expressions. All pages with titles that
                are matched by one of these regular expressions are skipped.
            text-contains
                A list of regular expressions. All pages with text that
                contains a part which is matched by one of these regular
                expressions are skipped.
            inside
                A list of regular expressions. All occurences are skipped which
                lie within a text region which is matched by one of these
                regular expressions.
            inside-tags
                A list of strings. These strings must be keys from the
                exceptionRegexes dictionary in wikipedia.replaceExcept().

        """
        self.generator = generator
        self.replacements = replacements
        self.exceptions = exceptions
        self.acceptall = acceptall
        self.allowoverlap = allowoverlap
        self.recursive = recursive
        if addedCat:
            site = wikipedia.getSite()
            cat_ns = site.category_namespaces()[0]
            self.addedCat = wikipedia.Page(site,
                                           cat_ns + ':' + addedCat)
        self.sleep = sleep

    def isTitleExcepted(self, title):
        """
        Iff one of the exceptions applies for the given title, returns True.
        """
        if self.exceptions.has_key('title'):
            for exc in self.exceptions['title']:
                if exc.search(title):
                    return True
        if self.exceptions.has_key('require-title'):
            for req in self.exceptions['require-title']:
                if not req.search(title):
                    return True
        return False

    def isTextExcepted(self, original_text):
        """
        Iff one of the exceptions applies for the given page contents,
        returns True.
        """
        if self.exceptions.has_key('text-contains'):
            for exc in self.exceptions['text-contains']:
                if exc.search(original_text):
                    return True
        return False

    def doReplacements(self, original_text):
        """
        Returns the text which is generated by applying all replacements to
        the given text.
        """
        new_text = original_text
        exceptions = []
        if self.exceptions.has_key('inside-tags'):
            exceptions += self.exceptions['inside-tags']
        if self.exceptions.has_key('inside'):
            exceptions += self.exceptions['inside']
        for old, new in self.replacements:
            if self.sleep != None:
                time.sleep(self.sleep)
            new_text = wikipedia.replaceExcept(new_text, old, new, exceptions,
                                               allowoverlap=self.allowoverlap)
        return new_text

    def run(self, simulate = None):
        """
        Starts the robot.
        """
        # Run the generator which will yield Pages which might need to be
        # changed.
        for page in self.generator:
            if (page.title() == conf['replacelist']): continue

            if self.isTitleExcepted(page.title()):
                wikipedia.output(
                    u'Skipping %s because the title is on the exceptions list.'
                    % page.aslink())
                continue
            try:
                # Load the page's text from the wiki
                original_text = page.get(get_redirect=True)
                if not page.canBeEdited():
                    wikipedia.output(u"You can't edit page %s"
                                     % page.aslink())
                    continue
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % page.aslink())
                continue
            new_text = original_text
            while True:
                if self.isTextExcepted(new_text):
                    wikipedia.output(
    u'Skipping %s because it contains text that is on the exceptions list.'
                        % page.aslink())
                    break
                new_text = self.doReplacements(new_text)
                if new_text.strip().replace('\r\n', '\n') == original_text.strip().replace('\r\n', '\n'):
                    wikipedia.output('No changes were necessary in %s'
                                     % page.aslink())
                    break
                if self.recursive:
                    newest_text = self.doReplacements(new_text)
                    while (newest_text!=new_text):
                        new_text = newest_text
                        newest_text = self.doReplacements(new_text)
                if hasattr(self, "addedCat"):
                    cats = page.categories(nofollow_redirects=True)
                    if self.addedCat not in cats:
                        cats.append(self.addedCat)
                        new_text = wikipedia.replaceCategoryLinks(new_text,
                                                                  cats)
                # Show the title of the page we're working on.
                # Highlight the title in purple.
                if simulate:
                    simulate.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                                     % page.title())
                    simulate.showDiff(original_text, new_text)
                else:
                    wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                                     % page.title())
                    wikipedia.showDiff(original_text, new_text)
                if self.acceptall:
                    break
                choice = wikipedia.inputChoice(
                            u'Do you want to accept these changes?',
                            ['Yes', 'No', 'Edit', 'open in Browser', 'All', "Quit"],
                            ['y', 'N', 'e', 'b', 'a', 'q'], 'N')
                if choice == 'e':
                    editor = editarticle.TextEditor()
                    as_edited = editor.edit(original_text)
                    # if user didn't press Cancel
                    if as_edited and as_edited != new_text:
                        new_text = as_edited
                    continue
                if choice == 'b':
                    webbrowser.open("http://%s%s" % (
                        page.site().hostname(),
                        page.site().nice_get_address(page.title())
                    ))
                    wikipedia.input("Press Enter when finished in browser.")
                    original_text = page.get(get_redirect=True, force=True)
                    new_text = original_text
                    continue
                if choice == 'q':
                    return
                if choice == 'a':
                    self.acceptall = True
                if choice == 'y':
                    if   simulate:
                        simulate.put_async(new_text)
                    elif debug['write2wiki']:
                        page.put_async(new_text)
                    else:
                        wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
                # choice must be 'N'
                break
            if self.acceptall and new_text != original_text:
                try:
                    if   simulate:
                        simulate.put(new_text)
                    elif debug['write2wiki']:
                        page.put(new_text)
                    else:
                        wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
                except wikipedia.EditConflict:
                    wikipedia.output(u'Skipping %s because of edit conflict'
                                     % (page.title(),))
                except wikipedia.SpamfilterError, e:
                    wikipedia.output(
                        u'Cannot change %s because of blacklist entry %s'
                        % (page.title(), e.url))
                except wikipedia.PageNotSaved, error:
                    wikipedia.output(u'Error putting page: %s'
                                     % (error.args,))
                except wikipedia.LockedPage:
                    wikipedia.output(u'Skipping %s (locked page)'
                                     % (page.title(),))

class ConfigRobot:
    """
    A bot that retrieves the config settings from wiki (only!).

    (a lot of code from sum_disc.py)
    """
    def __init__(self, ConfigPageTitle):
        '''
        constructor of ConfigRobot(), initialize needed vars
        '''

        offset = 10
        find_ptrn  = '^==(Bot|Bot sim): \{\{(.*?)\}\} nach \{\{(.*?)\}\}==$'
        index_ptrn = '==%s: {{%s}} nach {{%s}}=='

        # set config page
        #self.ConfigPage = wikipediaAPI.Page(wikipedia.getSite(), ConfigPageTitle)
        self.ConfigPage = wikipedia.Page(wikipedia.getSite(), ConfigPageTitle)

        # read config page
        wikipedia.output(u'\03{lightblue}Reading Wiki at %s...\03{default}' % self.ConfigPage.aslink())
        try:
            self._content = self.ConfigPage.get()
            #self._content = self.ConfigPage.getParsedContent()
        except (wikipedia.NoPage, wikipedia.IsRedirectPage):
            self._content = u''
        self._contentline = re.split(u'\n', self._content)

        # process config page
        #buf = re.split('\n', self._content)
        buf = self._contentline
        #print buf[9:-8]
        #text = buf[8:]
        text = buf[offset:]
        #print text

        buf = "\n"
        buf = re.findall('siehe (.*?) --', buf.join(text))
        infolist = []
        for item in buf:
            infolist.append( item )

        buf = "\n"
        #buf = re.findall('==(Bot|Bot sim): \{\{(.*?)\}\} nach \{\{(.*?)\}\}==', buf.join(text))
        buf = re.findall(find_ptrn, buf.join(text), re.M)
        #print buf
        self._cmdlist = []
        for i in range(len(buf)):
            item = buf[i][1:]
            cmd = buf[i][0]
            pos = text.index(index_ptrn % buf[i]) + offset
            # {{Vorlage:ABC}}
            # (<old-text>, <new-text>, <reason>, <page-ref>, <bot-cmd>, <config-pos>)
            item = ( self._convertEntry(item[0]), self._convertEntry(item[1]), '', self._convertEntry(item[0])[2:], cmd, pos )
            info = u'Ersetze Vorlage [[%s]] durch [[%s]], aufgrund von Auftrag %s' % (item[0][2:], item[1][2:], infolist[i])
            item = ( item[0], item[1], info, item[3], item[4], item[5] )
            self._cmdlist.append( item )
            # {{ABC}}
            # (<old-text>, <new-text>, <reason>, <page-ref>, <bot-cmd>, <config-pos>)
            item = ( re.sub(u'Vorlage:', u'', item[0]), re.sub(u'Vorlage:', u'', item[1]), info, item[3], cmd, pos )
            self._cmdlist.append( item )
        #print self._cmdlist

        return

    def _convertEntry(self, entry):
        if (entry[:2] == "[[") and (entry[-2:] == "]]"):
            entry = entry[2:-2]
        else:
            entry = re.sub('(\[\[)|(\]\])','',entry)
            entry = re.sub('\{\{!\}\}','|',entry)
        #return u'{{%s}}'%entry
        return u'{{%s'%entry

    def getCommands(self):
        '''
        return bot command list from wiki page
        '''
        return self._cmdlist

    def getSecurity(self):
        '''
        return result of security check of wiki page

        last edit must be from conf['security'][0] (default: u'DrTrigon') and
        edit comment must be conf['security'][0] (default: u'Bot: exec') for the
        check to be true.
        '''
        page = wikipediaAPI.PageFromPage(self.ConfigPage)
        #page = wikipediaAPI.Page(wikipedia.getSite(), item)
        try:	actual = page.getVersionHistory(revCount=1)[0]
        except:	pass

        secure = False
        for item in conf['security'][0]:
            secure = secure or (actual[2] == item)

        secure = secure and (actual[3] == conf['security'][1])

        #print actual[2:4]
        #return ( (actual[2] == conf['security'][0]) and (actual[3] == conf['security'][1]) )
        return secure

    def putSimulationResult(self, data, summary):
        '''
        write result of simulation to wiki page

        (most of the code from 'sum_disc.py')
        '''
        page = wikipedia.Page(wikipedia.getSite(), conf['sim_output'])

        wikipedia.output(u'\03{lightblue}Appending to Wiki on %s...\03{default}' % page.aslink())

        wikipedia.setAction(summary)

        try:
            #content = page.get() + u'\n\n' + data.decode('latin-1')
            content = page.get() + u'\n\n' + data.decode(config.textfile_encoding)
        except (wikipedia.NoPage, wikipedia.IsRedirectPage):
            #content = u'' + data.decode('latin-1')
            content = u'' + data.decode(config.textfile_encoding)
        #print content
        try:
            if debug['sim2wiki']:
                page.put(content)
            else:
                wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
        except wikipedia.SpamfilterError, error:
            wikipedia.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (page.aslink(), "error.url"))
        return

    def putDoneMarker(self, pos):
        '''
        gather modifications on config page

        (most of the code from 'sum_disc.py' and 'putSimulationResult(...)')
        '''
        self._contentline[pos] = self._contentline[pos][:-2] + u' (erledigt)=='
        #self._contentline[pos] = self._contentline[pos][:-2] + u' {{Erl.}}=='	# problem da AUCH '}}' am ende!!
        return

    def writeDoneMarker(self):
        '''
        write modifications to config page

        (most of the code from 'sum_disc.py' and 'putSimulationResult(...)')
        '''
        wikipedia.output(u'\03{lightblue}Modifing Wiki on %s...\03{default}' % self.ConfigPage.aslink())

        #wikipedia.setAction(u'DrTrigonBot: modified')
        wikipedia.setAction(conf['security'][1])

        try:
            buf = u'\n'
            #self.ConfigPage.put(buf.join(self._contentline))
            if debug['write2wiki']:
                self.ConfigPage.put(buf.join(self._contentline))
            else:
                wikipedia.output(u'\03{lightred}=== ! DEBUG MODE NOTHING WRITTEN TO WIKI ! ===\03{default}')
        except wikipedia.SpamfilterError, error:
            wikipedia.output(u'\03{lightred}SpamfilterError while trying to change %s: %s\03{default}' % (self.ConfigPage.aslink(), "error.url"))
        return

class SimulateRun:
    """
    A dummy writer class that log and counts all changes.
    """
    def __init__(self):
        self.log = []
        self.count = 0
        self._stderrbuf = None

    def put_async(self, text):
        '''
        put_async dummy
        '''
        self.log.append( ('put_async', self.count, text) )
        self.count += 1
        return

    def put(self, text):
        '''
        put dummy
        '''
        self.log.append( ('put', self.count, text) )
        self.count += 1
        return

    def _switchOutput(self):
        if self._stderrbuf:
            sys.stderr, self._stderrbuf = self._stderrbuf, None

            self._contents = self._output.getvalue()
            self._output.close()
            del self._output
        else:
            self._output = cStringIO.StringIO()

            self._stderrbuf, sys.stderr = sys.stderr, self._output
        return

    def showDiff(self, original_text, new_text):
        '''
        showDiff dummy
        (siehe wikipedia.py, config.py, terminal_interface.py)
        '''
        self._switchOutput()

        wikipedia.showDiff(original_text, new_text)

        self._switchOutput()

        self.log.append( ('showDiff', self.count, self._contents) )
        #self.count += 1
        return

    def output(self, text):
        '''
        output dummy
        (siehe showDiff dummy)
        '''
        self._switchOutput()

        wikipedia.output(text)

        self._switchOutput()

        self.log.append( ('output', self.count, self._contents) )
        #self.count += 1
        return

def prepareRegexForMySQL(pattern):
    pattern = pattern.replace('\s', '[:space:]')
    pattern = pattern.replace('\d', '[:digit:]')
    pattern = pattern.replace('\w', '[:alnum:]')

    pattern = pattern.replace("'", "\\" + "'")
    #pattern = pattern.replace('\\', '\\\\')
    #for char in ['[', ']', "'"]:
    #    pattern = pattern.replace(char, '\%s' % char)
    return pattern


def submain(old, new, info, ref, simulate = None, *args):
    add_cat = None
    gen = None
    # summary message
    summary_commandline = None
    # Array which will collect commandline parameters.
    # First element is original text, second element is replacement text.
    commandline_replacements = []
    # A list of 2-tuples of original text and replacement text.
    replacements = []
    # Don't edit pages which contain certain texts.
    exceptions = {
        'title':         [],
        'text-contains': [],
        'inside':        [],
        'inside-tags':   [],
        'require-title': [], # using a seperate requirements dict needs some
    }                        # major refactoring of code.

    # Should the elements of 'replacements' and 'exceptions' be interpreted
    # as regular expressions?
    #regex = False
    regex = True
    # Predefined fixes from dictionary 'fixes' (see above).
    fix = None
    # the dump's path, either absolute or relative, which will be used
    # if -xml flag is present
    xmlFilename = None
    useSql = False
    PageTitles = []
    # will become True when the user presses a ('yes to all') or uses the
    # -always flag.
    #acceptall = False
    acceptall = True
    # Will become True if the user inputs the commandline parameter -nocase
    caseInsensitive = False
    # Will become True if the user inputs the commandline parameter -dotall
    dotall = False
    # Will become True if the user inputs the commandline parameter -multiline
    multiline = False
    # Do all hits when they overlap
    allowoverlap = False
    # Do not recurse replacement
    recursive = False
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # Load default summary message.
    # BUG WARNING: This is probably incompatible with the -lang parameter.
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg))
    # Between a regex and another (using -fix) sleep some time (not to waste
    # too much CPU
    sleep = None

    # Read commandline parameters.
    for arg in wikipedia.handleArgs(*args):
        if arg == '-regex':
            regex = True
        elif arg.startswith('-xmlstart'):
            if len(arg) == 9:
                xmlStart = wikipedia.input(
                    u'Please enter the dumped article to start with:')
            else:
                xmlStart = arg[10:]
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(
                    u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
        elif arg =='-sql':
            useSql = True
        elif arg.startswith('-page'):
            if len(arg) == 5:
                PageTitles.append(wikipedia.input(
                                    u'Which page do you want to change?'))
            else:
                PageTitles.append(arg[6:])
        elif arg.startswith('-excepttitle:'):
            exceptions['title'].append(arg[13:])
        elif arg.startswith('-requiretitle:'):
            exceptions['require-title'].append(arg[14:])
        elif arg.startswith('-excepttext:'):
            exceptions['text-contains'].append(arg[12:])
        elif arg.startswith('-exceptinside:'):
            exceptions['inside'].append(arg[14:])
        elif arg.startswith('-exceptinsidetag:'):
            exceptions['inside-tags'].append(arg[17:])
        elif arg.startswith('-fix:'):
            fix = arg[5:]
        elif arg.startswith('-sleep:'):
            sleep = float(arg[7:])
        elif arg == '-always':
            acceptall = True
        elif arg == '-recursive':
            recursive = True
        elif arg == '-nocase':
            caseInsensitive = True
        elif arg == '-dotall':
            dotall = True
        elif arg == '-multiline':
            multiline = True
        elif arg.startswith('-addcat:'):
            add_cat = arg[len('addcat:'):]
        elif arg.startswith('-summary:'):
            wikipedia.setAction(arg[len('-summary:'):])
            summary_commandline = True
        elif arg.startswith('-allowoverlap'):
            allowoverlap = True
        else:
            if not genFactory.handleArg(arg):
                commandline_replacements.append(arg)

    if (len(commandline_replacements) % 2):
        raise wikipedia.Error, 'require even number of replacements.'
    elif (len(commandline_replacements) == 2 and fix == None):
        replacements.append((commandline_replacements[0],
                             commandline_replacements[1]))
        if summary_commandline == None:
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg )
                                % (' (-' + commandline_replacements[0] + ' +'
                                   + commandline_replacements[1] + ')'))
    elif (len(commandline_replacements) > 1):
        if (fix == None):
            for i in xrange (0, len(commandline_replacements), 2):
                replacements.append((commandline_replacements[i],
                                     commandline_replacements[i + 1]))
            if summary_commandline == None:
                pairs = [( commandline_replacements[i],
                           commandline_replacements[i + 1] )
                         for i in range(0, len(commandline_replacements), 2)]
                replacementsDescription = '(%s)' % ', '.join(
                    [('-' + pair[0] + ' +' + pair[1]) for pair in pairs])
                wikipedia.setAction(
                    wikipedia.translate(wikipedia.getSite(), msg )
                    % replacementsDescription)
        else:
           raise wikipedia.Error(
               'Specifying -fix with replacements is undefined')
    elif fix == None:
#        old = wikipedia.input(u'Please enter the text that should be replaced:')
#        old = u'[[%s]]' % repl_tmpl
#        old = u'{{%s}}' % repl_tmpl
#        new = wikipedia.input(u'Please enter the new text:')
#        new = new_tmpl
        change = '(-' + old + ' +' + new
        replacements.append((old, new))
#        while True:
#            old = wikipedia.input(
#u'Please enter another text that should be replaced, or press Enter to start:')
#            if old == '':
#                change = change + ')'
#                break
#            new = wikipedia.input(u'Please enter the new text:')
#            change = change + ' & -' + old + ' +' + new
#            replacements.append((old, new))
        if not summary_commandline == True:
            default_summary_message =  wikipedia.translate(wikipedia.getSite(), msg) % change
            wikipedia.output(u'The summary message will default to: %s'
                             % default_summary_message)
#            summary_message = wikipedia.input(
#u'Press Enter to use this default message, or enter a description of the\nchanges your bot will make:')
            #summary_message = u'Ersetze Vorlage [[%s]] durch [[%s]], aufgrund von Auftrag %s' % (old[2:], new[2:], info)
            summary_message = info
            if summary_message == '':
                summary_message = default_summary_message
            wikipedia.setAction(summary_message)
            wikipedia.output(u'The summary message will be: %s'
                             % summary_message)

    else:
        # Perform one of the predefined actions.
        try:
            fix = fixes.fixes[fix]
        except KeyError:
            wikipedia.output(u'Available predefined fixes are: %s'
                             % fixes.fixes.keys())
            return
        if fix.has_key('regex'):
            regex = fix['regex']
        if fix.has_key('msg'):
            wikipedia.setAction(
                wikipedia.translate(wikipedia.getSite(), fix['msg']))
        if fix.has_key('exceptions'):
            exceptions = fix['exceptions']
        if fix.has_key('nocase'):
            caseInsensitive = fix['nocase']
        replacements = fix['replacements']

    #Set the regular expression flags
    flags = re.UNICODE
    if caseInsensitive:
        flags = flags | re.IGNORECASE
    if dotall:
        flags = flags | re.DOTALL
    if multiline:
        flags = flags | re.MULTILINE

    # Pre-compile all regular expressions here to save time later
    for i in range(len(replacements)):
        old, new = replacements[i]
        if not regex:
            old = re.escape(old)
        oldR = re.compile(old, flags)
        replacements[i] = oldR, new

    for exceptionCategory in ['title', 'require-title', 'text-contains', 'inside']:
        if exceptions.has_key(exceptionCategory):
            patterns = exceptions[exceptionCategory]
            if not regex:
                patterns = [re.escape(pattern) for pattern in patterns]
            patterns = [re.compile(pattern, flags) for pattern in patterns]
            exceptions[exceptionCategory] = patterns

#    if xmlFilename:
#        try:
#            xmlStart
#        except NameError:
#            xmlStart = None
#        gen = XmlDumpReplacePageGenerator(xmlFilename, xmlStart,
#                                          replacements, exceptions)
#    elif useSql:
#        whereClause = 'WHERE (%s)' % ' OR '.join(
#            ["old_text RLIKE '%s'" % prepareRegexForMySQL(old.pattern)
#             for (old, new) in replacements])
#        if exceptions:
#            exceptClause = 'AND NOT (%s)' % ' OR '.join(
#                ["old_text RLIKE '%s'" % prepareRegexForMySQL(exc.pattern)
#                 for exc in exceptions])
#        else:
#            exceptClause = ''
#        query = u"""
#SELECT page_namespace, page_title
#FROM page
#JOIN text ON (page_id = old_id)
#%s
#%s
#LIMIT 200""" % (whereClause, exceptClause)
#        gen = pagegenerators.MySQLPageGenerator(query)
#    elif PageTitles:
#        pages = [wikipedia.Page(wikipedia.getSite(), PageTitle)
#                 for PageTitle in PageTitles]
#        gen = iter(pages)

    # Aufträge, also welche Vorlage durch welche ersetzt wird von wiki Seite annehmen
    #tmpl_page = wikipedia.Page(wikipedia.getSite(), old[2:-2])
    #tmpl_page = wikipedia.Page(wikipedia.getSite(), old[2:])
    tmpl_page = wikipedia.Page(wikipedia.getSite(), ref)
    gen = pagegenerators.ReferringPageGenerator(tmpl_page)
    #for item in gen:
    #    if (item.title() == conf['replacelist']): continue
    #    print item
    #return

    gen = genFactory.getCombinedGenerator(gen)
    if not gen:
        # syntax error, show help text from the top of this file
        wikipedia.showHelp('replace')
        return
    if xmlFilename:
        # XML parsing can be quite slow, so use smaller batches and
        # longer lookahead.
        preloadingGen = pagegenerators.PreloadingGenerator(gen,
                                            pageNumber=20, lookahead=100)
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber=60)
    bot = ReplaceRobot(preloadingGen, replacements, exceptions, acceptall, allowoverlap, recursive, add_cat, sleep)
    bot.run(simulate = simulate)

def main(*args):
    # get configuration/settings from ConfigRobot()
    confbot = ConfigRobot(conf['replacelist'])

    # check security needings
    if not confbot.getSecurity(): return

    # get jobs/command list
    cmdlist = confbot.getCommands()

    # execute bot commands
    sim = SimulateRun()
    sim_run = False
    #for item in cmdlist:
    for i in range(0, len(cmdlist), 2):	# in 'cmdlist' sind immer 2 ähnliche nacheinander (aufgrund des selben eintrages)
    # könnte hier in 2 verzweigen nicht in 'getCommands' oder iterator, der dann 'putDoneMarker' automatisch ausführt...
    # mit neuer 'putDoneMarker', 'writeDoneMarker' implementation können schon veränderte pos gemerkt und belassen werden...
    #for item in [cmdlist[1]]:
        item = cmdlist[i]
        (old, new, info, ref, cmd, pos) = item

        wikipedia.output(u'\03{lightgreen}* BOT COMMAND: %s\03{default}' % cmd)

        if   (cmd == u'Bot'):
            submain(old, new, info, ref, *args)

            item = cmdlist[i+1]
            (old, new, info, ref, cmd, pos) = item
            submain(old, new, info, ref, *args)
        elif (cmd == u'Bot sim'):
            submain(old, new, info, ref, simulate = sim, *args)
            sim_run = True

            item = cmdlist[i+1]
            (old, new, info, ref, cmd, pos) = item
            submain(old, new, info, ref, simulate = sim, *args)

        confbot.putDoneMarker( pos )

    confbot.writeDoneMarker()

    if sim_run:
        log = []
        now = time.strftime("%d %b %Y (%H:%M:%S)", time.gmtime())
        log.append('== Simulation vom %s ==\n' % now)
        for item in sim.log:
            if (item[0] == 'put'): continue
            if (item[0] == 'output'): log.append('')
            #print item[2]
            a = item[2]
            a = re.sub('\n+(\x1b\[0m)+', '', a)					# pre
            a = re.sub('\x1b\[35;1m', '<span style="color:magenta">', a)	# <span>
            a = re.sub('\x1b\[35;1m', '<span style="color:magenta">', a)	# <span>
            a = re.sub('\x1b\[0m', '</span>', a)				#
            a = re.sub('\x1b\[91;1m', '<span style="color:red">', a)		#
            a = re.sub('\x1b\[92;1m', '<span style="color:green">', a)		#
            a = re.sub('<<<', '<<< <br>', a)					# <br>
            a = re.sub('\n<span', '<br>\n<span', a)				#
            a = re.sub('\{\{', '<tt><nowiki>{{</nowiki></tt>', a)		# {{
            a = re.sub('\}\}', '<tt><nowiki>}}</nowiki></tt>', a)		# }}
            a = re.sub('\n{2,}', '', a)						# more than one '\n' -> ''
            a = re.sub('>>> <span style="color:magenta">', '>>> [[', a)		# heading to link
            a = re.sub('</span> <<<', ']] <<<', a)				#
            log.append(a)
        if len(log) > 0:
            a = '\n'
            confbot.putSimulationResult( a.join(log), u'Simulation vom %s' % now )
            #print a.join(log[:20])
            #print (a.join(log[:20]),)

    #if (sim.count > 50):
    #    print "%s > 50 CHANGES, ARE YOU SURE YOU WANT TO EXECUTE THIS?" % sim.count
    #    return
    # wäre praktisch, aber Simulation wird nicht immer ausgeführt, so wie der code jetzt ist...

    return

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
