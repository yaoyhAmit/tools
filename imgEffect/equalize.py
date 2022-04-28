from PIL import Image, ImageOps
import argparse

inPutFile = './patient23-7-m-cut.jpg'
outPutFile = './patient23-7-m_out-cut.png'

def main():
    # parser = argparse.ArgumentParser(description='Image equalize')
    full_img_color = Image.open(inPutFile)
    full_img = full_img_color.convert('L')
    # ヒストグラム平坦化
    pil_img = ImageOps.equalize(full_img)
    pil_img.save(outPutFile)

if __name__ == '__main__':
    main()
