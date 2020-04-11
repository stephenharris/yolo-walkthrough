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


if __name__ == '__main__':
    
    PIL.Image.MAX_IMAGE_PIXELS = None

    if len(sys.argv) < 2:
        print("Incorrect arguments. Please run python predict.py path/to/file")
        sys.exit(1)

    folder = sys.argv[1]
    folder = folder.rstrip('/') + '/'
    images = glob.glob( folder + "*.jpg")

    output = sys.argv[2]
    output = output.rstrip('/') + '/'

    matches = 0
    total = 0

    for filename in images:
        print(filename)
        base = os.path.basename(os.path.splitext(filename)[0])

        results = performDetect(
            filename, 
            0.25, 
            "./cfg/spark-counter-yolov3-tiny.cfg", 
            "weights/spark-counter-yolov3-tiny_best.weights", 
            "./cfg/spark-counter.data", 
            True, 
            True, 
            False
        )

        predictions = list(map(lambda o: Prediction(
            o[0].decode('utf-8'), 
            o[1],
            o[2][0] - o[2][2]/2,
            o[2][1] - o[2][3]/2,
            o[2][2],
            o[2][3]
        ), results['detections'])) 
        print("{0} predictions".format(len(predictions)))
        print("output " + output + base )
        im = Image.fromarray(results['image'])
        im.save(output + base + "-prediction.jpg")
        
        if(len(predictions) == 0) :
            continue

        predictions.sort(key=lambda prediction: prediction.confidence, reverse=True)
        prediction = predictions[0]
        
        im = Image.open(filename)
        width, height = im.size
        
        ratio = 1.2
        croppedImage = im.crop((
            prediction.leftx - (prediction.width * (ratio -1)),
            prediction.topy - (prediction.height * (ratio-1)),
            prediction.leftx + prediction.width * ratio,
            prediction.topy + prediction.height * ratio
        ))
        croppedImage.save(output + base + "-scaled-cropped.jpg")
    

