
import numpy as np
from PIL import Image
from ..annotation import *
from typing import List

class Crop:

    def __init__(self, crop_boundaries):
        self.crop_boundaries = crop_boundaries
        
    def apply(self, image, annotations):
        transformed_annotations = list(map(lambda annotation: self.__adjust_bounding_box(annotation, image), annotations))
        cropped = image.crop(self.crop_boundaries) 
        return cropped, transformed_annotations
    
    def __adjust_bounding_box(self, annotation, image):
        
        
        width_abs = annotation.width * image.width
        height_abs = annotation.height * image.height
        
        box_left_abs = annotation.centreX * image.width - width_abs / 2
        box_top_abs = annotation.centreY * image.height - height_abs / 2
        box_right_abs = box_left_abs + width_abs
        box_bottom_abs = box_top_abs + height_abs

        new_image_width = min(image.width, self.crop_boundaries[2] - self.crop_boundaries[0])
        new_image_height = min(image.height, self.crop_boundaries[3] - self.crop_boundaries[1])
        
        new_box_left_abs = max(0, box_left_abs - self.crop_boundaries[0])
        new_box_top_abs = max(0, box_top_abs - self.crop_boundaries[1])
        new_box_right_abs = min(box_right_abs - self.crop_boundaries[0],  new_image_width) 
        new_box_bottom_abs = min(box_bottom_abs - self.crop_boundaries[1], new_image_height) 
        

        return Annotation(
            annotation.className,
            (new_box_left_abs + new_box_right_abs)/(2*new_image_width),
            (new_box_top_abs + new_box_bottom_abs)/(2*new_image_height),
            (new_box_right_abs - new_box_left_abs)/new_image_width,
            (new_box_top_abs - new_box_bottom_abs)/new_image_height
        )
    
        #return (annotation[0], new_centrex, new_centrey, new_box_width, new_box_height)
    