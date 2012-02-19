#!/bin/bash
# from: https://github.com/valhallasw/pywikipedia-nightly-generation/blob/master/tests.sh
# see:  http://lists.wikimedia.org/pipermail/pywikipedia-l/2012-January/007120.html
# see:  http://nedbatchelder.com/code/coverage/
#source $HOME/src/nightly/test/bin/activate
#mkdir -p $HOME/data/nightly/test/output
#cd $HOME/data/nightly/test
#rm -rf pywikipedia
#tar -xzf ../package/pywikipedia/pywikipedia-nightly.tgz
#cd pywikipedia
#cat > user-config.py << $END
#usernames['wikipedia']['en'] = 'pwb-nightly-test-runner'
#mylang='en'
#family='wikipedia'
#$END
#date > ../output/test_pywikipedia.txt
#nosetests --with-xunit --xunit-file=../output/xunit_pywikipedia.xml tests 2>> ../output/test_pywikipedia.txt
#cd ..
#rm -rf pywikipedia

echo 'nosetests/unittest with coverage'
date > ../public_html/test/DrTrigonBot.txt
nosetests 2>> ../public_html/test/DrTrigonBot.txt
#coverage report -m
coverage html --directory=../public_html/test/htmlcov/

echo 'doxygen'
date > ../public_html/doc/DrTrigonBot.txt
doxygen &>> ../public_html/doc/DrTrigonBot.txt
