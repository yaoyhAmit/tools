import os
import argparse
import numpy as np
import json

W = 1023
H = 768

isOffSet = True
isChangeLabel = False

parser = argparse.ArgumentParser(description='Labelme Editor')
parser.add_argument('--inJsonPath','-inJsn',help = 'The path of the original Json')
parser.add_argument('--outJsonPath','-outJsn',help = 'The path of the Json after cutting')

args = parser.parse_args()

if __name__ == '__main__':
    print('Original Json Path is :',args.inJsonPath)
    if not args.inJsonPath == None:
        ijFiles = os.listdir(args.inJsonPath)
        for file in ijFiles:
            if not os.path.isdir(file):
                # print('Original Json file is ', file)
                ij = open(args.inJsonPath + '/' + file)
                # load json file
                d = json.load(ij)

                d['imageData'] = None
                imageHeight = d['imageHeight']
                imageWidth = d['imageWidth']
                
                if isOffSet:                
                    if imageHeight == 600 and imageWidth == 800:
                        x = 135
                        y = 50
                        shapes = d['shapes']
                        for shape in shapes:
                            points = shape['points']
                            for point in points:
                                point[0] = point[0] + x
                                point[1] = point[1] + y
                        
                        d['imageHeight'] = H
                        d['imageWidth'] = W

                    elif imageHeight == 540 and imageWidth == 753:
                        x = 208
                        y = 72
                        shapes = d['shapes']
                        for shape in shapes:
                            points = shape['points']
                            for point in points:
                                point[0] = point[0] + x
                                point[1] = point[1] + y

                        d['imageHeight'] = H
                        d['imageWidth'] = W
                    elif imageHeight == 605 and imageWidth == 710:
                        x = 188
                        y = 55
                        shapes = d['shapes']
                        for shape in shapes:
                            points = shape['points']
                            for point in points:
                                point[0] = point[0] + x
                                point[1] = point[1] + y

                        d['imageHeight'] = H
                        d['imageWidth'] = W
                    else:
                        print('Original Json file can not be mondify ', file)
                        print('Original Json file Height is %d Width is %d '%(imageHeight,imageWidth))
                
                elif isChangeLabel:
                    shapes = d['shapes']
                    for shape in shapes:
                        label = shape['label']
                        if label == 'N-C5' or label == 'N-C6' or label == 'N-C7' or label == 'N-C8':
                            shape['label'] = 'N'

                oj = open(args.outJsonPath + '/' + file, 'w')
                json.dump(d, oj, indent=2, ensure_ascii=False)