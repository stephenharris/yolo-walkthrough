#!python3
"""
Python 3 wrapper for identifying objects in images

Requires DLL compilation

Both the GPU and no-GPU version should be compiled; the no-GPU version should be renamed "yolo_cpp_dll_nogpu.dll".

On a GPU system, you can force CPU evaluation by any of:

- Set global variable DARKNET_FORCE_CPU to True
- Set environment variable CUDA_VISIBLE_DEVICES to -1
- Set environment variable "FORCE_CPU" to "true"


To use.

    model = YoloModel("/path/to/confg.cfg", "/path/to/weights.weights", "/path/to/meta.data")
    results = model.detect('/path/to/image.jpg', 0.25, False, False)

See the docstring of YoloModel() for parameters.

Directly viewing or returning bounding-boxed images requires scikit-image to be installed (`pip install scikit-image`)


Original *nix 2.7: https://github.com/pjreddie/darknet/blob/0f110834f4e18b30d5f101bf8f1724c34b7b83db/python/darknet.py
Windows Python 2.7 version: https://github.com/AlexeyAB/darknet/blob/fc496d52bf22a0bb257300d3c79be9cd80e722cb/build/darknet/x64/darknet.py

@author: Philip Kahn
@date: 20180503
"""
#pylint: disable=R, W0401, W0614, W0703
from ctypes import *
import math
import random
import os

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]



#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
#lib = CDLL("libdarknet.so", RTLD_GLOBAL)
hasGPU = True
if os.name == "nt":
    cwd = os.path.dirname(__file__)
    os.environ['PATH'] = cwd + ';' + os.environ['PATH']
    winGPUdll = os.path.join(cwd, "yolo_cpp_dll.dll")
    winNoGPUdll = os.path.join(cwd, "yolo_cpp_dll_nogpu.dll")
    envKeys = list()
    for k, v in os.environ.items():
        envKeys.append(k)
    try:
        try:
            tmp = os.environ["FORCE_CPU"].lower()
            if tmp in ["1", "true", "yes", "on"]:
                raise ValueError("ForceCPU")
            else:
                print("Flag value '"+tmp+"' not forcing CPU mode")
        except KeyError:
            # We never set the flag
            if 'CUDA_VISIBLE_DEVICES' in envKeys:
                if int(os.environ['CUDA_VISIBLE_DEVICES']) < 0:
                    raise ValueError("ForceCPU")
            try:
                global DARKNET_FORCE_CPU
                if DARKNET_FORCE_CPU:
                    raise ValueError("ForceCPU")
            except NameError:
                pass
            # print(os.environ.keys())
            # print("FORCE_CPU flag undefined, proceeding with GPU")
        if not os.path.exists(winGPUdll):
            raise ValueError("NoDLL")
        lib = CDLL(winGPUdll, RTLD_GLOBAL)
    except (KeyError, ValueError):
        hasGPU = False
        if os.path.exists(winNoGPUdll):
            lib = CDLL(winNoGPUdll, RTLD_GLOBAL)
            print("Notice: CPU-only mode")
        else:
            # Try the other way, in case no_gpu was
            # compile but not renamed
            lib = CDLL(winGPUdll, RTLD_GLOBAL)
            print("Environment variables indicated a CPU run, but we didn't find `"+winNoGPUdll+"`. Trying a GPU run anyway.")
else:
    lib = CDLL("./libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

copy_image_from_bytes = lib.copy_image_from_bytes
copy_image_from_bytes.argtypes = [IMAGE,c_char_p]

predict = lib.network_predict_ptr
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

init_cpu = lib.init_cpu

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict_ptr
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

predict_image_letterbox = lib.network_predict_image_letterbox
predict_image_letterbox.argtypes = [c_void_p, IMAGE]
predict_image_letterbox.restype = POINTER(c_float)

class YoloModel:

    def __init__(self, configPath = "./cfg/yolov3.cfg", weightPath = "yolov3.weights", metaPath= "./cfg/coco.data"):
        
        if not os.path.exists(configPath):
            raise ValueError("Invalid config path `"+os.path.abspath(configPath)+"`")
        if not os.path.exists(weightPath):
            raise ValueError("Invalid weight path `"+os.path.abspath(weightPath)+"`")
        if not os.path.exists(metaPath):
            raise ValueError("Invalid data file path `"+os.path.abspath(metaPath)+"`")
        
        self.netMain = load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
        self.metaMain = load_meta(metaPath.encode("ascii"))
        self.altNames = None
        self.debug = False

        # In Python 3, the metafile default access craps out on Windows (but not Linux)
        # Read the names file and create a list to feed to detect
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            self.altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass

    def setDebug(self, debug):
        self.debug = debug

    """
    Convenience function to handle the detection and returns of objects.

    Displaying bounding boxes requires libraries scikit-image and numpy

    Parameters
    ----------------
    imagePath: str
        Path to the image to evaluate. Raises ValueError if not found

    thresh: float (default= 0.25)
        The detection threshold

    showImage: bool (default= True)
        Compute (and show) bounding boxes. Changes return.

    makeImageOnly: bool (default= False)
        If showImage is True, this won't actually *show* the image, but will create the array and return it.

    Returns
    ----------------------


    When showImage is False, list of tuples like
        ('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px))
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.

    Otherwise, a dict with
        {
            "detections": as above
            "image": a numpy array representing an image, compatible with scikit-image
            "caption": an image caption
        }
    """
    def detect(self, imagePath="data/dog.jpg", thresh= 0.25, showImage= True, makeImageOnly = False):
        
        if not os.path.exists(imagePath):
            raise ValueError("Invalid image path `"+os.path.abspath(imagePath)+"`")

        assert 0 < thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
        
        im = load_image(imagePath.encode("ascii"), 0, 0)
        detections = self._detect_image(im, thresh, .5, .45)
        free_image(im)
        
        if showImage:
            try:
                from skimage import io, draw
                import numpy as np
                image = io.imread(imagePath)
                print("*** "+str(len(detections))+" Results, color coded by confidence ***")
                imcaption = []
                for detection in detections:
                    label = detection[0]
                    confidence = detection[1]
                    #pstring = label+": "+str(np.rint(100 * confidence))+"%"
                    #imcaption.append(pstring)
                    #print(pstring)
                    bounds = detection[2]
                    shape = image.shape
                    # x = shape[1]
                    # xExtent = int(x * bounds[2] / 100)
                    # y = shape[0]
                    # yExtent = int(y * bounds[3] / 100)
                    yExtent = int(bounds[3])
                    xEntent = int(bounds[2])
                    # Coordinates are around the center
                    xCoord = int(bounds[0] - bounds[2]/2)
                    yCoord = int(bounds[1] - bounds[3]/2)
                    boundingBox = [
                        [xCoord, yCoord],
                        [xCoord, yCoord + yExtent],
                        [xCoord + xEntent, yCoord + yExtent],
                        [xCoord + xEntent, yCoord]
                    ]
                    # Wiggle it around to make a 3px border
                    rr, cc = draw.polygon_perimeter([x[1] for x in boundingBox], [x[0] for x in boundingBox], shape= shape)
                    rr2, cc2 = draw.polygon_perimeter([x[1] + 1 for x in boundingBox], [x[0] for x in boundingBox], shape= shape)
                    rr3, cc3 = draw.polygon_perimeter([x[1] - 1 for x in boundingBox], [x[0] for x in boundingBox], shape= shape)
                    rr4, cc4 = draw.polygon_perimeter([x[1] for x in boundingBox], [x[0] + 1 for x in boundingBox], shape= shape)
                    rr5, cc5 = draw.polygon_perimeter([x[1] for x in boundingBox], [x[0] - 1 for x in boundingBox], shape= shape)
                    boxColor = (int(255 * (1 - (confidence ** 2))), int(255 * (confidence ** 2)), 0)
                    draw.set_color(image, (rr, cc), boxColor, alpha= 0.8)
                    draw.set_color(image, (rr2, cc2), boxColor, alpha= 0.8)
                    draw.set_color(image, (rr3, cc3), boxColor, alpha= 0.8)
                    draw.set_color(image, (rr4, cc4), boxColor, alpha= 0.8)
                    draw.set_color(image, (rr5, cc5), boxColor, alpha= 0.8)
                
                if not makeImageOnly:
                    io.imshow(image)
                    io.show()
                
                detections = {
                    "detections": detections,
                    "image": image,
                    "caption": "\n<br/>".join(imcaption)
                }
            except Exception as e:
                print("Unable to show image: "+str(e))
        
        return detections


    def _detect_image(self, im, thresh=.5, hier_thresh=.5, nms=.45):
        num = c_int(0)
        if self.debug: print("Assigned num")
        pnum = pointer(num)
        if self.debug: print("Assigned pnum")
        predict_image(self.netMain, im)
        letter_box = 0
        #predict_image_letterbox(net, im)
        #letter_box = 1
        if self.debug: print("did prediction")
        #dets = get_network_boxes(net, custom_image_bgr.shape[1], custom_image_bgr.shape[0], thresh, hier_thresh, None, 0, pnum, letter_box) # OpenCV
        dets = get_network_boxes(self.netMain, im.w, im.h, thresh, hier_thresh, None, 0, pnum, letter_box)
        if self.debug: print("Got dets")
        num = pnum[0]
        if self.debug: print("got zeroth index of pnum")
        if nms:
            do_nms_sort(dets, num, self.metaMain.classes, nms)
        if self.debug: print("did sort")
        res = []
        if self.debug: print("about to range")
        for j in range(num):
            if self.debug: print("Ranging on "+str(j)+" of "+str(num))
            if self.debug: print("Classes: "+str(self.metaMain), self.metaMain.classes, self.metaMain.names)
            for i in range(self.metaMain.classes):
                if self.debug: print("Class-ranging on "+str(i)+" of "+str(self.metaMain.classes)+"= "+str(dets[j].prob[i]))
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    if self.altNames is None:
                        nameTag = self.metaMain.names[i]
                    else:
                        nameTag = self.altNames[i]
                    if self.debug:
                        print("Got bbox", b)
                        print(nameTag)
                        print(dets[j].prob[i])
                        print((b.x, b.y, b.w, b.h))
                    res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
        if self.debug: print("did range")
        res = sorted(res, key=lambda x: -x[1])
        if self.debug: print("did sort")
        free_detections(dets, num)
        if self.debug: print("freed detections")
        return res
