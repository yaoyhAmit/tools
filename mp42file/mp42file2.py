import cv2
import argparse



def main():

    parser = argparse.ArgumentParser(description='Take a specified frame from the video')

    # parser.add_argument('--Prefix', required=True,
    #                     help='image file path include filename prefix')
    parser.add_argument('--FPS',required=False,type=int,default=30,
                        help='fps')
    # parser.add_argument('--W',required=False,type=int,default=1024,
    #                     help='the wide of image file')
    # parser.add_argument('--H',required=False,type=int,default=768,
    #                     help='the high of image file')
    # parser.add_argument('--Postfix',required=False,default='',
    #                     help='the postfix of image file exp. _class_0')
    parser.add_argument('--VideoFile',required=True,default='./us.mp4',
                        help='the VieoFile path of source')
    parser.add_argument('--OUTJPath',required=False,default='./',
                        help='the Image path of destination')
    parser.add_argument('--Indexs',required=True,default='',
                        help='the index list of images')

    # videoFile = '/home/yao/workspace/education-contents/test-contents/data/patient001/vid001-24.mp4'
    # outputFile = '/home/yao/workspace/education-contents/test-contents/data/labelme/patient001/img001-v24'
    
    args = parser.parse_args()

    videoFile = args.VideoFile
    outputFile = args.OUTJPath
    indexs = args.Indexs

    indexList = indexs.split(' ')

    vc = cv2.VideoCapture(videoFile)
    c = 1
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        print('video file open error!')
        rval = False
        return -1

    timeF = 1  #视频帧计数间隔次数
    while rval:
        # print(1)
        #print(c)
        rval, frame = vc.read()
        if rval and c % timeF == 0:
            # print(2)
            if str(c) in indexList:
                fn = outputFile + '-%06d' % int(c / timeF) + '.jpg'
                cv2.imwrite(fn, frame)
        c += 1
        cv2.waitKey(1)
    vc.release()

if __name__ == '__main__':
    main()