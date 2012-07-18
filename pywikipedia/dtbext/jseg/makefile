CC=gcc
CP=g++
#CFLAGS = -O3 -I./jpeg-6b -L./jpeg-6b
CFLAGS = -O3 -I./jpeg-6b -L./jpeg-6b -fPIC
# CFLAGS = -O2 -I/usr1.bizet/users/deng/Software/jpeg-6b
LIBS = -ljpeg -lm
#PYTHON = `pyversions -d`
PYTHON = python`python -V 2>&1 | grep -o '[0-9]*\.[0-9]*' | head -n 1`
#CONF = `pkg-config --libs --cflags python`
CONF = -I/usr/include/$(PYTHON)  -l$(PYTHON)

#all: segdist
all: segdist_cpp segdist_cpp.so
JPG = djpeg.o cjpeg.o
XVF = xvgif.o xvgifwr.o xvmisc.o xv24to8.o
SEGF = segment.o reggrow.o jfunc.o quan.o ioutil.o imgutil.o mathutil.o  memutil.o

#segdist: main.o $(SEGF) $(XVF) $(JPG)
segdist_cpp: main.o $(SEGF) $(XVF) $(JPG)
#	$(CC) $(CFLAGS) -o segdist main.o $(SEGF) $(XVF) $(JPG) $(LIBS)
	$(CP) main_cpp.cpp $(CFLAGS) $(CONF) -lboost_python -o segdist_cpp main.o $(SEGF) $(XVF) $(JPG) $(LIBS)
#	cp segdist /new1a.maya/JSEG/software/segsun

segdist_cpp.so: main.o $(SEGF) $(XVF) $(JPG)
	$(CP) main_cpp.cpp $(CFLAGS) $(CONF) -lboost_python -o segdist_cpp.so main.o $(SEGF) $(XVF) $(JPG) $(LIBS) -shared

main.o: main.c ioutil.c imgutil.c memutil.c segment.h
segment.o: segment.c ioutil.c imgutil.c memutil.c segment.h
reggrow.o: reggrow.c ioutil.c imgutil.c memutil.c segment.h
jfunc.o: jfunc.c ioutil.c imgutil.c memutil.c segment.h
quan.o: quan.c imgutil.c mathutil.c memutil.c
ioutil.o: ioutil.c 
imgutil.o: imgutil.c
mathutil.o: mathutil.c
memutil.o: memutil.c


