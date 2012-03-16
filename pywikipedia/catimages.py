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

-commons            The Bot will check if an image on Commons has the same name
                    and if true it report the image.

-duplicates[:#]     Checking if the image has duplicates (if arg, set how many
                    rollback wait before reporting the image in the report
                    instead of tag the image) default: 1 rollback.

-duplicatesreport   Report the duplicates in a log *AND* put the template in
                    the images.

-sendemail          Send an email after tagging.

-break              To break the bot after the first check (default: recursive)

-time[:#]           Time in seconds between repeat runs (default: 30)

-wait[:#]           Wait x second before check the images (default: 0)

-skip[:#]           The bot skip the first [:#] images (default: 0)

-start[:#]          Use allpages() as generator
                    (it starts already form File:[:#])

-cat[:#]            Use a category as generator

-regex[:#]          Use regex, must be used with -url or -page

-page[:#]           Define the name of the wikipage where are the images

-url[:#]            Define the url where are the images

-untagged[:#]       Use daniel's tool as generator:
                    http://toolserver.org/~daniel/WikiSense/UntaggedImages.php

-nologerror         If given, this option will disable the error that is risen
                    when the log is full.

---- Instructions for the real-time settings  ----
* For every new block you have to add:

<------- ------->

In this way the Bot can understand where the block starts in order to take the
right parameter.

* Name=     Set the name of the block
* Find=     Use it to define what search in the text of the image's description,
            while
  Findonly= search only if the exactly text that you give is in the image's
            description.
* Summary=  That's the summary that the bot will use when it will notify the
            problem.
* Head=     That's the incipit that the bot will use for the message.
* Text=     This is the template that the bot will use when it will report the
            image's problem.

---- Known issues/FIXMEs: ----
* Clean the code, some passages are pretty difficult to understand if you're not the coder.
* Add the "catch the language" function for commons.
* Fix and reorganise the new documentation
* Add a report for the image tagged.

"""

#
# (C) Kyle/Orgullomoore, 2006-2007 (newimage.py)
# (C) Siebrand Mazeland, 2007-2010
# (C) Filnik, 2007-2011
# (C) Pywikipedia team, 2007-2011
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

###############################################################################
# <--------------------------- Change only below! --------------------------->#
###############################################################################

# NOTE: in the messages used by the Bot if you put __botnick__ in the text, it
# will automatically replaced with the bot's nickname.

# That's what you want that will be added. (i.e. the {{no source}} with the
# right day/month/year )

# Text that the bot will try to see if there's already or not. If there's a

# Summary for when the will add the no source

# When the Bot find that the usertalk is empty is not pretty to put only the
# no source without the welcome, isn't it?

# Summary that the bot use when it notify the problem with the image's license

# if the file has an unknown extension it will be tagged with this template.
# In reality, there aren't unknown extension, they are only not allowed...

# The header of the Unknown extension's message.

# Text that will be add if the bot find a unknown extension.

# Summary of the delete immediately.
# (e.g: Adding {{db-meta|The file has .%s as extension.}})

# This is the most important header, because it will be used a lot. That's the
# header that the bot will add if the image hasn't the license.

# This is a list of what bots used this script in your project.

# The message that the bot will add the second time that find another license
# problem.

# You can add some settings to wikipedia. In this way, you can change them
# without touching the code. That's useful if you are running the bot on
# Toolserver.

# The bot can report some images (like the images that have the same name of an
# image on commons) This is the page where the bot will store them.

# Adding the date after the signature.

# The text added in the report

# The summary of the report

# If a template isn't a license but it's included on a lot of images, that can
# be skipped to analyze the image without taking care of it. (the template must
# be in a list)

# A page where there's a list of template to skip.

# A page where there's a list of template to consider as licenses.

# Template added when the bot finds only an hidden template and nothing else.
# Note: every __botnick__ will be repleaced with your bot's nickname (feel free not to use if you don't need it)

# In this part there are the parameters for the dupe images.

# Put here the template that you want to put in the image to warn that it's a dupe
# put __image__ if you want only one image, __images__ if you want the whole list

# Head of the message given to the author

# Message to put in the talk

# Comment used by the bot while it reports the problem in the uploader's talk

# Comment used by the bot while it reports the problem in the image

# Regex to detect the template put in the image's decription to find the dupe

# Category with the licenses and / or with subcategories with the other licenses.

## Put None if you don't use this option or simply add nothing if en
## is still None.
# Page where is stored the message to send as email to the users

# Title of the email

# Seems that uploaderBots aren't interested to get messages regarding the
# files that they upload.. strange, uh?

# Service images that don't have to be deleted and/or reported has a template inside them
# (you can let this param as None)

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = [u'ar', u'commons', u'de', u'en', u'fa', u'ga', u'hu', u'it',
                    u'ja', u'ko', u'ta', u'zh']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project.
################################################################################
# <--------------------------- Change only above! ---------------------------> #
################################################################################

# Error Classes
class LogIsFull(pywikibot.Error):
    """An exception indicating that the log is full and the Bot cannot add
    other data to prevent Errors.

    """

class NothingFound(pywikibot.Error):
    """ An exception indicating that a regex has return [] instead of results.

    """

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
    skip_number = 0          # How many images to skip before checking?
    waitTime = 0             # How many time sleep before the check?
    commonsActive = False    # Check if on commons there's an image with the same name?
    normal = False           # Check the new images or use another generator?
    urlUsed = False          # Use the url-related function instead of the new-pages generator
    regexGen = False         # Use the regex generator
    untagged = False         # Use the untagged generator
    duplicatesActive = False # Use the duplicate option
    duplicatesReport = False # Use the duplicate-report option
    sendemailActive = False  # Use the send-email
    logFullError = True      # Raise an error when the log is full


class main(checkimages.main):
    cats = {
        'people':        (u'Category:Unidentified people', 0),
        'maps':          (u'Category:Unidentified maps', 1),
        'flags':         (u'Category:Unidentified flags', 2),
        'plants':        (u'Category:Unidentified plants', 3),
        'coats of arms': (u'Category:Unidentified coats of arms', 4),
        'buildings':     (u'Category:Unidentified buildings', 5),
        'trains':        (u'Category:Unidentified trains', 6),
        'automobiles':   (u'Category:Unidentified automobiles', 7),
        'buses':         (u'Category:Unidentified buses', 8),
    }

#    def __init__(self, site, logFulNumber = 25000, sendemailActive = False,
#                 duplicatesReport = False, logFullError = True): pass
#    def setParameters(self, imageName, timestamp, uploader): pass
#    def report(self, newtext, image_to_report, notification=None, head=None,
#               notification2 = None, unver=True, commTalk=None, commImage=None): pass
#    def uploadBotChangeFunction(self, reportPageText, upBotArray): pass
#    def tag_image(self, put = True): pass
#    def put_mex_in_talk(self): pass
#    def untaggedGenerator(self, untaggedProject, limit): pass
#    def regexGenerator(self, regexp, textrun): pass
#    def loadHiddenTemplates(self): pass
#    def returnOlderTime(self, listGiven, timeListGiven): pass
#    def convert_to_url(self, page): pass
#    def countEdits(self, pagename, userlist): pass
#    def checkImageOnCommons(self): pass
#    def checkImageDuplicated(self, duplicates_rollback): pass
#    def report_image(self, image_to_report, rep_page = None, com = None, rep_text = None, addings = True, regex = None): pass
#    def takesettings(self): pass

    def load_licenses(self):
        return []

#    def miniTemplateCheck(self, template): pass
#    def templateInList(self): pass
#    def smartDetection(self): pass
#    def load(self, raw): pass
#    def skipImages(self, skip_number, limit): pass
#    def wait(self, waitTime, generator, normal, limit): pass
#    def isTagged(self): pass
#    def findAdditionalProblems(self): pass

    def downloadImage(self):
        #print self.image
        self.image_filename = os.path.split(self.image.fileUrl())[-1]
        self.image_path     = os.path.join('cache', self.image_filename)
        if os.path.exists(self.image_path):
            return

#        f, data = self.site.getUrl(self.image.fileUrl(), no_hostname=True, back_response=True)
        # !!! CHEAP HACK TO GET IT WORKING -> NEEDS PATCH IN 'getUrl' upstream !!!
        # (prevent unicode encoding at end or allow to re-read in back_response)
        # (this will be useful for 'subster' also; merge several get modes there)
        req = urllib2.Request(self.image.fileUrl(), None, {})
        f = pywikibot.MyURLopener.open(req)
        data = f.read()

        f = open(self.image_path, 'wb')
        f.write( data )
        f.close()

    # LOOK ALSO AT: checkimages.main.checkStep
    # (and actegory scripts/bots too...)
    def checkStep(self):
        #print self.image_path
        pywikibot.output(self.image.title())

        # use explicit searches for classification
        if hasattr(self, '_result_classify'):
            delattr(self, '_result_classify')
        for item in dir(self):
            if '_search' in item:
                (cat, result) = self.__class__.__dict__[item](self)
                #print cat, result
                if result:
                    pywikibot.output( u'   {{%s}} found %i time(s)'
                                      % (cat, len(result)) )

    # Category:Unidentified people
    def _searchPeople(self):
        result = []
        try:
            result = self._CVdetectObjects()
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
        #print self.image, '\n   ', result

        (c, r) = self._CVclassifyObjects('people')
        result += r

        return (c, result)

    def _CVdetectObjects(self):
        """Converts an image to grayscale and prints the locations of any
           faces found"""
        # http://python.pastebin.com/m76db1d6b
        # http://creatingwithcode.com/howto/face-detection-in-static-images-with-python/
        # http://opencv.willowgarage.com/documentation/python/objdetect_cascade_classification.html
        # http://opencv.willowgarage.com/wiki/FaceDetection
        # http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
        # http://www.cognotics.com/opencv/servo_2007_series/part_4/index.html
        
        #from opencv.cv import *
        #from opencv.highgui import *
        import cv

        image = cv.LoadImage(self.image_path)

        grayscale = cv.CreateImage((image.width, image.height), 8, 1)
        cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)

        storage = cv.CreateMemStorage(0)
        #storage = cv.CreateMemStorage()
        #cv.ClearMemStorage(storage)
        cv.EqualizeHist(grayscale, grayscale)
        #cascade = cv.LoadHaarClassifierCascade(
        cascade = cv.Load(
          '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
          #(1,1))
          )
        faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
                                   cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))

        if faces:
            for f in faces:
                (x, y, width, height) = f[0]
                #print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
                (x1, y1, x2, y2) = (x, y, x+width, y+height)
                #print("[(%d,%d) -> (%d,%d)]" % (x1, y1, x2, y2))
                self._drawRect(x1,y1,x2,y2) #call to a python pil

        return faces

    def _drawRect(self, x1,y1,x2,y2): #function to modify the img
        import Image, ImageDraw
        image_path_new = os.path.join('cache', '0_DETECTED_' + self.image_filename)
        im = Image.open(self.image_path)
        draw = ImageDraw.Draw(im)
        draw.rectangle([x1,y1,x2,y2], outline=(255,0,0))
        im.save(image_path_new)

    # Category:Unidentified maps
    def _searchMaps(self):
        return self._CVclassifyObjects('maps')

    # Category:Unidentified flags
    def _searchFlags(self):
        return self._CVclassifyObjects('flags')

    # Category:Unidentified plants
    def _searchPlants(self):
        return self._CVclassifyObjects('plants')

    # Category:Unidentified coats of arms
    def _searchCoatsOfArms(self):
        return self._CVclassifyObjects('coats of arms')

    # Category:Unidentified buildings
    def _searchBuildings(self):
        return self._CVclassifyObjects('buildings')

    # Category:Unidentified trains
    def _searchTrains(self):
        return self._CVclassifyObjects('trains')

    # Category:Unidentified automobiles
    def _searchAutomobiles(self):
        return self._CVclassifyObjects('automobiles')

    # Category:Unidentified buses
    def _searchBuses(self):
        return self._CVclassifyObjects('buses')

    def _CVclassifyObjects(self, cls):
        """Uses the 'The Bag of Words model' for classification"""

        # prevent multiple execute of code below
        if not hasattr(self, '_result_classify'):
            # http://app-solut.com/blog/2011/07/the-bag-of-words-model-in-opencv-2-2/
            # http://app-solut.com/blog/2011/07/using-the-normal-bayes-classifier-for-image-categorization-in-opencv/
            # http://authors.library.caltech.edu/7694/
            # http://www.vision.caltech.edu/Image_Datasets/Caltech256/

            info = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
                    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse',
                    'motorbike', 'person', 'pottedplant', 'sheep', 'sofa',
                    'train', 'tvmonitor',]
            bowDescPath = '/home/ursin/data/toolserver/pywikipedia/opencv/data/bowImageDescriptors/000000.xml.gz'

            # https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/cpp/bagofwords_classification.cpp?rev=3714
            # stand-alone (in shell) for training e.g. with:
            #   BoWclassify /data/toolserver/pywikipedia/opencv/VOC2007 /data/toolserver/pywikipedia/opencv/data FAST SURF BruteForce
            import opencv

            if os.path.exists(bowDescPath):
                os.remove(bowDescPath)

            #result = opencv.BoWclassify.main(0, '', '', '', '', '')
            result = opencv.BoWclassify.main(6, 
                                             '/data/toolserver/pywikipedia/opencv/VOC2007', 
                                             '/data/toolserver/pywikipedia/opencv/data', 
                                             'FAST', 
                                             'SURF', 
                                             'BruteForce',
                                             #['/data/toolserver/pywikipedia/opencv/VOC2007/JPEGImages/000019.jpg'])
                                             [str(os.path.abspath(self.image_path).encode('latin-1'))])
            try:
                os.remove(bowDescPath)
            except:
                print "PROBLEM!!!"
                raise
            print self.image_path
            for i in range(len(result)):
                print "%12s %.3f" % (info[i], result[i])
            raise

            # now make the algo working; confer also
            # http://www.xrce.xerox.com/layout/set/print/content/download/18763/134049/file/2004_010.pdf
            # http://people.csail.mit.edu/torralba/shortCourseRLOC/index.html

            self._result_classify = result

        (cat, cls) = self.cats[cls]
        if (self._result_classify[cls] >= 0.5): # >= threshold 50%
            result = [ self._result_classify[cls] ] # ok
        else:
            result = []                             # nothing found

        return (cat, result)

gbv = Global()

def checkbot():
    """ Main function """
    # Command line configurable parameters
    repeat = True # Restart after having check all the images?
    limit = 80 # How many images check?
    time_sleep = 30 # How many time sleep after the check?
    skip_number = 0 # How many images to skip before checking?
    waitTime = 0 # How many time sleep before the check?
    commonsActive = False # Check if on commons there's an image with the same name?
    normal = False # Check the new images or use another generator?
    urlUsed = False # Use the url-related function instead of the new-pages generator
    regexGen = False # Use the regex generator
    untagged = False # Use the untagged generator
    duplicatesActive = False # Use the duplicate option
    duplicatesReport = False # Use the duplicate-report option
    sendemailActive = False # Use the send-email
    logFullError = True # Raise an error when the log is full

    # emulate: 'python checkimages_content.py -limit:5 -break -lang:en'
    sys.argv += ['-limit:20', '-break', '-lang:en']
    print "http://commons.wikimedia.org/wiki/User:Multichill/Using_OpenCV_to_categorize_files"

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
        elif arg == '-commons':
            commonsActive = True
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
        elif arg.startswith('-skip'):
            if len(arg) == 5:
                skip = True
                skip_number = int(pywikibot.input(u'How many files do you want to skip?'))
            elif len(arg) > 5:
                skip = True
                skip_number = int(arg[6:])
        elif arg.startswith('-wait'):
            if len(arg) == 5:
                wait = True
                waitTime = int(pywikibot.input(u'How many time do you want to wait before checking the files?'))
            elif len(arg) > 5:
                wait = True
                waitTime = int(arg[6:])
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = pywikibot.input(u'From witch page do you want to start?')
            elif len(arg) > 6:
                firstPageTitle = arg[7:]
            firstPageTitle = firstPageTitle.split(":")[1:]
            generator = pywikibot.getSite().allpages(start=firstPageTitle, namespace=6)
            repeat = False
        elif arg.startswith('-page'):
            if len(arg) == 5:
                regexPageName = str(pywikibot.input(u'Which page do you want to use for the regex?'))
            elif len(arg) > 5:
                regexPageName = str(arg[6:])
            repeat = False
            regexGen = True
        elif arg.startswith('-url'):
            if len(arg) == 4:
                regexPageUrl = str(pywikibot.input(u'Which url do you want to use for the regex?'))
            elif len(arg) > 4:
                regexPageUrl = str(arg[5:])
            urlUsed = True
            repeat = False
            regexGen = True
        elif arg.startswith('-regex'):
            if len(arg) == 6:
                regexpToUse = str(pywikibot.input(u'Which regex do you want to use?'))
            elif len(arg) > 6:
                regexpToUse = str(arg[7:])
            generator = 'regex'
            repeat = False
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
    if skip_number == 0:
        skip = False
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
        # if urlUsed and regexGen, get the source for the generator
        if urlUsed == True and regexGen == True:
            textRegex = site.getUrl(regexPageUrl, no_hostname = True)
        # Not an url but a wiki page as "source" for the regex
        elif regexGen == True:
            pageRegex = pywikibot.Page(site, regexPageName)
            try:
                textRegex = pageRegex.get()
            except pywikibot.NoPage:
                pywikibot.output(u"%s doesn't exist!" % pageRegex.title())
                textRegex = '' # No source, so the bot will quit later.
        # If generator is the regex' one, use your own Generator using an url or page and a regex.
        if generator == 'regex' and regexGen == True:
            generator = mainClass.regexGenerator(regexpToUse, textRegex)
        # Ok, We (should) have a generator, so let's go on.
        # Take the additional settings for the Project
        mainClass.takesettings()
        # Not the main, but the most important loop.
        #parsed = False
        if wait:
            # Let's sleep...
            generator = mainClass.wait(waitTime, generator, normal, limit)
        for image in generator:
            # When you've a lot of image to skip before working use this workaround, otherwise
            # let this commented, thanks. [ decoment also parsed = False if you want to use it
            #
            #if image.title() != u'File:Nytlogo379x64.gif' and not parsed:
            #    pywikibot.output(u"%s already parsed." % image.title())
            #    continue
            #else:
            #    parsed = True
            # If the generator returns something that is not an image, simply skip it.
            if normal == False and regexGen == False:
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
            mainClass.downloadImage()
            # Skip block
            if skip == True:
                skip = mainClass.skipImages(skip_number, limit)
                if skip == True:
                    continue
            # Check on commons if there's already an image with the same name
            if commonsActive == True and site.family.name != "commons":
                response = mainClass.checkImageOnCommons()
                if response == False:
                    continue
            # Check if there are duplicates of the image on the project selected
            if duplicatesActive == True:
                response2 = mainClass.checkImageDuplicated(duplicates_rollback)
                if response2 == False:
                    continue
            resultCheck = mainClass.checkStep()
            if resultCheck:
                continue
    # A little block to perform the repeat or to break.
        if repeat == True:
            printWithTimeZone(u"Waiting for %s seconds," % time_sleep)
            time.sleep(time_sleep)
        else:
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
