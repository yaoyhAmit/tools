import cv2  #OpenCVをインポート
import numpy as np #numpyをインポート
from pathlib import Path
import os
import sys
import random
import math
import argparse
import json as json
from numba import njit,jit
from numba import types
from numba.typed import Dict
import datetime

W = 800
H = 600

def makeMask(points):
    ts = np.asarray(points).astype(np.int32)
    pts = np.array([[[e[0],e[1]] for e in ts]])
    
    mask = np.zeros((H,W,1),np.uint8)
    mask = cv2.fillPoly(mask,pts,(255))
    # binarization
    mask[mask<=125] = 0
    mask[mask>125] = 1

    return mask

@njit
def iou(masks_pred,masks_true,scores):

    for k in masks_true:
        if k in scores:
            TP_FP_FN = scores[k]
        else:
            TP_FP_FN = np.asarray([0,0,0],dtype=np.int64)

        mask_true = masks_true[k]
        if k not in masks_pred:
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
        if k in scores:
            TP_FP_FN = scores[k]
        else:
            TP_FP_FN = np.asarray([0,0,0],dtype=np.int64)

        mask_pred = masks_pred[k]
        # count FP 
        mask_tmp = mask_pred
        mask_tmp = mask_tmp.flatten()
        TP_FP_FN[1] = TP_FP_FN[1] + np.sum(mask_tmp == 1)
        
        scores[k] = TP_FP_FN

    return scores

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

    scores = Dict.empty(
        key_type=types.string,
        value_type=types.int64[:],
    )

    i = 0
    for filen_true in all_files:
        d_pred = Dict.empty(
            key_type = types.string,
            value_type=types.int32[:,:],
        )

        d_true = Dict.empty(
            key_type = types.string,
            value_type=types.int32[:,:],
        )
        # print(filen_true)
        i = i + 1
        filen_pred = mainArgs.pred + os.path.basename(str(filen_true))
        # print("Correct result file name is ", filen_true)
        
        # file exist check
        if os.path.exists(filen_pred):
            with open(filen_pred, 'r' ) as f:
                j_pred = json.load(f)
                polygons = j_pred['polygons']
                for p in polygons:
                    className = p['type']
                    d_pred[className] = np.asarray(p['points'],dtype=np.int32)
        
        # file exist check
        if os.path.exists(filen_true) :
            with open(filen_true,'r') as f:
                j_true = json.load(f)
                polygons = j_true['polygons']
                for p in polygons:
                    className = p['type']
                    d_true[className] = np.asarray(p['points'],dtype=np.int32)

        masks_pred = Dict.empty(
            key_type=types.string,
            value_type=types.int32[:,:,:],
        )
        masks_true =Dict.empty(
            key_type=types.string,
            value_type=types.int32[:,:,:],
        )

        for className in d_pred:
            data = d_pred[className]
            mask_pred = makeMask(data)
            masks_pred[className] = np.asarray(mask_pred,dtype=np.int32)

        for className in d_true:
            data = d_true[className]
            mask_true = makeMask(data)
            masks_true[className] = np.asarray(mask_true,dtype=np.int32)

        scores = iou(masks_pred,masks_true,scores)
    
    if mainArgs.eqn is not None and mainArgs.eqn > 0 and i > mainArgs.eqn:
            print('The number of evaluations is larger than expected. %d' % len(all_files) )
            sys.exit(-1)
    
    score_str = 'scores is '
    for k in scores:
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
