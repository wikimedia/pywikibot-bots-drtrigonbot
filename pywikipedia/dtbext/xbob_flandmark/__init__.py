
# === how to compile 'xbob.flandmark' ===
# https://pypi.python.org/pypi/xbob.flandmark
#
# * adopt prefixes in buildout.cfg
# * copy bob include to build dir
#   ( e.g. cp .../pywikipedia/dtbext/_bob/include .../pywikipedia/dtbext/_bob/build/include )
# * compile with
#   ```sh
#   $ python bootstrap.py
#   $ ./bin/buildout
#   ```
#
#@inproceedings{Uricar-Franc-Hlavac-VISAPP-2012,
#  author =      {U{\\v{r}}i{\\v{c}}{\\'{a}}{\\v{r}}, Michal and Franc, Vojt{\\v{e}}ch and Hlav{\\'{a}}{\\v{c}}, V{\\'{a}}clav},
#  title =       {Detector of Facial Landmarks Learned by the Structured Output {SVM}},
#  year =        {2012},
#  pages =       {547-556},
#  booktitle =   {VISAPP '12: Proceedings of the 7th International Conference on Computer Vision Theory and Applications},
#  editor =      {Csurka, Gabriela and Braz, Jos{\'{e}}},
#  publisher =   {SciTePress --- Science and Technology Publications},
#  address =     {Portugal},
#  volume =      {1},
#  isbn =        {978-989-8565-03-7},
#  book_pages =  {747},
#  month =       {February},
#  day =         {24-26},
#  venue =       {Rome, Italy},
#  keywords =    {Facial Landmark Detection, Structured Output Classification, Support Vector Machines, Deformable Part Models},
#  prestige =    {important},
#  authorship =  {50-40-10},
#  status =      {published},
#  project =     {FP7-ICT-247525 HUMAVIPS, PERG04-GA-2008-239455 SEMISOL, Czech Ministry of Education project 1M0567},
#  www = {http://www.visapp.visigrapp.org},
#}

import sys
sys.path.append('/home/ursin/data/toolserver/pywikipedia/dtbext/xbob.flandmark/build/lib.linux-x86_64-2.7')
#sys.path.append('/home/ursin/data/toolserver/pywikipedia/dtbext/bob/build/lib64')
from xbob import flandmark
#from xbob.flandmark import *
