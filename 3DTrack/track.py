from cmath import pi
from mpl_toolkits.mplot3d import axes3d, Axes3D
import matplotlib.pyplot as plt
import numpy as np
import csv
import codecs
import math
import os
import json as json
import argparse
# import mayavi.mlab
from PIL import Image

W_PIX = 1024
H_PIX = 768
########## depth 20(iTrason)
# W = 397.6
# H = 298.2
# X_OFFSET = 76.8  # mm
# Y_OFFSET = 52.8 # mm
# W_US = 259.4
# H_US = 200
########## depth 20(iTrason)
########## depth 4(WISONIC)
# W = 70.4
# H = 52.8
# X_OFFSET = 16  # mm
# Y_OFFSET = 9.7 # mm
# W_US = 38.3
# H_US = 40
########## depth 4(WISONIC)
########## depth 10(WISONIC)
# W = 176.0
# H = 132
# X_OFFSET = 68.9  # mm
# Y_OFFSET = 24.2 # mm
# W_US = 38
# H_US = 100
########## depth 10(WISONIC)
########## depth 18(BK)
W = 307.2
H = 230.4
X_OFFSET = 81.3  # mm
Y_OFFSET = 30.3 # mm
W_US = 225.9
H_US = 180

# X_RATIO = W/W_PIX  # mm/pixel
# Y_RATIO = H/H_PIX   # mm/pixel
X_RATIO = 0.3  # mm/pixel
Y_RATIO = 0.3  # mm/pixel

X_Po = W_PIX/2
Y_Po = H_PIX/2

X_P0 = (X_OFFSET+W_US)*W_PIX/W
Y_P0 = (Y_OFFSET+H_US)*H_PIX/H

X_P1 = (X_OFFSET+W_US)*W_PIX/W
Y_P1 = (Y_OFFSET)*H_PIX/H

X_P2 = (X_OFFSET)*W_PIX/W
Y_P2 = (Y_OFFSET)*H_PIX/H

X_P3 = (X_OFFSET)*W_PIX/W
Y_P3 = (Y_OFFSET+H_US)*H_PIX/H


# PX = (W_US/2)/1000 # m
PX = (W_US/2) # mm
PY = 0  # m

global mainArgs

logo_points=[]
logo_label = [] 

def loadJson(fileName):
    ts = []
    points=[]
    label = []    
    # file exist check
    if os.path.exists(fileName):
        with open(fileName, 'r' ) as f:
            d_pred = json.load(f)
            if d_pred['shapes'] and d_pred['shapes'][0]:
                for i in range(len(d_pred['shapes'])):
                    if i == 0 :
                        points = d_pred['shapes'][i]['points']
                        label = [d_pred['shapes'][i]['label']] * len(points)
                        # if mainArgs.needBorder:
                        #     points.insert(0,[X_Po,Y_Po])
                        #     points.insert(1,[X_P0,Y_P0])
                        #     points.insert(2,[X_P1,Y_P1])
                        #     points.insert(3,[X_P2,Y_P2])
                        #     points.insert(4,[X_P3,Y_P3])
                        #     label.insert(0,'centre')
                        #     label.insert(1,'border')
                        #     label.insert(2,'border')
                        #     label.insert(3,'border')
                        #     label.insert(4,'border')
                    else:
                        points.extend(d_pred['shapes'][i]['points'])
                        label_tmp = [d_pred['shapes'][i]['label']] * len(d_pred['shapes'][i]['points'])
                        label.extend(label_tmp)
                # ts = np.asarray(points).astype(np.float)
    # elif mainArgs.needBorder:
    #     points=[]
    #     points.insert(0,[X_Po,Y_Po])
    #     points.insert(1,[X_P0,Y_P0])
    #     points.insert(2,[X_P1,Y_P1])
    #     points.insert(3,[X_P2,Y_P2])
    #     points.insert(4,[X_P3,Y_P3])
    #     # ts = np.asarray(points).astype(np.float)
    #     label.insert(0,'centre')
    #     label.insert(1,'border')
    #     label.insert(2,'border')
    #     label.insert(3,'border')
    #     label.insert(4,'border')

    if mainArgs.needBorder:
        points.insert(0,[X_Po,Y_Po])
        points.insert(1,[X_P0,Y_P0])
        points.insert(2,[X_P1,Y_P1])
        points.insert(3,[X_P2,Y_P2])
        points.insert(4,[X_P3,Y_P3])
        # ts = np.asarray(points).astype(np.float)
        label.insert(0,'centre')
        label.insert(1,'border')
        label.insert(2,'border')
        label.insert(3,'border')
        label.insert(4,'border')
        # points,label =  pixel2point('./log-a.PNG',points,label)
    if mainArgs.needLogo:
        points.extend(logo_points)
        label.extend(logo_label)
    
    # ts = np.asarray(points).astype(np.float)
    return points, label

def writeCSV(ids,x,y,z,csvfile):
    csvfile = csvfile.split('.csv')[0] + '-' + str(ids[0]) + '.csv'
    with open(csvfile,mode='w') as csvoutput:
        fieldName = ['id','x','y','z']
        
        csv_writer = csv.writer(csvoutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(fieldName)
        for i in range(len(ids)):
            csv_writer.writerow([ids[i],x[len(x)-1-i],y[len(y)-1-i],z[len(z)-1-i]])

def writeCSV2(ids,x,y,z,csvfile):
    with open(csvfile,mode='w') as csvoutput:
        fieldName = ['id','x','y','z']
        csv_writer = csv.writer(csvoutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(fieldName)
        for i in range(len(ids)):
            csv_writer.writerow([ids[i],x[i],y[i],z[i]])

# def show(prefix,path,usCSVOut,pointCSVOut):

#     csvFile = open(path, "r")
#     reader = csv.reader(csvFile)

#     X = []
#     Y = []
#     Z = []

#     X1 = []
#     Y1 = []
#     Z1 = []
#     ids = []
#     index = 1
#     for row in reader:
#         # ignore first row
#         if reader.line_num == 1:
#             continue
#         x = float(row[1])
#         y = float(row[2])
#         z = float(row[3])
#         roll = float(row[4])
#         pitch = float(row[5])
#         yaw = float(row[6])
#         # X.append(x)
#         # Y.append(y)
#         # Z.append(z)
#         fileName = '%s%06d%s'%(prefix,index,'.json')
#         ts = loadJson(fileName)
#         for e in ts:
#             ids.append(index)
#             X.append(x)
#             Y.append(y)
#             Z.append(z)

#             x1 = (e[0] * X_RATIO - X_OFFSET)/1000
#             y1 = (e[1] * Y_RATIO - Y_OFFSET)/1000
#             d = (((x1 - PX) ** 2) + ((y1 - PY) ** 2)) ** 0.5

#             x1 = x1 - PX
#             y1 = y1 - PY
#             # if x1 == PX:
#             #     angle = 90
#             # elif x1 > PX:
#             #     angle = math.atan((y1-PY)/(x1-PX))
#             # else:
#             #     angle = 90 + math.atan((y1-PY)/(PX-x1))
#             # px = x + y1*math.cos(math.radians(p-90)) + x1*math.sin(math.radians(y))
#             # py = y + x1*math.cos(math.radians(r)) + y1*math.sin(math.radians(y))
#             # pz = z + y1*math.cos(math.radians(p)) + x1*math.sin(math.radians(r))
#             # px = x - x1*math.cos(math.radians(roll))*math.cos(math.radians(90-yaw)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(90-pitch))
#             # py = y + x1*math.cos(math.radians(roll))*math.cos(math.radians(yaw))
#             # pz = z + x1*math.cos(math.radians(yaw))*math.sin(math.radians(roll)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(pitch))

#             if x1 == 0:
#                 angle = 90
#             elif x1 > 0:
#                 angle = math.degrees(math.atan(y1/x1))
#             else:
#                 angle = math.degrees(math.atan(y1/x1))

#             px = x - x1*math.cos(math.radians(roll))*math.cos(math.radians(90-yaw)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(90-pitch))
#             if angle > 0:
#                 py = y + d*math.cos(math.radians(yaw))*math.cos(math.radians(roll-angle))
#             else:
#                 py = y - d*math.cos(math.radians(yaw))*math.cos(math.radians(roll-angle))
#             pz = z + x1*math.cos(math.radians(yaw))*math.sin(math.radians(roll)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(pitch))


#             X1.append(px)
#             Y1.append(py)
#             Z1.append(pz)

#         index=index + 1

#     writeCSV(ids,X,Y,Z,usCSVOut)
#     writeCSV(ids,X1,Y1,Z1,pointCSVOut)

#     # new a figure and set it into 3d
#     fig = plt.figure()
#     ax = fig.gca(projection='3d')

#     # set figure information
#     ax.set_title(path)
#     ax.set_xlabel("x")
#     ax.set_ylabel("y")
#     ax.set_zlabel("z")

#     # draw the figure, the color is r = read
#     figure = ax.plot(X, Y, Z, c='r')
#     figure = ax.plot(X1, Y1, Z1, c='b')

#     plt.show()


# def makePoints(i,j,roll,pitch,yaw,ps):

#     x = 1
#     y = 1
#     z = 1

#     PX = 30
#     PY = 0
    
#     X1 = []
#     Y1 = []
#     Z1 = []

#     for index in range(10):
#         # x1 = 32
#         # y1 = 1
#         # x1 = x1 + i*index
#         # y1 = y1 + j*index
#         # # x1 = x1 + 100 * math.cos(index)
#         # # y1 = y1 + 100* math.sin(index)

#         # x1 = x1 - PX
#         # y1 = y1 - PY
#         # z1 = y1 - z

#         # px = x1
#         # py = y1
#         # pz = z1
#         px = ps[index][0]
#         py = ps[index][1]
#         pz = ps[index][2]

#         # # #rotate about the X axis 
#         px = px
#         py = py*math.cos(math.radians(roll)) - pz*math.sin(math.radians(roll))
#         pz = py*math.sin(math.radians(roll)) + pz*math.cos(math.radians(roll))

#         # # #rotate about the Y axis 
#         px = px*math.cos(math.radians(pitch)) + pz*math.sin(math.radians(pitch))
#         py = py
#         pz = -px*math.sin(math.radians(pitch)) + pz*math.cos(math.radians(pitch)) 

#         # # #rotate about the Z axis 
#         px = px*math.cos(math.radians(yaw)) - py*math.sin(math.radians(yaw))
#         py = px*math.sin(math.radians(yaw)) + py*math.cos(math.radians(yaw)) 
#         pz = pz

#         # px = px*math.cos(math.radians(pitch)) - pz*math.sin(math.radians(pitch)) +  px*math.cos(math.radians(yaw)) - py*math.sin(math.radians(yaw))
#         # py = py*math.cos(math.radians(roll)) - pz*math.sin(math.radians(roll)) + py*math.cos(math.radians(yaw)) + px*math.sin(math.radians(yaw))
#         # pz = pz*math.cos(math.radians(roll)) + py*math.sin(math.radians(roll)) + pz*math.cos(math.radians(pitch)) + px*math.sin(math.radians(pitch))

#         # d = ((x1 ** 2) + (y1 ** 2)) ** 0.5
#         # if x1 == 0:
#         #     angle = 90
#         # elif x1 > 0:
#         #     angle = math.degrees(math.atan(y1/x1))
#         # else:
#         #     angle = math.degrees(math.atan(y1/x1))

#         # # px = x - x1*math.cos(math.radians(roll))*math.cos(math.radians(90-yaw)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(90-pitch))
#         # px = x - x1*math.cos(math.radians(90-yaw)) - y1*math.cos(math.radians(90-pitch))
#         # if angle > 0:
#         #     py = y + d*math.cos(math.radians(yaw))*math.cos(math.radians(roll-angle)) 
#         #     pz = z - d*math.cos(math.radians(yaw))*math.cos(math.radians(90-angle+roll)) - y1*math.cos(math.radians(pitch))
#         # else:
#         #     py = y - d*math.cos(math.radians(yaw))*math.cos(math.radians(roll-angle)) 
#         #     pz = z + d*math.cos(math.radians(yaw))*math.cos(math.radians(90-angle+roll)) - y1*math.cos(math.radians(pitch))
#         # # py = y + x1*math.cos(math.radians(yaw))*math.cos(math.radians(roll-angle))
#         # # pz = z + x1*math.cos(math.radians(yaw))*math.sin(math.radians(roll)) - y1*math.cos(math.radians(roll))*math.cos(math.radians(pitch))
        

#         X1.append(px)
#         Y1.append(py)
#         Z1.append(pz)
#         # print (('x1,y1: %f , %f')%(x1,y1))
#         # print (('px,py,pz: %f , %f, %f')%(px,py,pz))

#     return X1,Y1,Z1

def makePointsByMatrix(roll,pitch,yaw,ps):

    r = math.radians(roll)
    p = math.radians(pitch)
    y = math.radians(yaw)

    # Rx = np.mat([[1, 0, 0],
    #             [0, math.cos(r), -math.sin(r)],
    #             [0, math.sin(r), math.cos(r)]])

    # Ry = np.mat([[math.cos(p), 0, math.sin(p)],
    #             [0, 1, 0],
    #             [-math.sin(p), 0, math.cos(p)]])

    # Rz = np.mat([[math.cos(y), -math.sin(y), 0],
    #             [math.sin(y), math.cos(y), 0],
    #             [0, 0, 1]])

    # R = Rz*Ry*Rx

    # R = Ry*Rx*Rz
    # R = Rx*Rz*Ry #candidate NO2
    
    # R = Rz*Rx*Ry #candidate NO1
    # R = Rx*Ry*Rz
    # R = Ry*Rz*Rx    

    # R = Rz*Rx*Ry #candidate NO1

    # R = np.mat([[math.cos(y)*math.cos(p), (math.cos(y)*math.sin(p)*math.sin(r) - math.sin(y)*math.cos(r)), (math.cos(y)*math.sin(p)*math.cos(r) + math.sin(y)*math.sin(r))],
    #            [math.sin(y)*math.cos(p), (math.sin(y)*math.sin(p)*math.sin(r)+math.cos(y)*math.cos(r)),    (math.sin(y)*math.sin(p)*math.cos(r) - math.cos(y)*math.sin(r))],
    #            [-math.sin(p),            math.cos(p)*math.sin(r),                                       math.cos(p)*math.cos(r)]])

    # # pr = ps*R
    # ps = np.matrix(ps).T
    # pr = R*ps
    # return np.squeeze(pr[0,:].tolist()),np.squeeze(pr[1,:].tolist()),np.squeeze(pr[2,:].tolist())

    x = math.cos(y)*math.cos(p)*ps[0][0] + (math.cos(y)*math.sin(p)*math.sin(r) - math.sin(y)*math.cos(r))*ps[0][1] + (math.cos(y)*math.sin(p)*math.cos(r) + math.sin(y)*math.sin(r))*ps[0][2]

    y = math.sin(y)*math.cos(p)*ps[0][0] + (math.sin(y)*math.sin(p)*math.sin(r)+math.cos(y)*math.cos(r))*ps[0][1] + (math.sin(y)*math.sin(p)*math.cos(r) - math.cos(y)*math.sin(r))*ps[0][2]

    z = -math.sin(p)*ps[0][0] + math.cos(p)*math.sin(r)*ps[0][1] + math.cos(p)*math.cos(r)*ps[0][2]
    return (x,y,z)

def transformation(ps):

    x_offset = 537.603638
    y_offset = 36.841675
    z_offset = -272.224274
    offset = [x_offset, y_offset, z_offset]

    # R = np.mat([[0.790700, 0.601094, -0.116095],
    #      [-0.090357, -0.072973, -0.993232],
    #      [-0.605498, 0.795839, -0.003387]])
    # pr = ps*R - offset

    R = np.mat([[0.790700, 0.601094, -0.116095, 537.603638],
        [-0.090357, -0.072973, -0.993232, 36.841675],
        [-0.605498, 0.795839, -0.003387, -272.224274],
        [0.000000, 0.000000, 0.000000, 1.000000]])
    
    pr = ps*R

    return np.squeeze(pr[:,0].tolist()),np.squeeze(pr[:,1].tolist()),np.squeeze(pr[:,2].tolist())

def show2(prefix,path,usCSVOut,pointCSVOut):

    csvFile = open(path, "r")
    reader = csv.reader(csvFile)

    X = []
    Y = []
    Z = []

    X1 = []
    Y1 = []
    Z1 = []
    ids = []
    IDS = []
    index = 1
    for row in reader:
        # ignore first row
        if reader.line_num == 1:
            continue
        x = float(row[1])*1000
        y = float(row[2])*1000
        z = float(row[3])*1000
        roll = float(row[4])
        pitch = float(row[5])
        yaw = float(row[6])
        # X.append(x)
        # Y.append(y)
        # Z.append(z)
        fileName = '%s%06d%s'%(prefix,index,'.json')
        ts,label = loadJson(fileName)
        ids = []
        for e in ts:
            print('JSON file is : %s'%fileName)
            ids.append(index)
            IDS.append(index)

            isTransformation = False
            if (isTransformation):
                ps = []
                ps.append([x, y, z, 1])
                px,py,pz = transformation(ps)
            else:
                px = x
                py = y
                pz = z
            

            X.append(px)
            Y.append(py)
            Z.append(pz)

            x1 = (e[0] * X_RATIO - X_OFFSET)
            y1 = (e[1] * Y_RATIO - Y_OFFSET)
            # d = (((x1 - PX) ** 2) + ((y1 - PY) ** 2)) ** 0.5

            ps = []
            ps.append([0,x1 - PX,PY - y1])  # 3/30
            
            px,py,pz = makePointsByMatrix(roll,pitch,yaw,ps)

            # X1.append(x + px)
            # Y1.append(y + py)
            # Z1.append(z - pz)
            
            
            if (isTransformation):
                ps = []
                ps.append([x + px,y + py,z - pz, 1])
                px,py,pz = transformation(ps)
            else:
                px = x + px
                py = y + py
                pz = z + pz
            

            X1.append(px)
            Y1.append(py)
            Z1.append(pz)

            
        index=index + 1
        if (len(ids) > 0) and (mainArgs.needBorder):
            writeCSV(ids,X,Y,Z,usCSVOut)
            writeCSV(ids,X1,Y1,Z1,pointCSVOut)
        elif mainArgs.needBorder:
            ids.append(index)

            writeCSV(ids,X1,Y1,Z1,pointCSVOut)

    writeCSV2(IDS,X,Y,Z,usCSVOut)
    writeCSV2(IDS,X1,Y1,Z1,pointCSVOut)
    # new a figure and set it into 3d
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # set figure information
    ax.set_title(path)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    # draw the figure, the color is r = read
    figure = ax.plot(X, Y, Z, c='r')
    figure = ax.plot(X1, Y1, Z1, c='b')

    plt.show()

def pixel2point(imgfile,points,label):
    png = Image.open(imgfile)
    png.load()
    pix = png.split()
    offset = len(points)  
    R = np.array(pix[0])
    G = np.array(pix[1])
    B = np.array(pix[2])
    A = np.array(pix[3])
    for x in range(png.size[0]):
        for y in range(png.size[1]):
            points.insert(offset+x*y,[X_P1+1+y, Y_P1+x, R[x,y], G[x,y], B[x,y], A[x,y]])
            label.insert(offset+x*y,"logo")    
    return points, label

def img2point(imgfile):
    png = Image.open(imgfile)
    png.load()
    pix = png.split()
    print (png.size)
    # offset = len(points)
    index_offset = 0
    x_offset = 28
    y_offset = 28
    R = np.array(pix[0])
    G = np.array(pix[1])
    B = np.array(pix[2])
    A = np.array(pix[3])
    for x in range(17):
        for y in range(17):
            logo_points.insert(index_offset+x*y,
                [X_P1+1+y, Y_P1+x, 
                R[x+x_offset,y+y_offset], 
                G[x+x_offset,y+y_offset], 
                B[x+x_offset,y+y_offset], 
                A[x+x_offset,y+y_offset]])
            logo_label.insert(index_offset+x*y,"logo")    
    return logo_points, logo_label

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, uint8):
            return int(obj)
        else:
            return super(MyEncoder, self).default(obj)

# def writeToPLYFile():

def getCoordinate(x, y, z, roll, pitch, yaw, ts, X_RATIO, Y_RATIO, X_OFFSET, Y_OFFSET, PX, PY):

    X1 = []
    Y1 = []
    Z1 = []

    for i, e in enumerate(ts):
        # pointCount = pointCount + 1

        isTransformation = False
        if (isTransformation):
            ps = []
            ps.append([x, y, z, 1])
            px,py,pz = transformation(ps)
        else:
            px = x
            py = y
            pz = z

        x1 = (e[0] * X_RATIO - X_OFFSET)
        y1 = (e[1] * Y_RATIO - Y_OFFSET)
        # d = (((x1 - PX) ** 2) + ((y1 - PY) ** 2)) ** 0.5

        ps = []
        
        # ps.append([x1 - PX,0,y1 - PY])  #3/17
        # ps.append([x1 - PX,0,PY - y1])  #3/17
        # ps.append([PX - x1,0,PY - y1])  #3/17 L->R
        
        # ps.append([0,x1 - PX,y1 - PY])  # 3/30
        ps.append([0,x1 - PX,PY - y1])  # 3/30
        # ps.append([0,PX  - x1,PY - y1])  # 3/30 L->R
        
        # ps.append([e[0],0,e[1]])  # 3/300

        px,py,pz = makePointsByMatrix(roll,pitch,yaw,ps)

        # X1.append(x + px)
        # Y1.append(y + py)
        # Z1.append(z - pz)
        
        
        if (isTransformation):
            ps = []
            ps.append([x + px,y + py,z - pz, 1])
            px,py,pz = transformation(ps)
        else:
            px = x + px
            py = y + py
            pz = z + pz
        X1.append(px)
        Y1.append(py)
        Z1.append(pz)

    return X1, Y1, Z1

def writeToJson2(): 

    sameFrames = None
    sfcsv = mainArgs.sameFrames
    if len(sfcsv) > 0:
        with open(sfcsv) as csv_file:
            csv_reader = list(csv.reader(csv_file,delimiter=','))
            row_count = len(csv_reader)
            sameFrames = np.zeros(row_count)
            index = 0
            for row in csv_reader:
                sameFrames[index] = row[0]
                index += 1

    csvFile = open(mainArgs.csv_in, "r")
    reader = csv.reader(csvFile)
    X = []
    Y = []
    Z = []

    X1 = []
    Y1 = []
    Z1 = []
    ids = []
    IDS = []
    index = 1
    pointCount = 0

    # plyFile = open("./test.ply","w")
    plyFile = open(mainArgs.outPly,"w")

    plyFile.writelines("ply\n")
    plyFile.writelines("format ascii 1.0\n")
    plyFile.writelines("comment Created by CloudCompare v2.11.1 (Anoia)\n")
    plyFile.writelines("comment Created 2022/01/01 00:00\n")
    plyFile.writelines("obj_info Generated by CloudCompare!\n")
    plyFile.writelines("element vertex 5198\n")
    plyFile.writelines("property float x\n")
    plyFile.writelines("property float y\n")
    plyFile.writelines("property float z\n")
    plyFile.writelines("end_header\n")

    jsonData = {'frames':[]}

    # jsonData = {
    #     'frames':[
    #         'frame':{
    #             'id':0,
    #             'origin':[],
    #             'shapes':[
    #                 'label':'border',
    #                 'points':[]
    #             ]
    #         }
    #     ]
    # }
    for row in reader:
        # ignore first row
        if reader.line_num == 1:
            continue
        id =int(row[0])

        # skip same frames
        if sameFrames is not None:
            if id in sameFrames:
                continue

        x = float(row[1])*1000
        y = float(row[2])*1000
        z = float(row[3])*1000
        # x = float(row[1])
        # y = float(row[2])
        # z = float(row[3])
        roll = float(row[4])
        pitch = float(row[5])
        yaw = float(row[6])
        
        frame = {}
        frame['id'] = id
        frame['origin'] = [x,y,z,roll,pitch,yaw]
        frame['shapes'] = [{'label':'border','points':[]},{'label':'centre','points':[]},{'label':'logo','points':[]}]
        # X.append(x)
        # Y.append(y)
        # Z.append(z)
        fileName = '%s%06d%s'%(mainArgs.json_in,id,'.json')
        print('JSON file is : %s'%fileName)
        ts,labels = loadJson(fileName)
        ids = []

        if len(ts) > 0:
            xtmp, ytmp, ztmp = getCoordinate(x, y, z, roll, pitch, yaw, ts, X_RATIO, Y_RATIO, X_OFFSET, Y_OFFSET, PX, PY)
            X1[len(X1):len(X1)] = xtmp
            Y1[len(Y1):len(Y1)] = ytmp
            Z1[len(Z1):len(Z1)] = ztmp

        # for i, e in enumerate(ts):
        #     pointCount = pointCount + 1
        #     ids.append(index)
        #     IDS.append(index)

        #     isTransformation = False
        #     if (isTransformation):
        #         ps = []
        #         ps.append([x, y, z, 1])
        #         px,py,pz = transformation(ps)
        #     else:
        #         px = x
        #         py = y
        #         pz = z

        #     X.append(px)
        #     Y.append(py)
        #     Z.append(pz)

        #     x1 = (e[0] * X_RATIO - X_OFFSET)
        #     y1 = (e[1] * Y_RATIO - Y_OFFSET)
        #     # d = (((x1 - PX) ** 2) + ((y1 - PY) ** 2)) ** 0.5

        #     ps = []
            
        #     # ps.append([x1 - PX,0,y1 - PY])  #3/17
        #     # ps.append([x1 - PX,0,PY - y1])  #3/17
        #     # ps.append([PX - x1,0,PY - y1])  #3/17 L->R
            
        #     # ps.append([0,x1 - PX,y1 - PY])  # 3/30
        #     ps.append([0,x1 - PX,PY - y1])  # 3/30
        #     # ps.append([0,PX  - x1,PY - y1])  # 3/30 L->R
            
        #     # ps.append([e[0],0,e[1]])  # 3/30

        #     px,py,pz = makePointsByMatrix(roll,pitch,yaw,ps)

        #     # X1.append(x + px)
        #     # Y1.append(y + py)
        #     # Z1.append(z - pz)
            
            
        #     if (isTransformation):
        #         ps = []
        #         ps.append([x + px,y + py,z - pz, 1])
        #         px,py,pz = transformation(ps)
        #     else:
        #         px = x + px
        #         py = y + py
        #         pz = z + pz
        #     X1.append(px)
        #     Y1.append(py)
        #     Z1.append(pz)
            
        #     plyFile.writelines("%f %f %f\n"%(px,py,pz))

        #     added = False
        #     for shape in frame['shapes']:
        #         if labels[i] == shape['label']:
        #             if len(e) > 3:
        #                 shape['points'].extend([[px,py,pz,e[2],e[3],e[4],e[5]]])
        #             else:
        #                 shape['points'].extend([[px,py,pz]])
        #             added = True
        #             break
        #     if added == False:
        #         if len(e) > 3:
        #             frame['shapes'].append({'label':labels[i] ,'points':[[px,py,pz,e[2],e[3],e[4],e[5]]]})
        #         else:
        #             if labels[i] == "CA" or labels[i] == "IJV" or labels[i] == "ac" or labels[i] == "ca":
        #                 label = "1"
        #                 frame['shapes'].append({'label':label ,'points':[[px,py,pz]]})
        #             else:
        #                 frame['shapes'].append({'label':labels[i] ,'points':[[px,py,pz]]})
    
        # jsonData['frames'].append(frame)

    plyFile.close()
    print('element vertex %d '%pointCount)
    jfile = open(mainArgs.outJson, 'w')
    json.dump(jsonData, jfile,cls = MyEncoder)
    jfile.close()

    # new a figure and set it into 3d
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # set figure information
    ax.set_title(mainArgs.csv_in)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    # draw the figure, the color is r = read
    figure = ax.plot(X, Y, Z, c='r')
    figure = ax.plot(X1, Y1, Z1, c='b')

    plt.show()

def writeToJson(): 

    sameFrames = None
    sfcsv = mainArgs.sameFrames
    if len(sfcsv) > 0:
        with open(sfcsv) as csv_file:
            csv_reader = list(csv.reader(csv_file,delimiter=','))
            row_count = len(csv_reader)
            sameFrames = np.zeros(row_count)
            index = 0
            for row in csv_reader:
                sameFrames[index] = row[0]
                index += 1

    csvFile = open(mainArgs.csv_in, "r")
    reader = csv.reader(csvFile)
    X = []
    Y = []
    Z = []

    X1 = []
    Y1 = []
    Z1 = []
    ids = []
    IDS = []
    index = 1
    pointCount = 0

    # plyFile = open("./test.ply","w")
    plyFile = open(mainArgs.outPly,"w")

    plyFile.writelines("ply\n")
    plyFile.writelines("format ascii 1.0\n")
    plyFile.writelines("comment Created by CloudCompare v2.11.1 (Anoia)\n")
    plyFile.writelines("comment Created 2022/01/01 00:00\n")
    plyFile.writelines("obj_info Generated by CloudCompare!\n")
    plyFile.writelines("element vertex 5198\n")
    plyFile.writelines("property float x\n")
    plyFile.writelines("property float y\n")
    plyFile.writelines("property float z\n")
    plyFile.writelines("end_header\n")

    jsonData = {'frames':[]}

    # jsonData = {
    #     'frames':[
    #         'frame':{
    #             'id':0,
    #             'origin':[],
    #             'shapes':[
    #                 'label':'border',
    #                 'points':[]
    #             ]
    #         }
    #     ]
    # }
    for row in reader:
        # ignore first row
        if reader.line_num == 1:
            continue
        id =int(row[0])

        # skip same frames
        if sameFrames is not None:
            if id in sameFrames:
                continue

        x = float(row[1])*1000
        y = float(row[2])*1000
        z = float(row[3])*1000
        # x = float(row[1])
        # y = float(row[2])
        # z = float(row[3])
        roll = float(row[4])
        pitch = float(row[5])
        yaw = float(row[6])
        
        frame = {}
        frame['id'] = id
        frame['origin'] = [x,y,z,roll,pitch,yaw]
        frame['shapes'] = [{'label':'border','points':[]},{'label':'centre','points':[]},{'label':'logo','points':[]}]
        # X.append(x)
        # Y.append(y)
        # Z.append(z)
        fileName = '%s%06d%s'%(mainArgs.json_in,id,'.json')
        print('JSON file is : %s'%fileName)
        ts,labels = loadJson(fileName)
        ids = []
        for i, e in enumerate(ts):
            pointCount = pointCount + 1
            ids.append(index)
            IDS.append(index)

            isTransformation = False
            if (isTransformation):
                ps = []
                ps.append([x, y, z, 1])
                px,py,pz = transformation(ps)
            else:
                px = x
                py = y
                pz = z

            X.append(px)
            Y.append(py)
            Z.append(pz)

            x1 = (e[0] * X_RATIO - X_OFFSET)
            y1 = (e[1] * Y_RATIO - Y_OFFSET)
            # d = (((x1 - PX) ** 2) + ((y1 - PY) ** 2)) ** 0.5

            ps = []
            
            # ps.append([x1 - PX,0,y1 - PY])  #3/17
            # ps.append([x1 - PX,0,PY - y1])  #3/17
            # ps.append([PX - x1,0,PY - y1])  #3/17 L->R
            
            # ps.append([0,x1 - PX,y1 - PY])  # 3/30
            ps.append([0,x1 - PX,PY - y1])  # 3/30 // is ok?
            # ps.append([0,PX  - x1,PY - y1])  # 3/30 L->R
            
            # ps.append([e[0],0,e[1]])  # 3/30

            # for test
            # roll = roll - 30
            # yaw = yaw + 24.1

            px,py,pz = makePointsByMatrix(roll,pitch,yaw,ps)

            # X1.append(x + px)
            # Y1.append(y + py)
            # Z1.append(z - pz)
            
            
            if (isTransformation):
                ps = []
                ps.append([x + px,y + py,z - pz, 1])
                px,py,pz = transformation(ps)
            else:
                px = x + px
                py = y + py
                pz = z + pz
            X1.append(px)
            Y1.append(py)
            Z1.append(pz)
            
            plyFile.writelines("%f %f %f\n"%(px,py,pz))

            added = False
            for shape in frame['shapes']:
                if labels[i] == shape['label']:
                    if len(e) > 3:
                        shape['points'].extend([[px,py,pz,e[2],e[3],e[4],e[5]]])
                    else:
                        shape['points'].extend([[px,py,pz]])
                    added = True
                    break
            if added == False:
                if len(e) > 3:
                    frame['shapes'].append({'label':labels[i] ,'points':[[px,py,pz,e[2],e[3],e[4],e[5]]]})
                else:
                    if labels[i] == "CA" or labels[i] == "IJV" or labels[i] == "ac" or labels[i] == "ca" or labels[i] == "V":
                        label = "1"
                        frame['shapes'].append({'label':label ,'points':[[px,py,pz]]})
                    else:
                        frame['shapes'].append({'label':labels[i] ,'points':[[px,py,pz]]})
    
        jsonData['frames'].append(frame)

    plyFile.close()
    print('element vertex %d '%pointCount)
    jfile = open(mainArgs.outJson, 'w')
    json.dump(jsonData, jfile,cls = MyEncoder)
    jfile.close()

    # new a figure and set it into 3d
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # set figure information
    ax.set_title(mainArgs.csv_in)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.set_box_aspect((2,1,4))

    # draw the figure, the color is r = read
    figure = ax.plot(X, Y, Z, c='r')
    figure = ax.plot(X1, Y1, Z1, c='b')

    # plt.xticks([460,490,520,550])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw 3D Track and write out csv file')

    parser.add_argument('--csv_in', required=False,
                        metavar="path to robot arm track csv file",
                        help='path to robot arm track csv file')
    
    parser.add_argument('--json_in', required=False,
                        metavar="path to lableMe JSON file",
                        help='path to lableMe JSON file')

    parser.add_argument('--csv_us_out', required=False, type=str,default='./outputcsv/tmp-us.csv',
                        metavar="path to write out us track csv file",
                        help='path to write out us track csv file')
    
    parser.add_argument('--csv_points_out', required=False, type=str,default='./outputcsv/tmp-points.csv',
                        metavar="path to write out points track csv file",
                        help="path to write out points track csv file")

    parser.add_argument('--csvfile', required=False, type=str,default='./outputcsv/tmp-points.csv',
                        metavar="path to write out points track csv file",
                        help="path to write out points track csv file")

    parser.add_argument('--needBorder', required=False, type=bool,default=False,
                        metavar="whether to output four points in the border",
                        help="whether to output four points in the border")

    parser.add_argument('--needLogo', required=False, type=bool,default=False,
                        metavar="whether to output logo in the border",
                        help="whether to output logo in the border")

    parser.add_argument('--outJson', required=False, type=str,default='./outputJson/tmp-points.json',
                        metavar="path to write out points track json file",
                        help="path to write out points track json file")

    parser.add_argument('--outPly', required=False, type=str,default='./outputJson/tmp-points.ply',
                        metavar="path to write out points track json file",
                        help="path to write out points track json file")

    parser.add_argument('--sameFrames', required=False, type=str,default='')
    # parser.add_argument('--h', required=False, type=int,default=600,
    #                     metavar="the height of image",
    #                     help='the height of image')

    mainArgs = parser.parse_args()

    # a = 4
    # b = 3
    # c = 5
    # angle = math.degrees(math.atan(3/4))
    # print('angle is %f'%angle)
    # a1 = math.cos(math.radians(angle))*c
    # print('a1 is %f',a1)

    # show(mainArgs.json_in,mainArgs.csv_in,mainArgs.csv_us_out,mainArgs.csv_points_out)
    # show2(mainArgs.json_in,mainArgs.csv_in,mainArgs.csv_us_out,mainArgs.csv_points_out)
    img2point('./log-a.PNG')
    writeToJson()
    # writeToJson2()

    # pixel2point('./logs-amit-a.png')
    # pixel2point('./log-a.PNG')

    # testView()
    # checkCSV(mainArgs.csvfile)

