import os
import sys
import logging
import numpy as np
from os.path import splitext
from os import listdir
from glob import glob
from PIL import Image
import cv2 as cv2

fileName = '/media/yao/iot-hd/workspace/trainingdata-us/JJG/masks-classes3/multiple/patient18-3-m.png'
def main():
    mask = Image.open(fileName)
    w, h = mask.size
    maskArry = np.array(mask)
    for x in range(w):
        for y in range(h):
            if maskArry[x][y] < 0 or maskArry[x][y] >= 4:
                print("label is wrong %d "%(maskArry[x][y]))

def opencvRead():
    mask = cv2.imread(fileName)
    W, H ,C= mask.shape[:3]
    maskArry = np.array(mask)
    for x in range(W):
        for y in range(H):
            for c in range(C):
                if maskArry[x][y][c] < 0 or maskArry[x][y][c] >= 4:
                    print("label is wrong %d "%(maskArry[x][y][c]))    

if __name__ == '__main__':
    # main()
    opencvRead()
