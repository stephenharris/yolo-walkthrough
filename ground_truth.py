from __future__ import generators
import sys
import os
import subprocess
import json
from pandas import *
from util.yolo import *
import hashlib 
import random

def get_reading(filename):

    f = open(filename, "r")

    contents = list(map(lambda x: x.strip(), f.read().splitlines()))

    annotations = list(map(lambda line: YoloAnnotation.create_from_string(line), contents))
    
    # todo we sort by centreX here but leftX in prediction
    annotations.sort(key=lambda annotation: annotation.centreX)
    
    return ("".join(map(lambda annotation: str(annotation.className), annotations)))
        

class YoloAnnotation(object):

    def __init__(self, className, centreX, centreY, width, height):
        self.className = className
        self.centreX = centreX
        self.centreY = centreY
        self.width = width
        self.height = height

    # Create based on class name:#
    # 0 0.09534534534534535 0.463855421686747 0.0945945945945946 0.6626506024096386
    def create_from_string(type):
        parts = type.split()
        return YoloAnnotation(str(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]))

    create_from_string = staticmethod(create_from_string)

