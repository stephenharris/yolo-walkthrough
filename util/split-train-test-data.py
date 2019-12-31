#-------------------------------------------------------------------------------
# Purpose:     Split image data into training and test files
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys
import random

def splitTrainTestData(folder, seed):
    
    random.seed(seed)

    folder = folder.rstrip('/') + '/'
    
    imageList = glob.glob(os.path.join(folder, '*.jpg'))

    data_size = len(imageList)

    if data_size == 0:
        print ('No .JPG images found in the specified dir!')
        return

    # Create and/or truncate train.txt and test.txt
    file_train = open('train.txt', 'w+')  
    file_test = open('test.txt', 'w+')

    counter = 0
    data_test_size = int(0.1 * data_size)
    test_array = random.sample(range(data_size), k=data_test_size)
    
    for f in imageList:
        counter += 1
        
        if counter in test_array:
            file_test.write(f + "\n")
        else:
            file_train.write(f + "\n")
                
    return
    
if __name__ == '__main__':
    folder = ''
    seed = 42
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    elif len(sys.argv) == 3:
        folder = sys.argv[1]
        seed = int(sys.argv[2])
    else:
        print("Incorrect arguments. Please run python split-train-test-data.py <file-path> [seed]")
        sys.exit(1)

    splitTrainTestData(folder, seed)
