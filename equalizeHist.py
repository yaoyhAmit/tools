import cv2
import os
import sys
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description='According to the histogram, the image is homogenized')

    parser.add_argument('--i', required=True,
                        metavar='path to changed image file',
                        help = 'path to changed image file')

    parser.add_argument('--o', required=True,
                        metavar='path to changed result',
                        help = 'path to changed result')
    
    parser.add_argument('--isShow',required=False, type=bool, default=False,
                        metavar='show plt windows',
                        help = 'show plt windows')

    mainArgs = parser.parse_args()

    p = Path(mainArgs.i)

    exts = ['.jpg','.jpeg']
    # all_files = p.glob("*.jpg") if x.suffix in exts

    min = 0
    max = 255

    for f in (x for x in p.glob('**/*') if x.suffix in exts):
        img = cv2.imread(str(f))
        img_src = img
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img2 = cv2.equalizeHist(img)
        cv2.imwrite(mainArgs.o + f.name,img2)

        # img_dst = img_src
        # cv2.normalize(img_src, img_dst, min, max, cv2.NORM_MINMAX)
        # cv2.imwrite(mainArgs.o + '2-' + f.name ,img_dst)
        
        if mainArgs.isShow:
            plt.hist(img.ravel(),bins=256,range=[0,256])
            plt.show()
            plt.hist(img2.ravel(),bins=256,range=[0,256])
            plt.show()
            # plt.hist(img_dst.ravel(),bins=256,range=[0,256])
            # plt.show()
        






if __name__ == "__main__":
    main()
