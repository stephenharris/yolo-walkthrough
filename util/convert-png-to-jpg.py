#-------------------------------------------------------------------------------
# Purpose:     Convert all PNG files in a folder to JPG
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys
from PIL import Image

def convertToJpg(folder):
    folder = folder.rstrip('/') + '/'

    imageList = glob.glob(os.path.join(folder, '*.[pP][nN][gG]'))
    
    if len(imageList) == 0:
        print ('No .JPG images found in the specified dir!')
        return

    for (i, f) in enumerate(imageList):
        print('converting %s' %(f))
        newFileName = os.path.splitext(f)[0]+'.jpg'
        im = Image.open(f)
        rgb_im = im.convert('RGB')
        rgb_im.save(newFileName)

if __name__ == '__main__':
    folder = ''

    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python convert-png-to-jpg.py <file-path>")
        sys.exit(1)

    convertToJpg(folder)
