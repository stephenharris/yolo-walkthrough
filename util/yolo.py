
from collections import namedtuple

Prediction = namedtuple('Prediction', 'class_, confidence, leftx, topy, width height')

def area_of_intersection(a, b):  # returns 0 if predictions don't intersect
    dx = max(0,min(a.leftx + a.width, b.leftx + b.width) - max(a.leftx, b.leftx))
    dy = max(0, min(a.topy + a.height, b.topy + b.height) - max(a.topy, b.topy))
    return (dx*dy)/((a.width*a.height) + (b.width*b.height) - (dx*dy));

def remove_overlapping_predictions(predictions, threshold=.15):
    i = 0;
    while(i + 1 < len(predictions) and i < 10):
        j = i + 1

        while(j < len(predictions) and j < 10):
            if(area_of_intersection(predictions[i], predictions[j]) > threshold):
                removeIndex = i if predictions[i].confidence < predictions[j].confidence else j
                predictions.remove(predictions[removeIndex])
            else:
                j = j +1
        
        i = i + 1

    return predictions
