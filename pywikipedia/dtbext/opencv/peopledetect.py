# peopledetect.cpp
# https://code.ros.org/trac/opencv/ticket/1298
# http://opencv.itseez.com/modules/gpu/doc/object_detection.html
# http://opencv.willowgarage.com/documentation/cpp/basic_structures.html
# http://www.pygtk.org/docs/pygtk/class-gdkrectangle.html

import cv2, gtk, cv

import sys, time

def help():
    print(
            "\nDemonstrate the use of the HoG descriptor using\n",
            "  HOGDescriptor::hog.setSVMDetector(HOGDescriptor::getDefaultPeopleDetector());\n",
            "Usage:\n",
            "./peopledetect (<image_filename> | <image_list>.txt)\n\n")

def main(argc, argv):
    f = None

    if (argc == 1):
        print("Usage: peopledetect (<image_filename> | <image_list>.txt)\n")
        return 0
    img = cv2.imread(argv[1], 1)

    if (img.data):
        _filename = argv[1]
    else:
        f = open(argv[1], "r")
        if (not f):
            sys.stderr.write("ERROR: the specified file could not be loaded\n")
            return -1

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    cv2.namedWindow("people detector", 1)

    while True:
        filename = _filename
        if (f):
            filename = f.read(1024-2)
            if (not filename):
                break
            #while(*filename && isspace(*filename))
            #    ++filename;
            if (filename[0] == '#'):
                continue
            l = len(filename)
            while (l > 0 and filename[l-1].isspace()):
                l -= 1
            filename[l] = '\0'
            img = cv2.imread(filename, 1)
        print("%s:\n", filename)
        if (not img.data):
            continue
        
        sys.stdout.flush()
        found = found_filtered = []
        t = time.time()
        # run the detector with default parameters. to get a higher hit-rate
        # (and more false alarms, respectively), decrease the hitThreshold and
        # groupThreshold (set groupThreshold to 0 to turn off the grouping completely).
        found = hog.detectMultiScale(img, 0, (8,8), (32,32), 1.05, 2)
        t = time.time() - t
        print("tdetection time = %gms\n", t*1000.)
        for i in range(len(found)):
            r = gtk.gdk.Rectangle(*found[i])
            j = 0
            while (j < len(found)):
                #if (j != i and (r & found[j]) == r):
                if (j != i and r.intersect(gtk.gdk.Rectangle(*found[j])) == r):
                    break
                j += 1
            if (j == len(found)):
                found_filtered.append(r)
        for i in range(len(found_filtered)):
            r = found_filtered[i]
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            r.x += cv.Round(r.width*0.1)
            r.width = cv.Round(r.width*0.8)
            r.y += cv.Round(r.height*0.07)
            r.height = cv.Round(r.height*0.8)
            cv2.rectangle(img, (r.x, r.y), (r.x+r.width, r.y+r.height), cv.Scalar(0,255,0), 3)
        cv2.imshow("people detector", img)
        c = cv2.waitKey(0) & 255
        if (c == 'q' or c == 'Q' or not f):
            break
    if (f):
        f.close()
    return 0


main(len(sys.argv), sys.argv)
