# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 22:57:26 2012

@author: drtrigon
"""

import pickle, os


def storeData(filename, data):
    output = open(os.path.join(os.path.abspath(os.curdir), 'pycolorname', filename), 'wb')
    # Pickle dictionary using protocol 0.
    pickle.dump(data, output)
#    # Pickle the list using the highest protocol available.
#    pickle.dump(selfref_list, output, -1)
    output.close()   
    
def loadData(filename):
    pkl_file = open(os.path.join(os.path.abspath(os.curdir), 'pycolorname', filename), 'rb')
    data1 = pickle.load(pkl_file)
#    pprint.pprint(data1)
#    data2 = pickle.load(pkl_file)
#    pprint.pprint(data2)
    pkl_file.close()
    return data1
