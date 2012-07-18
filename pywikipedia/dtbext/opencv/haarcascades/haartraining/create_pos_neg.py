# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 12:56:38 2012

@author: ursin
"""

# http://note.sonots.com/SciSoftware/haartraining.html
# -> compile convert_cascade: g++ -o convert_cascade convert_cascade.c `pkg-config --libs --cflags opencv`
# http://www.computer-vision-software.com/blog/2009/11/faq-opencv-haartraining/
# (http://lab.cntl.kyutech.ac.jp/~kobalab/nishida/opencv/OpenCV_ObjectDetection_HowTo.pdf)
# http://code.google.com/p/tutorial-haartraining/
# -> compile mergevec by 'make mergevec' in 'HaarTraining/src/'
#    and a '-fpermissive' should be added to 'CFLAGS' in 'Makefile'
#
# for VOC2007 image data set/base
#
#  1.) read the link above
#  2.) get the e.g. VOC2007 set (as used here)
#  3.) use this script to create positive and negative images
#  4.) use: find neg/ -name '*.jpg' > negatives.dat
#  5.) use: find pos/ -name '*.jpg' > positives.dat
#           mkdir samples
#           perl createtrainsamples.pl positives.dat negatives.dat samples 7000
#  6.) use: find samples/ -name '*.vec' > samples.dat
#           sed -i 's/samples/\/home\/ursin\/Desktop\/test\/samples/g' samples.dat
#           HaarTraining/src/mergevec /home/ursin/Desktop/test/samples.dat /home/ursin/Desktop/test/samples.vec
#  7.) use: perl createtestsamples.pl positives.dat negatives.dat tests 1000
#  8.) use: nice -n 20 opencv_haartraining -data haarcascade -vec samples.vec -bg negatives.dat -nstages 20 -nsplits 2 -minhitrate 0.999 -maxfalsealarm 0.5 -npos 7000 -nneg 3019 -w 20 -h 20 -nonsym -mem 512 -mode ALL
#           (TEST WITH: opencv_traincascade !?)
#-->
#  9.) use: convert_cascade --size="20x20" haarcascade haarcascade.xml
# 10.) use: performance -data haarcascade.xml -info tests.dat -ni
#           (or: performance -data haarcascade -w 20 -h 20 -info tests.dat -ni)
#
#opencv_createsamples -img pos/000032_0000.jpg -num 10 -bg negatives.dat -vec samples.vec -maxxangle 0.6 -maxyangle 0 -maxzangle 0.3 -maxidev 100 -bgcolor 0 -bgthresh 0 -w 20 -h 20
#opencv_createsamples -vec samples.vec -w 20 -h 20


image_path    = '/home/ursin/data/toolserver/pywikipedia/opencv/VOC2007/JPEGImages'
info_path     = '/home/ursin/data/toolserver/pywikipedia/opencv/VOC2007/ImageSets/Main'
position_path = '/home/ursin/data/toolserver/pywikipedia/opencv/VOC2007/Annotations'

#filename   = 'aeroplane_trainval.txt'
filename   = 'aeroplane_train.txt'
#filename   = 'aeroplane_val.txt'

setname = 'aeroplane'

import os, BeautifulSoup, Image, shutil#, time

f = open(os.path.join(info_path, filename), 'r')

for item in f.readlines():
    (name, v) = item.split()
    v      = (v == '1')
    print name, v

    if not v:
        shutil.copyfile(os.path.join(image_path, name+'.jpg'), './neg/%s.jpg' % (name, ))
        continue

    fp  = open(os.path.join(position_path, name+'.xml'), 'r')
    img = Image.open(os.path.join(image_path, name+'.jpg'), 'r')
    #img.show()

    xml = BeautifulSoup.BeautifulStoneSoup(fp.read())
    fp.close()
    for i, obj in enumerate(xml.findAll('object')):
        if (obj.find('name').contents[0] == setname):
            bndbox = obj.bndbox
            box    = (int(bndbox.xmin.contents[0]), int(bndbox.ymin.contents[0]),
                      int(bndbox.xmax.contents[0]), int(bndbox.ymax.contents[0]))
            print box
            cropped = img.crop(box)
            #cropped.show()
            #time.sleep(5)
            cropped.save('./pos/%s_%04i.jpg' % (name, i))
    print

f.close()
