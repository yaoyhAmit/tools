import os as os
import sys as sys
import json as json

from numpy.core.numeric import isclose
import cv2 as cv2
import numpy as np
import skimage as skimage

JSON_PATH = '/mnt/iot-hd/workspace/02.Fukushima/01.JJG/patient/'
def main():

    for cur, _dirs, files in os.walk(JSON_PATH):
        for file in files:
            with open(file) as f:
                d = json.load(f)
                print('doctor is %s'%d['doctor'])

if __name__ == '__main__':
    main()
