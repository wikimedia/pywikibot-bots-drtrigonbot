
# === how to compile 'bob' ===
# https://github.com/idiap/bob/wiki/Releases
# INSTALL.md:
# ## Building
#
# Once you have built and installed all dependencies locally, you should use
# CMake to build Bob itself. From your shell, do:
#
# ```sh
# $ mkdir build
# $ cd build
# $ cmake -DCMAKE_BUILD_TYPE=Release ..
# $ make
# ```
#
#@inproceedings{Anjos_ACMMM_2012,
#  author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
#  title = {Bob: a free signal processing and machine learning toolbox for researchers},
#  year = {2012},
#  month = oct,
#  booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
#  publisher = {ACM Press},
#  url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
#}

import sys
sys.path.append('/home/ursin/data/toolserver/pywikipedia/dtbext/_bob/build/lib64/python2.7/site-packages')
#sys.path.append('/home/ursin/data/toolserver/pywikipedia/dtbext/_bob/build/lib64')
#import bob
from bob import io
