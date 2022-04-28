import cv2
import os
import sys
import argparse
from pathlib import Path
import json as json
import numpy as np
import copy

input_path = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images/'
output_path = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/images_augmentation/'

def augmentJsonFile(iPath, oPath, file):
    jpath = iPath + file.name
    jpath_o = oPath + file.name
    jpath_flip_ud = oPath + file.stem + '_flip_ud' + file.suffix
    jpath_flip_lr = oPath + file.stem + '_flip_lr' + file.suffix
    jpath_flip_ud_lr = oPath + file.stem + '_flip_ud_lr' + file.suffix
    jpath_rotate_90_clockwise = oPath + file.stem + '_rotate_90_clockwise' + file.suffix
    jpath_rotate_90_counterclockwise = oPath + file.stem + '_rotate_90_counterclockwise' + file.suffix
    jpath_rotate_180 = oPath + file.stem + '_rotate_180' + file.suffix
    with open(jpath) as f:
        d = json.load(f)
        d_flip_ud = copy.deepcopy(d)
        d_flip_lr = copy.deepcopy(d)
        d_flip_ud_lr = copy.deepcopy(d)
        d_rotate_90_clockwise = copy.deepcopy(d)
        d_rotate_90_counterclockwise = copy.deepcopy(d)
        d_rotate_180 = copy.deepcopy(d)

        with open(jpath_o, 'w') as f_o:
            json.dump(d,f_o)
        height = d['imageHeight']
        width = d['imageWidth']
        #上下反転
        shapes = d_flip_ud['shapes']
        for shape in shapes:
            points = shape['points']
            for point in points:
                point[1] = height - point[1]

        with open(jpath_flip_ud, 'w') as f_ud:
            json.dump(d_flip_ud,f_ud)

        #左右反転
        shapes = d_flip_lr['shapes']
        for shape in shapes:
            points = shape['points']
            for point in points:
                point[0] = width - point[0]

        with open(jpath_flip_lr, 'w') as f_lr:
            json.dump(d_flip_lr,f_lr)

        #上下左右反転
        shapes = d_flip_ud_lr['shapes']
        for shape in shapes:
            points = shape['points']
            for point in points:
                point[0] = width - point[0]
                point[1] = height - point[1]

        with open(jpath_flip_ud_lr, 'w') as f_ud_lr:
            json.dump(d_flip_ud_lr,f_ud_lr)
        
        #時計回りに90度
        shapes = d_rotate_90_clockwise['shapes']
        d_rotate_90_clockwise['imageHeight'] = width
        d_rotate_90_clockwise['imageWidth'] = height
        for shape in shapes:
            points = shape['points']
            for point in points:
                tmp = point[0]
                point[0] = height - point[1]
                point[1] = tmp

        with open(jpath_rotate_90_clockwise, 'w') as f_rotate_90_clockwise:
            json.dump(d_rotate_90_clockwise,f_rotate_90_clockwise)
        

        # 反時計回りに90度
        shapes = d_rotate_90_counterclockwise['shapes']
        d_rotate_90_counterclockwise['imageHeight'] = width
        d_rotate_90_counterclockwise['imageWidth'] = height
        for shape in shapes:
            points = shape['points']
            for point in points:
                tmp = point[0]
                point[0] = point[1]
                point[1] = width - tmp

        with open(jpath_rotate_90_counterclockwise, 'w') as f_rotate_90_counterclockwise:
            json.dump(d_rotate_90_counterclockwise,f_rotate_90_counterclockwise)
        
        # 180度
        shapes = d_rotate_180['shapes']
        for shape in shapes:
            points = shape['points']
            for point in points:
                point[0] = width - point[0]
                point[1] = height - point[1]

        with open(jpath_rotate_180, 'w') as f_rotate_180:
            json.dump(d_rotate_180,f_rotate_180)

def main():
    parser = argparse.ArgumentParser(description='Image date augmentaiton')

    parser.add_argument('--inPath', required=True,
                        metavar="path or URL to original image files",
                        help='path or URL to original image files') 
    parser.add_argument('--outPath', required=True, 
                        metavar="path or URL to augmentation image files",
                        help='path or URL to augmentation image files') 
    parser.add_argument('--isGray', required=False, default = False, type = bool, 
                        metavar="path or URL to augmentation image files",
                        help='path or URL to augmentation image files')
    parser.add_argument('--isJson', required=False, default = False, type = bool, 
                        metavar="path or URL is json files",
                        help='path or URL is json files')

    mainArgs = parser.parse_args()

    input_path = mainArgs.inPath
    output_path = mainArgs.outPath
    isGray = mainArgs.isGray
    isJson = mainArgs.isJson

    iPath = Path(input_path)
    if isGray:
        all_files = iPath.glob('*.png')
    elif isJson:
        all_files = iPath.glob('*.json')
    else: 
        all_files = iPath.glob('*.jpg')
    
    

    i = 0
    for ifile in all_files:
        if isJson:
            augmentJsonFile(input_path, output_path, ifile)
        else:
            if isGray:
                img = cv2.imread(input_path + ifile.name, cv2.IMREAD_GRAYSCALE)
            else:
                img = cv2.imread(input_path + ifile.name)
            
            cv2.imwrite(output_path + ifile.stem + ifile.suffix,img)
            #上下反転
            img_flip_ud = cv2.flip(img, 0)
            cv2.imwrite(output_path + ifile.stem + '_flip_ud' + ifile.suffix,img_flip_ud)
            #左右反転
            img_flip_lr = cv2.flip(img, 1)
            cv2.imwrite(output_path + ifile.stem + '_flip_lr' + ifile.suffix,img_flip_lr)
            #上下左右反転
            img_flip_ud_lr = cv2.flip(img, -1)
            cv2.imwrite(output_path + ifile.stem + '_flip_ud_lr' + ifile.suffix,img_flip_ud_lr)

            #時計回りに90度
            img_rotate_90_clockwise = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite(output_path + ifile.stem + '_rotate_90_clockwise' + ifile.suffix, img_rotate_90_clockwise)
            # 反時計回りに90度
            img_rotate_90_counterclockwise = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(output_path + ifile.stem + '_rotate_90_counterclockwise' + ifile.suffix, img_rotate_90_counterclockwise)
            # 180度
            img_rotate_180 = cv2.rotate(img, cv2.ROTATE_180)
            cv2.imwrite(output_path + ifile.stem + '_rotate_180' + ifile.suffix, img_rotate_180)


if __name__ == '__main__':
    main()
