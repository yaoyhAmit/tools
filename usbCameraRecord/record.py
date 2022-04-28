# -*- coding: utf-8 -*-
import cv2
import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='USB Camera Record')

    parser.add_argument('--filename',default='./us.mp4',type=str,
                        help='The storage path of the video file.')
    parser.add_argument('--deviceid',default=0,type=int,
                        help='usb camera ID .')
    parser.add_argument('--height',default=1080,type=int,help='height of the video')
    parser.add_argument('--width',default=1920,type=int,help='width of the video')
    parser.add_argument('--fps',default=30,type=int,help='fps of the video')
    args = parser.parse_args(argv)

    return args


def decode_fourcc(v):
        v = int(v)
        return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

def main(args=None):
    cap = cv2.VideoCapture (args.deviceid)

    # フォーマット・解像度・FPSの設定
    #cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V'))


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, args.fps)

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video = cv2.VideoWriter(args.filename,fourcc, args.fps, (args.width,args.height))

    # フォーマット・解像度・FPSの取得
    fourcc = decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC))
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("fourcc:{} fps:{}　width:{}　height:{}".format(fourcc, fps, width, height))

    while True:
        
        # カメラ画像取得
        _, frame = cap.read()
        if(frame is None):
            continue

        # write the flipped frame
        video.write(frame)

        # 画像表示
        cv2.imshow('frame', frame)

        # キュー入力判定(1msの待機)
        # waitKeyがないと、imshow()は表示できない
        # 'q'をタイプされたらループから抜ける
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # VideoCaptureオブジェクト破棄
    cap.release()
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    args = parse_args()
    main(args)
