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

def digitFrequency(folder):
    # outer dictionary: position => frequencies of each digit
    # inner dictionary: digit => count
    positionalFrequency ={
        1: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        2: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        3: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        4: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        5: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        6: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0},
        7: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
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

        # Each entry in annotationData should now be of the format
        # [<class number>, <cx ratio>, <cy ratio>, <width ratio>, <height ratio>]

        # To get the correct position we assume the image is displaying the counter left-to-right and
        # so order annotationData by the cx ratio (value at index 1 of the inner array) from highest to lowest
        annotationData = sorted(annotationData, key=lambda x: x[1])

        for position, entry in enumerate(annotationData):
            digit = int(entry[0])
            positionalFrequency[position+1][digit] += 1
    
    ax = plt.gca()
    ax.set_ylabel('Number of occurrences')
    ax.set_xlabel('Digit')
    ax.set_title('Number of occurrences of each digit, grouped by position')
    plt.xticks(np.arange(0, 10, step=1))
    
    # bottom positions used to stack bar graphs
    bottom = np.array([0,0,0,0,0,0,0,0,0,0])

    # colors for each position 1-6
    colors = [None, '#003f5c', '#444e86', '#955196', '#dd5182', '#ff6e54', '#ffa600', '#fffe26']

    # reverse position frequency so 1st digit is on top
    reversedPositionFrequency = OrderedDict(sorted(positionalFrequency.items(), reverse=True))
    for position, frequencies in reversedPositionFrequency.items():

        plt.bar(np.arange(10), frequencies.values(), .7, bottom=bottom, color=colors[position])
        bottom += list(frequencies.values())

    ax.legend(labels=['7th digit', '6th digit', '5th digit', '4th digit', '3rd digit', '2nd digit', '1st digit'])
    plt.show()



if __name__ == '__main__':
    folder = ''

    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python digit-frequency.py <path/to/annotations/>")
        sys.exit(1)

    digitFrequency(folder)
