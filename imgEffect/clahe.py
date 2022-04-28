import numpy as np
import cv2
import os
from pathlib import Path

# inPutFile = './patient23-7-m.jpg'
# outPutFile = './patient23-7-m_out-cv2clahe-5.jpg'
# inPutFile = '/media/yao/iot-hd/workspace/trainingdata-us/JJG/images/'
# outPutFile = '/media/yao/iot-hd/workspace/trainingdata-us/JJG/images_clahe/'
# inPutFile  = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images/'
# outPutFile = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images_clahe/'
inPutFile  = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images_augmentation/'
outPutFile = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images_augmentation_clahe/'

def output(inPutFile,outPutFile):
    img = cv2.imread(inPutFile, 0)
    # create a clahe object(arguments are optional)
    clahe = cv2.createCLAHE(clipLimit = 5.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img)

    cv2.imwrite(outPutFile, cl1)    

def main():
    if os.path.isfile(inPutFile):
        output(inPutFile,outPutFile)
    else:
        iPath = Path(inPutFile)
        all_files = iPath.glob('*.jpg')

        for ifile in all_files:
            inFile = inPutFile + ifile.name
            outFile = outPutFile + ifile.name
            output(inFile,outFile)


if __name__ == '__main__':
    main()
