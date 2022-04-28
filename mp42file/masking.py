"""
Q & A

Q: Execution enviroment ?
A: Python 3.7, 3.6

Q: program rise error regarding "skimage" not installed
A: pip install ckicit-image

Q: program rise error regarding "OpenCV" not installed
A: pip install opencv-python
"""

from ast import Try
import os as os
import sys as sys
import json as json

from numpy.core.numeric import isclose
import cv2 as cv2
import numpy as np
import skimage as skimage
from PIL import ImageFont, ImageDraw, Image

fontpath = "./simsun.ttc" # <== 这里是宋体路径
# $User shall customize below part
# W = 800
# H = 600

isLabelme = False
isResize = True
W_R = 512
H_R = 512

# W_R = 256
# H_R = 256

IMAGEPATH = "images/"
JSONPATH = "jsons/"
MASKPATH = "masks/"

# IMAGEPATH = "subImages/"
# JSONPATH = "subJsons/"
# MASKPATH = "subMasks/"

# IMAGEPATH = "fullScreenImages/"
# JSONPATH = "fullScreenJsons/"
# MASKPATH = "fullScreenMasks-256/"

# IMAGEPATH = "paddingImages/"
# JSONPATH = "paddingJsons/"
# MASKPATH = "paddingMasks/"

# IMAGEPATH = "fullScreenImages/"
# JSONPATH = "fullScreenJsons/"
# MASKPATH = "fullScreenMasks/"

# W_R = 256
# H_R = 256
# W_R = 320
# H_R = 320

# ROOT_PATH = "/media/yao/iot-hd/workspace/trainingdata-us/01.BeiJIng/"    # Linux
# ROOT_PATH = "/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/pytorch-nested-unet/inputs/JJG_C3_JP/"    # Linux
# ROOT_PATH = "/media/yao/iot-hd/workspace/trainingdata-us/JJG/"    # Linux
# ROOT_PATH = "C:/" # Windows

background = 0
# classDic ={'BG':0, 'CA':1, 'N':2, 'IJV':3, 'ASM':4, 'MSM':5, 'SCM':6}  # JP
# classDic ={'BG':0, 'CA':1, 'N':2} # BeiJing
# classDic ={'BG':0, 'CA':1, 'N':2, 'IJV':3} # JP
# classDic ={'CA':0, 'N':1, 'IJV':2} # JP Unet++
# classDic ={'BG':0, 'CA':1, 'N':2} # JP
# classDic ={'CA':0, 'N':1, 'IJV':2, 'ASM':3, 'MSM':4, 'SCM':5}  # JP CA-N-IJV-ASM-MSM-SCM-NOBG
# classDic ={'CA':0, 'N':1, 'IJV':2} # JP CA-N-IJV-NOBG
# background = 255
################ 01.JJG BJ ############################
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/LiveModel/imagesAndjsons/"    # Linux
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/JJG_Classify_20220222/葡萄状/"
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/02.fukushima/01.JJG-CK/"
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/LiveModel/ALL/"
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/训练数据集-人体/标记后数据/"
# ROOT_PATH = "/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220401/"
ROOT_PATH = "/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220421/"
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/Qualified_JJG_Beijing/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/98.検証用/01.JJG/patient10001/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/01.JJG-CK/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/01.US-AI-DATA_JJG_lable/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/98.検証用/01.JJG/patient10001/"    # Linux
# COLORS = ((255,255,    0),  # N     FFFF00
#           (255,  0,    0),  # CA    FF0000
#           (  6,186,  216)   # SA    06BAD8
# ) 
# COLORS = ((255,255,    0),  # N     FFFF00
#           (255,  0,    0),  # CA    FF0000
#           (  6,186,  216),  # SA    06BAD8
#         #   (255,255,    0),  # NR    FFFF00
#         #   (255,  0,    0),  # CCA   FF0000
#           (  6,186,  216),  # VA    06BAD8
#           (  0,255,  255)   # B     00FFFF
# ) 
# COLORS = ((255,255,    0),  # V     FFFF00
#           (255,  0,    0)  # C    FF0000
# )
# classDic ={'BG':0, 'V':1, 'C':2} #  LiveModel
COLORS = ((255,255,    0),  # V     FFFF00
          (255,  0,    0)  # G    FF0000
)
# classDic ={'BG':0, 'V':1, 'G':2} #  LiveModel
classDic ={'BG':0, 'V':1} #  LiveModel
# classDic ={'BG':0, 'CA':1} # 01.JJG JP 斜角筋間アプローチ

# classDic ={'BG':0, 'N':1, 'CA':2, 'SA':3} # 01.JJG BJ
# CLASSNAME = (
#     '神経',
#     '頭動脈',
#     '鎖骨下動脈'
# )

# classDic ={'BG':0, 'N':1, 'CA':2, 'SA':3, 'NR':4, 'CCA':5, 'VA':6, 'B':7 } # 01.JJG BJ
# CLASSNAME = (
#     '神経',
#     '頭動脈',
#     '鎖骨下動脈',
#     '神经根',
#     '颈总动脉',
#     '椎动脉',
#     '骨骼'
# )

# classDic ={'BG':0, 'N':1, 'CA':2, 'SA':3, 'VA':4, 'B':5 } # 01.JJG BJ
# CLASSNAME = (
#     '神経',
#     '頭動脈',
#     '鎖骨下動脈',
#     '椎动脉',
#     '骨骼'
# )

# classDic ={'BG':0, 'N':1, 'CA':2 } # 01.JJG JP
# CLASSNAME = (
#     '神経',
#     '動脈'
# )

# CLASSNAME = (
#     '血管',
#     '癌症'
# )
CLASSNAME = (
    '血管',
    '胆囊'
)
################ 01.JJG ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/01.JJG/"    # Linux
# # ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/98.検証用/01.JJG/patient10001/"    # Linux
# # ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/01.JJG-CK/"    # Linux
# # ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/01.US-AI-DATA_JJG_lable/"    # Linux
# # ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/98.検証用/01.JJG/patient10001/"    # Linux
# COLORS = ((255,  0,    0),  # CA    FF0000
#           (  0,176,  240),  # IJV   00B0F0
#           (255,255,    0),  # N     FFFF00
#           (255,255,    0),  # N-C5  FFFF00
#           (255,255,    0),  # N-C6  FFFF00
#           (255,255,  128),  # N-C7  FFFF00
#           (255,255,  128),  # N-C8  FFFF00
#           (255,  0,  128),  # VA    FF0080
#           (128,255,    0),  # MSM   80FF00
#           (  0,255,    0),  # SCM   00FF00
#           (  0,128,    0),  # ASM   008000
#           (255, 51,  204),  # Int-A FF33CC
#           (189,238,  255)   # Int-V BDEEFF
# ) 
# classDic ={'BG':0, 'CA':1, 'IJV':2, 'N':3, 'N-C5':4, 'N-C6':5, 'N-C7':6, 'N-C8':7, 'VA':8, 'MSM':9, 'SCM':10, 'ASM':11, 'Int-A':12, 'Int-V':13} # 01.JJG JP 斜角筋間アプローチ
# # classDic ={'BG':0, 'CA':1} # 01.JJG JP 斜角筋間アプローチ
# CLASSNAME = (
#     '頚動脈',
#     '内頸静脈',
#     '神経',
#     '神経C5',
#     '神経C6',
#     '神経C7',
#     '神経C8',
#     '椎骨動脈',
#     '中斜角筋',
#     '胸鎖乳突筋',
#     '前斜角筋',
#     '動脈',
#     '静脈'
# )
################ 02.SGS ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/02.SGS/"    # Linux
# COLORS = ((255,  0,    0),  # SA    FF0000
#           (255,255,    0),  # N     FFFF00
#           (160, 82,   45),  # FR    A0522D
#           (128,  0,  128),  # P     800080
#           (255, 51,  204)   # Sup-A FF33CC
# ) 
# classDic ={'BG':0, 'SA':1, 'N':2, 'FR':3, 'P':4, 'Sup-A':5} # 02.SGS JP 鎖骨上アプローチ
################ 03.SGX ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/03.SGX/"    # Linux
# COLORS = ((255,  0,    0),  # AA    FF0000
#           (  0,176,  240),  # AV    00B0F0
#           (255,255,    0),  # N     FFFF00
#           (  0,255,    0),  # PMM   00FF00
#           (  0,128,    0),  # PMiN  008000
#           (128,  0,  128),  # P     800080
#           (255, 51,  204),  # Inf-A FF33CC
#           (189,238,  255)   # Inf-V BDEEFF
# ) 
# classDic ={'BG':0, 'AA':1, 'AV':2, 'N':3, 'PMM':4, 'PMiN':5, 'P':6, 'Inf-A':7, 'Inf-V':8} # 03.SGX JP 鎖骨下アプローチ
################ 04.YLB ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/04.YLB/"    # Linux
# COLORS = ((255,  0,    0),  # AA    FF0000
#           (  0,176,  240),  # AV    00B0F0
#           (255,255,    0),  # MN    FFFF00
#           (255,255,    0),  # UN    FFFF00
#           (255,255,    0),  # RN    FFFF00
#           (255,255,    0),  # MCN   FFFF00
#           (160, 82,   45),  # H     A0522D
#           (255, 51,  204),  # Axi-A FF33CC
#           (189,238,  255)   # Axi-V BDEEFF
# ) 
# classDic ={'BG':0, 'AA':1, 'AV':2, 'MN':3, 'UN':4, 'RN':5, 'MCN':6, 'H':7, 'Axi-A':8, 'Axi-V':9} # 04.YLB JP 腋窩アプローチ
################ 05.GSJ ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/05.GSJ/"    # Linux
# COLORS = ((255,  0,  0),  # FA FF0000
#           (0,  176,  240),  # FV 00B0F0
#           (255,255,  0),  # FN FFFF00
#           (0,  255,  0),  # IPM 00FF00
#           (255, 51,  204),  # Fem-A FF33CC
#           (189,238,  255)   # Fem-V BDEEFF
# ) 
# classDic ={'BG':0, 'FA':1, 'FV':2, 'FN':3, 'IPM':4, 'Fem-A':5, 'Fem-V':6} # 05.GSJ JP 大腿神経
################ 06.GWZ ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/06.GWZ/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/01.Beijing/11.Ed-GWZ/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/03.BeJingFukushima/06.GWZ/"    # Linux
# COLORS = ((255,255,    0),  # SN    FFFF00
#           (255,  0,    0),  # PA    FF0000
#           (  0,176,  240),  # PV    00B0F0
#           (255,255,    0),  # CPN   FFFF00
#           (255,255,    0),  # TN    FFFF00
#           (255, 51,  204),  # Sci-A FF33CC
#           (189,238,  255)   # Sci-V BDEEFF
# ) 
# classDic ={'BG':0, 'SN':1, 'PA':2, 'PV':3, 'CPN':4, 'TN':5, 'Sci-A':6, 'Sci-V':7} # 06.GWZ JP 膝窩部アプローチ
################ 07.SJG ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/02.Fukushima/07.SJG/"    # Linux
# COLORS = ((255,  0,    0),  # FA    FF0000
#           (  0,176,  240),  # FV    00B0F0
#           (255,255,    0),  # N     FFFF00
#           (  0,255,    0),  # SM    00FF00
#           (  0,128,    0),  # VMM   008000
#           (112, 48,  160),  # MG    7030A0
#           (255, 51,  204),  # Sap-A FF33CC
#           (189,238,  255)   # Sap-V BDEEFF
# ) 
# classDic ={'BG':0, 'FA':1, 'FV':2, 'N':3, 'SM':4, 'VMM':5, 'MG':6, 'Sap-A':7, 'Sap-V':8} # 07.SJG JP 伏在神経
# classDic ={'BG':0, 'FA':1, 'FV':2, 'N':3} # 07.SJG JP 伏在神経
################ Beijing 11.Ed-GWZ ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/01.Beijing/11.Ed-GWZ/"    # Linux
# COLORS = ((255,  0,    0),  # PA    FF0000
#           (  0,  0,  139),  # PV    00008B
#           (255,255,    0),  # SCN   FFFF00
#           (255,255,    0),  # TN    FFFF00
#           (255,255,    0),  # CPN   FFFF00
#           (  0,128,    0),  # BFM   008000
#           (  0,128,    0),  # SMM   008000
#           (  0,128,    0),  # STM   008000
#           (135,206,  250)   # B     87CEFA
# ) 
# classDic ={'BG':0, 'PA':1, 'PV':2, 'SCN':3, 'TN':4, 'CPN':5, 'BFM':6, 'SMM':7, 'STM':8, 'B':9} # 11.Ed-GWZ 腘窝坐骨（教育）

################ 20. LIV ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/trainingdata-us-second/liver/patient90003/"    # Linux
# ROOT_PATH = "/mnt/iot-hd/workspace/trainingdata-us-second/liver/"    # Linux
# COLORS = (( 99,184,  255),  # IVC   63B8FF 下腔静脉 下大静脈
#           (153,  0,  255),  # HV    9900FF 肝静脉   肝静脉
#           (153, 51,  255),  # RHV   9933FF 肝右静脉 右肝静脈
#           (153,102,  255),  # MHV   9966FF 肝中静脉 中肝静脈
#           (153,153,  255),  # LHV   9999FF 肝左静脉 左肝静脈
#           (  0,102,  255),  # PV    0066FF 门静脉   門脈
#           (  0,  0,  255),  # RPV   0000FF 门静脉右支 右門脈
#           (  0,204,  255),  # LPV   00CCFF 门静脉左支 左門脈
#           (255,  0,    0),  # HA    FF0000 肝动脉   肝動脈
#           (154,205,   50),  # GB    9ACD32 胆囊     胆嚢
#           (202,255,  112),  # BD    CAFF70 胆管     胆管
#           (237,237,  237),  # LTH   EDEDED 肝圆韧带  肝円索
#           (218,165,   32),  # SE    DAA520 肝上缘   肝臓の上端
#           (210,105,   30)   # LE    D2691E 肝下缘   肝臓の下端
# ) 
# classDic ={'BG':0, 'IVC':1, 'HV':2, 'RHV':3, 'MHV':4, 'LHV':5, 'PV':6, 'RPV':7, 'LPV':8, 'HA':9, 'GB':10, 'BD':11, 'LTH':12, 'SE':13, 'LE':14} # 20.LIV  肝臓
# CLASSNAME = (
#     '下腔静脉',
#     '肝静脉',
#     '肝右静脉',
#     '肝中静脉',
#     '肝左静脉',
#     '门静脉',
#     '门静脉右支',
#     '门静脉左支',
#     '肝动脉',
#     '胆囊',
#     '胆管',
#     '肝圆韧带',
#     '肝上缘',
#     '肝下缘'
# )
# ################ 03.XZP BJ ############################
# ROOT_PATH = "/mnt/iot-hd/workspace/01.Beijing/03.XZP/"    # Linux
# COLORS = ((255,  0,    0),  # P    FF0000
#           (  0,176,  240),  # PVS  00B0F0
#           (175,171,  171)   # RIB  AFABAB
# ) 
# classDic ={'BG':0, 'P':1, 'PVS':2, 'RIB':3} # 03.XZP BJ 胸椎旁
# CLASSNAME = (
#     '胸膜',
#     '椎旁间隙',
#     '肋骨'
# )
################ MODEL BJ ############################
# ROOT_PATH = "/home/yao/workspace/trainingdata-us/20220115185506_images/"    # Linux
# COLORS = ((  0,176,  240),   # V   00B0F0
#           (189,238,  255)   # Int-V BDEEFF
# ) 
# classDic ={'BG':0, 'V':1} # MODEL BJ
# CLASSNAME = (
#     '肝静脉'
# )

# create image filename list from path
def WalkPath(root_path):
    mask_list=[]
    image_dir = ROOT_PATH + IMAGEPATH
    json_dir = ROOT_PATH + JSONPATH
    # mask_dir = ROOT_PATH + "masks-CA-N-IJV_512/"
    # json_dir = "/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/jsons/"
    mask_dir = ROOT_PATH + MASKPATH
    # mask_dir = ROOT_PATH + "masks-CA-N-IJV-ASM-MSM-SCM/"
    # mask_dir = ROOT_PATH + "masks-CA-N-IJV-NOBG/"


    for cur, _dirs, files in os.walk(image_dir):
        json_path = cur.replace(image_dir,json_dir)
        mask_path = cur.replace(image_dir,mask_dir)

        if( os.path.exists(mask_path)==False):
            os.makedirs(mask_path)

        for f in files:
            # json_file = f.replace('.jpg', '.json')  # $User customize type
            # mask_file = f                           # $User customize type          
            fileName = f.split('.')[0]  
            image_fullpath = cur + '/' + f
            json_fullpath = json_path + fileName + '.json'
            mask_fullpath = mask_path + fileName + '.jpg'
            if not isLabelme:
                # CreateMaskByPath(image_fullpath, json_fullpath, mask_path, fileName)
                # CreateMaskByPath_Labelme(image_fullpath, json_fullpath, mask_path, fileName)
                CreateMultipleMaskByPath(image_fullpath, json_fullpath, mask_path, fileName)
            else:
                CreateMultipleMaskByPath_Labelme(image_fullpath, json_fullpath, mask_path, fileName)
            # CreateMultipleMaskByPath2_Labelme(image_fullpath, json_fullpath, mask_path, fileName)
    return


def CreateMaskByPath(image_fullpath, json_fullpath, mask_path, fileName):
    
    # $User can read image to get height & width in case it is variant
    img = cv2.imread(image_fullpath, cv2.IMREAD_UNCHANGED)
    H, W, C = img.shape[:3]
    
    if (os.path.exists(json_fullpath)==False):
        # Json file not exit, print "error" and process next
        print(json_fullpath + "not exist!")
    else:
        with open(json_fullpath) as f:

            #load json file
            print('open json file: %s' % json_fullpath )
            d = json.load(f)
            polygons = d['polygons']
            for polygon in polygons:
                className = polygon['type']
                if className is None:
                    className = 'TODO'
                classPath = mask_path + className + '/'
                if( os.path.exists(classPath)==False):
                        os.makedirs(classPath)

                #create mask image
                mask_image = np.zeros((H,W,3), np.uint8)
                data = polygon['points']
                #print(len(data))
                ts = np.asarray(data).astype(np.int32)
                pts= np.array([[e[0], e[1]] for e in ts])

                pts = pts.reshape((-1,1,2))
                mask_image= cv2.fillPoly(mask_image, [pts], (255,255,255))
                #else do nothing

                cv2.imwrite(classPath + fileName + '.jpg', mask_image)    
    return

def CreateMultipleMaskByPath(image_fullpath, json_fullpath, mask_path, fileName):
    
    # $User can read image to get height & width in case it is variant
    # img = cv2.imread(image_fullpath, cv2.IMREAD_UNCHANGED)
    img = cv2.imread(image_fullpath)
    w_scale = 1
    h_scale = 1
    if isResize:
        H, W, C = img.shape[:3]
        # H, W, C = 594, 883, 3
        h_scale = H_R/H
        w_scale = W_R/W 
        H = H_R
        W = W_R
        img = cv2.resize(img,(H,W))
    else:
        H, W, C = img.shape[:3]
    
    if (os.path.exists(json_fullpath)==False):
        # Json file not exit, print "error" and process next
        print(json_fullpath + "not exist!")
    else:
        with open(json_fullpath) as f:

            #load json file
            print('open json file: %s' % json_fullpath )
            d = json.load(f)
            polygons = d['polygons']
            #create mask image
            # mask_image = np.zeros((H,W,1), np.uint8)
            # ignore background
            mask_image = np.full((H,W,1), background,np.uint8)
            for polygon in polygons:
                className = polygon['type']
                className = className.upper()
                if className is None:
                    className = 'TODO'
                # classPath = mask_path + className + '/'
                # if( os.path.exists(classPath)==False):
                #         os.makedirs(classPath)

                data = polygon['points']
                #print(len(data))
                ts = np.asarray(data).astype(np.int32)
                pts= np.array([[e[0]*w_scale, e[1]*h_scale] for e in ts]).astype(np.int32)

                pts = pts.reshape((-1,1,2))
                if className in classDic:
                    mask_image= cv2.fillPoly(mask_image, [pts], (classDic[className]))
                    color = COLORS[classDic[className] - 1]
                    # RGB => BGR
                    color = (color[2],color[1],color[0])
                    img = cv2.polylines(img,[pts],isClosed = True, color = color, thickness=2)

                    img_pil = Image.fromarray(img)
                    draw = ImageDraw.Draw(img_pil)
                    font = ImageFont.truetype(fontpath, 16)
                    className = CLASSNAME[classDic[className] - 1]
                    x = pts.min(axis=0)[0][0]
                    y = pts.min(axis=1)[0][1]
                    draw.text((x, y),  className, font = font, fill = (color[0], color[1], color[2], 0))
                    img = np.array(img_pil)
                    # cv2.putText(img, text=className, org=(x,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=color, thickness=2, lineType=cv2.LINE_4)
                else:
                    mask_image= cv2.fillPoly(mask_image, [pts], (background))
                    print('warning found not detected class: %s'%className)

                # cv2.imwrite(classPath + fileName + '.jpg', mask_image)
            classPath = mask_path +  'multiple/'
            if( os.path.exists(classPath)==False):
                    os.makedirs(classPath)
            cv2.imwrite(classPath + fileName + '.png', mask_image)
            img = cv2.resize(img,(W,H))
            cv2.imwrite(mask_path + fileName + '.jpg', img)   
    return

def CreateMaskByPath_Labelme(image_fullpath, json_fullpath, mask_path, fileName):
    
    # $User can read image to get height & width in case it is variant
    img = cv2.imread(image_fullpath, cv2.IMREAD_UNCHANGED)
    H, W, C = img.shape[:3]
    
    if (os.path.exists(json_fullpath)==False):
        # Json file not exit, print "error" and process next
        print(json_fullpath + "not exist!")
    else:
        with open(json_fullpath) as f:

            #load json file
            print('open json file: %s' % json_fullpath )
            d = json.load(f)
            shapes = d['shapes']
            mImageDic={}
            for shape in shapes:
                className = shape['label']
                if className is None:
                    className = 'TODO'
                classPath = mask_path + className + '/'
                if( os.path.exists(classPath)==False):
                        os.makedirs(classPath)

                #key
                if className in mImageDic.keys():
                    mask_image = mImageDic[className]
                else:
                    #create mask image
                    mask_image = np.zeros((H,W,1), np.uint8)
                    mImageDic[className] = mask_image

                data = shape['points']
                #print(len(data))
                ts = np.asarray(data).astype(np.int32)
                pts= np.array([[e[0]*w_scale, e[1]*h_scale] for e in ts])

                pts = pts.reshape((-1,1,2))
                mask_image= cv2.fillPoly(mask_image, [pts], (255))
                #else do nothing
            
            # out to image file
            for key in mImageDic:
                cv2.imwrite(mask_path + key + '/' + fileName + '.jpg', mImageDic[key])    
    return

def CreateMultipleMaskByPath_Labelme(image_fullpath, json_fullpath, mask_path, fileName):
    
    # $User can read image to get height & width in case it is variant
    # img = cv2.imread(image_fullpath, cv2.IMREAD_UNCHANGED)
    img = cv2.imread(image_fullpath)
    w_scale = 1
    h_scale = 1
    if isResize:
        H, W, C = img.shape[:3]
        h_scale = H_R/H
        w_scale = W_R/W 
        H = H_R
        W = W_R
        img = cv2.resize(img,(H,W))
    else:
        H, W, C = img.shape[:3]
    
    if (os.path.exists(json_fullpath)==False):
        # Json file not exit, print "error" and process next
        print(json_fullpath + "not exist!")
    else:
        try:
            with open(json_fullpath) as f:

                #load json file
                # print('open json file: %s' % json_fullpath )
                d = json.load(f)
                shapes = d['shapes']
                # mImageDic={}
                #create mask image
                # mask_image = np.zeros((H,W,1), np.uint8)
                # ignore background
                mask_image = np.full((H,W,1), background,np.uint8)
                for shape in shapes:
                    className = shape['label']
                    className = className.upper()
                    if className is None:
                        className = 'TODO'

                    # #key
                    # if className in mImageDic.keys():
                    #     mask_image = mImageDic[className]
                    # else:
                    #     #create mask image
                    #     mask_image = np.zeros((H,W,1), np.uint8)
                    #     mImageDic[className] = mask_image
                    
                    data = shape['points']
                    #print(len(data))
                    ts = np.asarray(data).astype(np.int32)
                    pts= np.array([[e[0]*w_scale, e[1]*h_scale] for e in ts]).astype(np.int32)

                    pts = pts.reshape((-1,1,2))
                    if className in classDic:
                        mask_image= cv2.fillPoly(mask_image, [pts], (classDic[className]))
                        color = COLORS[classDic[className] - 1]
                        # RGB => BGR
                        color = (color[2],color[1],color[0])
                        img = cv2.polylines(img,[pts],isClosed = True, color = color, thickness=2)
                    
                        img_pil = Image.fromarray(img)
                        draw = ImageDraw.Draw(img_pil)
                        font = ImageFont.truetype(fontpath, 16)
                        className = CLASSNAME[classDic[className] - 1]
                        x = pts.min(axis=0)[0][0]
                        y = pts.min(axis=1)[0][1]
                        draw.text((x, y),  className, font = font, fill = (color[0], color[1], color[2], 0))
                        img = np.array(img_pil)
                    else:
                        mask_image= cv2.fillPoly(mask_image, [pts], (background))
                    
                    # for x in range(mask_image.shape[0]):
                    #     for y in range(mask_image.shape[1]):
                    #         if mask_image[x][y] < 0 or mask_image[x][y] >= 4:
                    #             print("file is %s lable is wrong %d"%(fileName,mask_image[x][y]))
                
                # out to image file
                classPath = mask_path +  'multiple/'
                if( os.path.exists(classPath)==False):
                        os.makedirs(classPath)
                cv2.imwrite(classPath + fileName + '.png', mask_image)
                cv2.imwrite(mask_path + fileName + '.jpg', img)             
        except:
            print(json_fullpath + " had error happened!")
    return

def CreateMultipleMaskByPath2_Labelme(image_fullpath, json_fullpath, mask_path, fileName):
    
    # $User can read image to get height & width in case it is variant
    img = cv2.imread(image_fullpath, cv2.IMREAD_UNCHANGED)
    w_scale = 1
    h_scale = 1
    if isResize:
        H, W, C = img.shape[:3]
        h_scale = H_R/H
        w_scale = W_R/W 
        H = H_R
        W = W_R
        img = cv2.resize(img,(H,W))
    else:
        H, W, C = img.shape[:3]
    
    if (os.path.exists(json_fullpath)==False):
        # Json file not exit, print "error" and process next
        print(json_fullpath + "not exist!")
    else:
        with open(json_fullpath) as f:

            #load json file
            # print('open json file: %s' % json_fullpath )
            d = json.load(f)
            shapes = d['shapes']

            masks=[np.full((H,W,1), background,np.uint8) for i in range(len(classDic))]

            for shape in shapes:
                className = shape['label']
                className = className.upper()
                if className is None:
                    className = 'TODO'
                
                data = shape['points']
                #print(len(data))
                ts = np.asarray(data).astype(np.int32)
                pts= np.array([[e[0]*w_scale, e[1]*h_scale] for e in ts]).astype(np.int32)
                pts = pts.reshape((-1,1,2))

                if className in classDic:
                    mask_image = masks[classDic[className]]
                    mask_image= cv2.fillPoly(mask_image, [pts], 255)
                # else:
                #     mask_image= cv2.fillPoly(mask_image, [pts], (background))
                
                # for x in range(mask_image.shape[0]):
                #     for y in range(mask_image.shape[1]):
                #         if mask_image[x][y] < 0 or mask_image[x][y] >= 4:
                #             print("file is %s lable is wrong %d"%(fileName,mask_image[x][y]))
            
            # out to image file
            for i in range(len(masks)):
                classPath = mask_path +  str(i) + '/'
                if( os.path.exists(classPath)==False):
                        os.makedirs(classPath)
                cv2.imwrite(classPath + fileName + '.png', masks[i])    
    return


def CreateMultipleMaskByPath_Labelme2(image_fullpath, json_fullpath, mask_path, fileName):
    
    return

WalkPath(ROOT_PATH)

