#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test CGI python script

to make it usable from server, use: 'chmod 755 test.py', which results in
'-rwxr-xr-x 1 drtrigon users 447 2009-04-16 19:13 test.py'
"""
# http://www.scipy.org/Cookbook/Matplotlib/Using_MatPlotLib_in_a_CGI_script
# http://lost-theory.org/python/dynamicimg.html

#
# (C) Dr. Trigon, 2008, 2009, 2010
#
# Distributed under the terms of the MIT license.
# (is part of DrTrigonBot-"framework")
#
# keep the version of 'clean_sandbox2.py', 'new_user.py', 'runbotrun.py', 'replace_tmpl.py', ... (and others)
# up to date with this:
# Versioning scheme: A.B.CCCC
#  CCCC: beta, minor/dev relases, bugfixes, daily stuff, ...
#  B: bigger relases with tidy code and nice comments
#  A: really big release with multi lang. and toolserver support, ready
#     to use in pywikipedia framework, should also be contributed to it
__version__='$Id: logstat_graph.py 0.1.0013 2009-06-04 23:15:00Z drtrigon $'
#


# debug
import cgitb
cgitb.enable()


import Image,ImageDraw
import cStringIO
import cgi

import urllib2, time, re, sys

X,Y = 500, 275 #image width and height

def graph(xdata, xscale=1, xticks=10, xmajor=5, yscale=1, yticks=10, ymajor=1):
    img = Image.new("RGB", (X,Y), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    #draw some axes and markers
    for i in range(X/10):
        draw.line((i*10+30, Y-15, i*10+30, 20), fill="#DDD")
        if i % xmajor == 0:
            draw.text((xscale*(i*xticks)+15, Y-15), `i*xticks`, fill="#000")
    for j in range(1,Y/10-2):
        if i % ymajor == 0:
            draw.text((xscale*(0),Y-15-yscale*(j*yticks)), `j*yticks`, fill="#000")
    draw.line((20,Y-19,X,Y-19), fill="#000")
    draw.line((19,20,19,Y-18), fill="#000")

    #graph data (file)
    #log = file(r"c:\python\random_img\%s" % filename)
    #log = file(filename)
    for (i, value) in enumerate(xdata):
        #value = int(value.strip())
        draw.line((xscale*(i)+20,Y-20,xscale*(i)+20,Y-20-yscale*(value)), fill="#55d")

    #write to file object
    f = cStringIO.StringIO()
    img.save(f, "PNG")
    f.seek(0)

    #output to browser
    print "Content-type: image/png\n"
    print f.read()

def logstat():
    #print "Content-type: text/html\n"
    #print """<html><body>"""

    req = urllib2.Request("http://toolserver.org/~drtrigon/cgi-bin/panel.py?action=logstat&format=plain")

    f = urllib2.urlopen(req)
    buffer = f.read()
    f.close()

    #def subst(matchobj): return "{" + matchobj.group(1) + "}"
    def subst(matchobj):
        result = matchobj.group(1)
        result = re.sub("=", "':", result)
        result = re.sub(",\s", ", '", result)
        return "{'" + result + "}"
    #buffer = re.sub("time.struct_time\(.*?\)", "None", buffer)
    buffer = re.sub("time.struct_time\((.*?)\)", subst, buffer)
    stat = eval(buffer)
    #print "stat keys:", stat.keys()


#    # create needed dirs
#    basedir = os.path.realpath(os.curdir)
#    workdir = os.path.join(basedir, "logstat_" + time.strftime("%Y%m%d%H%M"))
#    try:
#        os.chdir(workdir)
#    except:
#        os.makedirs(workdir)
#    os.chdir(workdir)
#
#    logstat		= os.path.join(workdir, "logstat.txt")
#    #logstat_plot	= os.path.join(workdir, "logstat.png")
#    logstat_plot	= os.path.join(workdir, "logstat.pdf")
#
#
#    f = open(logstat, "w")

    stat['diff'] = stat['run_count'] - stat['successful_count']
    stat['warn_list'] = re.sub("\n\s", "\n", "\n".join(stat['warn_list']))[1:] + "\n"
    gettime = lambda a: str(time.strftime("%a %b %d %Y", (a['tm_year'], a['tm_mon'], a['tm_mday'], a['tm_hour'], a['tm_min'], a['tm_sec'], a['tm_wday'], a['tm_yday'], a['tm_isdst'])))
    stat['start_date'] = gettime(stat['start_date'])
    stat['end_date'] = gettime(stat['end_date'])
    #stat['logstat_plot'] = logstat_plot
    stat['logstat_plot'] = 'n/a'
    stat['script'] = sys.argv[0]
    data = """Evaluated data period from %(start_date)s to %(end_date)s.

Created by '%(script)s', see also 'http://toolserver.org/~drtrigon/cgi-bin/panel.py?action=logstat'.

Total runs:		%(run_count)s
Successful runs:	%(successful_count)s
Difference:		%(diff)s

History compressed: %(histcomp_count)s (times)

Problem rate (in %%):
(siehe '%(logstat_plot)s')

Warnings:
%(warn_list)s
""" % stat
#    f.write( data )
#
#    f.close()
    #print re.sub("\n", "<br>\n", data)
    #print stat['reliability_list']
    #print """</body></html>"""
    #return
    text = "Content-type: text/html\n"
    text += """<html><body>"""
    text += re.sub("\n", "<br>\n", data)
    text += """</body></html>"""


    # http://matplotlib.sourceforge.net/examples/api/barchart_demo.html

    x = [ item[1]*100 for item in stat['reliability_list'] ]
    return (text, x)
    N = len(x)

    ind = np.arange(N)	# the x locations for the groups
    #width = 0.35		# the width of the bars
    #width = 0.4		# the width of the bars (ok for .png)
    width = 0.5		# the width of the bars (ok for .pdf)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    #rects1 = ax.bar(ind, x, width, color='r')
    rects1 = ax.bar(ind, x, width)

    # add some
    # http://matplotlib.sourceforge.net/api/axes_api.html?highlight=set_xticks#matplotlib.axes.Axes.set_xticks
    ax.set_title('DrTrigonBot log statistics')
    ax.set_ylabel('Problem rate [%]')
    ax.set_xticks(7*np.arange(N/7))
    #ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4', 'G5') )

    #ax.legend( (rects1[0], rects2[0]), ('Men', 'Women') )
    #ax.legend( (rects1[0],), ('x',) )

    #def autolabel(rects):
    #    # attach some text labels
    #    for rect in rects:
    #        height = rect.get_height()
    #        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
    #                ha='center', va='bottom')
    #
    #autolabel(rects1)
    #autolabel(rects2)

    # http://matplotlib.sourceforge.net/api/pyplot_api.html?highlight=save#matplotlib.pyplot.savefig
    # http://matplotlib.sourceforge.net/api/pyplot_api.html?highlight=save#matplotlib.pyplot.imsave
    plt.savefig(logstat_plot)
    #plt.show()

if __name__ == "__main__":
    form = cgi.FieldStorage()
    if "action" in form:
        #read in file and graph it
        #log = file(form["filename"].value)
        #xdata = [ int(value.strip()) for (i, value) in enumerate(log) ]
        #log.close()
        (text, xdata) = logstat()
        if (form["action"].value == 'text'):
            print text
        else:
            #graph(xdata)
            graph(xdata, xscale=3, xticks=10, xmajor=1, yscale=4, yticks=10, ymajor=1)
    else:
        print "Content-type: text/html\n"
        print """<html><body>No action given</body></html>"""

