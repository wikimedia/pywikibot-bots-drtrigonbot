#!/usr/bin/env python

# http://www.alecjacobson.com/weblog/?p=1039

import subprocess, re, smtplib, email.mime.text, sys

alarm = 90.

quota   = subprocess.Popen("quota -v", shell=True, stdout=subprocess.PIPE).stdout.readlines()
size    = re.findall("[\d\.]+", quota[-1])
percent = float(size[0])/float(size[1]) * 100

# show resulting output with '-v' like quota
if '-v' in sys.argv:
    print "".join(quota)
    print "Actual user space usage: %.03f%%" % percent

# if the percentage is a above some threshold then send an email
if (percent > alarm):
    # sender's and recipient's email addresses
    FROM = "drtrigon@toolserver.org"
    TO   = ["dr.trigon@surfeu.ch"]    # must be a list
    # Create a text/plain message
    msg = email.mime.text.MIMEText("".join(quota))
    msg['Subject'] = "!QUOTA! %.1f%%" % percent
    msg['From']    = FROM
    msg['To']      = ", ".join(TO)
    # Send the mail
    server = smtplib.SMTP("localhost")
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()

## update rrdtool
## http://oss.oetiker.ch/rrdtool/tut/rrdtutorial.en.html
## http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
## rrdtool create quota.rrd --start 1350165600 --step 86400 DS:quota:GAUGE:172800:U:U RRA:AVERAGE:0.5:1:30 RRA:AVERAGE:0.5:7:10
#rrdtool = subprocess.Popen("rrdtool update quota.rrd `date +%%s`:%s" % size[0], shell=True, stdout=subprocess.PIPE).stdout.readlines()
## rrdtool fetch quota.rrd AVERAGE
#rrdtool = subprocess.Popen("rrdtool graph public_html/DrTrigonBot/quota.png DEF:myquota=quota.rrd:quota:AVERAGE LINE2:myquota#FF0000", shell=True, stdout=subprocess.PIPE).stdout.readlines()
# (does not work on solaris and linux in parallel; one is 32bit the other 64bit)

# http://supportex.net/2011/09/rrd-python/
# (https://jira.toolserver.org/browse/DRTRIGON-74)
try:
    import platform
    import rrdtool

    #rrd_fn = "quota-%s.rrd" % platform.platform()
    rrd_fn = "quota-%s.rrd" % platform.system()

    if '-rrdinit' in sys.argv:
        ret = rrdtool.create(rrd_fn, "--step", "86400", "--start", '0',
         "DS:metric1:GAUGE:144000:U:U",
         "DS:metric2:GAUGE:144000:U:U",
         "RRA:AVERAGE:0.5:1:600",
         "RRA:AVERAGE:0.5:6:700",
         "RRA:AVERAGE:0.5:24:775",
         "RRA:AVERAGE:0.5:288:797",
#         "RRA:MIN:0.5:1:600",
#         "RRA:MIN:0.5:6:700",
#         "RRA:MIN:0.5:24:775",
#         "RRA:MIN:0.5:444:797",
         "RRA:MAX:0.5:1:600",
         "RRA:MAX:0.5:6:700",
         "RRA:MAX:0.5:24:775",
         "RRA:MAX:0.5:444:797")
    else:
        # update
        (metric1, metric2) = (percent, alarm)
        ret = rrdtool.update(rrd_fn, 'N:%s:%s' %(metric1, metric2));

        # show
        #for sched in ['hourly', 'daily', 'weekly', 'monthly']:
        for sched in ['monthly']:
            fn  = "/home/drtrigon/public_html/DrTrigonBot/metrics-%s.png" %(sched)
            ret = rrdtool.graph( fn, "--start", "-1%s" %(sched[0]), "--vertical-label=Quota [%]",
                 '--watermark=DrTrigonBot.TS.Quota',
#                 "-w 800",
                 "DEF:m1_num=%s:metric1:AVERAGE" % rrd_fn,
                 "DEF:m2_num=%s:metric2:AVERAGE" % rrd_fn,
                 "LINE1:m1_num#0000FF:home\\r",
                 "LINE2:m2_num#FF0000:alarm\\r",
                 "GPRINT:m1_num:AVERAGE:Avg home\: %6.0lf ",
#                 "GPRINT:m1_num:MIN:Min home\: %6.0lf \\r",
                 "GPRINT:m1_num:MAX:Max home\: %6.0lf \\r")

    if '-v' in sys.argv:
        print "RRDtool: %s" % rrdtool.fetch(rrd_fn, 'AVERAGE')[2]
except ImportError:
    pass    # rrdtool not available (linux host)
