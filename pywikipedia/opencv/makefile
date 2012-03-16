
all: build test

build: BoWclassify.so BoWclassify

BoWclassify.so: bagofwords_classification_python.cpp
	g++ bagofwords_classification_python.cpp `pkg-config --libs --cflags opencv python` -lboost_python -o BoWclassify.so -shared -fPIC

BoWclassify: bagofwords_classification_python.cpp
	g++ bagofwords_classification_python.cpp `pkg-config --libs --cflags opencv python` -lboost_python -o BoWclassify

test: build
	-./BoWclassify
	python -c "import BoWclassify; print BoWclassify.main(0, '', '', '', '', '', [])"
	python -c "import BoWclassify; print BoWclassify.main(0, '', '', '', '', '', [str(u'äbc'.encode('latin-1'))])"

clean:
	-rm BoWclassify.so BoWclassify

