#-------------------------------------------------------------------------------
# Purpose:     Split image data into training and test files
# Author:      Stephen Harris
#
#-------------------------------------------------------------------------------
import os
import glob
import sys
import random
import pandas as pd
import numpy as np

def splitTrainTestData(folder, seed):
    
    random.seed(seed)

    folder = folder.rstrip('/') + '/'
    
    nonDigitalImageList = glob.glob(os.path.join(folder, '*[!d].jpg'))
    digitalImageList = glob.glob(os.path.join(folder, '*d.jpg'))

    strataImages = [
       nonDigitalImageList, digitalImageList 
    ]

    # Create and/or truncate train.txt and test.txt
    #file_train = open('train.txt', 'w+')  
    #file_test = open('test.txt', 'w+')

    if not os.path.exists(folder + 'training'):
        os.mkdir(folder + 'training')

    if not os.path.exists(folder + 'validation'):
        os.mkdir(folder + 'validation')

    if not os.path.exists(folder + 'testing'):
        os.mkdir(folder + 'testing')

    for imageList in strataImages:

        data_size = len(imageList)
        counter = 0
    
        df = pd.DataFrame(imageList)
        train, validate, test = np.split(df.sample(frac=1, random_state=seed), [int(.6*len(df)), int(.8*len(df))])

        print("{0} for training, {1} for validation, {2} for testing".format(len(train), len(validate), len(test)))

        for f in train.values:
            basename = os.path.basename(f[0])
            (file, ext) = os.path.splitext(basename)
            os.rename(f[0],folder + '/training/' + basename)
            os.rename(folder + file + '.txt', folder + 'training/' + file + '.txt')
        
        for f in validate.values:
            basename = os.path.basename(f[0])
            (file, ext) = os.path.splitext(basename)
            os.rename(f[0],folder + '/validation/' + basename)
            os.rename(folder + file + '.txt', folder + 'validation/' + file + '.txt')

        for f in test.values:
            basename = os.path.basename(f[0])
            (file, ext) = os.path.splitext(basename)
            os.rename(f[0],folder + '/testing/' + basename)
            os.rename(folder + file + '.txt', folder + 'testing/' + file + '.txt')
    
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
