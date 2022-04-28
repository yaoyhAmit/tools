import sys
import cv2
import argparse
import shutil
import os

FPS = 30
# FPS = 50
FPS_slow = 14
W = 1024
H = 768
# W = 710FV
# H = 605

From = 1
To = 137

# Prefix = '/media/yao/iot-hd/workspace/trainingdata-us/TEST20210530/images/20210530161824-1'
Prefix = '/mnt/iot-hd/workspace/02.Fukushima/05.GSJ/patient10010/inference_res'
Postfix = 'img10010-v011-'


def main():

    parser = argparse.ArgumentParser(description='create mp4 video from image files.')

    parser.add_argument('--Prefix', required=True,
                        help='image file path include filename prefix')
    parser.add_argument('--From',required=False,type=int,default=1,
                        help='minimun index of image files')
    parser.add_argument('--To',required=True,type=int,
                        help='maximun index of image files')
    parser.add_argument('--FPS',required=False,type=int,default=30,
                        help='fps')
    parser.add_argument('--FPS_slow',required=False,type=int,default=30,
                        help='the pfs of slow play')
    parser.add_argument('--W',required=False,type=int,default=1024,
                        help='the wide of image file')
    parser.add_argument('--H',required=False,type=int,default=768,
                        help='the high of image file')
    parser.add_argument('--Postfix',required=False,default='',
                        help='the postfix of image file exp. _class_0')
    parser.add_argument('--INJPath',required=False,default='',
                        help='the JSON path of copy source')
    parser.add_argument('--OUTJPath',required=False,default='',
                        help='the JSON path of copy destination')

    args = parser.parse_args()
    
    Prefix = args.Prefix
    From = args.From
    To = args.To
    FPS = args.FPS
    FPS_slow = args.FPS_slow
    W = args.W
    H = args.H
    Postfix = args.Postfix
    sJPath = args.INJPath
    dJPath = args.OUTJPath
    

    # encoder(for mp4)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    # output file name, encoder, fps, size(fit to image size)
    fileName = Prefix.split('/')[-1] + '.mp4'
    fileName_slow = Prefix.split('/')[-1] + '_slow.mp4'
    video = cv2.VideoWriter(fileName,fourcc, FPS, (W,H))
    video_slow = cv2.VideoWriter(fileName_slow,fourcc, FPS_slow, (W,H))

    if not Postfix == '':
        fileNamePost = Prefix.split('/')[-1] + Postfix + '.mp4'
        fileName_slowPost = Prefix.split('/')[-1] + Postfix + '_slow.mp4'
        videoPost = cv2.VideoWriter(fileNamePost,fourcc, FPS, (W,H))
        video_slowPost = cv2.VideoWriter(fileName_slowPost,fourcc, FPS_slow, (W,H))

    if not video.isOpened():
        print("can't be opened")
        sys.exit()

    for i in range(From, To+1):
        # Prefix-000.jpg, Prefix-001.jpg,..., Prefix-090.jpg
        # fn = '%s-%06d_res.png' % (Prefix,i)
        fn = '%s %04d.jpg' % (Prefix,i)
        img = cv2.imread(fn)

        # can't read image, escape
        if img is None:
            print("can't read %s"%(fn))
            continue
        text = Prefix.split('/')[-1] + '-%06d' % i
        cv2.putText(img, text,(50,50),cv2.FONT_HERSHEY_DUPLEX,0.6, [255, 255, 255],1,cv2.LINE_AA)
        # add
        video.write(img)
        # video_slow.write(img)
        for j in range(2):
            video_slow.write(img)
            if sJPath is not None and dJPath is not None:
                src = '%s/%s-%06d.json' % (sJPath,Prefix.split('/')[-1],i)
                dest = '%s/%s-%06d.json' % (dJPath,Prefix.split('/')[-1],2*i-1+j)
                if os.path.isfile(src):
                    shutil.copyfile(src,dest)
                    print('src %06d dest %06d' % (i,2*i-1+j))
        # print(i)

        if not Postfix == '':
            # Prefix-000.jpg, Prefix-001.jpg,..., Prefix-000090.jpg
            imgPost = cv2.imread('%s %04d%s.jpg' % (Prefix,i,Postfix))

            # can't read image, escape
            if imgPost is None:
                print("can't read")
                imgPost = img
                text = Prefix.split('/')[-1] + '-%06d' % i + ' No recognizable objects found'
            else:
                text = Prefix.split('/')[-1] + '-%06d%s' % (i,Postfix)
            
            cv2.putText(imgPost, text,(50,50),cv2.FONT_HERSHEY_DUPLEX,0.6, [255, 255, 255],1,cv2.LINE_AA)
            # add
            videoPost.write(imgPost)
            for j in range(2):
                video_slowPost.write(imgPost)
                if sJPath is not None and dJPath is not None:
                    src = '%s/%s-%06d%s.json' % (sJPath,Prefix,i,Postfix)
                    dest = '%s/%s-%06d%s.json' % (dJPath,Prefix,2*i-1+j,Postfix)
                    if os.path.isfile(src):
                        shutil.copyfile(src,dest)

    video.release()
    video_slow.release()
    if not Postfix == '':
        videoPost.release()
        video_slowPost.release()
    print('written')


if __name__ == '__main__':
    main()
