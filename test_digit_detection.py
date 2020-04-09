from __future__ import generators
import glob
import sys
from yolo_lib.darknet import *
from yolo_lib.non_maximal_suppression import *
from collections import namedtuple
from yolo_lib.annotation import *
from PIL import Image
from yolo_lib.non_maximal_suppression import *
from yolo_lib.annotation import *
import PIL

#Prediction = namedtuple('Prediction', 'class_, confidence, leftx, topy, width height')

def get_reading(filename):
    annotations = Annotation.create_from_file(filename)
    # todo we sort by centreX here but leftX in prediction
    annotations.sort(key=lambda annotation: annotation.centreX)
    return ("".join(map(lambda annotation: str(annotation.className), annotations)))
        

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Incorrect arguments. Please run python predict.py path/to/file")
        sys.exit(1)

    folder = sys.argv[1]
    folder = folder.rstrip('/') + '/'
    images = glob.glob( folder + "*.jpg")

    #images = images[:10]
    results_file = open("tmp-spark-digits-results-poc-proj-0-15-best-weights.txt", "w")

    matches = 0
    total = 0

    for filename in images:

        base = os.path.splitext(filename)[0]
        ground_truth = base  + '.txt'

        actual = get_reading(ground_truth)

        results = performDetect(filename, 0.25, "./cfg/spark-digits-yolov3-tiny.cfg", "weights/spark-digits-yolov3-tiny_best.weights", "./cfg/spark-digits.data", False, False, False)
        
        predictions = list(map(lambda o: Prediction(
            o[0].decode('utf-8'), 
            o[1],
            o[2][0] - o[2][2]/2,
            o[2][1] - o[2][3]/2,
            o[2][2],
            o[2][3]
        ), results)) 

        predictions = non_maximal_suppression(predictions, projected_overlap_coefficient, .15) 
        predictions = predictions[:len(actual)] # take top 5 (ordered by confidence) TODO extend to variable coutner sizes
    
        # sort from left to right
        predictions.sort(key=lambda prediction: prediction.leftx)
        predictedReading = str(("".join(map(lambda prediction: str(prediction.class_), predictions))))
            
        if(actual == predictedReading):
            matches = matches + 1

        total =  total + 1
        
        print('%s %s %s' %(filename, actual, predictedReading))
        results_file.write('%s %s %s\n' %(filename, actual, predictedReading))

    
    print(matches/total)
    results_file.write("\n" + str(100*matches/total))
    results_file.close()

