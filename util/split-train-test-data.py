#-------------------------------------------------------------------------------
# Purpose:     Split image data into training and test files
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys

def splitTrainTestData(folder):
    folder = folder.rstrip('/') + '/'

    imageList = glob.glob(os.path.join(folder, '*.jpg'))
    
    if len(imageList) == 0:
        print ('No .JPG images found in the specified dir!')
        return

    # Create and/or truncate train.txt and test.txt
    file_train = open('train.txt', 'w+')  
    file_test = open('test.txt', 'w+')

    # Percentage of images to be used for the test set
    percentage_test = 10

    # Populate train.txt and test.txt
    counter = 1  
    index_test = round(100 / percentage_test)      

    for pathAndFilename in imageList:
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        if counter == index_test:
            counter = 1
            file_test.write(folder + title + '.jpg' + "\n")
        else:
            file_train.write(folder + title + '.jpg' + "\n")
            counter = counter + 1  

if __name__ == '__main__':
    folder = ''

    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python split-train-test-data.py <file-path>")
        sys.exit(1)

    splitTrainTestData(folder)
