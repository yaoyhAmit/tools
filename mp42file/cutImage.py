import cv2
import os
import argparse
import json

# #########(wisonic)
# x = 232
# y = 140
# w = 557
# h = 583
# #########(wisonic)

#########(iTrason)
# x = 198
# y = 136
# w = 668
# h = 536
#########(iTrason)

#########(JP)
# x = 185
# y = 55
# w = 760
# h = 605

# x = 137
# y = 55
# w = 817
# h = 605
#########(JP)
# #########(BJ)
# x = 208
# y = 72
# w = 707
# h = 531
# x = 153
# y = 60
# w = 817
# h = 605
# #########(BJ)
# # #########(BJ KONICA depth2.5)
# x = 208
# y = 75
# w = 754
# h = 525
# #########(BJ)
# #########(BJ KONICA depth3)
# x = 253
# y = 75
# w = 664
# h = 525
# #########(BJ)
# #########(BJ KONICA depth3.5)
# x = 300
# y = 75
# w = 568
# h = 525
# #########(BJ)
# #########(BJ KONICA depth4)
# x = 335
# y = 75
# w = 499
# h = 525
# #########(BJ)
# #########(BJ KONICA depth4.5)
# x = 362
# y = 75
# w = 444
# h = 525
# #########(BJ)

# #########(BJ BK depth18)
# x = 270
# y = 102
# w = 754
# h = 586
# #########(BJ)

# #########(BJ KONICA depth2.5)
x = 55
y = 77
w = 784
h = 613

resize_w = 1024
resize_h = 768


parser = argparse.ArgumentParser(description='cut image tool')
parser.add_argument('--inImgPath','-inImg',help = 'The path of the original images')
parser.add_argument('--outImgPath','-outImg',help = 'The path of the image after cutting')
parser.add_argument('--inJsonPath','-inJsn',help = 'The path of the original Json')
parser.add_argument('--outJsonPath','-outJsn',help = 'The path of the Json after cutting')
parser.add_argument('--needResize','-needRs',type=bool,default=False,help = 'Need resize before cutting')
parser.add_argument('--needScaling','-needSc',type=bool,default=False,help = 'Need scaling json file after cutting')
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
                    im = cv2.imread(args.inImgPath + '/' + file)
                    if args.needResize:
                        im = cv2.resize(im,(resize_w,resize_h))
                    # draw rectangle
                    #  start point (208,72) W 753 H 540
                    # im2 = cv2.rectangle(im,(x,y),(x+w,y+h),(255,0,0),1)
                    # cv2.imwrite('7-rectangle.jpg',im2)
                    # output image
                    om = im[y:y+h,x:x+w]
                    cv2.imwrite(args.outImgPath + '/' + file,om)
    
    print('Original Json Path is :',args.inJsonPath)
    if not args.inJsonPath == None:
        ijFiles = os.listdir(args.inJsonPath)
        for file in ijFiles:
            if not os.path.isdir(file) and file.split('.')[1] == 'json':
                print('Original Json file is ', file)
                ij = open(args.inJsonPath + '/' + file)
                # load json file
                d = json.load(ij)
                polygons = d['polygons']
                params = d['params']
                scale_x = int(params['sourceW'])/int(params['clipW'])
                scale_y = int(params['sourceH'])/int(params['clipH'])
                for polygon in polygons:
                    points = polygon['points']
                    for point in points:
                        # print('point is ',point[0],point[1])
                        if args.needScaling:
                            point[0] = point[0]*scale_x - x
                            point[1] = point[1]*scale_y - y
                        else: 
                            point[0] = point[0] - x
                            point[1] = point[1] - y
                params = d['params']
                params['sourceW'] = str(w)
                params['sourceH'] = str(h)
                params['clipW'] = str(w)
                params['clipH'] = str(h)

                oj = open(args.outJsonPath + '/' + file, 'w')
                json.dump(d, oj, indent=2, ensure_ascii=False)


                
                        





