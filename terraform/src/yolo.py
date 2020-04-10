from __future__ import print_function, generators

import os
import subprocess
import boto3
import base64
from datetime import datetime
import hashlib 
import json
from tools import *
from darknet import *
from PIL import Image

DATA_SOURCE_BUCKET = 'yolo-amr-inference-data-source'

def uploadToS3(file, strBucket,strKey):
    print("uploading to " + strBucket + "/" + strKey)
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(file, strBucket, strKey)

def downloadFromS3(strBucket, strKey, destination):
    s3 = boto3.resource('s3')
    s3.Bucket(strBucket).download_file(strKey, destination)
    print("downloaded" + strBucket + "/" + strKey + " to " + destination)

def convertToString(predictions):
    string_predictions = list(map(lambda prediction:
        prediction.class_
        + " " + str(prediction.leftx + (prediction.width/2))
        + " " + str(prediction.topy + (prediction.height/2))
        + " " + str(prediction.width)
        + " " + str(prediction.height)
        + " " + str(prediction.confidence)
    , predictions))
    return "\n".join(string_predictions)
        
def handler(event, context):
    try:
        payload = json.loads(event['body'])
        imgdata = base64.b64decode(payload['evidence'])
        reading = payload['reading']
        hashValue = hashlib.md5(payload['evidence'].encode()).hexdigest()
        name = datetime.today().strftime('%Y/%m/%d-') + reading + "-" + hashValue
        
        with open('/tmp/original.jpg', 'wb') as f:
            f.write(imgdata)

        # Upload image to S3
        s3 = boto3.resource('s3')
        obj = s3.Object(DATA_SOURCE_BUCKET, name + '-counter.jpg')
        obj.put(Body=imgdata)

        try:
            downloadFromS3(DATA_SOURCE_BUCKET, 'spark-counter-yolov3-tiny_best.weights', '/tmp/spark-counter-yolov3-tiny_best.weights')
            results = performDetect('/tmp/original.jpg', 0.25, "./cfg/spark-counter-yolov3-tiny.cfg", "/tmp/spark-counter-yolov3-tiny_best.weights", "./cfg/counter.data", False, False, False, True)
            
            counterPredictions = list(map(lambda o: Prediction(
                o[0].decode('utf-8'), 
                o[1],
                o[2][0] - o[2][2]/2,
                o[2][1] - o[2][3]/2,
                o[2][2],
                o[2][3]
            ), results)) 

            print("{0} predictions".format(len(counterPredictions)))
            

            if(len(counterPredictions) == 0) :
                print("no predictions found");
                return response({
                    'error': "Counter not found",
                    'detections': [],
                    'predictedReading': null
                })

            counterPredictions.sort(key=lambda prediction: prediction.confidence, reverse=True)
            counterPrediction = counterPredictions[0]
        
            im = Image.open('/tmp/original.jpg')
            
            ratio = 1.2
            cropLeft = counterPrediction.leftx - (counterPrediction.width * (ratio -1))
            cropTop = counterPrediction.topy - (counterPrediction.height * (ratio-1))
            cropRight = counterPrediction.leftx + counterPrediction.width * ratio
            cropBottom = counterPrediction.topy + counterPrediction.height * ratio
            croppedImage = im.crop((cropLeft, cropTop, cropRight, cropBottom))

            # Upload counter prediction
            obj = s3.Object(DATA_SOURCE_BUCKET, name + '-counter.txt')
            obj.put(Body=convertToString(counterPredictions))

            # Upload scaled image
            croppedImage.save("/tmp/scaled-cropped.jpg", format="JPEG");
            with open('/tmp/scaled-cropped.jpg', 'rb') as f:
                uploadToS3(f, DATA_SOURCE_BUCKET, name + '-scaled-cropped.jpg');


        except subprocess.CalledProcessError as e:
            print('Error finding counter =============>')
            print(e.output)

        # Now we have found the counter, and cropped it, find digits in the counter region

        try:
            downloadFromS3(DATA_SOURCE_BUCKET, 'spark-digits-yolov3-tiny_best.weights', '/tmp/spark-digits-yolov3-tiny_best.weights')
            results = performDetect('/tmp/scaled-cropped.jpg', 0.25, "./cfg/spark-digits-yolov3-tiny.cfg", "/tmp/spark-digits-yolov3-tiny_best.weights", "./cfg/digits.data", False, False, False, True)
            originalPredictions = list(map(lambda o: Prediction(
                o[0].decode('utf-8'), 
                o[1],
                o[2][0] - o[2][2]/2,
                o[2][1] - o[2][3]/2,
                o[2][2],
                o[2][3]
            ), results)) 

            print("{0} predictions digits".format(len(originalPredictions)))
                    
            predictions = non_maximal_suppression(originalPredictions, projected_overlap_coefficient, .15) 
            predictions = predictions[:len(reading)] # take top 5 (ordered by confidence)
        
            # sort from left to right
            predictions.sort(key=lambda prediction: prediction.leftx)
            predictedReading = str(("".join(map(lambda prediction: str(prediction.class_), predictions))))
            
            # Upload detections to S3
            obj = s3.Object(DATA_SOURCE_BUCKET, name + '-scaled-cropped.txt')
            obj.put(Body=convertToString(originalPredictions))

            # Shift predictions by cropped image to position digit bounding boxes on original image
            shiftedPredictions = [];
            for prediction in predictions:
                shiftedPredictions.append(
                    Prediction(
                        prediction.class_,
                        prediction.confidence,
                        cropLeft + prediction.leftx,
                        cropTop + prediction.topy,
                        prediction.width,
                        prediction.height
                    )
                )
            
            return response({
                'digits': shiftedPredictions,
                'counter': counterPrediction,
                'predictedReading': predictedReading
            })

        except subprocess.CalledProcessError as e:
            print('Error=============>')
            print(e.output)

    except Exception as e:
        print('Error -------------------->e')
        print(e)
        raise e
    return 0 


def response(data, statusCode = 200):
    response = {
        "statusCode": statusCode,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }
    return response