from __future__ import generators
import os
import subprocess
import json
from collections import namedtuple

Prediction = namedtuple('Prediction', 'class_, confidence, leftx, topy, width height')


def get_prediction(file, intersection_score_fn, confidence_threshold = .25, overlapping_threshold =.15):
    result_file = "/tmp/"+ os.path.basename(file) + ".result.json"   
    subprocess.check_output([
        'LD_LIBRARY_PATH=./:$LD_LIBRARY_PATH ./uselib',
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
    ], shell=True, stderr=subprocess.STDOUT) 
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
        
        #predictions = remove_low_confidence_predictions(predictions, confidence_threshold)
        
        predictions = non_maximal_supression(predictions, intersection_score_fn, overlapping_threshold) 

        #predictions = predictions[:5] # take top 5 (ordered by confidence)
        
        # sort from left to right
        predictions.sort(key=lambda prediction: prediction.leftx)   
        
        os.remove(result_file) 
        
        data[0]['predictedReading'] = str(("".join(map(lambda prediction: str(prediction.class_), predictions))))
        return data[0]


def intersection_over_union(a, b): 
    dx = max(0,min(a.leftx + a.width, b.leftx + b.width) - max(a.leftx, b.leftx))
    dy = max(0, min(a.topy + a.height, b.topy + b.height) - max(a.topy, b.topy))
    return (dx*dy)/((a.width*a.height) + (b.width*b.height) - (dx*dy)); # IoU (Jaccard_index)


def overlap_coefficient(a,b):
    dx = max(0,min(a.leftx + a.width, b.leftx + b.width) - max(a.leftx, b.leftx))
    dy = max(0, min(a.topy + a.height, b.topy + b.height) - max(a.topy, b.topy))
    return (dx*dy)/(min(a.width*a.height, b.width*b.height)); # Szymkiewicz–Simpson coefficient


def projected_overlap_coefficient(a,b):
    dx = max(0,min(a.leftx + a.width, b.leftx + b.width) - max(a.leftx, b.leftx))
    score = (dx)/(min(a.width,b.width)) # Szymkiewicz–Simpson coefficient of projection onto x-plane
    return score


def remove_low_confidence_predictions(predictions, threshold = .25):
    j = 0
    filtered = predictions.copy()
    while(j < len(predictions)):
        if(predictions[j].confidence < threshold):
            filtered.remove(predictions[j])
        j = j +1

    return filtered



def non_maximal_supression(predictions, intersection_score_fn, threshold=.15):

    if (len(predictions) < 1):
        return predictions

    filtered = list()
    original = predictions.copy()

    # Order by most confident first
    original.sort(key=lambda prediction: prediction.confidence, reverse=False)

    # Add most confident prediction to filtered list
    a = original.pop()
    filtered.append(a)

    while(len(original) > 0):

        a = original.pop()

        j = 0
        score = 0
        while(j < len(filtered) and score <= threshold):
            score = intersection_score_fn(a, filtered[j])
            if(score > threshold):
                break

            j = j + 1

        if(score <= threshold):
            filtered.append(a)
            
    return filtered