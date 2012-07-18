# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 22:57:26 2012

@author: drtrigon
"""

import pickle, os


target = 'dtbext/pycolorname'
if 'pywikipedia' in os.listdir(os.curdir):
    target = 'pywikipedia/' + target
path = list(os.path.split(os.path.abspath(os.curdir)))
if target not in path:
    path.append( target )
path.append( '%s' )
path = os.path.join(*path)


def storeData(filename, data):
    output = open(path % filename, 'wb')
    # Pickle dictionary using protocol 0.
    pickle.dump(data, output)
#    # Pickle the list using the highest protocol available.
#    pickle.dump(selfref_list, output, -1)
    output.close()   
    
def loadData(filename):
    pkl_file = open(path % filename, 'rb')
    data1 = pickle.load(pkl_file)
#    pprint.pprint(data1)
#    data2 = pickle.load(pkl_file)
#    pprint.pprint(data2)
    pkl_file.close()
    return data1
