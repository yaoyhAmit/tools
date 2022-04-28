import os
import sys
import json
import argparse
from pathlib import Path
import shutil

def main():
    parser = argparse.ArgumentParser(description='distribution json and image files to directory ')

    parser.add_argument('--sPath',required=True,
                        help='the relative path the image file and the Json file exp ./')
    parser.add_argument('--dPath',required=True,
                        help='the relative destliation path')
    
    global mainArgs
    mainArgs = parser.parse_args()

    sp = Path(mainArgs.sPath)
    dp = Path(mainArgs.dPath)

    all_files = sp.glob('*.json')

    for sf in all_files:
        dirName = str(dp) + '/' + os.path.basename(sf).split('-')[0].replace('img','patient')
        if not os.path.exists(dirName):
            os.makedirs(dirName, exist_ok=True)
        shutil.move(str(sf),dirName)
        imgfile = str(sp) + '/' + os.path.basename(sf).split('.')[0] + '.jpg'
        shutil.move(imgfile,dirName)
        print('file name is %',dirName)

if __name__ == '__main__':
    main()