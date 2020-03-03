
import numpy as np
from PIL import Image
from .crop import *
from ..annotation import *
from typing import List

class RotationAndCrop:

    def __init__(self, angle):
        self.angle = angle
        
    def apply(self, image, annotations: List[Annotation]):
        transformed_annotations = list(map(lambda annotation: self.__rotate_bounding_box(annotation, image), annotations))
        rotated = image.rotate(self.angle)
        
        crop = Crop(self.__calculate_crop(image.width, image.height))
    
        rotated, transformed_annotations = crop.apply(rotated, transformed_annotations)
        return rotated, transformed_annotations
    
    def __rotate_bounding_box(self, annotation, image):
        box_width = annotation.width * image.width
        box_height = annotation.height * image.height
    
        box_left = annotation.centreX* image.width - box_width/2
        box_top = annotation.centreY * image.height  - box_height/2

        rectPoints = [
            np.array([box_left, box_top]),
            np.array([box_left + box_width, box_top]),
            np.array([box_left, box_top + box_height]),
            np.array([box_left + box_width, box_top + box_height])
        ]
    
        centre = np.array([image.width/2, image.height/2])
        rotatedPoints = list(map(lambda pt: self.__rotate_point(pt, centre), rectPoints))

        minX = image.width
        minY = image.height
        maxX = 0
        maxY = 0

        for i in [0,1,2,3]:
            minX = min(minX, rotatedPoints[i][0])
            maxX = max(maxX, rotatedPoints[i][0])
            minY = min(minY, rotatedPoints[i][1])
            maxY = max(maxY, rotatedPoints[i][1])
        
        relative_width = (maxX - minX)/image.width
        relative_height = (maxY - minY)/image.height
        relative_centre_x = (maxX + minX)/(2*image.width)
        relative_centre_y = (maxY + minY)/(2*image.height)
        return Annotation(annotation.className, relative_centre_x, relative_centre_y, relative_width, relative_height)

    
    def __rotate_point(self, point, centre):
        theta = np.radians(-self.angle)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        return self.__translate(R.dot(self.__translate(point, centre)), -centre)  
    
    def __calculate_crop(self, width,height):
        theta = np.radians(self.angle)
        side_long, side_short = (width,height) if width > height else (height, width)
        scale = side_short/((side_short*np.cos(theta) + side_long*np.sin(theta)))
        
        left = ((1-scale)/2) * width
        top = ((1-scale)/2) * height
        right = ((1+scale)/2) * width
        bottom = ((1+scale)/2) * height
        return (left, top, right, bottom)
    
    def __translate(self, point, translate):
        return (point - translate)