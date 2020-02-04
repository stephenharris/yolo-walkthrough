from __future__ import print_function, generators

import urllib
import os
import subprocess
import boto3

import json
from tools import *
from darknet import *

DATA_SOURCE_BUCKET = 'yolo-amr-inference-data-source'

def downloadFromS3(strBucket,strKey,strFile):
    print("downloading " + strBucket + "/" + strKey + " to " + strFile)
    s3_client = boto3.client('s3')
    s3_client.download_file(strBucket, strKey, strFile)


def handler(event, context):
    try:
        payload = json.loads(event['body'])
        
        localImgFilepath = '/tmp/image.jpg'

        downloadFromS3(DATA_SOURCE_BUCKET, payload['s3key'], localImgFilepath)
        try:
            results = performDetect(localImgFilepath, 0.25, "./cfg/counters-yolov3-tiny.cfg", "weights/counters-yolov3-tiny-b633ebb_best.weights", "./cfg/counters.data", False, False, False)
            
            predictions = list(map(lambda o: Prediction(
                o[0].decode('utf-8'), 
                o[1],
                o[2][0] - o[2][2]/2,
                o[2][1] - o[2][3]/2,
                o[2][2],
                o[2][3]
            ), results)) 
        
            predictions = non_maximal_supression(predictions, projected_overlap_coefficient, .15) 
            #predictions = predictions[:5] # take top 5 (ordered by confidence)
        
            # sort from left to right
            predictions.sort(key=lambda prediction: prediction.leftx)
            predictedReading = str(("".join(map(lambda prediction: str(prediction.class_), predictions))))
            
            print(predictions)
            print(predictedReading)
            
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
        "headers": {},
        "body": json.dumps(data)
    }
    return response