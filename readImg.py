import os
import sys
import logging
import numpy as np

from os.path import splitext
from os import listdir
from glob import glob
from PIL import Image, ImageOps

imgFile = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/masks-CA-N-IJV-ASM-MSM-SCM_augmentation/multiple/img10240-v001-000636_flip_ud.png'

def main(imgFile):
    mask = Image.open(imgFile)
    mask = mask.resize((550, 550))
    img_nd = np.array(mask)
    if len(img_nd.shape) == 2:
        img_nd = np.expand_dims(img_nd, axis=2)

    # HWC to CHW
    img_trans = img_nd.transpose((2, 0, 1))
    print('max is : %d min is : %d fileName is %s'%(img_trans.max(),img_trans.min(),imgFile))

if __name__ == '__main__':
    main(imgFile)
