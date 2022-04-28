import numpy as np
import math
import scipy.linalg as linalg
import matplotlib as mpl 
from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.pyplot as plt
import json as json
import argparse
import os

global mainArgs

# rot_matrix=[
#     [-0.427881032228,  0.888071298599, -0.168070837855, 655.447143554688],
#     [ 0.112007528543, -0.132419094443, -0.984845221043, 262.812194824219],
#     [-0.896868169308, -0.440221518278, -0.042811065912, -317.262268066406],
#     [ 0.000000000000,  0.000000000000,  0.000000000000, 1.000000000000],
# ]

# rot_matrix=[
#     [-0.512699,  0.677542, -0.527329,  567.702759],
#     [-0.185783, -0.687194, -0.702317,  216.110672],
#     [-0.838227, -0.262109,  0.478200, -212.392715],
#     [ 0.000000,  0.000000,  0.000000,    1.000000],
# ]
rot_matrix=[
    [ 0.704359, -0.628114,  0.330684,  25.435478],
    [ 0.013909,  0.477977,  0.878262,   0.929165],
    [-0.709708, -0.614013,  0.345403,   9.891584],
    [ 0.000000,  0.000000,  0.000000,   1.000000],
]
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

#旋转矩阵 欧拉角
def rotate_mat(axis, radian):
    rot_matrix = linalg.expm(np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
    return rot_matrix

# # 分别是x,y和z轴,也可以自定义旋转轴
# axis_x, axis_y, axis_z = [1,0,0], [0,1,0], [0, 0, 1]
# rand_axis = [0,0,1]
# # axis_x, axis_y, axis_z = [0.631670,0,0], [0,0.553020,0], [0, 0, -0.543288]
# # rand_axis = [0.631670,0.553020,-0.543288]
# #旋转角度
# yaw = math.pi/180
# print(yaw)
# # yaw = 150.609865
# #返回旋转矩阵
# rot_matrix = rotate_mat(rand_axis, yaw)
# rot_matrix=[
#     [-0.427881032228,  0.888071298599, -0.168070837855, 655.447143554688],
#     [ 0.112007528543, -0.132419094443, -0.984845221043, 262.812194824219],
#     [-0.896868169308, -0.440221518278, -0.042811065912, -317.262268066406],
#     [ 0.000000000000,  0.000000000000,  0.000000000000, 1.000000000000],
# ]
# print(rot_matrix)
# # 计算点绕着轴运动后的点
# x = [-1010,105.43,-244,1]
# x1 = np.dot(rot_matrix,x)
# # 旋转后的坐标
# print(x1)   
# # 计算各轴偏移量
# print([x1[i]-x[i] for i in range(3)])


def transformateJson(fileName):
    points=[]
    pt = []
     # file exist check
    if os.path.exists(fileName):
        with open(fileName, 'r' ) as f:
            json_o = json.load(f)
            json_t = json_o
            if json_o['frames'] and json_o['frames'][0]:
                for i in range(len(json_o['frames'])):
                    shapes = json_o['frames'][i]['shapes']
                    for j in range(len(shapes)):
                        pt = []
                        points = json_o['frames'][i]['shapes'][j]['points']
                        for k in range(len(points)):
                            p = json_o['frames'][i]['shapes'][j]['points'][k]
                            p = np.append(p,[1.0],axis=0)
                            if len(pt) > 0:
                                pt = np.append(pt,[np.dot(rot_matrix, p)],axis=0)
                            else:
                                pt = [np.dot(rot_matrix, p)]
                        
                        if len(pt) > 0:
                            # delete last column
                            pt = np.delete(pt,3,axis=1)
                            json_t['frames'][i]['shapes'][j]['points'] = pt
        
        # dump json file
        ft = open(mainArgs.json_out, 'w')
        json.dump(json_t, ft, cls = MyEncoder)
        ft.close

        f.close

                        
# def transformatePly():




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='transformate points')

    parser.add_argument('--json_in', required=False,
                        metavar="path to lableMe JSON file",
                        help='path to lableMe JSON file')

    parser.add_argument('--json_out', required=False, type=str,default='./outputJson/tmp-points.json',
                        metavar="path to write out points track json file",
                        help="path to write out points track json file")

    parser.add_argument('--needBorder', required=False, type=bool,default=False,
                        metavar="whether to output four points in the border",
                        help="whether to output four points in the border")

    parser.add_argument('--ply_in', required=False,
                        metavar="path to lableMe JSON file",
                        help='path to lableMe JSON file')

    parser.add_argument('--ply_out', required=False, type=str,default='./outputJson/tmp-points.ply',
                        metavar="path to write out points track json file",
                        help="path to write out points track json file")

    parser.add_argument('--sameFrames', required=False, type=str,default='')
    # parser.add_argument('--h', required=False, type=int,default=600,
    #                     metavar="the height of image",
    #                     help='the height of image')

    mainArgs = parser.parse_args()

    # transformateJson(mainArgs.json_in)

    # origin_points =[
    #     [0 , 0, 0, 1],
    #     [10, 0, 0, 1],
    #     [10,10, 0, 1],
    #     [10,10,10, 1],
    #     [ 0,10, 0, 1],
    #     [ 0,10,10, 1],
    #     [ 0, 0,10, 1],
    #     [10, 0,10, 1],
    # ]

    origin_points =[
        [10, 0, 0, 1],
        [10,10, 0, 1],
        [10,10,10, 1],
        [ 0,10,10, 1],
        [ 0,10, 0, 1],
        [0 , 0, 0, 1],
        [ 0, 0,10, 1],
        [10, 0,10, 1],
    ]

    for p in origin_points:
        transformate_points = np.dot(rot_matrix, p)
        print(p)
        print(transformate_points)

    # if mainArgs.ply_in and mainArgs.ply_out:
    #     transformatePly()

