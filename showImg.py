from PIL import Image
import numpy as np

fileName = '/media/yao/iot-hd/workspace/trainingdata-us/02_Fukushima/US-AI-DATA_JJG_lable/JJG/masks-CA-N-IJV/multiple/img10001-v001-000259.png'
def main():
    image = Image.open(fileName)
    # image = image.resize((550,550))
    img_nd = np.array(image)
    img_nd = np.where(img_nd == 0,75,img_nd)
    img_nd = np.where(img_nd == 1,125,img_nd)
    img_nd = np.where(img_nd == 2,175,img_nd)

    imgout = Image.fromarray(img_nd)
    imgout.show()

if __name__ == '__main__':
    main()
