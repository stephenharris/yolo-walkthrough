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
            "reading": None,
            "counterPosition": None,
            "digitPositions": OrderedDict(),
            "imageWidth": None,
            "imageHeight": None,
        }

        for row in contents:
            readingRegex = re.match("^reading: (\d+)$", row)

            if readingRegex:
                data["reading"] = list(map(int, list(readingRegex.group(1))))
                continue

            counterPositionRegex = re.match("^position: ([\d\s]+)$", row)
            if counterPositionRegex:
                data["counterPosition"] = list(map(int, counterPositionRegex.group(1).split()))
                continue

            digitRegex = re.match("^digit ([\d\s]+): ([\d\s]+)$", row)
            if digitRegex:
                digitKey = "digit"+digitRegex.group(1)
                data["digitPositions"][digitKey] = list(map(int, digitRegex.group(2).split()))
                continue
            
        im = Image.open(imageFilename)
        width, height = im.size

        data["imageWidth"] = width
        data["imageHeight"] = height

        # Validate
        if not data["reading"]:
            print("************************************ invalid reading found in %s!" %(filename))
            continue

        if not data["counterPosition"]:
            print("************************************ invalid counter co-ordinates found in %s!" %(filename))
            continue

        if not data["digitPositions"]:
            print("************************************ invalid digit co-ordinates found in %s!" %(filename))
            continue

        # Create a cropped copy (cropped to the counter)
        croppedImage = im.crop((
            data['counterPosition'][0],
            data['counterPosition'][1],
            data['counterPosition'][0] + data['counterPosition'][2],
            data['counterPosition'][1] + data['counterPosition'][3]
        ))
        temp = croppedImage.copy()  # <-- Instead of copy.copy(image)
        temp.save('%s-cropped.jpg' % (base), quality=100)

        # Convert to yolo
        # once for the original image, once for the cropped (to the counter) image
        yoloFormat = []

        for index, value in enumerate(data['reading'], start=1):
            position = data['digitPositions'].get("digit"+str(index))

            yoloFormat.append(" ".join(
                (
                str(value),
                str((position[0] + (position[2]/2))/data["imageWidth"]), # x_centre/width
                str((position[1] + (position[3]/2))/data["imageHeight"]), # y_centre/height
                str(position[2]/data["imageWidth"]), # boundingBoxWidth/width
                str(position[3]/data["imageHeight"]), # boundingBoxHeight/height
                )
            ))

        text_file = open(base + ".yolo", "w")
        text_file.write("\n".join(yoloFormat))
        text_file.close()

        # now convert to yolo for the cropped image
        yoloFormatCropped = []
        for index, value in enumerate(data['reading'], start=1):
            position = data['digitPositions'].get("digit"+str(index))

            croppedX = data["counterPosition"][0] #upperLeft x o-ordinate of the crop
            croppedY = data["counterPosition"][1] #upperLeft y co-ordinate of the crop
            croppedWidth = data["counterPosition"][2]
            croppedHeight = data["counterPosition"][3]

            relativeWidth=position[2]/croppedWidth
            relativeHeight=position[3]/croppedHeight

            yoloFormatCropped.append(" ".join(
                (
                str(value),
                str(max(0,min((position[0] - croppedX + (position[2]/2))/croppedWidth, 1))), # x_centre/width
                str(max(0,min((position[1] - croppedY + (position[3]/2))/croppedHeight, 1))), # x_centre/width
                str(min(relativeWidth, 1)), # boundingBoxWidth/width
                str(min(relativeHeight, 1)), # boundingBoxHeight/height
                )
            ))

        text_file = open(base + ".cropped.yolo", "w")
        text_file.write("\n".join(yoloFormatCropped))
        text_file.close()


if __name__ == '__main__':
    folder = ''

    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python convert-amr-dataset-to-yolo.py <file-path>")
        sys.exit(1)

    convertToYolo(folder)
