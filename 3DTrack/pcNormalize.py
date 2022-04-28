import os
import os.path
import json
import numpy as np
import sys

def pc_normalize(pc):
    l = pc.shape[0]
    centroid = np.mean(pc, axis=0)
    pc = pc - centroid
    m = np.max(np.sqrt(np.sum(pc**2, axis=1)))
    pc = pc/m

    return pc

if __name__ == '__main__':
    
