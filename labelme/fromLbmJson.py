import os
import sys
import argparse
from pathlib import Path
import json as json


def main():
    
    parser = argparse.ArgumentParser(description='transform Labelmes Json to My Json.')

    parser.add_argument('--SJsonPath',required=True,
                        help='Source json path (Labelme Json file path)')
    parser.add_argument('--DJsonPath',required=True,
                        help='Destliation json path (My Json file path)')

    mainArgs = parser.parse_args()

    sp = Path(mainArgs.SJsonPath)

    all_files = sp.glob('*.json')

    for sf in all_files:
        
        with open(sf,'r') as f:
            sjson = json.load(f)
        
        with open(mainArgs.DJsonPath + os.path.basename(str(sf)), 'r') as f:
            djson = json.load(f)
        
        myjson = {}
        polygons = []
        for shape in sjson['shapes']:
            polygon = {}
            polygon['points'] = shape['points']
            polygon['type'] = shape['label']

            polygons.append(polygon)

        myjson['polygons'] = polygons
        myjson['params'] = djson['params']
        myjson['depth'] = djson['depth']
    
        with open(mainArgs.DJsonPath + os.path.basename(str(sf)), 'w') as f:
            json.dump(myjson, f)
    

if __name__ == "__main__":
    main()
