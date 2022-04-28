import cv2 as cv
import numpy as np
 
# 读入图片
src = cv.imread('./1-mask.jpg')
# 转换成灰度图
gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
# 二值化
ret, thresh = cv.threshold(gray, 1, 127, cv.THRESH_BINARY)

cv.imshow('thresh - 1-127', thresh)
 
# 查找轮廓
# binary-二值化结果，contours-轮廓信息，hierarchy-层级
# binary, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
# 显示轮廓，tmp为黑色的背景图
tmp = np.zeros(src.shape, np.uint8)
res = cv.drawContours(tmp, contours, -1, (250, 255, 255), 1)
cv.imshow('Allcontours', res)
 
cnt = contours[8]
tmp2 = np.zeros(src.shape, np.uint8)
res2 = cv.drawContours(tmp2, cnt, -1, (250, 255, 255), 2)
cv.imshow('cnt', res2)
 
# 轮廓特征
# 面积
print(cv.contourArea(cnt))
# 周长,第二个参数指定图形是否闭环,如果是则为True, 否则只是一条曲线.
print(cv.arcLength(cnt, True))
 
# 轮廓近似，epsilon数值越小，越近似
epsilon = 0.08 * cv.arcLength(cnt, True)
approx = cv.approxPolyDP(cnt, epsilon, True)
tmp2 = np.zeros(src.shape, np.uint8)
# 注意，这里approx要加中括号
res3 = cv.drawContours(tmp2, [approx], -1, (250, 250, 255), 1)
cv.imshow('approx', res3)
 
# 外接图形
x, y, w, h = cv.boundingRect(cnt)
# 直接在图片上进行绘制，所以一般要将原图复制一份，再进行绘制
tmp3 = src.copy()
res4 = cv.rectangle(tmp3, (x, y), (x + w, y + h), (0, 0, 255), 2)
cv.imshow('rectangle', res4)
 
cv.waitKey()
cv.destroyAllWindows()