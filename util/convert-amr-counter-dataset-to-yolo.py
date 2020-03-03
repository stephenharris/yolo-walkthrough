# see https://stackoverflow.com/questions/10768724/why-does-python-return-0-for-simple-division-calculation
from __future__ import division
import glob
import re
from PIL import Image
import os
from collections import OrderedDict
import sys

def convertToYolo(folder):

    folder = folder.rstrip('/') + '/'
    txt_files = glob.glob( folder + "/*.txt")

    for filename in txt_files:

        # Read
        base = os.path.splitext(filename)[0]
        imageFilename = base  + '.jpg'

        f = open(filename, "r")

        contents = list(map(lambda x: x.strip(), f.read().splitlines()))
        
        data = {
            "counterPosition": None,
            "imageWidth": None,
            "imageHeight": None,
        }

        for row in contents:
            counterPositionRegex = re.match("^position: ([\d\s]+)$", row)
            if counterPositionRegex:
                data["counterPosition"] = list(map(int, counterPositionRegex.group(1).split()))
                continue
            
        im = Image.open(imageFilename)
        width, height = im.size

        data["imageWidth"] = width
        data["imageHeight"] = height

        # Validate
        if not data["counterPosition"]:
            print("************************************ invalid counter co-ordinates found in %s!" %(filename))
            continue

        # Convert to yolo
        yoloFormat = []

        position = data['counterPosition']
        yoloFormat.append(" ".join(
            (
            "counter",
            str((position[0] + (position[2]/2))/data["imageWidth"]), # x_centre/width
            str((position[1] + (position[3]/2))/data["imageHeight"]), # y_centre/height
            str(position[2]/data["imageWidth"]), # boundingBoxWidth/width
            str(position[3]/data["imageHeight"]), # boundingBoxHeight/height
            )
        ))

        text_file = open(base + ".counter.txt", "w")
        text_file.write("\n".join(yoloFormat))
        text_file.close()

if __name__ == '__main__':
    folder = ''

    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python convert-amr-counter-dataset-to-yolo.py <file-path>")
        sys.exit(1)

    convertToYolo(folder)
