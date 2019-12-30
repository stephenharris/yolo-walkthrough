#-------------------------------------------------------------------------------
# Purpose:     Rename jpg files as incrementing integers from a starting 
#              Used to convert images from multiple sources into the same naming
#              convention
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys

def rename(folder, start = 1):
    folder = folder.rstrip('/') + '/'
    start = int(start)

    imageList = glob.glob(os.path.join(folder, '*.[jJ][pP][gG]'))
    
    if len(imageList) == 0:
        print ('No .JPG images found in the specified dir!')
        return

    for (i, f) in enumerate(imageList):
        newFileName = folder + ('{0:06d}'.format(i + start)) + ".jpg"
        os.rename(f,newFileName)
        print('renaming %s as %s' %(f, newFileName))

if __name__ == '__main__':
    folder = ''
    start = 1
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    elif len(sys.argv) == 3:
        folder = sys.argv[1]
        start = sys.argv[2]
    else:
        print("Incorrect arguments. Please run python rename-files.py <file-path> [start]")
        sys.exit(1)

    rename(folder, start)
