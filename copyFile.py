import os
import shutil

# source_path = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220401/22222')
# target_path_jpg = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220401/images')
# target_path_json = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220401/jsons')
source_path = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220421/LIV_130-135_0421')
target_path_jpg = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220421/images')
target_path_json = os.path.abspath('/media/yao/ボリューム/ubuntu/workspace/trainingdata-us/pigLive20220421/jsons')

if not os.path.exists(target_path_jpg):
    os.makedirs(target_path_jpg)

if not os.path.exists(target_path_json):
    os.makedirs(target_path_json)

if os.path.exists(source_path):
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.find('jpg') > -1:
                src_file = os.path.join(root, file)
                shutil.copy(src_file,target_path_jpg)
                print(src_file)
            elif file.find('json') > -1:
                src_file = os.path.join(root, file)
                shutil.copy(src_file,target_path_json)
                print(src_file)

print('copy is finished')