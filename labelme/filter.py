import os
import sys
import json
import argparse
from pathlib import Path
import math

mainArgs = None

FILTERCLASS = ['CA', 'IJV', 'N', 'N-C5', 'N-C6', 'N-C7', 'N-C8']

def main():

    parser = argparse.ArgumentParser(description='transform My Json to Labelmes Json.')

    parser.add_argument('--SJsonPath',required=True,
                        help='Source json path')
    parser.add_argument('--DJsonPath',required=True,
                        help='Destliation json path')

    mainArgs = parser.parse_args()

    sp = Path(mainArgs.SJsonPath)

    all_files = sp.glob('*.json')

    for sf in all_files:
        djson = {}
        with open(sf, 'r') as f:
            sjson = json.load(f)
        
        djson['version'] = sjson['version']
        djson['flags'] = sjson['flags']
        djson['shapes'] = []
        for shape in sjson['shapes']:
            if shape['label'] in FILTERCLASS:
                djson['shapes'].append(shape)
        
        djson['imagePath'] = sjson['imagePath']
        djson['imageData'] = sjson['imageData']
        djson['imageHeight'] = sjson['imageHeight']
        djson['imageWidth'] = sjson['imageWidth']

        with open(mainArgs.DJsonPath + os.path.basename(str(sf)),'w') as f:
            json.dump(djson, f , indent=4)

    return

if __name__ == "__main__":
    main()
