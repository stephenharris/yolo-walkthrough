import sys
import os
import subprocess
import json
from pandas import *
from util.yolo import *
import hashlib 
  
def predict(file):

    result_file = hashlib.md5(file.encode()).hexdigest() + ".result.json" 

    subprocess.check_output([
        './darknet-alex/darknet',
        'detector',
        'test', 
        'cfg/counters.data',
        'cfg/counters-yolov3-tiny.cfg',
        'weights/counters-yolov3-tiny-b633ebb_best.weights',
        file,
        '-ext_output',
        '-dont_show',
        '-out',
        result_file
    ])

    with open(result_file) as json_file:
        data = json.load(json_file)
        predictions = list(map(lambda o: Prediction(
            o['name'], 
            o['confidence'],
            o['relative_coordinates']['center_x'] - o['relative_coordinates']['width']/2,
            o['relative_coordinates']['center_y'] - o['relative_coordinates']['height']/2,
            o['relative_coordinates']['width'],
            o['relative_coordinates']['height']
        ), data[0]['objects']))

        predictions = remove_overlapping_predictions(predictions)

        # sort from left to right
        predictions.sort(key=lambda prediction: prediction.leftx)

        os.remove(result_file)

        # output classes
        return ("".join(map(lambda prediction: str(prediction.class_), predictions)))


if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Incorrect arguments. Please run python predict.py path/to/file")
        sys.exit(1)

    print(predict(sys.argv[1]))
