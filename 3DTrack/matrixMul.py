import json
import sys
import time
import traceback
from datetime import datetime
import numpy as np
import scipy as sp
# from typing_extensions import Self
from queue import Queue
from threading import Lock
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QTime, QTimer 
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtGui import QTextCursor
from pip import main
# import Ui_BelowScreen
# import conf
# from logger import get_logger
# from hm_trans import HMTransThread
# from ha_trans import HATransThread
# from hp_trans import HPTransThread
# from deal_ai import InferenceThread_tensorrt
from scipy.spatial.transform import Rotation as R
import math

def robot_matrix_get_slot(list,isDegrees):
    robot_matrix = np.zeros(shape=(4,4))
    # get_rotation = R.from_euler('zyx', list[3:6], degrees=True)
    get_rotation = R.from_euler('xyz', list[3:6], degrees=isDegrees)
    rotation_matrix = get_rotation.as_matrix()
    get_position = np.array(list[0:3]).reshape(3,1)
    robot_matrix = np.insert(rotation_matrix,[3],get_position,axis=1)
    robot_matrix = np.insert(robot_matrix,[3],[0,0,0,1],axis=0)

    print(robot_matrix)

    # rotation_matrix =[
    #     [ 0.628125,  -0.477976, 0.614001],
    #     [ 0.330684,   0.878263, 0.345403],
    #     [-0.704349,  -0.013916, 0.709717]
    # ]
    # p = [28.708950, 9.678196, 13.311845, 1]
    p = [28.708950, 9.678196, 13.311845, 1]
    p = np.dot(robot_matrix,p)


    [0.329447, 0.899031, 0.344629]
    # print(p)

    matrix_res = np.dot(rotation_matrix, rotation_matrix)

    # print(matrix_res)

    return robot_matrix


def matrix2AxisAngle(robot_M):
    
    angle = math.acos((robot_M[0,0] + robot_M[1,1] + robot_M[2,2] -1 )/2)
    
    axisList=[
        robot_M[2,1] - robot_M[1,2],
        robot_M[0,2] - robot_M[2,0],
        robot_M[1,0] - robot_M[0,1],
    ]
    axis = np.array(axisList).reshape(1,3)
    r = axis/(2*math.sin(angle))

    return r, math.degrees(angle)

if __name__ == '__main__':
    list =[-11.606060, -12.643732, 20.908216, -1.123301, 44.776954, 27.765085]
    # list =[0, 0, 0, -1.123301, 44.776954, 27.765085]
    # list =[-11.606060, -12.643732, 20.908216, -25.9511025, 37.8793869, 37.2695817]
    # list =[26.198, 5.848, -3.346, 25.9394523, -37.8710844, -37.2755519]
    # list =[26.198, 5.848, -3.346, 0.4527288, -0.6609751, -0.6505811]
    robot_matrix = robot_matrix_get_slot(list,True)

    list =[28.708950, 9.678196, 13.311845, 30, 0, 0]

    robot_matrix_2 =robot_matrix_get_slot(list,True)

    robot_M = np.dot(robot_matrix_2,robot_matrix)

    print(robot_M)

    r, angle = matrix2AxisAngle(robot_M)
    
    print(r)
    print(angle)

    quaternion = R.from_matrix(robot_M[0:3,0:3]).as_quat()
    
    

    print(quaternion)


