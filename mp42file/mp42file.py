import cv2
import numpy as np
# import pyocr

# videoFile = '/mnt/iot-hd/workspace/02.Fukushima/01.JJG/patient10001/vid10001-001.mp4'
# outputFile ='/mnt/iot-hd/workspace/02.Fukushima/98.検証用/01.JJG/patient10001/fullScreenImages/img10001-v001'
# videoFile = '/mnt/iot-hd/workspace/trainingdata-us-second/liver/patient90005/patient90005/vid90005-002.mp4'
# outputFile ='/mnt/iot-hd/workspace/trainingdata-us-second/liver/patient90005/patient90005/images/vid90005-002/vid90005-002'
# videoFile = '/home/yao/workspace/trainingdata-us/29220122模型视频/18cm/20220122172632/20220122172632.mp4'
# outputFile ='/home/yao/workspace/trainingdata-us/29220122模型视频/18cm/20220122172632/images/20220122172632'
# videoFile = '/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/标准模型/20220124215740/20220124215740.mp4'
# outputFile ='/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/标准模型/20220124215740/images/20220124215740'
# videoFile = '/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/腹部体膜/20220124220552/20220124220552.mp4'
# outputFile ='/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/腹部体膜/20220124220552/images/20220124220552'
videoFile = '/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/腹部体膜/20220124220645/20220124220645.mp4'
outputFile ='/home/yao/workspace/trainingdata-us/20220124标注模型及腹部体模视频/腹部体膜/20220124220645/images/20220124220645'


# filename = 'img224-v03-'
isNeedCut = False
#depth 3.3
# cut_point = [188,55]
# width_height=[710,605]
#depth 2.7
cut_point = [134,72]
width_height=[818,564]
#depth 4.0
# cut_point = [252,55]
# width_height=[581,605]

def colorFilter(img):
    lower_range = np.array([0,0,0])
    upper_range = np.array([0,255,255]) # yellow color
    mask = cv2.inRange(img,lower_range,upper_range)
    result = cv2.bitwise_and(img,img,mask=mask)
    
    # OCR
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    

    res = tools[0].image_to_string(Image.open("target.png"),lang="eng")

    cv2.imshow('Image',result)
    cv2.waitKey(0)
    cv2.destroyWindow('Image')

def main():
    vc = cv2.VideoCapture(videoFile)
    c = 1
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        print('openerror!')
        rval = False

    timeF = 1  #视频帧计数间隔次数
    while rval:
        # print(1)
        #print(c)
        rval, frame = vc.read()
        if rval and c % timeF == 0:
            # print(2)
            fn = outputFile + '-%06d' % int(c / timeF) + '.jpg'
            # colorFilter(frame)
            if isNeedCut:
                frame = frame[cut_point[1]:cut_point[1]+width_height[1], cut_point[0]:cut_point[0]+width_height[0]]
            cv2.imwrite(fn, frame)
        c += 1
        # cv2.waitKey(1)
    vc.release()

if __name__ == '__main__':
    main()