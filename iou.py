import cv2  #OpenCVをインポート
import numpy as np #numpyをインポート
from pathlib import Path
import os
import sys
import random
import math
import argparse
import json as json
import datetime

# $User shall customize below part
W = 800
H = 600

def makeMask(points):
    ts = np.asarray(points).astype(np.int32)
    pts = np.array([[[e[0],e[1]] for e in ts]])
    
    mask = np.zeros((H,W,1))
    mask = cv2.fillPoly(mask,pts,(255))
    # binarization
    mask[mask<=125] = 0
    mask[mask>125] = 1

    return mask

def iou(d_pred,d_true,scores):

    masks_pred ={}
    masks_true ={}
    polygons_pred = d_pred['polygons']
    for polygon in polygons_pred:
        className = polygon['type']
        data = polygon['points']
 
        mask_pred = makeMask(data)
        masks_pred[className] = mask_pred
        # while(1):
        #     cv2.imshow('mask image',mask_pred)
        #     k = cv2.waitKey(1) & 0xFF
        #     if k == 27:
        #         break
        
        # cv2.destroyAllWindows()

    polygon_true = d_true['polygons']
    for polygon in polygon_true:
        className = polygon['type']
        data = polygon['points']

        mask_true = makeMask(data)
        masks_true[className] = mask_true
    
    for k in masks_true:
        if k in scores.keys():
            TP_FP_FN = scores[k]
        else:
            TP_FP_FN = [0,0,0]

        mask_true = masks_true[k]
        if k not in masks_pred.keys():
            # count FN 
            mask_tmp = mask_true
            mask_tmp = mask_tmp.flatten()
            TP_FP_FN[2] = TP_FP_FN[2] + np.sum(mask_tmp == 1)
        else:
            mask_pred = masks_pred[k]
            # count TP
            mask_tmp = mask_true + mask_pred
            mask_tmp = mask_tmp.flatten()
            TP_FP_FN[0] = TP_FP_FN[0] + np.sum(mask_tmp == 2)

            # count FP
            mask_tmp = mask_pred - mask_true
            mask_tmp = mask_tmp.flatten()
            TP_FP_FN[1] = TP_FP_FN[1] + np.sum(mask_tmp == 1)
            
            # count FN
            mask_tmp = mask_true - mask_pred
            mask_tmp = mask_tmp.flatten()
            TP_FP_FN[2] = TP_FP_FN[2] + np.sum(mask_tmp == 1)

            # delete mask
            masks_pred.pop(k)
        
        scores[k] = TP_FP_FN
    
    for k in masks_pred:
        if k in scores.keys():
            TP_FP_FN = scores[k]
        else:
            TP_FP_FN = [0,0,0]

        mask_pred = masks_pred[k]
        # count FP 
        mask_tmp = mask_pred
        mask_tmp = mask_tmp.flatten()
        TP_FP_FN[1] = TP_FP_FN[1] + np.sum(mask_tmp == 1)
        
        scores[k] = TP_FP_FN

    return scores

                    

    # IoU,TP,FP,FN = 0,0,0,0

    # height = img_model.shape[0]
    # width = img_model.shape[1]

    # print("height",height)
    # print("width",width)

    # for i in range(height):
    #     for j in range(width):
    #         # if any(img_model[i][j] == np.array([255,0,0])):
    #         #     # print(img_model[i][j])
    #         # if any(img_model[i][j] == np.array([255,0,0])):
    #         #     # print(img_model[i][j])
    #         # if any(img_model[i][j] == np.array([255,0,0])):
    #         #     # print(img_model[i][j])
    #         if all(img_model[i][j] == color): #色だったら
    #             if all((img_label[i][j]) == np.array([255,255,255])): #正解画像(ラベル)
    #                 TP = TP + 1
    #             else:
    #                 FP = FP + 1
    #         elif  all(img_label[i][j] == np.array([255,255,255])):
    #             if all(img_model[i][j] != color):
    #                 FN = FN + 1
    #                 # print(img_label[i][j])

    # print("(TP,FP,FN)=(",TP,",",FP,",",FN,")")
    # if TP + FP + FN > 0:
    #     IoU = TP/(TP + FP + FN)
    # print("IoT:", IoU)

    # return IoU

def main():

    parser = argparse.ArgumentParser(description='Detect image file by  Mask R-CNN.')

    parser.add_argument('--pred', required=True,
                        metavar="path or URL to predicted JSON file",
                        help='path or URL to predicted JSON file')
    
    parser.add_argument('--true', required=True,
                        metavar="path or URL to Correct result",
                        help='path or URL to Correct result')

    parser.add_argument('--eqn', required=False, type=int,default=0,
                        metavar="exam questions count",
                        help='Minimum number of images evaluated')
    
    parser.add_argument('--w', required=False, type=int,default=800,
                        metavar="the width of image",
                        help='the width of image')
    
    parser.add_argument('--h', required=False, type=int,default=600,
                        metavar="the height of image",
                        help='the height of image')

    mainArgs = parser.parse_args()

    if mainArgs.w is not None:
        W = mainArgs.w
    
    if mainArgs.h is not None:
        H = mainArgs.h

    p  = Path(mainArgs.true)
    # ファイル名の条件指定
    all_files=p.glob("*.json")

    scores = {}
    i = 0
    for filen_true in all_files:
        # print(filen_true)
        i = i + 1
        filen_pred = mainArgs.pred + os.path.basename(str(filen_true))
        # print("Correct result file name is ", filen_true)
        
        # file exist check
        if os.path.exists(filen_pred):
            with open(filen_pred, 'r' ) as f:
                d_pred = json.load(f)
        else:
            d_pred = {}
            d_pred['polygons'] = []
        
        # file exist check
        if os.path.exists(filen_true) :
            with open(filen_true,'r') as f:
                d_true = json.load(f)
        else:
            d_true = {}
            d_true['polygons'] = []

        scores = iou(d_pred,d_true,scores)
    
    if mainArgs.eqn is not None and mainArgs.eqn > 0 and i > mainArgs.eqn:
            print('The number of evaluations is larger than expected. %d' % len(all_files) )
            sys.exit(-1)
    
    score_str = 'scores is '
    for k in scores.keys():
        TP_FP_FN = scores[k]
        # if TP + FP + FN > 0:
        # IoU = TP/(TP + FP + FN)
        IoU = 0
        print('TP %03d FP %03d FN %03d' % (TP_FP_FN[0],TP_FP_FN[1],TP_FP_FN[2]))
        allsum = np.sum(TP_FP_FN)
        if allsum > 0:
            IoU = TP_FP_FN[0]/allsum
        # tmp = ' : %s : %.3f ' % (k, pow(IoU,0.5) * 100)
        tmp = ' : %s : %.4f ' % (k, IoU)
        score_str = score_str + tmp
    
    print(score_str)


if __name__ == '__main__':
    dt_now = datetime.datetime.now()
    print('start time:',dt_now)
    main()
    dt_now = datetime.datetime.now()
    print('end time:',dt_now)

