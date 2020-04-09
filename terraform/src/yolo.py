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

DATA_SOURCE_BUCKET = 'yolo-amr-inference-data-source'

def uploadToS3(file, strBucket,strKey):
    print("uploading to " + strBucket + "/" + strKey)
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(file, strBucket, strKey)

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
        name = datetime.today().strftime('%Y/%m/%d-digits-') + reading + "-" + hashValue
        
        with open('/tmp/evidence.jpg', 'wb') as f:
            f.write(imgdata)

        # Upload image to S3
        s3 = boto3.resource('s3')
        obj = s3.Object(DATA_SOURCE_BUCKET, name + '.jpg')
        obj.put(Body=imgdata)

        try:
            results = performDetect('/tmp/evidence.jpg', 0.25, "./cfg/spark-digits-yolov3-tiny", "weights/spark-digits-yolov3-tiny_best", "./cfg/digits.data", False, False, False)
            
            originalPredictions = list(map(lambda o: Prediction(
                o[0].decode('utf-8'), 
                o[1],
                o[2][0] - o[2][2]/2,
                o[2][1] - o[2][3]/2,
                o[2][2],
                o[2][3]
            ), results)) 
        
            predictions = non_maximal_suppression(originalPredictions, projected_overlap_coefficient, .15) 
            predictions = predictions[:len(reading)] # take top 5 (ordered by confidence)
        
            # sort from left to right
            predictions.sort(key=lambda prediction: prediction.leftx)
            predictedReading = str(("".join(map(lambda prediction: str(prediction.class_), predictions))))
            
            # Upload detections to S3
            obj = s3.Object(DATA_SOURCE_BUCKET, name + '.txt')
            obj.put(Body=convertToString(originalPredictions))
            
            return response({
                'detections': predictions,
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