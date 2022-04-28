# import the necessary packages
from skimage.metrics import structural_similarity
# from skimage import measure
import argparse
import imutils
import cv2
import csv

# x = 232
# y = 140
# w = 557
# h = 583

# resize_w = 1024
# resize_h = 768

def main():
    parser = argparse.ArgumentParser(description="computing two image files diffence")

    parser.add_argument('--Prefix', required=True,help='image file path include filename prefix')
    parser.add_argument('--From',required=False,type=int,default=1,help='minimun index of image files')
    parser.add_argument('--To',required=True,type=int,help='maximun index of image files')
    parser.add_argument('--Show',required=False,type=bool,default=False,help='maximun index of image files')
    parser.add_argument('--OutCSV',required=False,default='./out.csv',help='maximun index of image files')
    parser.add_argument('--Threshold',required=False,type=float,default=0.9999,help='threshold value of similarity')

    args = parser.parse_args()

    Prefix = args.Prefix
    From = args.From
    To = args.To
    Show = args.Show
    outCSV = args.OutCSV
    threshold = args.Threshold

    samecount = 0

    with open(outCSV,mode='w') as csvoutput:
        csv_writer = csv.writer(csvoutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(From, To):
            # Prefix-000.jpg, Prefix-001.jpg,..., Prefix-090.jpg
            imageA = cv2.imread('%s-%06d.jpg' % (Prefix,i))
            imageB = cv2.imread('%s-%06d.jpg' % (Prefix,i+1))
            if imageA is None or imageB is None:
                print("can't read")
                continue

            grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
            # can't read image, escape

            # (score, diff) = compare_ssim(grayA, grayB, full=True)
            (score, diff) = structural_similarity(grayA, grayB, full=True)
            diff = (diff * 255).astype("uint8")
            if score > threshold :
                print('SSIM: %f  ImageA: %s-%06d.jpg  %06d.jpg '%(score,Prefix,i,i+1))
                # print('ImageB: %s-%06d.jpg'%(Prefix,i+1))
                samecount = samecount + 1
                csv_writer.writerow([i+1])
            else:
                print("SSIM: {}".format(score))

            if Show:
                # threshold the difference image, followed by finding contours to
                # obtain the regions of the two input images that differ
                thresh = cv2.threshold(diff, 0, 255,
                    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # loop over the contours
                for c in cnts:
                    # compute the bounding box of the contour and then draw the
                    # bounding box on both input images to represent where the two
                    # images differ
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # show the output images
                cv2.imshow("Original", imageA)
                cv2.imshow("Modified", imageB)
                cv2.imshow("Diff", diff)
                cv2.imshow("Thresh", thresh)
                cv2.waitKey(0)

    print('same image count is: %d'%(samecount))

if __name__ == '__main__':
    main()