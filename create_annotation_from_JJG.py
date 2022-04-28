import os
import json
import numpy as np
import sys
from PIL import Image, ImageDraw


def get_all_json(path):
    found = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            found.append(os.path.join(root, filename))
        for dirname in dirs:
            found.append(os.path.join(root, dirname))

    return list(sorted([f.split('/')[-1] for f in found if f[-4:]=='json']))


def get_area(points):
    val = np.array(points)
    min_x = val.min(axis=0)[0]
    min_y = val.min(axis=0)[1]
    max_x = val.max(axis=0)[0]
    max_y = val.max(axis=0)[1]
    img = Image.new('RGB', (int(max_x)+10, int(max_y)+10), (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon(list(map(tuple, points)), fill='white')
    area = float(np.count_nonzero(np.array(img))/3)
    return area


def get_bbox(val):
    #val = points.copy()
    val = np.array(val)

    min_x = val.min(axis=0)[0]
    min_y = val.min(axis=0)[1]
    max_x = val.max(axis=0)[0]
    max_y = val.max(axis=0)[1]

    #print(min_x, max_x, min_y, max_y)
    bbox = [min_x, min_y, max_x-min_x, max_y-min_y]
    return bbox


def type_1(all_json, path_output_image, path_output_json):
    data_set_dic = {
        "images":[],
        "annotations":[]
    }

    image_id = 0
    ann_id = 0

    counter = 0
    for json_file in all_json:
        if counter % 100 == 0:
            print(counter, 'of', len(all_json))
        counter += 1
        try:
            image_id += 1
            #---------------image---------------------
            image_name = json_file.split('.')[0] + '.jpeg'
            im = Image.open(path_output_image + image_name)
            width = im.size[0]
            height = im.size[1]
            #file_name = pair[0].split('.')[0]+'.jpg'
            image = {"id":image_id,"width": width,"height": height,"file_name": image_name}

            data_set_dic["images"].append(image)

            #---------------annotation---------------------

            temp_list = json.load(open(path_output_json + json_file))['shapes']

            for temp in temp_list:
                ann_id += 1
                segmentation = []
                for seg in temp['points']:
                    segmentation += seg

                bbox = get_bbox(temp['points'])
                #print(temp['points'])
                area = get_area(temp['points'])
                annotation = {"id":ann_id, "image_id":image_id, "category_id":1, "segmentation":[segmentation],
                              "bbox": bbox, "iscrowd": 0,"area": area}

                data_set_dic["annotations"].append(annotation)
        except:
            print('this is not created '+json_file)
    return data_set_dic

def type_2(all_json, path_output_image, path_output_json):
    data_set_dic = {
        "images":[],
        "annotations":[]
    }

    image_id = 0
    ann_id = 0

    counter = 0
    for json_file in all_json:
        if counter % 100 == 0:
            print(counter, 'of', len(all_json))
        counter += 1
        try:
            image_id += 1
            #---------------image---------------------
            image_name = json_file.split('.')[0] + '.jpg'
            im = Image.open(path_output_image + image_name)
            width = im.size[0]
            height = im.size[1]
            #file_name = pair[0].split('.')[0]+'.jpg'
            image = {"id":image_id,"width": width,"height": height,"file_name": image_name}

            data_set_dic["images"].append(image)

            #---------------annotation---------------------

            temp_list = json.load(open(path_output_json + json_file))['polygons']

            for temp in temp_list:
                try:
                    ann_id += 1
                    segmentation = []
                    for seg in temp['points']:
                        segmentation += seg

                    bbox = get_bbox(temp['points'])

                    area = get_area(temp['points'])
                    annotation = {"id":ann_id, "image_id":image_id, "category_id":1, "segmentation":[segmentation],
                                  "bbox": bbox, "iscrowd": 0,"area": area}

                    data_set_dic["annotations"].append(annotation)
                except:
                    print('bbox is outside of picture')
        except:
            print('this is not created '+json_file)
    return data_set_dic


def all_type(all_json, path_output_image, path_output_json):
    data_set_dic = {
        "images":[],
        "annotations":[]
    }

    image_id = 0
    ann_id = 0

    counter = 0
    for json_file in all_json:
        if counter % 100 == 0:
            print(counter, 'of', len(all_json))
        counter += 1
        try:
            image_id += 1
            #---------------image---------------------
            image_name = json_file.split('.')[0] + '.jpg'
            im = Image.open(path_output_image + image_name)
            width = im.size[0]
            height = im.size[1]
            #file_name = pair[0].split('.')[0]+'.jpg'
            image = {"id":image_id,"width": width,"height": height,"file_name": image_name}

            data_set_dic["images"].append(image)

            #---------------annotation---------------------


            try:
                temp_list = json.load(open(path_output_json + json_file))['shapes']
                json_type = 'type1'
            except:
                try:
                    temp_list = json.load(open(path_output_json + json_file))['polygons']
                    json_type = 'type2'
                except:
                    try:
                        temp_list = json.load(open(path_output_json + json_file))
                        json_type = 'type3'
                    except:
                        print('could not create ann due to new json type')

            for temp in temp_list:
                try:
                    ann_id += 1
                    segmentation = []
                    for seg in temp['points']:
                        segmentation += seg

                    bbox = get_bbox(temp['points'])

                    area = get_area(temp['points'])


                    category_id = 0
                    if json_type == 'type1':
                        temp['label']
                        category_id = 1

                    if json_type == 'type2':
                        try:
                            #category_id = ['SN', 'TN', 'CPN', 'PA', 'PV'].index(temp['type'])  # , 'ASM', 'MSM', 'SCM'].index(temp['type'])
                            category_id = ['N', 'CA', 'JV'].index(temp['type'])
                            category_id += 1
                        except:
                            #print(temp['type'], ' is not in LABEL.')
                            pass
                    if json_type == 'type3':
                        category_id = 1

                    if category_id != 0:
                        annotation = {"id":ann_id, "image_id":image_id, "category_id":category_id, "segmentation":[segmentation],"bbox": bbox, "iscrowd": 0,"area": area}
                        data_set_dic["annotations"].append(annotation)
                except:
                    print('bbox is outside of image '+image_name)
        except:
            print('this is not created '+json_file)
    return data_set_dic

def get_specific_files_with_condition(all_json):
    def exist_in_specific_files(js_file):
#JIJIANGOU

# train dataset
        # get_list = ['patient1-', 'patient3-', 'patient4-', 'patient5-', 'patient6-', 'patient7-', 'patient9-', 'patient10-', 'patient11-', 'patient12-', 'patient13-', 'patient15-', 'patient16-', 'patient17-', 'patient18-', 'patient19-', 'patient21-', 'patient22-', 'patient23-', 'patient24-', 'patient25-', 'patient27-', 'patient28-', 'patient29-', 'patient30-', 'patient31-']# train
# validition dataset
        get_list = ['patient33-', 'patient34-', 'patient35-', 'patient37-', 'patient38-', 'patient39-']# validation
# test dataset
        #get_list = ['patient2-', 'patient8-', 'patient14-', 'patient20-', 'patient26-', 'patient32-', 'patient36-']# test


#GWWO
# train dataset
        #get_list = ['patient3020-','patient3028-','patient3034-','patient3045-','patient3046-','patient3049-','patient3052-','patient3056-','patient3059-','patient3072-','patient3078-','patient3108-','patient3109-','patient3114-','patient3115-','patient3117-','patient3120-','patient3122-','patient3123-','patient5033-','patient5035-','patient5037-','patient5043-','patient5045-','patient5052-','patient5061-','patient5065-','patient5067-','patient5070-','patient5085-', 'patient3116-', 'patient3143-', 'patient5083-', 'patient3144-', 'patient3171-', 'patient5086-', 'patient3142-', 'patient5074-', 'patient3025-', 'patient5098-', 'patient5073-', 'patient5075-', 'patient3081-', 'patient3018-', 'patient3157-', 'patient5082-', 'patient5080-', 'patient5066-', 'patient6006-', 'patient5077-']# train GUOWO
# validation dataset
        #get_list = ['patient3053-', 'patient3060-', 'patient3075-','patient5021-', 'patient5041-','patient5050-', 'patient5058-','patient3166-', 'patient3138-', 'patient3128-', 'patient3148-', 'patient5062-', 'patient4029-']# validation GUOWO
# test dataset
        #get_list = ['patient5069-', 'patient5039-', 'patient3121-', 'patient3063-', 'patient5024-','patient5079-', 'patient4036-', 'patient5084-', 'patient3125-', 'patient3126-', 'patient3139-', 'patient5096-']


#SHOUJIGUAN
# Train dataset
        #get_list = ['patient3134', 'patient3104', 'patient3169', 'patient3062', 'patient3164', 'patient3163', 'patient3112', 'patient5040', 'patient3129', 'patient3167', 'patient3043', 'patient3155', 'patient4018', 'patient4022', 'patient3110', 'patient5042', 'patient3154', 'patient3107', 'patient5022', 'patient5044', 'patient5094', 'patient5103', 'patient5046', 'patient6072', 'patient5104', 'patient5102', 'patient3016', 'patient3111', 'patient4027', 'patient5047', 'patient5097', 'patient3106', 'patient3147', 'patient3074', 'patient3061', 'patient3055', 'patient3039', 'patient3132', 'patient3058', 'patient3022', 'patient3040', 'patient3076', 'patient3119']
# validation dataset
        #get_list = ['patient6074', 'patient3156', 'patient3042', 'patient3170', 'patient3133', 'patient3153', 'patient3051', 'patient4028', 'patient3168', 'patient3071', 'patient4019', 'patient3054', 'patient3041', 'patient3158'] # validation shoujiguan ADD DATA_3
# test dataset
        #get_list = ['patient3064', 'patient5048', 'patient3021', 'patient3017', 'patient3165', 'patient5105', 'patient3135', 'patient3146', 'patient5072', 'patient3019', 'patient4023', 'patient6070', 'patient3118', 'patient3113']# test shou jiguan ADD DATA_3




        flag = 0
        for f in get_list:
            if (f in js_file) and ('patient') in js_file: # and ('scaled_105' not in js_file)

                flag = 1
        if flag == 1:
            return True
        else:
            return False

    ret_list = []
    for json_file in all_json:
        if exist_in_specific_files(json_file):
        #if ('scaled_105' not in json_file) and exist_in_specific_files(json_file):
            ret_list.append(json_file)
    return ret_list

def main():
    base_path = sys.argv[1]
    path_annotion_save = sys.argv[2]
    name_annotion_save = sys.argv[3]
    #json_type = sys.argv[4]

    #base_path = '../DATA/output_data_before'
    if not base_path.endswith('/'):
        base_path += '/'

    if not path_annotion_save.endswith('/'):
        path_annotion_save += '/'

    path_output_image = base_path + 'output_image/'
    path_output_json = base_path + 'output_json/'

    all_json = get_all_json(path_output_json)
    all_json = get_specific_files_with_condition(all_json)
    # print(sorted(all_json))
    # print(len(all_json))

    # if json_type == 'type1':
    #     annotation_dic = type_1(all_json, path_output_image, path_output_json)
    # elif json_type == 'type2':
    #     annotation_dic = type_2(all_json, path_output_image, path_output_json)
    # else:
    #     print('insert type correctly')

    annotation_dic = all_type(all_json, path_output_image, path_output_json)

    f2 = open(path_annotion_save + name_annotion_save, 'w')
    json.dump(annotation_dic, f2)
    f2.close()

    json.load(open(path_annotion_save+'/'+name_annotion_save))
    print('total json number is ', len(all_json))
    print('all process are finished')

main()
