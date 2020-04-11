#-------------------------------------------------------------------------------
# Purpose:     Scans folder for YOLO annoted files, and displays a graph of
#              how many times a digit appears and in what position
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys
from PIL import Image
import numpy as np 
import matplotlib.pyplot as plt
from collections import OrderedDict

def counterSizes(folder):
    counterSizes ={
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0
    }

    folder = folder.rstrip('/') + '/'
    annotationList = glob.glob(os.path.join(folder, '*.txt'))
    
    if len(annotationList) == 0:
        print ('No annotations found in the specified dir!')
        return

    for (i, f) in enumerate(annotationList):

        annotation = open(f, "r")

        annotationData = map(lambda line: line.split(), annotation)

        # filter out any empty lines or lines with incomplete data
        annotationData = list(filter(lambda line: line and len(line) == 5, annotationData))
        numberOfDigits = len(annotationData)

        if (numberOfDigits < 4):
            print(f)
        
        counterSizes[numberOfDigits] += 1
    
    ax = plt.gca()
    ax.set_ylabel('Number of instances of counter sizes')
    ax.set_xlabel('Number of digits')
    plt.xticks(np.arange(3, 9, step=1))
    
    plt.bar(np.arange(3, 9, step=1), counterSizes.values(), .7, color='#003f5c')

    plt.show()



if __name__ == '__main__':
    folder = ''
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python counter-sizes.py <path/to/annotations/>")
        sys.exit(1)

    counterSizes(folder)
