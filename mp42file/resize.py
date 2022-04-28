import cv2 as cv
import numpy as np

img = cv.imread('./1.jpg',cv.IMREAD_GRAYSCALE)

ret,img = cv.threshold(img,127,255,cv.THRESH_BINARY)
img = cv.resize(img,(1024,768))

# cv.imshow('imgresize',img)


# cv.imshow('imgthreshold',img)


contours,hierarchy = cv.findContours(img,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)

print('contours is ',contours[0].shape)
print('contours is ',contours[0])
print('contours is ',contours[0][:,0,1])
print('contours is ',contours[0][:,0,0])
y = min(contours[0][:,0,1])
print('y is ',y)
x = min(contours[0][:,0,0])
print('x is ',x)
w = max(contours[0][:,0,0]) - x
h = max(contours[0][:,0,1]) - y
print('w is',w)
print('h is',h)


imgorg = cv.imread('./1-mask.jpg')
om = imgorg[y:y+h,x:x+w]
cv.imwrite('./i-cut.jpg',om)

# cv.imshow('cut image is',om)

# 显示轮廓，tmp为黑色的背景图
# tmp = np.zeros(img.shape, np.uint8)
# res = cv.drawContours(tmp, contours, -1, (250, 255, 255), 1)
# cv.imshow('Allcontours', res)

# cv.waitKey()
# cv.destroyAllWindows()
