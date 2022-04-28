import cv2
import os
import argparse
import numpy as np
import json

x = 137
y = 55
w = 817
h = 605

W = 1024
H = 768

parser = argparse.ArgumentParser(description='cut image tool')
parser.add_argument('--inImgPath','-inImg',help = 'The path of the original images')
parser.add_argument('--outImgPath','-outImg',help = 'The path of the image after cutting')
parser.add_argument('--inJsonPath','-inJsn',help = 'The path of the original Json')
parser.add_argument('--outJsonPath','-outJsn',help = 'The path of the Json after cutting')
parser.add_argument('--isLabelme','-islb', type = bool, default=False, required= False ,help = 'The format of json is labelme or amit')
# parser.add_argument('--needResize','-needRs',type=bool,default=False,help = 'Need resize before cutting')
args = parser.parse_args()

if __name__ == '__main__':
    print('Original Image Path is :',args.inImgPath)
    if not args.inImgPath == None:
        imFiles = os.listdir(args.inImgPath)
        for file in imFiles:
            if not os.path.isdir(file):
                if file.split('.')[1] == 'jpg' or file.split('.')[1] == 'jpeg':
                    print('Original file is',file)
                    # input image
                    img = cv2.imread(args.inImgPath + '/' + file)
                    h = img.shape[0]
                    w = img.shape[1]
                    blank_img = np.zeros((H, W, 3), np.uint8)
                    blank_img[y:y+h,x:x+w] = img
                    cv2.imwrite(args.outImgPath + '/' + file, blank_img)

    print('Original Json Path is :',args.inJsonPath)
    isLabelme = args.isLabelme
    if not args.inJsonPath == None:
        ijFiles = os.listdir(args.inJsonPath)
        for file in ijFiles:
            if not os.path.isdir(file):
                print('Original Json file is ', file)
                ij = open(args.inJsonPath + '/' + file)
                # load json file
                d = json.load(ij)

                # The format of json is amit
                if not isLabelme:
                    polygons = d['polygons']
                    for polygon in polygons:
                        points = polygon['points']
                        for point in points:
                            # print('point is ',point[0],point[1]) 
                            point[0] = point[0] + x
                            point[1] = point[1] + y
                    params = d['params']
                    params['sourceW'] = str(w)
                    params['sourceH'] = str(h)
                    params['clipW'] = str(w)
                    params['clipH'] = str(h)
                
                # The format of json is labelme
                else:
                    shapes = d['shapes']
                    for shape in shapes:
                        points = shape['points']
                        for point in points:
                            # print('point is ',point[0],point[1]) 
                            point[0] = point[0] + x
                            point[1] = point[1] + y

                oj = open(args.outJsonPath + '/' + file, 'w')
                json.dump(d, oj, indent=2, ensure_ascii=False)