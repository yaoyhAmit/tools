import os
import sys
import argparse
from pathlib import Path
import json as json


def main():

    parser = argparse.ArgumentParser(description='change class name form JV to IJV')

    parser.add_argument('--SJsonPath',required=True,
                        help='Source json path (Labelme Json file path)')


    mainArgs = parser.parse_args()

    sp = Path(mainArgs.SJsonPath)

    all_files = sp.glob('*.json')

    for sf in all_files:
        with open(sf,'r') as f:
            sjson = json.load(f)

        for p in sjson['polygons']:        
            if p['type'] == 'JV':
                p['type'] = 'IJV'
        

        with open(sf,'w') as f:
            json.dump(sjson,f)

if __name__ == "__main__":
    main()