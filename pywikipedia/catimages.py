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

-cat[:#]            Use a category as recursive generator
                    (if no given 'Category:Media_needing_categories' is used)

-start[:#]          Start already form File:[:#] or if no file given start
                    from top (instead of resuming last run).

-limit              The number of images to check (default: 80)

-noguesses          If given, this option will disable all guesses (which are
                    less reliable than true searches).

-single:#           Run for one (any) single page only.

X-sendemail          Send an email after tagging.

X-untagged[:#]       Use daniel's tool as generator:
X                    http://toolserver.org/~daniel/WikiSense/UntaggedImages.php


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

import re, time, urllib2, os, locale, sys, datetime
import wikipedia as pywikibot
import pagegenerators, catlib
import checkimages

locale.setlocale(locale.LC_ALL, '')


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
|"""

# this list is auto-generated during bot run (may be add notifcation about NEW templates)
#tmpl_available_spec = [ u'Properties', u'ColorRegions', u'Faces', u'ColorAverage' ]
tmpl_available_spec = []    # auto-generated


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
    limit = 80               # How many images check?
    untagged = False         # Use the untagged generator
    sendemailActive = False  # Use the send-email
    useGuesses = True        # Use guesses which are less reliable than true searches


# EXPERIMENTAL BOT SCRIPT DERIVED FROM 'checkimages.py' and should use 'catlib.py'
class CatImagesBot(checkimages.main):
#    def __init__(self, site, logFulNumber = 25000, sendemailActive = False,
#                 duplicatesReport = False, logFullError = True): pass
#    def setParameters(self, imageName, timestamp, uploader): pass
#    def report(self, newtext, image_to_report, notification=None, head=None,
#               notification2 = None, unver=True, commTalk=None, commImage=None): pass

    #ignore = []
    ignore = ['color']
    
    _thrhld_group_size = 4
    _thrshld_guesses = 0.1
    _thrshld_default = 0.75

    # or may be '__init__' ... ???
    def load_licenses(self):
        #pywikibot.output(u'\n\t...Listing the procedures available...\n')
        pywikibot.output(u'\n\t...Listing the procedures used...\n')
        
        self._funcs = {'filter': [], 'cat': [], 'guess': []}

        for item in dir(self):
            s = item.split('_')
            if (len(s) < 3) or (s[1] not in self._funcs) or (s[2] in self.ignore):
                continue
            pywikibot.output( item )
            self._funcs[s[1]].append( item )

        self.tmpl_available_spec = tmpl_available_spec
        gen = pagegenerators.PrefixingPageGenerator(prefix = u'Template:FileContentsByBot/')
        buf = []
        for item in gen:
            item = item.title()
            if (item[-4:] == "/doc"):           # all docs
                continue
            item = os.path.split(item)[1]
            if (item[0].lower() == item[0]):    # e.g. 'generic'
                continue
            buf.append( item )
        if buf:
            self.tmpl_available_spec = buf
            pywikibot.output( u'\n\t...Following specialized templates found, check them since they are used now...\n' )
            pywikibot.output( u'tmpl_available_spec = [ %s ]\n' % u", ".join(buf) )

        return []

    def downloadImage(self):
        self.image_filename  = os.path.split(self.image.fileUrl())[-1]
        self.image_fileext   = os.path.splitext(self.image_filename)[1]
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

        # SVG: rasterize the SVG to bitmap (MAY BE GET FROM WIKI BY DOWNLOAD?...)
        # http://stackoverflow.com/questions/6589358/convert-svg-to-png-in-python
        # http://cairographics.org/pythoncairopil/
        # http://cairographics.org/pyrsvg/
        if self.image_fileext == u'.svg':
            import cairo, rsvg, Image       # gnome-python2-rsvg

            svg = rsvg.Handle(self.image_path)
            img = cairo.ImageSurface(cairo.FORMAT_ARGB32, svg.props.width, svg.props.height)
            ctx = cairo.Context(img)
            svg.render_cairo(ctx)
            #img.write_to_png("svg.png")
            Image.frombuffer("RGBA",( img.get_width(),img.get_height() ),
                             img.get_data(),"raw","RGBA",0,1).save(self.image_path_JPEG, "JPEG")
        else:
            try:
                import Image
                im = Image.open(self.image_path) # might be png, gif etc, for instance
                #im.thumbnail(size, Image.ANTIALIAS) # size is 640x480
                im.convert('RGB').save(self.image_path_JPEG, "JPEG")
            except IOError, e:
                if 'image file is truncated' in str(e):
                    # im object has changed due to exception raised
                    im.convert('RGB').save(self.image_path_JPEG, "JPEG")
                else:
                    self.image_path_JPEG = self.image_path
            except:
                self.image_path_JPEG = self.image_path

    # LOOK ALSO AT: checkimages.CatImagesBot.checkStep
    # (and category scripts/bots too...)
    def checkStep(self):
        #print self.image_path
        pywikibot.output(self.image.title())

        if gbv.useGuesses:
            self.thrshld = self._thrshld_guesses
        else:
            self.thrshld = self._thrshld_default

        self._info         = {}     # used for LOG/DEBUG OUTPUT ONLY
        self._info_filter  = {}     # used for CATEGORIZATION
        self._result_check = []

        # gather all information related to current image
        self.gatherInformation()

        # information template: use filter to select from gathered information
        self._info_filter = {}
        for item in self._funcs['filter']:
            self._info_filter.update( self.__class__.__dict__[item](self) )

        # categorization: use explicit searches for classification (rel = ?)
        for item in self._funcs['cat']:
            (cat, rel) = self.__class__.__dict__[item](self)
            #print cat, result, len(result)
            if rel:
                self._result_check.append( cat )
        self._result_check = list(set(self._result_check))

        # categorization: use guesses for unreliable classification (rel = 0.1)
        if not gbv.useGuesses:
            return self._result_check
        for item in self._funcs['guess']:
            (cat, result, rel) = self.__class__.__dict__[item](self)
            #print cat, result, len(result)
            if result:
                self._result_check.append( (cat, result, rel) )

        return self._result_check

    def tag_image(self):
        self.clean_cache()

        #if not self._existInformation(self._info_filter):  # information available?
        if not self._result_check:                          # category available?
            return u""

        pywikibot.get_throttle()
        content = self.image.get()

        content = self._append_to_template(content, u"Information", tmpl_FileContentsByBot)
        for i, key in enumerate(self._info_filter):
            item = self._info_filter[key]

            info = self._make_infoblock(key, item)
            if info:
                content = self._append_to_template(content, u"FileContentsByBot", info)

        tags = set([])
        for i, cat in enumerate(self._result_check):
            tags.add( u"[[:Category:%s]]" % cat )
            content = self._add_category(content, u"Category:%s" % cat)

        tags.add( u"[[:Category:Categorized by DrTrigonBot]]" )
        content = self._add_category(content, u"Category:Categorized by DrTrigonBot")
        content = self._add_template(content, u"Check categories|year={{subst:#time:Y}}|month={{subst:#time:F}}|day={{subst:#time:j}}|category=[[Category:Categorized by DrTrigonBot]]", top=True)
        content = self._remove_category_or_template(content, u"Uncategorized")
        content = self._gather_category(content)
        print u"--- " * 20
        print content
        print u"--- " * 20
        pywikibot.put_throttle()
        self.image.put( content, comment="bot automatic categorization; adding %s" % u", ".join(tags) )

        return

    def log_output(self):
        # ColorRegions always applies here since there is at least 1 (THE average) color...
        ignore = ['Properties', 'ColorAverage', 'ColorRegions'] # + ColorRegions
        #if not self._existInformation(self._info):  # information available?
        # information available? AND/OR category available?
        if not (self._existInformation(self._info, ignore = ignore) or self._result_check):
            return u""

        ret  = []
        ret.append( u"" )
        ret.append( u"== [[:%s]] ==" % self.image.title() )
        ret.append( u'<div style="position:relative;">' )
        ret.append( u"[[%s|200px]]" % self.image.title() )
        ret.append( self._make_markerblock(self._info[u'Faces'], 200.) )
        #ret.append( self._make_markerblock(self._info[u'ColorRegions'], 200.,
        #                                   structure=['Position'], line='dashed') )
        ret.append( self._make_markerblock(self._info[u'People'], 200.,
                                           structure=['Position'], line='dashed') )
        ret.append( u"</div>" )

        color = {True: "rgb(0,255,0)", False: "rgb(255,0,0)"}[bool(self._result_check)]
        ret.append( u"<div style='background:%s'>'''automatic categorization''': %s</div>" % (color, u", ".join(self._result_check)) )

        buf = []
        for i, key in enumerate(self._info):
            item = self._info[key]

            info = self._make_infoblock(key, item, [])
            if info:
                buf.append( info )
        ret.append( tmpl_FileContentsByBot[3:] + u"\n" + u"\n".join( buf ) + u"\n}}" )

        return u"\n".join( ret )

    def clean_cache(self):
        if os.path.exists(self.image_path):
            os.remove( self.image_path )
        if os.path.exists(self.image_path_JPEG):
            os.remove( self.image_path_JPEG )
        image_path_new = self.image_path_JPEG.replace(u"cache/", u"cache/0_DETECTED_")
        if os.path.exists(image_path_new):
            os.remove( image_path_new )

    def _make_infoblock(self, cat, res, tmpl_available=None):
        if not res:
            return u''

        if (tmpl_available == None):
            tmpl_available = self.tmpl_available_spec

        generic = (cat not in tmpl_available)
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
                    buf[key].append( self._output_format(item[key]) )
            for key in titles:
                result.append( u"  {{FileContentsByBot/generic|name=%s|value=%s}}" % (key, u"; ".join(buf[key])) )
        else:
            result.append( u"{{FileContentsByBot/%s|" % cat )
            for item in res:
                result.append( u"  {{FileContentsByBot/%s" % cat )
                for key in titles:
                    if not (item[key] == []):   # (work-a-round for empty 'Eyes')
                        result.append( self._output_format_flatten(key, item[key]) )
                result.append( u"  }}" )
        result.append( u"}}" )

        return u"\n".join( result )

    def _output_format(self, value):
        if (type(value) == type(float())):
            # round/strip floats
            return "%.3f" % value
        else:
            # output string representation of variable
            return str(value)

    def _output_format_flatten(self, key, value):
        # flatten structured varible recursively
        if (type(value) == type(tuple())) or (type(value) == type(list())):
            buf = []
            for i, t in enumerate(value):
                buf.append( self._output_format_flatten(key + (u"-%02i" % i), t) )
            return u"\n".join( buf )
        else:
            # end of recursion
            return u"  | %s = %s" % (key, self._output_format(value))

    def _make_markerblock(self, res, size, structure=['Position', 'Eyes'], line='solid'):
        import numpy

        # same as in '_detectObjectFaces_CV'
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
            if ('RGB' in r):
                color = list(numpy.array((255,255,255))-numpy.array(r['RGBref']))
            else:
                color = list(colors[i%8])
            color.reverse()
            color = u"%02x%02x%02x" % tuple(color)
            
            #scale = r['size'][0]/size
            scale = self.image_size[0]/size
            f     = list(numpy.array(r[structure[0]])/scale)
            
            result.append( u'<div class="%s-marker" style="position:absolute; left:%ipx; top:%ipx; width:%ipx; height:%ipx; border:2px %s #%s;"></div>' % tuple([structure[0].lower()] + f + [line, color]) )

            if (len(structure) > 1):
                for e in r[structure[1]]:
                    e = list(numpy.array(e)/scale)
    
                    result.append( u'<div class="%s-marker" style="position:absolute; left:%ipx; top:%ipx; width:%ipx; height:%ipx; border:2px solid #%s;"></div>' % tuple([structure[1].lower()] + e + [color]) )

        return u"\n".join( result )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def _remove_category_or_template(self, text, name):
        text = re.sub(u"[\{\[]{2}%s.*?[\}\]]{2}\n?" % name, u"", text)
        return text

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def _gather_category(self, text):
        cat  = []
        page = []
        for line in text.split(u"\n"):
            if re.match(u"^\[\[Category:.*?\]\]$", line):
                cat.append( line )
            else:
                page.append( line )
        return u"\n".join( page + cat )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def _add_category(self, text, name, top=False):
        if top:
            buf = [(u"[[%s]]" % name), text]
        else:
            buf = [text, (u"[[%s]]" % name)]
        return u"\n".join( buf )
    #    import catlib
    #    catlib.add_category(self.image, category, comment=None, createEmptyPages=False)

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def _add_template(self, text, name, params={}, top=False, raw=False):
        if top:
            buf = [(u"{{%s}}" % name), text]
        else:
            if raw:
                buf = [text, name]
            else:
                buf = [text, (u"{{%s}}" % name)]
        return u"\n".join( buf )

    # place into 'textlib' (or else e.g. 'catlib'/'templib'...)
    def _append_to_template(self, text, name, append):
        pattern  = re.compile(u"(\{\{%s.*?\n)(\s*\}\}\n{2})" % name, flags=re.S)
        template = pattern.search(text).groups()
        
        template = u"".join( [template[0], append, u"\n", template[1]] )
        
        text = pattern.sub(template, text)
        return text

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

    # gather data from all information interfaces and assign confidences
    def gatherInformation(self):
        # Image size
        self._detectProperties_PIL()
        
        # Faces and eyes (opencv pre-trained)
        self._detectObjectFaces_CV()
        
        for i in range(len(self._info['Faces'])):
            data = self._info['Faces'][i]

            c = (len(data['Eyes']) + 2.) / 4.
            self._info['Faces'][i]['Confidence'] = c

        # Segments and colors
        self._detectSegmentColors_JSEGnPIL()
        # Average color
        self._detectAverageColor_PIL()

        max_dim = max(self.image_size)
        for i in range(len(self._info['ColorRegions'])):
            data = self._info['ColorRegions'][i]

            # has to be in descending order since only 1 resolves (!)
            #if   (data['Coverage'] >= 0.40) and (data['Delta_E']  <=  5.0):
            #    c = 1.0
            ##elif (data['Coverage'] >= 0.20) and (data['Delta_E']  <= 15.0):
            ##elif (data['Coverage'] >= 0.20) and (data['Delta_E']  <= 10.0):
            #elif (data['Coverage'] >= 0.25) and (data['Delta_E']  <= 10.0):
            #    c = 0.75
            #elif (data['Coverage'] >= 0.10) and (data['Delta_E']  <= 20.0):
            #    c = 0.5
            #else:
            #    c = 0.1
            ca = (data['Coverage'])**(1./6)                 # 0.20 -> ~0.75
            #ca = (data['Coverage'])**(1./5)                 # 0.25 -> ~0.75
            #ca = (data['Coverage'])**(1./4)                 # 0.35 -> ~0.75
            #cb = (0.02 * (50. - data['Delta_E']))**(1.2)    # 10.0 -> ~0.75
            cb = (0.02 * (50. - data['Delta_E']))**(1./2)   # 20.0 -> ~0.75
            #cb = (0.02 * (50. - data['Delta_E']))**(1./3)   # 25.0 -> ~0.75
            cc = (1. - (data['Delta_R']/max_dim))**(1.)     # 0.25 -> ~0.75
            c  = ( 3*ca + cb ) / 4
            #c  = ( cc + 6*ca + 2*cb ) / 9
            self._info['ColorRegions'][i]['Confidence'] = c

        # People (opencv pre-trained)
        self._detectObjectPeople_CV()
        
        for i in range(len(self._info['People'])):
            data = self._info['People'][i]

            if (data['Coverage'] >= 0.20):
                c = 0.75
            if (data['Coverage'] >= 0.10):    # at least 10% coverage needed
                c = 0.5
            else:
                c = 0.1
            self._info['People'][i]['Confidence'] = c

        # general (self trained) classification
        # !!! train a own cascade classifier like for face detection used
        # !!! with 'opencv_haartraing' -> xml (file to use like in face/eye detection)
        # !!! do NOT train 'people', there is already 'haarcascade_fullbody.xml', a.o. ...
        #
        # http://www.computer-vision-software.com/blog/2009/11/faq-opencv-haartraining/
        #self._detectObjectTrained_CV()

        # optical text recognition (tesseract?)
        #self._recognizeOpticalText_x()
        # (no full recognition but just classify as 'contains text')

        # barcode and Data Matrix recognition (gocr? libdmtx/pydmtx?)
        #self._recognizeOpticalCodes_x()

        # general (trained) classification
        #self._classifyObjectAll_CV()

    def _existInformation(self, info, ignore = ['Properties', 'ColorAverage']):
        result = []
        for item in info:
            if item in ignore:
                continue
            if info[item]:
                result.append( item )
        return result

    def _filter_Properties(self):
        # >>> never drop <<<
        result = self._info['Properties']
        return {'Properties': result}

    def _filter_Faces(self):
        result = self._info['Faces']
        if (len(result) < self._thrhld_group_size):
            buf = []
            for item in self._info['Faces']:
                # >>> drop if below thrshld <<<
                if (item['Confidence'] >= self.thrshld):
                    buf.append( item )
            result = buf
        return {'Faces': result}

    def _filter_People(self):
        result = self._info['People']
        if (len(result) < self._thrhld_group_size):
            buf = []
            for item in self._info['People']:
                # >>> drop if below thrshld <<<
                if (item['Confidence'] >= self.thrshld):
                    buf.append( item )
            result = buf
        return {'People': result}

    def _filter_ColorRegions(self):
        #result = {}
        result = []
        for item in self._info['ColorRegions']:
            ## >>> drop wrost ones... (ignore all below 0.2) <<<
            #if (result.get(item['Color'], {'Confidence': 0.2})['Confidence'] < item['Confidence']):
            #    result[item['Color']] = item
            # >>> drop if below thrshld <<<
            if (item['Confidence'] >= self.thrshld):
                result.append( item )
        #return {'ColorRegions': [result[item] for item in result]}
        return {'ColorRegions': result}

    def _filter_ColorAverage(self):
        # >>> never drop <<<
        result = self._info['ColorAverage']
        return {'ColorAverage': result}

    # Category:Unidentified people
    def _cat_people_People(self):
        #relevance = bool(self._info_filter['People'])
        relevance = self._cat_people_Groups()[1]

        return (u'Unidentified people', relevance)

    # Category:Unidentified people
    #def _cat_multi_People(self):
    def _cat_face_People(self):
        relevance = bool(self._info_filter['Faces'])
        #relevance = bool(self._info_filter['People']) or relevance

        return (u'Unidentified people', relevance)

    # Category:Groups
    def _cat_people_Groups(self):
        result = self._info_filter['People']

        relevance = (len(result) >= self._thrhld_group_size)

        return (u'Groups', relevance)

    # Category:Groups
    def _cat_face_Groups(self):
        result = self._info_filter['Faces']

        #if not (len(result) > 1): # 5 should give 0.75 and get reported
        #    relevance = 0.
        #else:
        #    relevance = 1 - 1./(len(result)-1)
        relevance = (len(result) >= self._thrhld_group_size)

        return (u'Groups', relevance)

    # Category:Faces
    def _cat_face_Faces(self):
        result = self._info_filter['Faces']

        return (u'Faces', ((len(result) == 1) and (result[0]['Coverage'] >= .50)))

    # Category:Portraits
    def _cat_face_Portraits(self):
        result = self._info_filter['Faces']

        #return (u'Portraits', ((len(result) == 1) and (result[0]['Coverage'] >= .25)))
        return (u'Portraits', ((len(result) == 1) and (result[0]['Coverage'] >= .20)))

    # Category:Unidentified people
    def _guess__People(self):
        #result  = copy.deepcopy(self._info_filter['Faces'])

        cls = 'person'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result = [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found

        return (u'Unidentified people', result, 0.1)

    ## Category:Unidentified maps
    #def _guess__Maps(self):
    #    return (u'Unidentified maps', self._classifyObjectAll_CV('maps'), 0.1)

    ## Category:Unidentified flags
    #def _guess__Flags(self):
    #    return (u'Unidentified flags', self._classifyObjectAll_CV('flags'), 0.1)

    # Category:Unidentified plants
    def _guess__Plants(self):
        cls = 'pottedplant'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result = [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found

        return (u'Unidentified plants', result, 0.1)

    ## Category:Unidentified coats of arms
    #def _guessCoatsOfArms(self):
    #    return (u'Unidentified coats of arms', self._classifyObjectAll_CV('coats of arms'), 0.1)

    ## Category:Unidentified buildings
    #def _guessBuildings(self):
    #    return (u'Unidentified buildings', self._classifyObjectAll_CV('buildings'), 0.1)

    # Category:Unidentified trains
    def _guess__Trains(self):
        cls = 'train'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result = [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found

        return (u'Unidentified trains', result, 0.1)

    # Category:Unidentified automobiles
    def _guess__Automobiles(self):
        cls = 'bus'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result = [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found
        cls = 'car'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result += [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        cls = 'motorbike'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result += [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        return (u'Unidentified automobiles', result, 0.1)

    # Category:Unidentified buses
    def _guess__Buses(self):
        cls = 'bus'
        if (self._info_filter['classify'].get(cls, 0.0) >= 0.5): # >= threshold 50%
            #result = [ {'confidence': self._info_filter['classify'][cls]} ] # ok
            result = [ {'confidence': -self._info_filter['classify'][cls]} ] # ok - BUT UNRELIABLE THUS (-)
        else:
            result = []                             # nothing found

        return (u'Unidentified buses', result, 0.1)

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
    def _cat_color_Black(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Black' == item[u'Color']):
                return (u'Black', True)
        return (u'Black', False)

    def _cat_color_Blue(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Blue' == item[u'Color']):
                return (u'Blue', True)
        return (u'Blue', False)

    def _cat_color_Brown(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Brown' == item[u'Color']):
                return (u'Brown', True)
        return (u'Brown', False)

    def _cat_color_Green(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Green' == item[u'Color']):
                return (u'Green', True)
        return (u'Green', False)

    def _cat_color_Orange(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Orange' == item[u'Color']):
                return (u'Orange', True)
        return (u'Orange', False)

    def _cat_color_Pink(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Pink' == item[u'Color']):
                return (u'Pink', True)
        return (u'Pink', False)

    def _cat_color_Purple(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Purple' == item[u'Color']):
                return (u'Purple', True)
        return (u'Purple', False)

    def _cat_color_Red(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Red' == item[u'Color']):
                return (u'Red', True)
        return (u'Red', False)

    def _cat_color_Turquoise(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Turquoise' == item[u'Color']):
                return (u'Turquoise', True)
        return (u'Turquoise', False)

    def _cat_color_White(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'White' == item[u'Color']):
                return (u'White', True)
        return (u'White', False)

    def _cat_color_Yellow(self):
        info = self._info_filter['ColorRegions']
        for item in info:
            if (u'Yellow' == item[u'Color']):
                return (u'Yellow', True)
        return (u'Yellow', False)

    # .../opencv/samples/c/facedetect.cpp
    # http://opencv.willowgarage.com/documentation/python/genindex.html
    def _detectObjectFaces_CV(self):
        """Converts an image to grayscale and prints the locations of any
           faces found"""
        # http://python.pastebin.com/m76db1d6b
        # http://creatingwithcode.com/howto/face-detection-in-static-images-with-python/
        # http://opencv.willowgarage.com/documentation/python/objdetect_cascade_classification.html
        # http://opencv.willowgarage.com/wiki/FaceDetection
        # http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
        # http://www.cognotics.com/opencv/servo_2007_series/part_4/index.html

        import cv, cv2, numpy

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
          # MAY BE USE 'haarcascade_frontalface_alt_tree.xml' ALSO / INSTEAD...?!!
          )
        cascadeprofil = cv2.CascadeClassifier(
          'opencv/haarcascades/haarcascade_profileface.xml',
          )

        self._info['Faces'] = []
        scale = 1.
        # So, to find an object of an unknown size in the image the scan
        # procedure should be done several times at different scales.
        # http://opencv.itseez.com/modules/objdetect/doc/cascade_classification.html
        try:
            #image = cv.LoadImage(self.image_path)
            #img    = cv2.imread( self.image_path, 1 )
            img    = cv2.imread( self.image_path_JPEG, 1 )
            #image  = cv.fromarray(img)
            if img == None:
                raise IOError
            
            # !!! the 'scale' here IS RELEVANT FOR THE DETECTION RATE;
            # how small and how many features are detected as faces (or eyes)
            scale  = max([1., numpy.average(numpy.array(img.shape)[0:2]/500.)])
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return
        except AttributeError:
            pywikibot.output(u'WARNING: unknown file type')
            return

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
        faces = list(cascade.detectMultiScale( smallImg,
            1.1, 2, 0
            #|cv.CV_HAAR_FIND_BIGGEST_OBJECT
            #|cv.CV_HAAR_DO_ROUGH_SEARCH
            |cv.CV_HAAR_SCALE_IMAGE,
            (30, 30) ))
        #faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
        #                           cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))
        if not faces:
            faces += list(cascadeprofil.detectMultiScale( smallImg,
                1.1, 2, 0
                #|cv.CV_HAAR_FIND_BIGGEST_OBJECT
                #|cv.CV_HAAR_DO_ROUGH_SEARCH
                |cv.CV_HAAR_SCALE_IMAGE,
                (30, 30) ))
        faces = numpy.array(faces)
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
            data = { 'ID':       (i+1),
                     'Position': tuple(numpy.int_(r*scale)), 
                     'Eyes':     [], }
            data['Coverage'] = float(data['Position'][2]*data['Position'][3])/(self.image_size[0]*self.image_size[1])
            #if (c >= confidence):
            #    eyes = nestedObjects
            #    if not (type(eyes) == type(tuple())):
            #        eyes = tuple((eyes*scale).tolist())
            #    result.append( {'Position': r*scale, 'eyes': eyes, 'confidence': c} )
            #print {'Position': r, 'eyes': nestedObjects, 'confidence': c}
            for nr in nestedObjects:
                (nrx, nry, nrwidth, nrheight) = nr
                cx = cv.Round((rx + nrx + nrwidth*0.5)*scale)
                cy = cv.Round((ry + nry + nrheight*0.5)*scale)
                radius = cv.Round((nrwidth + nrheight)*0.25*scale)
                cv2.circle( img, (cx, cy), radius, color, 3, 8, 0 )
                data['Eyes'].append( (cx-radius, cy-radius, 2*radius, 2*radius) )
            result.append( data )

        # see '_drawRect'
        if result:
            #image_path_new = os.path.join('cache', '0_DETECTED_' + self.image_filename)
            image_path_new = self.image_path_JPEG.replace(u"cache/", u"cache/0_DETECTED_")
            cv2.imwrite( image_path_new, img )

        #return faces.tolist()
        self._info['Faces'] = result
        return

    # .../opencv/samples/cpp/peopledetect.cpp
    def _detectObjectPeople_CV(self):
        # http://stackoverflow.com/questions/10231380/graphic-recognition-of-people
        # https://code.ros.org/trac/opencv/ticket/1298
        # http://opencv.itseez.com/modules/gpu/doc/object_detection.html
        # http://opencv.willowgarage.com/documentation/cpp/basic_structures.html
        # http://www.pygtk.org/docs/pygtk/class-gdkrectangle.html
        
        # MAY BE USE 'haarcascade_fullbody.xml' ALSO...?!! (like face detection)

        import cv2, gtk, cv, numpy#, time

        self._info['People'] = []
        scale = 1.
        try:
            img = cv2.imread(self.image_path_JPEG, 1)

            if (img == None) or (min(img.shape[:2]) < 50) or (not img.data):
                raise IOError

            #scale  = max([1., numpy.average(numpy.array(img.shape)[0:2]/500.)])
            #scale  = max([1., numpy.average(numpy.array(img.shape)[0:2]/350.)])
            scale  = max([1., numpy.average(numpy.array(img.shape)[0:2]/300.)])
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return
        except AttributeError:
            pywikibot.output(u'WARNING: unknown file type')
            return

        # similar to face detection
        smallImg = numpy.empty( (cv.Round(img.shape[1]/scale), cv.Round(img.shape[0]/scale)), dtype=numpy.uint8 )
        gray = cv2.cvtColor( img, cv.CV_BGR2GRAY )
        smallImg = cv2.resize( gray, smallImg.shape, interpolation=cv2.INTER_LINEAR )
        smallImg = cv2.equalizeHist( smallImg )
        img = smallImg
        
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        #cv2.namedWindow("people detector", 1)
        
        found = found_filtered = []
        #t = time.time()
        # run the detector with default parameters. to get a higher hit-rate
        # (and more false alarms, respectively), decrease the hitThreshold and
        # groupThreshold (set groupThreshold to 0 to turn off the grouping completely).
        found = hog.detectMultiScale(img, 0, (8,8), (32,32), 1.05, 2)
        #t = time.time() - t
        #print("tdetection time = %gms\n", t*1000.)
        bbox = gtk.gdk.Rectangle(*(0,0,img.shape[1],img.shape[0]))
        for i in range(len(found)):
            r = gtk.gdk.Rectangle(*found[i])
            j = 0
            while (j < len(found)):
                if (j != i and r.intersect(gtk.gdk.Rectangle(*found[j])) == r):
                    break
                j += 1
            if (j == len(found)):
                found_filtered.append(r)
                #found_filtered.append(bbox.intersect(r))   # crop to image size
        result = []
        for i in range(len(found_filtered)):
            r = found_filtered[i]
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            r.x += cv.Round(r.width*0.1)
            r.width = cv.Round(r.width*0.8)
            r.y += cv.Round(r.height*0.07)
            r.height = cv.Round(r.height*0.8)
            data = { 'ID':       (i+1),
                     'Center':   (int(r.x + r.width*0.5), int(r.y + r.height*0.5)), }
            # crop to image size (because of the slightly bigger boxes)
            r = bbox.intersect(r)
            #cv2.rectangle(img, (r.x, r.y), (r.x+r.width, r.y+r.height), cv.Scalar(0,255,0), 3)
            data['Position'] = tuple(numpy.int_(numpy.array(r)*scale))
            data['Coverage'] = float(data['Position'][2]*data['Position'][3])/(self.image_size[0]*self.image_size[1])
            result.append( data )
        #cv2.imshow("people detector", img)
        #c = cv2.waitKey(0) & 255

        self._info['People'] = result
        return

    # .../opencv/samples/cpp/bagofwords_classification.cpp
    def _classifyObjectAll_CV(self, cls):
        """Uses the 'The Bag of Words model' for classification"""

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
            self._info['Classify'] = {}
            return []
        #result = list(numpy.abs(numpy.array(result)))
        (mi, ma) = (min(result), max(result))
        #for i in range(len(result)):
        #    print "%12s %.3f" % (trained[i], result[i]), ((result[i] == mi) or (result[i] == ma))

        # now make the algo working; confer also
        # http://www.xrce.xerox.com/layout/set/print/content/download/18763/134049/file/2004_010.pdf
        # http://people.csail.mit.edu/torralba/shortCourseRLOC/index.html

        self._info['Classify'] = dict([ (trained[i], abs(r)) for i, r in enumerate(result) ])
        return

    # a lot more paper and possible algos exist; (those with code are...)
    # http://www.lix.polytechnique.fr/~schwander/python-srm/
    # http://library.wolfram.com/infocenter/Demos/5725/#downloads
    # http://code.google.com/p/pymeanshift/wiki/Examples
    # (http://pythonvision.org/basic-tutorial, http://luispedro.org/software/mahotas, http://packages.python.org/pymorph/)
    def _detectSegmentColors_JSEGnPIL(self):    # may be SLIC other other too...
        #from PIL import Image
        import Image, math

        self._info['ColorRegions'] = []
        try:
            im = Image.open(self.image_path)

            # crop 25% of the image in order to give the bot a more human eye
            scale  = 0.75    # crop 25% percent (area) bounding box
            (w, h) = ( self.image_size[0]*math.sqrt(scale), self.image_size[1]*math.sqrt(scale) )
            (l, t) = ( (self.image_size[0]-w)/2, (self.image_size[1]-h)/2 )
            i = im.crop( (int(l), int(t), int(l+w), int(t+h)) )
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return

        result = []
        #h = i.histogram()   # average over WHOLE IMAGE
        (pic, scale) = self._JSEGdetectColorSegments(i)          # split image into segments first
        #(pic, scale) = self._SLICdetectColorSegments(i)          # split image into superpixel first
        hist = self._PILgetColorSegmentsHist(i, pic, scale)         #
        #pic  = self._ColorRegionsMerge_ColorSimplify(pic, hist)  # iteratively in order to MERGE similar regions
        #(pic, scale_) = self._JSEGdetectColorSegments(pic)       # (final split)
        ##(pic, scale) = self._JSEGdetectColorSegments(pic)        # (final split)
        #hist = self._PILgetColorSegmentsHist(i, pic, scale)         #
        i = 0
        # (may be do an additional region merge according to same color names...)
        for (h, coverage, (center, bbox)) in hist:
            if (coverage < 0.05):    # at least 5% coverage needed (help for debugging/log_output)
                continue

            data = self._colormathDeltaEaverageColor(h)
            data['Coverage'] = coverage
            data['ID']       = (i+1)
            data['Center']   = (int(center[0]+l), int(center[1]+t))
            data['Position'] = (int(bbox[0]+l), int(bbox[1]+t), int(bbox[2]), int(bbox[3]))
            data['Delta_R']  = math.sqrt( (self.image_size[0]/2 - center[0])**2 + \
                                          (self.image_size[1]/2 - center[1])**2 )

            result.append( data )
            i += 1

        self._info['ColorRegions'] = result
        return

    # http://stackoverflow.com/questions/2270874/image-color-detection-using-python
    # https://gist.github.com/1246268
    # colormath-1.0.8/examples/delta_e.py, colormath-1.0.8/examples/conversions.py
    # http://code.google.com/p/python-colormath/
    # http://en.wikipedia.org/wiki/Color_difference
    # http://www.farb-tabelle.de/en/table-of-color.htm
    def _detectAverageColor_PIL(self):
        #from PIL import Image
        import Image
        
        self._info['ColorAverage'] = []
        try:
            # we need to have 3 channels (but e.g. grayscale 'P' has only 1)
            i = Image.open(self.image_path).convert(mode = 'RGB')
            h = i.histogram()
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return
        
        self._info['ColorAverage'] = [self._colormathDeltaEaverageColor(h)]
        return

    def _detectProperties_PIL(self):
        import Image

        self._info['Properties'] = []
        self.image_size = (None, None)
        if self.image_fileext == u'.svg':
            import rsvg     # gnome-python2-rsvg
            svg = rsvg.Handle(self.image_path)

            # http://validator.w3.org/docs/api.html#libs
            # http://pypi.python.org/pypi/py_w3c/
            from py_w3c.validators.html.validator import HTMLValidator
            vld = HTMLValidator()
            vld.validate(self.image.fileUrl())
            valid = (True if vld.result.validity == 'true' else False)
            #print vld.errors, vld.warnings

            result = { 'Format':     u'SVG%s' % (u' (valid)' if valid else u''),
                       'Mode':       u'-',
                       'Dimensions': (svg.props.width, svg.props.height),
                       'Filesize':   os.path.getsize(self.image_path),
                       'Palette':    u'-', }
            # may be set {{validSVG}} also or do something in bot template to
            # recognize 'Format=SVG (valid)' ...
        else:
            try:
                i = Image.open(self.image_path)
            except IOError:
                pywikibot.output(u'WARNING: unknown file type')
                return

            result = { #'bands':      i.getbands(),
                       #'bbox':       i.getbbox(),
                       'Format':     i.format,
                       'Mode':       i.mode,
                       'Dimensions': i.size,
                       #'info':       i.info,
                       'Filesize':   os.path.getsize(self.image_path),
                       #'stat':       os.stat(self.image_path),
                       'Palette':    str(len(i.palette.palette)) if i.palette else u'-', }

        self.image_size = result['Dimensions']

        self._info['Properties'] = [result]
        return

    # http://stackoverflow.com/questions/2270874/image-color-detection-using-python
    # https://gist.github.com/1246268
    # colormath-1.0.8/examples/delta_e.py, colormath-1.0.8/examples/conversions.py
    # http://code.google.com/p/python-colormath/
    # http://en.wikipedia.org/wiki/Color_difference
    # http://www.farb-tabelle.de/en/table-of-color.htm
    def _colormathDeltaEaverageColor(self, h):
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
                 'RGB':       rgb, }

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

        # according to Categories available in Commons and more
        colors = { u'Black':       (  0,   0,   0),
                   u'DarkBlue':    (  0,   0, 139),
                   u'DarkCyan':    (  0, 139, 139),
                   u'LightBlue':   (173, 216, 230),
                   u'LightCyan':   (224, 255, 255),
                   u'Blue':        (  0,   0, 255),
                   u'Cyan':        (  0, 255, 255),
                   u'Turquoise':   ( 64, 224, 208),
                   u'Brown':       (165,  42,  42),
                   u'DimGray':     (105, 105, 105),
                   u'LightGray':   (211, 211, 211),
                   u'Gray':        (190, 190, 190),
                   u'DarkGreen':   (  0, 100,   0),
                   u'LightGreen':  (144, 238, 144),
                   u'Green':       (  0, 255,   0),
                   u'DarkOrange':  (	255,140,0),
                   u'Orange':      (255, 165,   0),
                   u'DarkRed':     (139,   0,   0),
                   u'DeepPink':    (255,  20, 147),
                   u'Pink':        (255, 192, 203),
                   u'DarkMagenta': (139,   0, 139),
                   u'Magenta':     (255,   0, 255),
                   u'Purple':      (160,  32, 240),
                   u'Red':         (255,   0,   0),
                   u'Violet':      (238, 130, 238),
                   u'White':       (255, 255, 255),
                   u'Yellow':      (255, 255,   0), }

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
                res = (r, c, colors[c])
        data['Color']   = res[1]
        data['Delta_E'] = res[0]
        data['RGBref']  = res[2]

        return data

    def _JSEGdetectColorSegments(self, im):
        import Image, numpy, os
        
        tmpjpg = os.path.join(os.path.abspath(os.curdir), "cache/jseg_buf.jpg")
        tmpgif = os.path.join(os.path.abspath(os.curdir), "cache/jseg_buf.gif")

        # same scale func as in '_detectObjectFaces_CV'
        scale  = max([1., numpy.average(numpy.array(im.size)[0:2]/200.)])
        #print numpy.array(im.size)/scale, scale
        try:
            smallImg = im.resize( tuple(numpy.int_(numpy.array(im.size)/scale)), Image.ANTIALIAS )
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return
        
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
        #pix = numpy.array(pic)
        #Image.fromarray(10*pix).show()
        
        os.remove( tmpgif )

        return (pic, scale)

    # http://planet.scipy.org/
    # http://peekaboo-vision.blogspot.ch/2012/05/superpixels-for-python-pretty-slic.html
    # http://ivrg.epfl.ch/supplementary_material/RK_SLICSuperpixels/index.html
    def _SLICdetectColorSegments(self, img):
        import numpy as np
        #import Image
        import slic

        im = np.array(img)
        image_argb = np.dstack([im[:, :, :1], im]).copy("C")
        #region_labels = slic.slic_n(image_argb, 1000, 10)
        region_labels = slic.slic_n(image_argb, 1000, 50)
        slic.contours(image_argb, region_labels, 10)
        #import matplotlib.pyplot as plt
        #plt.imshow(image_argb[:, :, 1:].copy())
        #plt.show()

        #pic = Image.fromarray(region_labels)
        #pic.show()

        #return (pic, 1.)
        return (region_labels, 1.)

    def _PILgetColorSegmentsHist(self, im, pic, scale):
        import Image, numpy
        
        if not (type(numpy.ndarray(None)) == type(pic)):
            pix = numpy.array(pic)
            #Image.fromarray(10*pix).show()
        else:
            pix = pic
            #Image.fromarray(255*pix/numpy.max(pix)).show()

        try:
            smallImg = im.resize( tuple(numpy.int_(numpy.array(im.size)/scale)), Image.ANTIALIAS )
        except IOError:
            pywikibot.output(u'WARNING: unknown file type')
            return

        imgsize = float(smallImg.size[0]*smallImg.size[1])
        hist = []
        for i in range(numpy.max(pix)+1):
            mask   = numpy.uint8(pix == i)*255
            (y, x) = numpy.where(mask != 0)
            center = (numpy.average(x)*scale, numpy.average(y)*scale)
            bbox   = (numpy.min(x)*scale, numpy.min(y)*scale, 
                      (numpy.max(x)-numpy.min(x))*scale, (numpy.max(y)-numpy.min(y))*scale)
            coverage = numpy.count_nonzero(mask)/imgsize
            mask = Image.fromarray( mask )
            h    = smallImg.histogram(mask)
            #smallImg.show()
            #dispImg = Image.new('RGBA', smallImg.size)
            #dispImg.paste(smallImg, mask)
            #dispImg.show()
            if (len(h) == 256):
                print "gray scale image, try to fix..."
                h = h*3
            if (len(h) == 256*4):
                print "4-ch. image, try to fix (exclude transparency)..."
                h = h[0:(256*3)]
            hist.append( (h, coverage, (center, bbox)) )
        
        return hist

    # http://www.scipy.org/SciPyPackages/Ndimage
    # http://www.pythonware.com/library/pil/handbook/imagefilter.htm
    def _ColorRegionsMerge_ColorSimplify(self, im, hist):
        # merge regions by simplifying through average color and re-running
        # JSEG again...

        import Image, numpy 
        from scipy import ndimage
        
        if not (type(numpy.ndarray(None)) == type(im)):
            pix = numpy.array(im)
        else:
            pix = im
            im  = Image.fromarray(255*pix/numpy.max(pix))

        im = im.convert('RGB')

        for j, (h, coverage, (center, bbox)) in enumerate(hist):
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
            # color frequency analysis; do not average regions with high fluctations
            #rgb2 = (
            #        sum( i*i*w for i, w in enumerate(r) ) / max(1, sum(r)),
            #        sum( i*i*w for i, w in enumerate(g) ) / max(1, sum(g)),
            #        sum( i*i*w for i, w in enumerate(b) ) / max(1, sum(b))
            #)
            #if ( 500. < numpy.average( (
            #       rgb2[0] - rgb[0]**2,
            #       rgb2[1] - rgb[1]**2,
            #       rgb2[2] - rgb[2]**2, ) ) ):
            #           continue

            mask = numpy.uint8(pix == j)*255
            mask = Image.fromarray( mask )
            #dispImg = Image.new('RGB', im.size)
            #dispImg.paste(rgb, mask=mask)
            #dispImg.show()
            im.paste(rgb, mask=mask)

        pix = numpy.array(im)
        pix[:,:,0] = ndimage.gaussian_filter(pix[:,:,0], .5)
        pix[:,:,1] = ndimage.gaussian_filter(pix[:,:,1], .5)
        pix[:,:,2] = ndimage.gaussian_filter(pix[:,:,2], .5)
        im = Image.fromarray( pix, mode='RGB' )
        #import ImageFilter
        #im = im.filter(ImageFilter.BLUR)   # or 'SMOOTH'

        return im

    def _detectObjectTrained_CV(self):
        # general (self trained) classification
        # http://www.computer-vision-software.com/blog/2009/11/faq-opencv-haartraining/

        # !!! train a own cascade classifier like for face detection used
        # !!! with 'opencv_haartraing' -> xml (file to use like in face/eye detection)
        # !!! do NOT train 'people', there is already 'haarcascade_fullbody.xml', a.o. ...
        pass

    def _recognizeOpticalText_x(self):
        # optical text recognition (tesseract?)
        # (no full recognition but just classify as 'contains text')
        pass

    def _recognizeOpticalCodes_x(self):
        # barcode and Data Matrix recognition (gocr? libdmtx/pydmtx?)
        # http://libdmtx.wikidot.com/libdmtx-python-wrapper

        from pydmtx import DataMatrix   # linux distro package
        from PIL import Image
        
        ## Write a Data Matrix barcode
        #dm_write = DataMatrix()
        #dm_write.encode("Hello, world!")
        #dm_write.save("hello.png", "png")
        
        # Read a Data Matrix barcode
        dm_read = DataMatrix()
        img = Image.open("hello.png")
        
        print dm_read.decode(img.size[0], img.size[1], buffer(img.tostring()))
        print dm_read.count()
        print dm_read.message(1)
        print dm_read.stats(1)
        
        return

gbv = Global()

def checkbot():
    """ Main function """
    # Command line configurable parameters
    limit = 100 # How many images check?
    untagged = False # Use the untagged generator
    sendemailActive = False # Use the send-email

    # default
    if len(sys.argv) < 2:
        sys.argv += ['-cat']

    # debug:    'python catimages.py -debug'
    # run/test: 'python catimages.py [-start:File:abc]'
    sys.argv += ['-family:commons', '-lang:commons']
    sys.argv += ['-noguesses']

    # try to resume last run and continue
    if os.path.exists( os.path.join('cache', 'catimages_start') ):
        import shutil
        shutil.copy2(os.path.join('cache', 'catimages_start'), os.path.join('cache', 'catimages_start.bak'))
        posfile = open(os.path.join('cache', 'catimages_start'), "r")
        firstPageTitle = posfile.read().decode('utf-8')
        posfile.close()
    else:
        firstPageTitle = None

    # Here below there are the parameters.
    for arg in pywikibot.handleArgs():
        if arg.startswith('-limit'):
            if len(arg) == 7:
                limit = int(pywikibot.input(u'How many files do you want to check?'))
            else:
                limit = int(arg[7:])
#        elif arg == '-sendemail':
#            sendemailActive = True
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = None
            elif len(arg) > 6:
                firstPageTitle = arg[7:]
            #firstPageTitle = firstPageTitle.split(":")[1:]
            #generator = pywikibot.getSite().allpages(start=firstPageTitle, namespace=6)
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                catName = u'Media_needing_categories'
            elif len(arg) > 4:
                catName = str(arg[5:])
            catSelected = catlib.Category(pywikibot.getSite(), 'Category:%s' % catName)
            generator = pagegenerators.CategorizedPageGenerator(catSelected, recurse = True)
#        elif arg.startswith('-untagged'):
#            untagged = True
#            if len(arg) == 9:
#                projectUntagged = str(pywikibot.input(u'In which project should I work?'))
#            elif len(arg) > 9:
#                projectUntagged = str(arg[10:])
        elif arg == '-noguesses':
            gbv.useGuesses = False
        elif arg.startswith('-single'):
            if len(arg) > 7:
                pageName = str(arg[8:])
            generator = [ pywikibot.Page(pywikibot.getSite(), pageName) ]
            firstPageTitle = None

    # Understand if the generator is present or not.
    try:
        generator
    except:
        pywikibot.output(u'no generator defined... EXIT.')
        sys.exit()
            
    # Define the site.
    site = pywikibot.getSite()

    # Block of text to translate the parameters set above.
    image_old_namespace = u"%s:" % site.image_namespace()
    image_namespace = u"File:"

    # A little block-statement to ensure that the bot will not start with en-parameters
    if site.lang not in project_inserted:
        pywikibot.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        return

    # Defing the Main Class.
    mainClass = CatImagesBot(site, sendemailActive = sendemailActive,
                     duplicatesReport = False, logFullError = False)
    # Untagged is True? Let's take that generator
    if untagged == True:
        generator =  mainClass.untaggedGenerator(projectUntagged, limit)
    # Ok, We (should) have a generator, so let's go on.
    # Take the additional settings for the Project
    mainClass.takesettings()
    # Not the main, but the most important loop.
    #parsed = False
    outresult = []
    for image in generator:
        if firstPageTitle:
            if (image.title() == firstPageTitle):
                pywikibot.output( u"found starting page '%s' ..." % image.title() )
                firstPageTitle = None
            else:
                #pywikibot.output( u"skipping page '%s' ..." % image.title() )
                continue

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
        resultCheck = mainClass.checkStep()
        try:
            mainClass.tag_image()
            ret = mainClass.log_output()
            if ret:
                outresult.append( ret )
        except AttributeError:
            pywikibot.output(u"ERROR: was not able to process page %s!!!\n" %\
                             image.title(asLink=True))
        limit += -1
        posfile = open(os.path.join('cache', 'catimages_start'), "w")
        posfile.write( image.title().encode('utf-8') )
        posfile.close()
        if limit <= 0:
            break
        if pywikibot.debug:
            break
        if resultCheck:
            continue

    if outresult:
        outpage = pywikibot.Page(site, u"User:DrTrigon/User:DrTrigonBot/logging")
        #outresult = [ outpage.get() ] + outresult   # append to page
        outpage.put( u"\n".join(outresult), comment="bot writing log for last run" )
        if pywikibot.simulate:
            print u"--- " * 20
            print u"--- " * 20
            print u"\n".join(outresult)

main = checkbot


# Main loop will take all the (name of the) images and then i'll check them.
if __name__ == "__main__":
    old = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S") #timezones are UTC
    try:
        checkbot()
        #main()
    finally:
        final = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S") #timezones are UTC
        delta = final - old
        secs_of_diff = delta.seconds
        pywikibot.output("Execution time: %s" % secs_of_diff)
        pywikibot.stopme()
