import SimpleITK as sitk
import glob
import numpy as np
from PIL import Image
import cv2
 
# import matplotlib.pyplot as plt # plt 用于显示图片
 
 
def save_array_as_nii_volume(data, filename, reference_name = None):
	"""
	save a numpy array as nifty image
	inputs:
		data: a numpy array with shape [Depth, Height, Width]
		filename: the ouput file name
		reference_name: file name of the reference image of which affine and header are used
	outputs: None
	"""
	img = sitk.GetImageFromArray(data)
	if(reference_name is not None):
		img_ref = sitk.ReadImage(reference_name)
		img.CopyInformation(img_ref)
	sitk.WriteImage(img, filename)
 
 
image_path = '/media/yao/iot-hd/workspace/trainingdata-us/TEST20210530/images/'
image_arr = glob.glob(str(image_path) + str("/*"))
image_arr.sort()

print(image_arr, len(image_arr))
allImg = []
# allImg = np.zeros([165, 768,1024], dtype='uint8')
allImg = np.zeros([len(image_arr), 768,1024], dtype='uint8')
for i in range(len(image_arr)):
	single_image_name = image_arr[i]
	img_as_img = Image.open(single_image_name).convert('L')
	# img_as_img.show()
	img_as_np = np.asarray(img_as_img)
	allImg[i, :, :] = img_as_np
 
 
# np.transpose(allImg,[2,0,1])
save_array_as_nii_volume(allImg, './testImg.nii.gz')
print(np.shape(allImg))
img = allImg[:, :, 55]
# plt.imshow(img, cmap='gray')
# plt.show()
