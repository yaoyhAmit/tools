import cv2
import numpy as np
from pathlib import Path
import os
import sys
from PIL import Image
import argparse

def iou(dt,dp,scores,c):
    if c in scores.keys():
        TP_FP_FN = scores[c]
    else:
        TP_FP_FN = [0,0,0]
    
    TP_FP_FN_File = [0,0,0]
    
    dt_c = (dt == c)
    np.sum(dt_c == True)
    np.sum(dp == 1)
    # if c == 0:
    #     dt_c[dt_c == True] = False
    #     dt_c[dt_c == False] = True
    # count TP
    mask_tmp = dt_c + dp
    mask_tmp = mask_tmp.flatten()
    TP_FP_FN_File[0] = np.sum(mask_tmp == 2)
    TP_FP_FN[0] = TP_FP_FN[0] + TP_FP_FN_File[0]

    # count FP
    mask_tmp = dp - dt_c
    mask_tmp = mask_tmp.flatten()
    TP_FP_FN_File[1] = np.sum(mask_tmp == 1)
    TP_FP_FN[1] = TP_FP_FN[1] + TP_FP_FN_File[1]

    # count FN
    mask_tmp = dt_c - dp
    mask_tmp = mask_tmp.flatten()
    TP_FP_FN_File[2] = np.sum(mask_tmp == 1)
    TP_FP_FN[2] = TP_FP_FN[2] + TP_FP_FN_File[2]

    scores[c] = TP_FP_FN

    return scores, TP_FP_FN_File

def main():
    parser = argparse.ArgumentParser(description='computing the IOU')

    parser.add_argument('--pred', required=True,
                    metavar="path or URL to predicted mask file",
                    help='path or URL to predicted mask file')

    parser.add_argument('--true', required=True,
                        metavar="path or URL to Correct result",
                        help='path or URL to Correct result') 
    parser.add_argument('--classNum', type = int, default = 2, required=False,
                        metavar="classes count",
                        help='classes count') 
    parser.add_argument('--perFile', type = bool, default = False, required=False,
                        help='print scorce per file unit') 

    mainArgs = parser.parse_args()

    classNum = mainArgs.classNum
    perFile = mainArgs.perFile

    p  = Path(mainArgs.true)    
    all_files=p.glob("*.png")

    # print result
    score_IoU = 'IoU  is '
    score_Dice = 'Dice  is '
    score_Precison = 'Precison is '
    score_Recall = 'Recall is '

    scores = {}
    i = 0
    for file_true in all_files:
        i = i + 1
        img_true = Image.open(file_true)
        data_true = np.asarray(img_true)
        for c in range(0,classNum):
            file_pred = mainArgs.pred + os.path.basename(str(file_true)).split('.')[0] + '_' + str(c) + '.png'
            
            if os.path.exists(file_pred):
                img_pred = Image.open(file_pred)
                img_pred = img_pred.resize((img_true.width,img_true.height))
                data_pred = np.asarray(img_pred).copy()
                data_pred[data_pred<=125] = 0
                data_pred[data_pred>125] = 1
                scores,TP_FP_FN_File= iou(data_true,data_pred,scores,c)
                if perFile:
                    TP_FP_FN = TP_FP_FN_File
                    Dice = 0
                    TP = np.sum(TP_FP_FN[0])
                    FP = np.sum(TP_FP_FN[1])
                    FN = np.sum(TP_FP_FN[2])
                    if TP + FP + FN > 0:
                        Dice = 2*TP/(2*TP + FP + FN)
                    tmp2 = ' : %s : %.4f ' % (c, Dice)
                    score_Dice = score_Dice + tmp2

            else:
                print('file is not exist: %s'%(file_pred))
        
                
        if perFile:
            print('file is : %s'%(file_true))
            print(score_Dice)
            score_Dice = 'Dice  is '


    # print result
    score_IoU = 'IoU  is '
    score_Dice = 'Dice  is '
    score_Precison = 'Precison is '
    score_Recall = 'Recall is '
    for k in scores.keys():
        TP_FP_FN = scores[k]
        IoU = 0
        print('TP %03d FP %03d FN %03d' % (TP_FP_FN[0],TP_FP_FN[1],TP_FP_FN[2]))
        allsum = np.sum(TP_FP_FN)
        if allsum > 0:
            IoU = TP_FP_FN[0]/allsum
        tmp = ' : %s : %.4f ' % (k, IoU)
        score_IoU = score_IoU + tmp

        Dice = 0
        TP = np.sum(TP_FP_FN[0])
        FP = np.sum(TP_FP_FN[1])
        FN = np.sum(TP_FP_FN[2])
        if TP + FP + FN > 0:
            Dice = 2*TP/(2*TP + FP + FN)
        tmp2 = ' : %s : %.4f ' % (k, Dice)
        score_Dice = score_Dice + tmp2

        Precison = 0
        if TP+FP > 0:
            Precison = TP/(TP+FP)
        tmp3 = ' : %s : %.4f ' % (k, Precison)
        score_Precison = score_Precison + tmp3

        Recall = 0
        if TP+FN > 0:
            Recall = TP/(TP+FN)
        tmp4 = ' : %s : %.4f ' % (k, Recall)
        score_Recall = score_Recall + tmp4


    print(score_IoU)
    print(score_Dice)
    print(score_Precison)
    print(score_Recall)

if __name__ == '__main__':
    main()