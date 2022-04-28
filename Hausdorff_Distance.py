import numpy as np
from monai.metrics import compute_hausdorff_distance
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from plyfile import PlyData, PlyElement

import warnings
warnings.filterwarnings('ignore')

def main():
    #HD算出
    n_classes = 2
    arr = np.zeros((1,n_classes,32,32,32),dtype=np.uint8) #(batch,n_classes,H,W,D) array must be one-hot format
    arr2 = np.zeros((1,n_classes,32,32,32),dtype=np.uint8)

    arr[0,0,0,0,0] = 1
    arr2[0,0,8,8,8] = 1

    arr[0,1,0,0,0] = 1
    arr2[0,1,16,16,16] = 1

    print("manual : ")
    print(round((((8-0)**2)*3)**0.5,4),round((((16-0)**2)*3)**0.5,4)) # Euclidean distance between two points. 2点のユークリッド距離の手動計算
    print("MONAI : ")
    HD = compute_hausdorff_distance(arr,arr2,include_background=True)
    print(f"{HD[0][0]:.4f} {HD[0][1]:.4f}")

    n_classes = 1
    arr = np.zeros((1,n_classes,32,32,32),dtype=np.uint8) #(batch,n_classes,H,W,D) array must be one-hot format
    arr2 = np.zeros((1,n_classes,32,32,32),dtype=np.uint8)

    #２つの立方体についてHDを計算
    arr[0,0,5:15,5:15,5:15] = 1
    arr2[0,0,20:30,20:30,20:30] = 1

    # plot_3d(arr[0,0,:,:,:],arr2[0,0,:,:,:])

    HD = compute_hausdorff_distance(arr,arr2,include_background=True)
    print(f"{HD[0][0]:.4f}")

    n_classes = 1
    arr = np.zeros((1,n_classes,32,32,32),dtype=np.uint8) #(batch,n_classes,H,W,D) array must be one-hot format
    arr2 = np.zeros((1,n_classes,32,32,32),dtype=np.uint8)

    arr[0,0,5:15,5:15,5:15] = 1
    arr[0,0,1:3,1:3,1:3] = 1 #outlier 外れ値 
    arr2[0,0,20:30,20:30,20:30] = 1

    # plot_3d(arr[0,0,:,:,:],arr2[0,0,:,:,:])

    HD_100 = compute_hausdorff_distance(arr,arr2,include_background=True)
    HD_95 = compute_hausdorff_distance(arr,arr2,include_background=True,percentile=95)

    #95% HD excludes the effect of outliers
    #95%では外れ値の影響を除外できていることが分かる
    print(f"HD 100% : {HD_100[0][0]:.4f}")
    print(f"HD 95% : {HD_95[0][0]:.4f}")


def readPly(fileName):

    plydata = PlyData.read(fileName)
    n = plydata.elements[0].count
    print('elements[0].name is ',plydata.elements[0].name)
    print('elements[0].count is ',plydata.elements[0].count)
    
    n_classes = 1
    # n = 20000
    # arr = np.zeros((1,n_classes,n,n,n), dtype=np.uint8)
    arr = np.zeros((1,n_classes,n,n,n), dtype=np.uint8)
    # print(arr.share)
    # arr2 = np.zeros((1,n_classes,n,n,n),dtype=np.float32)
    # for k in range(n):
        # arr[k] = plydata.elements[0].data[k]
    arr[:,2] = plydata.elements[0].data['x']
    arr[:,3] = plydata.elements[0].data['y']
    arr[:,4] = plydata.elements[0].data['z']
        # arr[k] = plydata.elements[0].data[k][1]
        # arr[k] = plydata.elements[0].data[k][2]
        # print(arr[k])
        
        # arr2[k][1] = plydata.elements[0].data[k][1]
        # arr2[k][2] = plydata.elements[0].data[k][2]
    # arr2 = arr
    # arr = np.c_[ np.zeros(n), np.zeros(n), arr]
    print(arr)
    # arr2 = np.c_[ np.zeros(n), np.zeros(n), arr2]
    # arr2 = arr

    # HD_95 = compute_hausdorff_distance(arr,arr2,include_background=True,percentile=95)

    # print(f"HD 95% : {HD_95[0][0]:.4f}")


if __name__ == '__main__':
    main()
    readPly('/home/yao/workspace/MITK/data/Blood5000.ply')
