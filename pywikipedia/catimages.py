#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
EXPERIMENTAL BOT SCRIPT DERIVED FROM 'checkimages.py' and should use 'catlib.py'
...

Script to check recently uploaded files. This script checks if a file
description is present and if there are other problems in the image's description.

This script will have to be configured for each language. Please submit
translations as addition to the pywikipediabot framework.

Everything that needs customisation is indicated by comments.

This script understands the following command-line arguments:

-limit              The number of images to check (default: 80)

-duplicates[:#]     Checking if the image has duplicates (if arg, set how many
                    rollback wait before reporting the image in the report
                    instead of tag the image) default: 1 rollback.

-duplicatesreport   Report the duplicates in a log *AND* put the template in
                    the images.

-sendemail          Send an email after tagging.

-break              To break the bot after the first check (default: recursive)

-time[:#]           Time in seconds between repeat runs (default: 30)

-wait[:#]           Wait x second before check the images (default: 0)

-start[:#]          Start already form File:[:#] or if no file given resume
                    last run.

-cat[:#]            Use a category as generator

-untagged[:#]       Use daniel's tool as generator:
                    http://toolserver.org/~daniel/WikiSense/UntaggedImages.php

-nologerror         If given, this option will disable the error that is risen
                    when the log is full.

-noguesses          If given, this option will disable all guesses (which are
                    less reliable than true searches).


"""

#
# (C) Kyle/Orgullomoore, 2006-2007 (newimage.py)
# (C) Pywikipedia team, 2007-2011 (checkimages.py)
# (C) DrTrigon, 2012
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re, time, urllib, urllib2, os, locale, sys, datetime
import wikipedia as pywikibot
import config, pagegenerators, catlib, query, userlib
import checkimages

locale.setlocale(locale.LC_ALL, '')


# debug tools
# (look at 'bot_control.py' for more info)
debug = []                       # no write, all users
#debug.append( 'write2wiki' )    # write to wiki (operational mode)
#debug.append( 'code' )          # code debugging


###############################################################################
# <--------------------------- Change only below! --------------------------->#
###############################################################################

# NOTE: in the messages used by the Bot if you put __botnick__ in the text, it
# will automatically replaced with the bot's nickname.

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = [u'commons',]

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project.
################################################################################
# <--------------------------- Change only above! ---------------------------> #
################################################################################

#tmpl_FileContentsByBot = u"""{{FileContentsByBot
#| botName = %(botName)s
#<!--| dimX    = ?-->   <!-- is this REALLY needed...?? -->
#<!--| dimY    = ?-->   <!-- is this REALLY needed...?? -->
#|
#%(items)s
#}}"""
tmpl_FileContentsByBot = u"""}}
{{FileContentsByBot
| botName = ~~~
<!--| dimX    = ?-->   <!-- is this REALLY needed...?? -->
<!--| dimY    = ?-->   <!-- is this REALLY needed...?? -->
|"""

# TODO: auto-generate this list during bot run, i.e. notify about NEW templates added
#tmpl_available_spec = [ u'Unidentified people', u'Brown' ]
tmpl_available_spec = []


# Other common useful functions
def printWithTimeZone(message):
    """ Function to print the messages followed by the TimeZone encoded
    correctly.

    """
    if message[-1] != ' ':
        message = '%s ' % unicode(message)
    if locale.getlocale()[1]:
        time_zone = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()), locale.getlocale()[1])
    else:
        time_zone = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
    pywikibot.output(u"%s%s" % (message, time_zone))

class Global(object):
    # default environment settings
    # Command line configurable parameters
    repeat = True            # Restart after having check all the images?
    limit = 80               # How many images check?
    time_sleep = 30          # How many time sleep after the check?
    waitTime = 0             # How many time sleep before the check?
    normal = False           # Check the new images or use another generator?
    untagged = False         # Use the untagged generator
    duplicatesActive = False # Use the duplicate option
    duplicatesReport = False # Use the duplicate-report option
    sendemailActive = False  # Use the send-email
    logFullError = True      # Raise an error when the log is full
    useGuesses = True        # Use guesses which are less reliable than true searches


# EXPERIMENTAL BOT SCRIPT DERIVED FROM 'checkimages.py' and should use 'catlib.py'
class main(checkimages.main):
#    def __init__(self, site, logFulNumber = 25000, sendemailActive = False,
#                 duplicatesReport = False, logFullError = True): pass
#    def setParameters(self, imageName, timestamp, uploader): pass
#    def report(self, newtext, image_to_report, notification=None, head=None,
#               notification2 = None, unver=True, commTalk=None, commImage=None): pass

    def load_licenses(self):
        pywikibot.output(u'\n\t...Listing the procedures available...\n')
        for item in dir(self):
            if ('_search' in item) or ('_guess' in item) or ('_collect' in item):
                pywikibot.output( item )
        return []

    def downloadImage(self):
        self.image_filename  = os.path.split(self.image.fileUrl())[-1]
        if pywikibot.debug:
            self.image_filename = "Ali_1_-_IMG_1378.jpg"
            #self.image_filename = "Gyorche_Petrov_Todor_Alexandrov_Andrey_Lyapchev_Simeon_Radev_Stamatov_and_others.jpg"
        self.image_path      = urllib2.quote(os.path.join('cache', self.image_filename[-128:]))
        
        image_path_JPEG      = self.image_path.split(u'.')
        self.image_path_JPEG = u'.'.join(image_path_JPEG[:-1]+[u'jpg'])
        
        if os.path.exists(self.image_path):
            return

        maxtries = 5
        while maxtries:
            maxtries -= 1
            
            pywikibot.get_throttle()
#            f, data = self.site.getUrl(self.image.fileUrl(), no_hostname=True, back_response=True)
            # !!! CHEAP HACK TO GET IT WORKING -> NEEDS PATCH IN 'getUrl' upstream !!!
            # (prevent unicode encoding at end or allow to re-read in back_response)
            # (this will be useful for 'subster' also; merge several get modes there)
            try:
                req = urllib2.Request(self.image.fileUrl(), None, {})
                f = pywikibot.MyURLopener.open(req)
                data = f.read()
                break
            except urllib2.URLError:
                pywikibot.output( u"Error downloading data: retrying in 60 secs." )
                time.sleep(60.)
        if not maxtries:
            raise pywikibot.exceptions.NoPage(u'MaxTries reached; skipping page!')

        f = open(self.image_path, 'wb')
        f.write( data )
        f.close()

        try:
            import Image
            im = Image.open(self.image_path) # might be png, gif etc, for instance
            #im.thumbnail(size, Image.ANTIALIAS) # size is 640x480
            im.convert('RGB').save(self.image_path_JPEG, "JPEG")
        except:
            self.image_path_JPEG = self.image_path

    # LOOK ALSO AT: checkimages.main.checkStep
    # (and category scripts/bots too...)
    def checkStep(self):
        #print self.image_path
        pywikibot.output(self.image.title())

        for attr in ['_result_classify', '_result_detectFaces', '_result_detectcolor']:
            if hasattr(self, attr):
                delattr(self, attr)

        self._result_info  = []
        self._result_check = []

        # use information collectors for generic data (rel = 1.0)
        for item in dir(self):
            if '_collect' in item:
                (cat, result, rel) = self.__class__.__dict__[item](self)
                #print cat, result, len(result)
                if result:
                    self._result_info.append( (cat, result, rel) )

        # use explicit searches for classification (rel = ?)
        for item in dir(self):
            if '_search' in item:
                (cat, result, rel) = self.__class__.__dict__[item](self)
                #print cat, result, len(result)
                if result:
                    self._result_check.append( (cat, result, rel) )

        # use guesses for unreliable classification (rel = 0.1)
        if not gbv.useGuesses:
            return self._result_check
        for item in dir(self):
            if '_guess' in item:
                (cat, result, rel) = self.__class__.__dict__[item](self)
                #print cat, result, len(result)
                if result:
                    self._result_check.append( (cat, result, rel) )

        return self._result_check

    def tag_image(self, put = False):
        if not self._result_check:
            self.clean_cache()
            return u""

        pywikibot.get_throttle()
        content = self.image.get()

        if gbv.useGuesses:
            thrshld = 0.1
        else:
            thrshld = 0.75

        report_topage = False
        ret  = []
        tags = set([])
        ret.append( u"" )
        ret.append( u"== [[:%s]] ==" % self.image.title() )
        ret.append( u'<div style="position:relative;">' )
        ret.append( u"[[%s|200px]]" % self.image.title() )
        #ret.append( u"[[%s]]" % self.image.title() )
        imaganot_done = False
        content = self.append_to_template(content, u"Information", tmpl_FileContentsByBot)
        for i, item in enumerate(self._result_check):
            (cat, res, rel) = item
            report = (rel >= thrshld)
            report_topage = report_topage or report

            if not i:   # not very nice; if e.g. a color like 'Black' is first, nothing will be done!!!
                if (cat in [u'Faces', u'Groups', u'Unidentified people']):
                    marker = self.make_markerblock(item, 200.)
                    ret.append( marker )
                ret.append( u"</div>" )

            info   = self.make_infoblock(item)

# TODO: WHAT CATEGORY/-IES TO USE HERE?!?
            ret.append( u"=== [[:Category:%s]] [[File:%s|16px]] ===" % (cat, {True: 'ButtonGreen.svg', False: 'ButtonRed.svg'}[report]) )
#            ret.append( u"=== [[:Category:%s (bot tagged)]] ===" % cat )
            ret.append( tmpl_FileContentsByBot[3:] + info + u"\n}}" )

            if report:
                tags.add( u"[[:Category:%s]]" % cat )
#                tags.add( u"%s (bot tagged)" % cat )
                content = self.add_category(content, u"Category:%s" % cat)
#                content = self.add_category(content, u"Category:%s (bot tagged)" % cat)
                if info:
                    content = self.append_to_template(content, u"FileContentsByBot", info)
#                if (cat in [u'Faces', u'Groups', u'Unidentified people']) and (not imaganot_done):
#                    marker  = self.make_ImageAnnotatorBlock(item)
#                    content = self.add_template(content, marker, raw=True)
#                    imaganot_done = True

        # again the same code as before but for other list
        # (HACKY; should be done more clever!!)
        for item in self._result_info:
            (cat, res, rel) = item

            info   = self.make_infoblock(item)

# TODO: WHAT CATEGORY/-IES TO USE HERE?!?
            ret.append( u"=== [[:Category:%s]] ===" % cat )
#            ret.append( u"=== [[:Category:%s (bot tagged)]] ===" % cat )
            ret.append( tmpl_FileContentsByBot[3:] + info + u"\n}}" )

            if report_topage:
                tags.add( u"[[:Category:%s]]" % cat )
#                tags.add( u"%s (bot tagged)" % cat )
                content = self.add_category(content, u"Category:%s" % cat)
#                content = self.add_category(content, u"Category:%s (bot tagged)" % cat)
                if info:
                    # works multiple times
                    content = self.append_to_template(content, u"FileContentsByBot", info)

        if report_topage:
            tags.add( u"[[:Category:Categorized by bot]]" )
            content = self.add_category(content, u"Category:Categorized by bot")
            #content = self.add_template(content, u"Check categories", top=True)
            content = self.add_template(content, u"Check categories|year={{subst:#time:Y}}|month={{subst:#time:F}}|day={{subst:#time:j}}|category=[[Category:Categorized by bot]]", top=True)
            content = self.remove_category_or_template(content, u"Uncategorized")
            content = self.gather_category(content)
            print u"--- " * 20
            print content
            print u"--- " * 20
            if put:
                pywikibot.put_throttle()
                #self.image.put( content, comment="bot automatic categorization" )
                self.image.put( content, comment="bot automatic categorization; adding %s" % u", ".join(tags) )

        self.clean_cache()

        return u"\n".join( ret )

    def clean_cache(self):
        if os.path.exists(self.image_path):
            os.remove( self.image_path )
        if os.path.exists(self.image_path_JPEG):
            os.remove( self.image_path_JPEG )
        image_path_new = self.image_path_JPEG.replace(u"cache/", u"cache/0_DETECTED_")
        if os.path.exists(image_path_new):
            os.remove( image_path_new )

#    def make_infoblock(self, item):
#        (cat, res, rel) = item
#        if not res:
#            return u''
#
#        titles = res[0].keys()
#        if not titles:
#            return u''
#        result = []
#        result.append( u"{{(!}}" )
#        #result.append( u'{{(!}}style="background:%s;"' % {True: 'green', False: 'red'}[report] )
#        result.append( u"{{!}}-" )
#        for key in titles:
#            #if (key == 'Confidence'):
#            #    result.append( u"!%s [[File:%s|16px]]" % (key, {True: 'ButtonGreen.svg', False: 'ButtonRed.svg'}[report]) )
#            #else:
#            #    result.append( u"!%s" % key )
#            #    #result.append( u"{{!}}%s" % c )
#            result.append( u"!%s" % key )
#        result.append( u"{{!}}-" )
#        for item in res:
#            for key in titles:
#                result.append( u"{{!}}%s" % str(item[key]) )
#            result.append( u"{{!}}-" )
#        result.append( u"{{!)}}" )
#
#        return u"\n".join( result )

    def make_infoblock(self, item):
        (cat, res, rel) = item
        if not res:
            return u''

        generic = (cat not in tmpl_available_spec)
        titles = res[0].keys()
        if not titles:
            return u''

        result = []
        #result.append( u'{{(!}}style="background:%s;"' % {True: 'green', False: 'red'}[report] )
        if generic:
            result.append( u"{{FileContentsByBot/generic|name=%s|" % cat )
            buf = dict([ (key, []) for key in titles ])
            for item in res:
                for key in titles:
                    buf[key].append( str(item[key]) )
            for key in titles:
                result.append( u"  {{FileContentsByBot/generic|name=%s|value=%s}}" % (key, u"; ".join(buf[key])) )
        else:
            result.append( u"{{FileContentsByBot/%s|" % cat )
            for item in res:
                result.append( u"  {{FileContentsByBot/%s" % cat )
                for key in titles:
                    result.append( u"  | %s = %s" % (key, str(item[key])) )
                result.append( u"  }}" )
        result.append( u"}}" )

        return u"\n".join( result )

    def make_markerblock(self, item, size):
        import numpy

        (cat, res, rel) = item

        # same as in '_CVdetectObjects_Faces'
        colors = [ (0,0,255),
            (0,128,255),
            (0,255,255),
            (0,255,0),
            (255,128,0),
            (255,255,0),
            (255,0,0),
            (255,0,255) ]
        result = []
        for i, r in enumerate(res):
            color = list(colors[i%8])
            color.reverse()
            color = u"%02x%02x%02x" % tuple(color)
            
            #scale = r['size'][0]/size
            scale = self.image_size[0]/size
            f     = list(numpy.array(r['Face'])/scale)
            
            result.append( u'<div class="face-marker" style="position:absolute; left:%ipx; top:%ipx; width:%ipx; height:%ipx; border:2px solid #%s;"></div>' % tuple(f + [color]) )

            for e in r['Eyes']:
                e = list(numpy.array(e)/scale)

                result.append( u'<div class="eye-marker" style="position:absolute; left:%ipx; top:%ipx; width:%ipx; height:%ipx; border:2px solid #%s;"></div>' % tuple(e + [color]) )

        return u"\n".join( result )

    # http://commons.wikimedia.org/wiki/Help:Gadget-ImageAnnotator
    # (example: http://commons.wikimedia.org/wiki/File:13054_1198498614793_1598345855_498977_4395881_n.jpg)
    def make_ImageAnnotatorBlock(self, item):
        import numpy

        (cat, res, rel) = item

        # same as in '_CVdetectObjects_Faces'
        colors = [ (0,0,255),
            (0,128,255),
            (0,255,255),
            (0,255,0),
            (255,128,0),
            (255,255,0),
            (255,0,0),
            (255,0,255) ]
        result = []
        k = 0
        for i, r in enumerate(res):
            color = list(colors[i%8])
            color.reverse()
            color = u"%02x%02x%02x" % tuple(color)
            
            ##scale = r['size'][0]/size
            #scale = self.image_size[0]/size
            #f     = list(numpy.array(r['Face'])/scale)
            
            k += 1
            param = {'id': k, 'x': r['Face'][0], 'y': r['Face'][1], 
                     'w': r['Face'][2], 'h': r['Face'][3], 'dx': self.image_size[0], 'dy': self.image_size[1], 
                     'color': color}
            result.append( u'{{ImageNote|id=%(id)i|x=%(x)i|y=%(y)i|w=%(w)i|h=%(h)i|dimx=%(dx)i|dimy=%(dy)i|style=2}}' % param )
            result.append( u'{{LangSwitch' )
            result.append( u'|en=face' )
            result.append( u'}}' )
            #result.append( u'{{ImageNoteColors|inner=#%(color)s|active=#%(color)s}}' % param )
            result.append( u'{{ImageNoteEnd|id=%(id)i}}' % param )

            for j, e in enumerate(r['Eyes']):
                #e = list(numpy.array(e)/scale)

                k += 1
                param.update({'id': k, 'x': e[0], 'y': e[1], 
                              'w': e[2], 'h': e[3]})
                result.append( u'{{ImageNote|id=%(id)i|x=%(x)i|y=%(y)i|w=%(w)i|h=%(h)i|dimx=%(dx)i|dimy=%(dy)i|style=2}}' % param )
                result.append( u'{{LangSwitch' )
                result.append( u'|en=eye' )
                result.append( u'}}' )
                #result.append( u'{{ImageNoteColors|inner=#%(color)s|active=#%(color)s}}' % param )
                result.append( u'{{ImageNoteEnd|id=%(id)i}}' % param )

        return u"\n".join( result )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def remove_category_or_template(self, text, name):
        text = re.sub(u"[\{\[]{2}%s.*?[\}\]]{2}\n?" % name, u"", text)
        return text

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def gather_category(self, text):
        cat  = []
        page = []
        for line in text.split(u"\n"):
            if re.match(u"^\[\[Category:.*?\]\]$", line):
                cat.append( line )
            else:
                page.append( line )
        return u"\n".join( page + cat )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def add_category(self, text, name, top=False):
        if top:
            buf = [(u"[[%s]]" % name), text]
        else:
            buf = [text, (u"[[%s]]" % name)]
        return u"\n".join( buf )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def add_template(self, text, name, params={}, top=False, raw=False):
        if top:
            buf = [(u"{{%s}}" % name), text]
        else:
            if raw:
                buf = [text, name]
            else:
                buf = [text, (u"{{%s}}" % name)]
        return u"\n".join( buf )

    ## place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    #def change_category(self, text, oldname, newname):
    #    text = re.sub(u"\[\[%s\]\]" % oldname, u"\[\[%s\]\]" % newname, text)
    #    return text
    #
    #    import catlib
    ##    catlib.change_category(article, oldCat, newCat, comment=None, sortKey=None,
    ##                inPlace=False)
    #    catlib.add_category(self.image, category, comment=None, createEmptyPages=False)

    ## place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    #def change_template(self, text, name, params={}):
    ##    templates = pywikibot.textlib.extract_templates_and_params(text)
    ##    params = None
    ##    for t, p in templates:
    ##        if t == name:
    ##            params = p
    ##            break
    ##    if params == None:
    ##        raise
    ##    print params
    #
    #    pattern  = re.compile(u"\{\{%s.*?\n\s*\}\}" % name, flags=re.S)
    #    template = pattern.search(text).group()
    #
    #    for item in params:
    #        new = re.sub(u"\|%s\s*=\s*?\n" % item, u"|%s = %s\n" % (item, params[item]), template)
    #        if not (template == new):
    #            break
    #    if not (template == new):
    #        pass    # append param, since it was not used until here
    #    template = new
    #
    #    text = pattern.sub(template, text)
    #    return text

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def append_to_template(self, text, name, append):
        pattern  = re.compile(u"(\{\{%s.*?\n)(\s*\}\})" % name, flags=re.S)
        template = pattern.search(text).groups()
        
        template = u"".join( [template[0], append, u"\n", template[1]] )
        
        text = pattern.sub(template, text)
        return text

    ## Category:Faces
    #def _searchFaces(self):
    # Category:Unidentified people
    def _searchPeople(self):
        result = self._CVdetectObjects_Faces()
        result = [{'Confidence': item['confidence'],
                   'Face':       item['face'],
                   'Eyes':       item['eyes'],
                  } for item in result]
        relevance = max([item['Confidence'] for item in result] + [0.])

        return (u'Unidentified people', result, relevance)

    # Category:Groups
    def _searchGroups(self):
        result = self._CVdetectObjects_Faces()
        result = [{'Number':     (i+1),
                   'Face':       item['face'],
                   'Eyes':       item['eyes'], # if anyone has 1 eye it is in 'Category:Faces' BUT STILL NEEDED for ImageAnnotation in 'tag_image'
                  } for i, item in enumerate(result)]
        # ...could also create a bounding box for the whole group 'group'

        if not (len(result) > 1): # 5 should give 0.75 and get reported
            result    = []
            relevance = 0.
        else:
            relevance = 1 - 1./(len(result)-1)

        return (u'Groups', result, relevance)

    # Category:Unidentified people
    def _guessPeople(self):
        #result  = self._CVdetectObjects_Faces()
        #result += self._CVdetectObjects_People()

        return (u'Unidentified people', self._CVclassifyObjects_All('person'), 0.1)

    # .../opencv/samples/c/facedetect.cpp
    # http://opencv.willowgarage.com/documentation/python/genindex.html
    def _CVdetectObjects_Faces(self, confidence=0.5):
        """Converts an image to grayscale and prints the locations of any
           faces found"""
        # http://python.pastebin.com/m76db1d6b
        # http://creatingwithcode.com/howto/face-detection-in-static-images-with-python/
        # http://opencv.willowgarage.com/documentation/python/objdetect_cascade_classification.html
        # http://opencv.willowgarage.com/wiki/FaceDetection
        # http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
        # http://www.cognotics.com/opencv/servo_2007_series/part_4/index.html

        if hasattr(self, '_result_detectFaces'):
            return self._result_detectFaces

        import cv, cv2, numpy

        scale = 1.

        # https://code.ros.org/trac/opencv/browser/trunk/opencv_extra/testdata/gpu/haarcascade?rev=HEAD
        #nestedCascade = cv.Load(
        nestedCascade = cv2.CascadeClassifier(
          'opencv/haarcascades/haarcascade_eye_tree_eyeglasses.xml',
          #'opencv/haarcascades/haarcascade_eye.xml',
          )
        # http://tutorial-haartraining.googlecode.com/svn/trunk/data/haarcascades/
        #cascade       = cv.Load(
        cascade       = cv2.CascadeClassifier(
          'opencv/haarcascades/haarcascade_frontalface_alt.xml',
          )

        try:
            #image = cv.LoadImage(self.image_path)
            #img    = cv2.imread( self.image_path, 1 )
            img    = cv2.imread( self.image_path_JPEG, 1 )
            #image  = cv.fromarray(img)
            
            # !!! the 'scale' here IS RELEVANT FOR THE DETECTION RATE;
            # how small and how many features are detected as faces (or eyes)
            scale  = max([1., numpy.average(numpy.array(img.shape)[0:2]/500.)])
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return []
        except AttributeError:
            pywikibot.output(u'WARNING: unknown file type')
            return []

        self.image_size = (img.shape[1], img.shape[0])

        #detectAndDraw( image, cascade, nestedCascade, scale );
        # http://nullege.com/codes/search/cv.CvtColor
        #smallImg = cv.CreateImage( (cv.Round(img.shape[0]/scale), cv.Round(img.shape[1]/scale)), cv.CV_8UC1 )
        #smallImg = cv.fromarray(numpy.empty( (cv.Round(img.shape[0]/scale), cv.Round(img.shape[1]/scale)), dtype=numpy.uint8 ))
        smallImg = numpy.empty( (cv.Round(img.shape[1]/scale), cv.Round(img.shape[0]/scale)), dtype=numpy.uint8 )

        #cv.CvtColor( image, gray, cv.CV_BGR2GRAY )
        gray = cv2.cvtColor( img, cv.CV_BGR2GRAY )
        #cv.Resize( gray, smallImg, smallImg.size(), 0, 0, INTER_LINEAR )        
        smallImg = cv2.resize( gray, smallImg.shape, interpolation=cv2.INTER_LINEAR )
        #cv.EqualizeHist( smallImg, smallImg )
        smallImg = cv2.equalizeHist( smallImg )

        t = cv.GetTickCount()
        faces = numpy.array(cascade.detectMultiScale( smallImg,
            1.1, 2, 0
            #|cv.CV_HAAR_FIND_BIGGEST_OBJECT
            #|cv.CV_HAAR_DO_ROUGH_SEARCH
            |cv.CV_HAAR_SCALE_IMAGE,
            (30, 30) ))
        #faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
        #                           cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))
        #if faces:
        #    self._drawRect(faces) #call to a python pil
        t = cv.GetTickCount() - t
        #print( "detection time = %g ms\n" % (t/(cv.GetTickFrequency()*1000.)) )
        colors = [ (0,0,255),
            (0,128,255),
            (0,255,255),
            (0,255,0),
            (255,128,0),
            (255,255,0),
            (255,0,0),
            (255,0,255) ]
        result = []
        for i, r in enumerate(faces):
            color = colors[i%8]
            (rx, ry, rwidth, rheight) = r
            cx = cv.Round((rx + rwidth*0.5)*scale)
            cy = cv.Round((ry + rheight*0.5)*scale)
            radius = cv.Round((rwidth + rheight)*0.25*scale)
            cv2.circle( img, (cx, cy), radius, color, 3, 8, 0 )
            if nestedCascade.empty():
                continue
            dx, dy = cv.Round(img.shape[1]/5.), cv.Round(img.shape[0]/5.)
            (rx, ry, rwidth, rheight) = (max([rx-dx,0]), max([ry-dy,0]), min([rwidth+2*dx,img.shape[1]]), min([rheight+2*dy,img.shape[0]]))
            #smallImgROI = smallImg
            #print r, (rx, ry, rwidth, rheight)
            smallImgROI = smallImg[ry:(ry+rheight),rx:(rx+rwidth)]
            nestedObjects = nestedCascade.detectMultiScale( smallImgROI,
                1.1, 2, 0
                #|CV_HAAR_FIND_BIGGEST_OBJECT
                #|CV_HAAR_DO_ROUGH_SEARCH
                #|CV_HAAR_DO_CANNY_PRUNING
                |cv.CV_HAAR_SCALE_IMAGE,
                (30, 30) )
            c = (len(nestedObjects) + 2.) / 4.
            data = { 'face': tuple(numpy.int_(r*scale)), 
                     'eyes': [], 
                     'confidence': c, 
                     'size': self.image_size, }
            data['coverage'] = float(data['face'][2]*data['face'][3])/(data['size'][0]*data['size'][1])
            #if (c >= confidence):
            #    eyes = nestedObjects
            #    if not (type(eyes) == type(tuple())):
            #        eyes = tuple((eyes*scale).tolist())
            #    result.append( {'face': r*scale, 'eyes': eyes, 'confidence': c} )
            #print {'face': r, 'eyes': nestedObjects, 'confidence': c}
            for nr in nestedObjects:
                (nrx, nry, nrwidth, nrheight) = nr
                cx = cv.Round((rx + nrx + nrwidth*0.5)*scale)
                cy = cv.Round((ry + nry + nrheight*0.5)*scale)
                radius = cv.Round((nrwidth + nrheight)*0.25*scale)
                cv2.circle( img, (cx, cy), radius, color, 3, 8, 0 )
                data['eyes'].append( (cx-radius, cy-radius, 2*radius, 2*radius) )
            if (c >= confidence):
                result.append( data )

        # see '_drawRect'
        if result:
            #image_path_new = os.path.join('cache', '0_DETECTED_' + self.image_filename)
            image_path_new = self.image_path_JPEG.replace(u"cache/", u"cache/0_DETECTED_")
            cv2.imwrite( image_path_new, img )

        #return faces.tolist()
        self._result_detectFaces = result
        return result

    # .../opencv/samples/cpp/peopledetect.cpp
    def _CVdetectObjects_People(self):
        # needs an .so (C++) module since python bindings are missing, but
        # results do not look very probising, so forget about it...
        pass

    #def _drawRect(self, faces): #function to modify the img
    #    import Image, ImageDraw
    #    image_path_new = os.path.join('cache', '0_DETECTED_' + self.image_filename)
    #    im = Image.open(self.image_path)
    #    draw = ImageDraw.Draw(im)
    #    for f in faces:
    #        (x, y, width, height) = f[0]
    ##        (x, y, width, height) = f
    #        #print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
    #        (x1, y1, x2, y2) = (x, y, x+width, y+height)
    #        #print("[(%d,%d) -> (%d,%d)]" % (x1, y1, x2, y2))
    ##        draw.rectangle([x1,y1,x2,y2], outline=(255,0,0))
    #        draw.rectangle([x1,y1,x2,y2], outline="#ff0000")
    #    im.save(image_path_new)

    ## Category:Unidentified maps
    #def _guessMaps(self):
    #    return (u'Unidentified maps', self._CVclassifyObjects_All('maps'), 0.1)

    ## Category:Unidentified flags
    #def _guessFlags(self):
    #    return (u'Unidentified flags', self._CVclassifyObjects_All('flags'), 0.1)

    # Category:Unidentified plants
    def _guessPlants(self):
        return (u'Unidentified plants', self._CVclassifyObjects_All('pottedplant'), 0.1)

    ## Category:Unidentified coats of arms
    #def _guessCoatsOfArms(self):
    #    return (u'Unidentified coats of arms', self._CVclassifyObjects_All('coats of arms'), 0.1)

    ## Category:Unidentified buildings
    #def _guessBuildings(self):
    #    return (u'Unidentified buildings', self._CVclassifyObjects_All('buildings'), 0.1)

    # Category:Unidentified trains
    def _guessTrains(self):
        return (u'Unidentified trains', self._CVclassifyObjects_All('train'), 0.1)

    # Category:Unidentified automobiles
    def _guessAutomobiles(self):
        result  = self._CVclassifyObjects_All('bus')
        result += self._CVclassifyObjects_All('car')
        result += self._CVclassifyObjects_All('motorbike')
        return (u'Unidentified automobiles', result, 0.1)

    # Category:Unidentified buses
    def _guessBuses(self):
        return (u'Unidentified buses', self._CVclassifyObjects_All('bus'), 0.1)

    # .../opencv/samples/cpp/bagofwords_classification.cpp
    def _CVclassifyObjects_All(self, cls, confidence=0.5):
        """Uses the 'The Bag of Words model' for classification"""

        # prevent multiple execute of code below
        if not hasattr(self, '_result_classify'):
            # http://app-solut.com/blog/2011/07/the-bag-of-words-model-in-opencv-2-2/
            # http://app-solut.com/blog/2011/07/using-the-normal-bayes-classifier-for-image-categorization-in-opencv/
            # http://authors.library.caltech.edu/7694/
            # http://www.vision.caltech.edu/Image_Datasets/Caltech256/
            # http://opencv.itseez.com/modules/features2d/doc/object_categorization.html
            
            # http://www.morethantechnical.com/2011/08/25/a-simple-object-classifier-with-bag-of-words-using-opencv-2-3-w-code/
            #   source: https://github.com/royshil/FoodcamClassifier
            # http://app-solut.com/blog/2011/07/using-the-normal-bayes-classifier-for-image-categorization-in-opencv/
            #   source: http://code.google.com/p/open-cv-bow-demo/downloads/detail?name=bowdemo.tar.gz&can=2&q=

            # parts of code here should/have to be placed into e.g. a own
            # class in 'opencv/__init__.py' script/module
            
            trained = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
                       'car', 'cat', 'chair', 'cow', 'diningtable', 'dog',
                       'horse', 'motorbike', 'person', 'pottedplant', 'sheep',
                       'sofa', 'train', 'tvmonitor',]
            bowDescPath = '/home/ursin/data/toolserver/pywikipedia/opencv/data/bowImageDescriptors/000000.xml.gz'

            # https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/cpp/bagofwords_classification.cpp?rev=3714
            # stand-alone (in shell) for training e.g. with:
            #   BoWclassify /data/toolserver/pywikipedia/opencv/VOC2007 /data/toolserver/pywikipedia/opencv/data FAST SURF BruteForce | tee run.log
            #   BoWclassify /data/toolserver/pywikipedia/opencv/VOC2007 /data/toolserver/pywikipedia/opencv/data HARRIS SIFT BruteForce | tee run.log
            # http://experienceopencv.blogspot.com/2011/02/object-recognition-bag-of-keypoints.html
            import opencv
            import StringIO#, numpy

            if os.path.exists(bowDescPath):
                os.remove(bowDescPath)

            stdout = sys.stdout
            sys.stdout = StringIO.StringIO()
            #result = opencv.BoWclassify.main(0, '', '', '', '', '')
            result = opencv.BoWclassify.main(6, 
                                             '/data/toolserver/pywikipedia/opencv/VOC2007', 
                                             '/data/toolserver/pywikipedia/opencv/data', 
                                             'HARRIS',      # not important; given by training
                                             'SIFT',        # not important; given by training
                                             'BruteForce',  # not important; given by training
                                             [str(os.path.abspath(self.image_path).encode('latin-1'))])
            out = sys.stdout.getvalue()
            sys.stdout = stdout
            #print out
            try:
                if not result:
                    raise
                os.remove(bowDescPath)
            except:
                print "PROBLEM!!!"
                #raise
                self._result_classify = {}
                return []
            #result = list(numpy.abs(numpy.array(result)))
            (mi, ma) = (min(result), max(result))
            #for i in range(len(result)):
            #    print "%12s %.3f" % (trained[i], result[i]), ((result[i] == mi) or (result[i] == ma))

            # now make the algo working; confer also
            # http://www.xrce.xerox.com/layout/set/print/content/download/18763/134049/file/2004_010.pdf
            # http://people.csail.mit.edu/torralba/shortCourseRLOC/index.html

            self._result_classify = dict([ (trained[i], abs(r)) for i, r in enumerate(result) ])

        if (self._result_classify.get(cls, 0.0) >= confidence): # >= threshold 50%
            #result = [ {'confidence': self._result_classify[cls]} ] # ok
            result = [ {'confidence': -self._result_classify[cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found

        return result

    # Category:Black     (  0,   0,   0)
    # Category:Blue‎      (  0,   0, 255)
    # Category:Brown     (165,  42,  42)
    # Category:Green     (  0, 255,   0)
    # Category:Orange    (255, 165,   0)
    # Category:Pink‎      (255, 192, 203)
    # Category:Purple    (160,  32, 240)
    # Category:Red‎       (255,   0,   0)
    # Category:Turquoise ( 64, 224, 208)
    # Category:White‎     (255, 255, 255)
    # Category:Yellow    (255, 255,   0)
    # http://www.farb-tabelle.de/en/table-of-color.htm
    #def _collectColor(self):
    def _searchBlack(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Black' not in info):
            return (u'Black', [], 0.)

        return (u'Black', [info[u'Black']], info[u'Black'][u'Confidence'])

    def _searchBlue(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Blue‎' not in info):
            return (u'Blue‎', [], 0.)

        return (u'Blue‎', [info[u'Blue‎']], info[u'Blue‎'][u'Confidence'])

    def _searchBrown(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Brown' not in info):
            return (u'Brown', [], 0.)

        return (u'Brown', [info[u'Brown']], info[u'Brown'][u'Confidence'])

    def _searchGreen(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Green' not in info):
            return (u'Green', [], 0.)

        return (u'Green', [info[u'Green']], info[u'Green'][u'Confidence'])

    def _searchOrange(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Orange' not in info):
            return (u'Orange', [], 0.)

        return (u'Orange', [info[u'Orange']], info[u'Orange'][u'Confidence'])

    def _searchPink(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Pink‎' not in info):
            return (u'Pink‎', [], 0.)

        return (u'Pink‎', [info[u'Pink‎']], info[u'Pink‎'][u'Confidence'])

    def _searchPurple(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Purple' not in info):
            return (u'Purple', [], 0.)

        return (u'Purple', [info[u'Purple']], info[u'Purple'][u'Confidence'])

    def _searchRed(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Red‎' not in info):
            return (u'Red‎', [], 0.)

        return (u'Red‎', [info[u'Red‎']], info[u'Red‎'][u'Confidence'])

    def _searchTurquoise(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Turquoise' not in info):
            return (u'Turquoise', [], 0.)

        return (u'Turquoise', [info[u'Turquoise']], info[u'Turquoise'][u'Confidence'])

    def _searchWhite(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'White‎' not in info):
            return (u'White‎', [], 0.)

        return (u'White‎', [info[u'White‎']], info[u'White‎'][u'Confidence'])

    def _searchYellow(self):
        (result, info) = self._JSEGnPILdetectColorSegments()
        if (u'Yellow' not in info):
            return (u'Yellow', [], 0.)

        return (u'Yellow', [info[u'Yellow']], info[u'Yellow'][u'Confidence'])

    def _JSEGnPILdetectColorSegments(self):
        if not hasattr(self, '_result_detectcolor'):
            #from PIL import Image
            import Image
    
            try:
                i = Image.open(self.image_path)
            except IOError:
                pywikibot.output(u'WARNING: unknown file type')
                return ([], [])
            
            result = []
            info   = {}
            #h = i.histogram()   # average over WHOLE IMAGE
            hist = self._JSEGdetectColorSegmentsHist(i)  # split image into segments first
            for h, coverage in hist:
                data = self._DeltaEaverageColor(h)
                data['coverage'] = coverage

                # has to be in descending order since only 1 resolves (!)
                if   (data['coverage'] >= 0.40) and (data['delta_e']  <=  5.0):
                    data['confidence'] = 1.0
                elif (data['coverage'] >= 0.20) and (data['delta_e']  <= 15.0):
                    data['confidence'] = 0.75
                elif (data['coverage'] >= 0.10) and (data['delta_e']  <= 20.0):
                    data['confidence'] = 0.5
                else:
                    data['confidence'] = 0.1

                #result.append( data )

                if (info.get(data['color'], {'Confidence': 0.2})['Confidence'] < data['confidence']):
                    info[data['color']] = {'RGB': data['rgb'], 
                                           'Distance': u"%.3f" % data['delta_e'], 
                                           'Coverage': u"%.3f" % data['coverage'],
                                           'Confidence': data['confidence']}

            self._result_detectcolor = (result, info)

        return self._result_detectcolor

    # http://stackoverflow.com/questions/2270874/image-color-detection-using-python
    # https://gist.github.com/1246268
    # colormath-1.0.8/examples/delta_e.py, colormath-1.0.8/examples/conversions.py
    # http://code.google.com/p/python-colormath/
    # http://en.wikipedia.org/wiki/Color_difference
    # http://www.farb-tabelle.de/en/table-of-color.htm
    def _DeltaEaverageColor(self, h):
        # split into red, green, blue
        r = h[0:256]
        g = h[256:256*2]
        b = h[256*2: 256*3]
        
        # perform the weighted average of each channel:
        # the *index* 'i' is the channel value, and the *value* 'w' is its weight
        rgb = (
                sum( i*w for i, w in enumerate(r) ) / max(1, sum(r)),
                sum( i*w for i, w in enumerate(g) ) / max(1, sum(g)),
                sum( i*w for i, w in enumerate(b) ) / max(1, sum(b))
        )

        data = { #'histogram': h,
                 'rgb':       rgb, }

        from colormath.color_objects import RGBColor
        
        #print "=== RGB Example: RGB->LAB ==="
        # Instantiate an Lab color object with the given values.
        rgb = RGBColor(rgb[0], rgb[1], rgb[2], rgb_type='sRGB')
        # Show a string representation.
        #print rgb
        # Convert RGB to LAB using a D50 illuminant.
        lab = rgb.convert_to('lab', target_illuminant='D65')
        #print lab
        #print "=== End Example ===\n"
        
        # Reference color.
        #color1 = LabColor(lab_l=0.9, lab_a=16.3, lab_b=-2.22)
        # Color to be compared to the reference.
        #color2 = LabColor(lab_l=0.7, lab_a=14.2, lab_b=-1.80)
        color2 = lab

        # according to Categories available in Commons
        # (only using these color makes sense, detect other is useles...)
        colors = { u'Black':     (  0,   0,   0),
                   u'Blue':      (  0,   0, 255),
                   u'Brown':     (165,  42,  42),
                   u'Green':     (  0, 255,   0),
                   u'Orange':    (255, 165,   0),
                   u'Pink':      (255, 192, 203),
                   u'Purple':    (160,  32, 240),
                   u'Red':       (255,   0,   0),
                   u'Turquoise': ( 64, 224, 208),
                   u'White':     (255, 255, 255),
                   u'Yellow':    (255, 255,   0), }

        res = (1.E100, '')
        for c in colors:
            rgb = colors[c]
            rgb = RGBColor(rgb[0], rgb[1], rgb[2], rgb_type='sRGB')
            color1 = rgb.convert_to('lab', target_illuminant='D65')

            #print "== Delta E Colors =="
            #print " COLOR1: %s" % color1
            #print " COLOR2: %s" % color2
            #print "== Results =="
            #print " CIE2000: %.3f" % color1.delta_e(color2, mode='cie2000')
            ## Typically used for acceptability.
            #print "     CMC: %.3f (2:1)" % color1.delta_e(color2, mode='cmc', pl=2, pc=1)
            ## Typically used to more closely model human percetion.
            #print "     CMC: %.3f (1:1)" % color1.delta_e(color2, mode='cmc', pl=1, pc=1)

            r = color1.delta_e(color2, mode='cmc', pl=2, pc=1)
            if (r < res[0]):
                res = (r, c)
        data['color']   = res[1]
        data['delta_e'] = res[0]

        return data

    def _JSEGdetectColorSegmentsHist(self, im):
        import Image, numpy, os
        
        tmpjpg = os.path.join(os.path.abspath(os.curdir), "cache/jseg_buf.jpg")
        tmpgif = os.path.join(os.path.abspath(os.curdir), "cache/jseg_buf.gif")

        # same scale func as in '_CVdetectObjects_Faces'
        scale  = max([1., numpy.average(numpy.array(im.size)[0:2]/200.)])
        #print numpy.array(im.size)/scale, scale
        try:
            smallImg = im.resize( tuple(numpy.int_(numpy.array(im.size)/scale)), Image.ANTIALIAS )
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return []
        
        #im.thumbnail(size, Image.ANTIALIAS) # size is 640x480
        smallImg.convert('RGB').save(tmpjpg, "JPEG", quality=100, optimize=True)
        
        # Program limitation: The total number of regions in the image must be less
        # than 256 before the region merging process. This works for most images
        # smaller than 512x512.
        
        # Processing time will be about 10 seconds for an 192x128 image and 60 seconds
        # for a 352x240 image. It will take several minutes for a 512x512 image.
        # Minimum image size is 64x64.
        
        # ^^^  THUS RESCALING TO ABOUT 200px ABOVE  ^^^

#        import StringIO
#        stdout, stderr = sys.stdout, sys.stderr
#        sys.stdout = StringIO.StringIO()
#        sys.stderr = StringIO.StringIO()
        
        # stdout, stderr not properly handeled yet
        import jseg
        # e.g. "segdist -i test3.jpg -t 6 -r9 test3.map.gif"
        pywikibot.output(u'')
        jseg.segdist_cpp.main( ("segdist -i %s -t 6 -r9 %s"%(tmpjpg, tmpgif)).split(" ") )
        pywikibot.output(u'')
        
        os.remove( tmpjpg )
        
        # http://stackoverflow.com/questions/384759/pil-and-numpy
        pic = Image.open(tmpgif)
        pix = numpy.array(pic)
        
        os.remove( tmpgif )

# TODO: try to merge similar regions ...
        imgsize = float(smallImg.size[0]*smallImg.size[1])
        hist = []
        for i in range(numpy.max(pix)+1):
            mask = numpy.uint8(pix == i)
            coverage = numpy.count_nonzero(mask)/imgsize
            mask = Image.fromarray( mask )
            h    = smallImg.histogram(mask)
            if (len(h) == 256):
                print "gray scale image, try to fix..."
                h = h*3
            if (len(h) == 256*4):
                print "4-ch. image, try to fix (can include transperancy)..."
                h = h[0:(256*3)]
            hist.append( (h, coverage) )
        
        return hist

    ## Category:Unidentified people
    #def _collectPeople(self):
    #    result = self._CVdetectObjects_Faces()
    #
    #    result = [{} for item in result]
    #
    #    return (u'Unidentified people', result, 1.0)

    # Category:Faces
    def _collectFaces(self):
        result = self._CVdetectObjects_Faces()

        if not ((len(result) == 1) and (result[0]['coverage'] >= .50)):
            result = []

        result = [{'Coverage': "%.3f" % item['coverage']} for item in result]

        return (u'Faces', result, 1.0)

    # Category:Portraits
    def _collectPortraits(self):
        result = self._CVdetectObjects_Faces()

        #if not ((len(result) == 1) and (result[0]['coverage'] >= .25)):
        if not ((len(result) == 1) and (result[0]['coverage'] >= .20)):
            result = []

        result = [{'Coverage': "%.3f" % item['coverage']} for item in result]

        return (u'Portraits', result, 1.0)

gbv = Global()

def checkbot():
    """ Main function """
    # Command line configurable parameters
    repeat = True # Restart after having check all the images?
    limit = 80 # How many images check?
    time_sleep = 30 # How many time sleep after the check?
    waitTime = 0 # How many time sleep before the check?
    normal = False # Check the new images or use another generator?
    untagged = False # Use the untagged generator
    duplicatesActive = False # Use the duplicate option
    duplicatesReport = False # Use the duplicate-report option
    sendemailActive = False # Use the send-email
    logFullError = True # Raise an error when the log is full

    # emulate:  'python checkimages_content.py -limit:5 -break -lang:en'
    # debug:    'python catimages.py -noguesses -debug'
    # run/test: 'python catimages.py [-start:File:abc]'
    #sys.argv += ['-limit:20', '-break', '-lang:en']
    #sys.argv += ['-limit:100', '-break', '-family:commons', '-lang:commons', '-noguesses']#, '-start']
    #sys.argv += ['-limit:100', '-break', '-family:commons', '-lang:commons', '-noguesses', '-start']
    sys.argv += ['-limit:100', '-break', '-family:commons', '-lang:commons', '-noguesses']
    print "http://commons.wikimedia.org/wiki/User:Multichill/Using_OpenCV_to_categorize_files"

    firstPageTitle = None

    # Here below there are the parameters.
    for arg in pywikibot.handleArgs():
        if arg.startswith('-limit'):
            if len(arg) == 7:
                limit = int(pywikibot.input(u'How many files do you want to check?'))
            else:
                limit = int(arg[7:])
        if arg.startswith('-time'):
            if len(arg) == 5:
                time_sleep = int(pywikibot.input(u'How many seconds do you want runs to be apart?'))
            else:
                time_sleep = int(arg[6:])
        elif arg == '-break':
            repeat = False
        elif arg == '-nologerror':
            logFullError = False
        elif arg.startswith('-duplicates'):
            duplicatesActive = True
            if len(arg) == 11:
                duplicates_rollback = 1
            elif len(arg) > 11:
                duplicates_rollback = int(arg[12:])
        elif arg == '-duplicatereport':
            duplicatesReport = True
        elif arg == '-sendemail':
            sendemailActive = True
        elif arg.startswith('-wait'):
            if len(arg) == 5:
                wait = True
                waitTime = int(pywikibot.input(u'How many time do you want to wait before checking the files?'))
            elif len(arg) > 5:
                wait = True
                waitTime = int(arg[6:])
        elif arg.startswith('-start'):
            if len(arg) == 6:
                #firstPageTitle = pywikibot.input(u'From witch page do you want to start?')
                if os.path.exists( os.path.join('cache', 'catimages_pos') ):
                    import shutil
                    shutil.copy2(os.path.join('cache', 'catimages_pos'), os.path.join('cache', 'catimages_pos.bak'))
                    posfile = open(os.path.join('cache', 'catimages_pos'), "r")
                    firstPageTitle = posfile.read().decode('utf-8')
                    print firstPageTitle
                    posfile.close()
            elif len(arg) > 6:
                firstPageTitle = arg[7:]
            firstPageTitle = firstPageTitle.split(":")[1:]
            #generator = pywikibot.getSite().allpages(start=firstPageTitle, namespace=6)
            #repeat = False
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                catName = str(pywikibot.input(u'In which category do I work?'))
            elif len(arg) > 4:
                catName = str(arg[5:])
            catSelected = catlib.Category(pywikibot.getSite(), 'Category:%s' % catName)
            generator = pagegenerators.CategorizedPageGenerator(catSelected)
            repeat = False
        elif arg.startswith('-ref'):
            if len(arg) == 4:
                refName = str(pywikibot.input(u'The references of what page should I parse?'))
            elif len(arg) > 4:
                refName = str(arg[5:])
            generator = pagegenerators.ReferringPageGenerator(pywikibot.Page(pywikibot.getSite(), refName))
            repeat = False
        elif arg.startswith('-untagged'):
            untagged = True
            if len(arg) == 9:
                projectUntagged = str(pywikibot.input(u'In which project should I work?'))
            elif len(arg) > 9:
                projectUntagged = str(arg[10:])
        elif arg == '-noguesses':
            gbv.useGuesses = False
            
    #generator = pagegenerators.GeneratorFactory().getCategoryGen(u"-catr:Media_needing_categories|fromtitle", len('-catr'), recurse = True)
    generator = pagegenerators.GeneratorFactory().getCategoryGen(u"-catr:Media_needing_categories", len('-catr'), recurse = True)

    # Understand if the generator it's the default or not.
    try:
        generator
    except NameError:
        normal = True
    
    # Define the site.
    site = pywikibot.getSite()

    # Block of text to translate the parameters set above.
    image_old_namespace = u"%s:" % site.image_namespace()
    image_namespace = u"File:"

    # If the images to skip are 0, set the skip variable to False (the same for the wait time)
    if waitTime == 0:
        wait = False

    # A little block-statement to ensure that the bot will not start with en-parameters
    if site.lang not in project_inserted:
        pywikibot.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        return

    # Reading the log of the new images if another generator is not given.
    if normal == True:
        if limit == 1:
            pywikibot.output(u"Retrieving the latest file for checking...")
        else:
            pywikibot.output(u"Retrieving the latest %d files for checking..." % limit)
    # Main Loop
    while 1:
        # Defing the Main Class.
        mainClass = main(site, sendemailActive = sendemailActive,
                         duplicatesReport = duplicatesReport, logFullError = logFullError)
        # Untagged is True? Let's take that generator
        if untagged == True:
            generator =  mainClass.untaggedGenerator(projectUntagged, limit)
            normal = False # Ensure that normal is False
        # Normal True? Take the default generator
        if normal == True:
            generator = site.newimages(number = limit)
        # Ok, We (should) have a generator, so let's go on.
        # Take the additional settings for the Project
        mainClass.takesettings()
        # Not the main, but the most important loop.
        #parsed = False
        if wait:
            # Let's sleep...
            generator = mainClass.wait(waitTime, generator, normal, limit)
        outresult = []
        for image in generator:
            if firstPageTitle and not (image.title() == u":".join([u'File']+firstPageTitle)):
                pywikibot.output( u"skipping page '%s' ..." % image.title() )
                continue
            if firstPageTitle and (image.title() == u":".join([u'File']+firstPageTitle)):
                pywikibot.output( u"skipping page '%s' ..." % image.title() )
                firstPageTitle = None
                continue
            if normal == False:
                if image_namespace.lower() not in image.title().lower() and \
                image_old_namespace.lower() not in image.title().lower() and 'file:' not in image.title().lower():
                    pywikibot.output(u'%s seems not an file, skip it...' % image.title())
                    continue
            if normal:
                imageData = image
                image = imageData[0]
                #20100511133318L --- 15:33, 11 mag 2010 e 18 sec
                #b = str(imageData[1]) # use b as variable to make smaller the timestamp-formula used below..
                # fixing the timestamp to the format that we normally use..
                timestamp = imageData[1]#"%s-%s-%sT%s:%s:%sZ" % (b[0:4], b[4:6], b[6:8], b[8:10], b[10:12], b[12:14])
                uploader = imageData[2]
                comment = imageData[3] # useless, in reality..
            else:
                timestamp = None
                uploader = None
                comment = None # useless, also this, let it here for further developments
            try:
                imageName = image.title().split(image_namespace)[1] # Deleting the namespace (useless here)
            except IndexError:# Namespace image not found, that's not an image! Let's skip...
                try:
                    imageName = image.title().split(image_old_namespace)[1]
                except IndexError:
                    pywikibot.output(u"%s is not a file, skipping..." % image.title())
                    continue
            mainClass.setParameters(imageName, timestamp, uploader) # Setting the image for the main class
            try:
                mainClass.downloadImage()
            except pywikibot.exceptions.NoPage:
                continue
            # Check if there are duplicates of the image on the project selected
            if duplicatesActive == True:
                response2 = mainClass.checkImageDuplicated(duplicates_rollback)
                if response2 == False:
                    continue
            resultCheck = mainClass.checkStep()
            ret = mainClass.tag_image(put=('write2wiki' in debug))
            if ret:
                outresult.append( ret )
            limit += -1
            posfile = open(os.path.join('cache', 'catimages_pos'), "w")
            posfile.write( image.title().encode('utf-8') )
            posfile.close()
            if limit < 0:
                break
            if pywikibot.debug:
                break
            if resultCheck:
                continue
    # A little block to perform the repeat or to break.
        if repeat == True:
            printWithTimeZone(u"Waiting for %s seconds," % time_sleep)
            time.sleep(time_sleep)
        else:
            if outresult:
                outpage = pywikibot.Page(site, u"User:DrTrigon/Category:Unidentified people (bot tagged)")
                outresult = [ outpage.get() ] + outresult
                if ('write2wiki' in debug):
                    outpage.put( u"\n".join(outresult), comment="bot adding test results" )
                else:
                    print u"--- " * 20
                    print u"--- " * 20
                    print u"\n".join(outresult[1:])

            pywikibot.output(u"\t\t\t>> STOP! <<")
            break # Exit


# Main loop will take all the (name of the) images and then i'll check them.
if __name__ == "__main__":
    old = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S") #timezones are UTC
    try:
        checkbot()
    finally:
        final = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S") #timezones are UTC
        delta = final - old
        secs_of_diff = delta.seconds
        pywikibot.output("Execution time: %s" % secs_of_diff)
        pywikibot.stopme()
