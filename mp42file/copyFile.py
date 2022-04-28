import shutil
import argparse

parser = argparse.ArgumentParser(description='copy file')
parser.add_argument('--src','-o',help='Copy of the source')
parser.add_argument('--dst','-d',help='Copy of the destination')
parser.add_argument('--file','-f',help='Copy of file')
parser.add_argument('--fnf','-fnf',help='File name is from')
parser.add_argument('--fnt','-fnt',help='File name is to')

args = parser.parse_args()

if __name__ == '__main__':

    for i in  range(int(args.fnf),int(args.fnt)):
        shutil.copyfile(args.src + '/' + args.file,args.dst + '/' + str(i) + '.jpg')

