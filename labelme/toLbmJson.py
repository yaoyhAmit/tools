import os
import sys
import json
import argparse
from pathlib import Path
import math

mainArgs = None

# 胸椎旁
filterClass = {'P','PVS','RIB'}

def simplifyPoints(points):
    resPoints=[]
    p1 = None
    for p in points:
        if p1 is None:
            p1 = p
            p2 = p
            resPoints.append(p1)
        else:
            p2 = p
        # compute the distance between two points
        distance = math.sqrt(((p1[0]-p2[0])**2) + ((p1[1]-p2[1])**2))
        if distance > mainArgs.distance:
            resPoints.append(p2)
            p1 = p2
    
    return resPoints



def main():

    parser = argparse.ArgumentParser(description='transform My Json to Labelmes Json.')

    parser.add_argument('--imagePath',required=True,
                        help='the relative path between the image file and the Json file exp ./')
    parser.add_argument('--SJsonPath',required=True,
                        help='Source json path')
    parser.add_argument('--DJsonPath',required=True,
                        help='Destliation json path')
    parser.add_argument('--imageHeight',required=False,
                        help='the height of image file')
    parser.add_argument('--imageWidth',required=False,
                        help='the width of image file')
    parser.add_argument('--distance',required=False,default=0,type=int,
                        help='if you want to simlify points,you can set the distance between two points')
    
    global mainArgs
    mainArgs = parser.parse_args()

    sp = Path(mainArgs.SJsonPath)

    all_files = sp.glob('*.json')

    for sf in all_files:
        djson = {}
        djson['version'] = '4.5.6'
        djson['flags'] = {}

        with open(sf, 'r') as f:
            sjson = json.load(f)

        djson['shapes'] = []
        polygons_pred = sjson['polygons']
        scale_x = int(sjson['params']['sourceW'])/int(sjson['params']['clipW'])
        scale_y = int(sjson['params']['sourceH'])/int(sjson['params']['clipH'])
        for p in polygons_pred:
            shape = {}
            if p['type'] in filterClass:
                shape['label'] = p['type']
                if mainArgs.distance > 0:
                    resPoints = simplifyPoints(p['points'])
                else:
                    resPoints = p['points']
                if not(scale_x == 1 and scale_y == 1) :
                    for p in resPoints:
                        p[0] = p[0]*scale_x
                        p[1] = p[1]*scale_y
                shape['points'] = resPoints
                shape['group_id'] = None
                shape['shape_type'] = 'polygon'
                shape['flags'] = {}

                djson['shapes'].append(shape)

        djson['imagePath'] = mainArgs.imagePath + os.path.basename(str(sf)).split('.', 1)[0] + '.jpg'
        djson['imageData'] = None

        if mainArgs.imageHeight is not None:
            djson['imageHeight'] = int(mainArgs.imageHeight)
        else:
            djson['imageHeight'] = int(sjson['params']['sourceH'])
        
        if mainArgs.imageWidth is not None:
            djson['imageWidth'] = int(mainArgs.imageWidth)
        else:
            djson['imageWidth'] = int(sjson['params']['sourceW'])
        
        with open(mainArgs.DJsonPath + os.path.basename(str(sf)),'w') as f:
            json.dump(djson, f , indent=4)


if __name__ == "__main__":
    main()
