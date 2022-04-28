import os
import pandas as pd
from PIL import ImageDraw
from PIL import Image
import math
import json
import matplotlib as plt
import sys
import argparse

def get_images_with_json(raw_data_root_path):
    found = []
    for root, dirs, files in os.walk(raw_data_root_path):
        for filename in files:
            found.append(os.path.join(root, filename))
        for dirname in dirs:
            found.append(os.path.join(root, dirname))

    all_images = [f for f in found if (f[-3:] == 'png' or f[-4:] == 'jpeg' or f[-3:] == 'jpg')]
    all_json = [f for f in found if f[-4:] == 'json']

    all_json_df = pd.DataFrame({'json_with_path':all_json})
    all_images_df = pd.DataFrame({'image_with_path':all_images})

    all_json_df['json_file'] = all_json_df['json_with_path'].apply(lambda x: x.split('/')[-1])
    all_json_df['json_path'] = all_json_df['json_with_path'].apply(lambda x: '/'.join(x.split('/')[:-1]))
    all_json_df['json_no_extension'] = all_json_df['json_with_path'].apply(lambda x: (x.split('/')[-1]).split('.')[0])

    all_images_df['image_file'] = all_images_df['image_with_path'].apply(lambda x: x.split('/')[-1])
    all_images_df['image_path'] = all_images_df['image_with_path'].apply(lambda x: '/'.join(x.split('/')[:-1]))
    all_images_df['image_no_extension'] = all_images_df['image_with_path'].apply(lambda x: (x.split('/')[-1]).split('.')[0])

    temp_df = pd.merge(all_json_df, all_images_df, how = 'inner', left_on = ['json_path', 'json_no_extension'], right_on = ['image_path', 'image_no_extension'])


    return list(temp_df['json_with_path']), list(temp_df['image_with_path'])

def ScaleRotateTranslate(image, angle, center=None, new_center=None,
                             scale=None, expand=False, ):
        '''
        experimental - not used yet
        '''
        if center is None:
            return image.rotate(angle, expand)
        angle = -angle / 180.0 * math.pi
        nx, ny = x, y = center
        #if new_center != center:
        #    (nx, ny) = new_center
        sx = sy = 1.0
        if scale:
            (sx, sy) = scale
        cosine = math.cos(angle)
        sine = math.sin(angle)

        a = cosine / sx
        b = sine / sx
        c = x - nx * a - ny * b
        d = -sine / sy
        e = cosine / sy
        f = y - nx * d - ny * e
        return image.transform(image.size, Image.AFFINE,
                               (a,b,c,d,e,f), resample=Image.BICUBIC)


def Points_coordinate_transformer(point_list, angle, center=None, new_center=None,
                             scale=None, expand=False, ):
        '''
        experimental - not used yet
        '''
        if center is None:
            return image.rotate(angle, expand)
        angle = -angle / 180.0 * math.pi
        nx, ny = x, y = center
        #if new_center != center:
        #    (nx, ny) = new_center
        sx = sy = 1.0
        if scale:
            (sx, sy) = scale
        cosine = math.cos(angle)
        sine = math.sin(angle)

        a = cosine / sx
        b = sine / sx
        c = x - nx * a - ny * b
        d = -sine / sy
        e = cosine / sy
        f = y - nx * d - ny * e

        result_list = []

        #output (x,y) from original (a x + b y + c, d x + e y + f)

        for pairs in point_list:
            temp_x = ((pairs[0]-c)*e - (pairs[1]-f)*b) / (a*e - b*d)
            temp_y = ((pairs[1]-f)*a - (pairs[0]-c)*d) / (a*e - b*d)

            result_list.append([temp_x, temp_y])

        return result_list

def type1(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path):
    img_size_list = []

    for js, im in zip(json_list, image_list):
        data_json = json.load(open(js))

        height = data_json['imageHeight']
        width = data_json['imageWidth']

        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        #heigth = img_raw.size[1]
        #width = img_raw.size[0]
        #print(heigth, width, img_raw.size)
        for ang in rotation_angle:
            for sc in zoom_rate:
                img_out = ScaleRotateTranslate(img_raw, ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                img_out = img_out.convert('RGB')
                img_out_with_label = img_out.copy()
                img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
                data_json_output = {'shapes':[]}
                for temp in data_json['shapes']:
                    transformed_coordinates = Points_coordinate_transformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                    d = ImageDraw.Draw(img_mask)
                    #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                    #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                    d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                    #temp_out['points'] = transformed_coordinates
                    data_json_output['shapes'].append({'label':temp['label'], 'points':transformed_coordinates})

                    d1 = ImageDraw.Draw(img_out_with_label)
                    d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')


                save_name_common_part = ('_rotated_%d_scaled_%d' % (ang, sc*100))
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')



                img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
                img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
                img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')


                f2 = open(output_json_path+read_name + save_name_common_part+'.json', 'w')
                json.dump(data_json_output, f2)

def type2(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path):
    img_size_list = []

    for js, im in zip(json_list, image_list):
        data_json = json.load(open(js))

#         height = data_json['imageHeight']
#         width = data_json['imageWidth']

        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        heigth = img_raw.size[1]
        width = img_raw.size[0]

        for ang in rotation_angle:
            for sc in zoom_rate:
                img_out = ScaleRotateTranslate(img_raw, ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                img_out = img_out.convert('RGB')
                img_out_with_label = img_out.copy()
                img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
                data_json_output = {'polygons':[]}
                for temp in data_json['polygons']:
                    transformed_coordinates = Points_coordinate_transformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                    d = ImageDraw.Draw(img_mask)
                    #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                    #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                    ######### JJG ##################
                    if temp['type']=='CA':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(224,  0,  0))
                    elif temp['type']=='N':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(224,  224,  224))
                    elif temp['type']=='JV':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(0, 224, 0))
                    ######### GW ##################
                    elif temp['type']=='SN':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(255,  255,  0))
                    elif temp['type']=='CPN':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(255,  255,  0))
                    elif temp['type']=='TN':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(255,  255,  0))
                    elif temp['type']=='PA':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(255,  0,    0))
                    elif temp['type']=='PV':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(35,  35,  255))
                    ######### SJJ ##################
                    elif temp['type']=='SM':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(0,  255,  0))
                    elif temp['type']=='VMM':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(0,  128,  0))
                    elif temp['type']=='MG':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(128,  255,  0))
                    elif temp['type']=='FA':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(255,  0,    0))
                    elif temp['type']=='FV':
                        d.polygon(list(map(tuple, transformed_coordinates)), fill=(35,  35,  255))
                    else:
                        print('please check type')
                    #temp_out['points'] = transformed_coordinates
                    data_json_output['polygons'].append({'type':temp['type'], 'points':transformed_coordinates})

                    d1 = ImageDraw.Draw(img_out_with_label)
                    ######### JJG ##################
                    if temp['type']=='CA':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  0,  0))
                    elif temp['type']=='N':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255, 255, 0))
                    elif temp['type']=='JV':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(35,  35,  255))
                    ######### GW ##################
                    elif temp['type']=='SN':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  255,  0))
                    elif temp['type']=='CPN':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  255,  0))
                    elif temp['type']=='TN':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  255,  0))
                    elif temp['type']=='PA':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  0,    0))
                    elif temp['type']=='PV':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(35,  35,  255))
                    ######### SJJ ##################
                    elif temp['type']=='SM':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(0,  255,  0))
                    elif temp['type']=='VMM':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(0,  128,  0))
                    elif temp['type']=='MG':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(128,  255,  0))
                    elif temp['type']=='FA':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(255,  0,    0))
                    elif temp['type']=='FV':
                        d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill=(35,  35,  255))
                    else:
                        print('please check type')
                save_name_common_part = ('_rotated_%d_scaled_%d' % (ang, sc*100))
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')
                img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
                img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
                img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')

                f2 = open(output_json_path+read_name + save_name_common_part+'.json', 'w')
                json.dump(data_json_output, f2)

def type3(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path):
    img_size_list = []

    for js, im in zip(json_list, image_list):
        data_json = json.load(open(js))

#         height = data_json['imageHeight']
#         width = data_json['imageWidth']

        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        heigth = img_raw.size[1]
        width = img_raw.size[0]

        for ang in rotation_angle:
            for sc in zoom_rate:
                img_out = ScaleRotateTranslate(img_raw, ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                img_out = img_out.convert('RGB')
                img_out_with_label = img_out.copy()
                img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
                data_json_output = []
                for temp in data_json:
                    transformed_coordinates = Points_coordinate_transformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                    d = ImageDraw.Draw(img_mask)
                    #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                    #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                    d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                    #temp_out['points'] = transformed_coordinates
                    data_json_output.append({'type':temp['type'], 'points':transformed_coordinates})

                    d1 = ImageDraw.Draw(img_out_with_label)
                    d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')
                save_name_common_part = ('_rotated_%d_scaled_%d' % (ang, sc*100))
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')
                img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
                img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
                img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')

                f2 = open(output_json_path+read_name + save_name_common_part+'.json', 'w')
                json.dump(data_json_output, f2)

def main():

    parser = argparse.ArgumentParser(description='transform image from jjg')
    parser.add_argument('--inPath',required=True,help='raw_data_root_path')
    parser.add_argument('--outPath',required=True,help='output_dir')

    mainArgs = parser.parse_args()

    # raw_data_root_path = sys.argv[1]
    raw_data_root_path = mainArgs.inPath
    #raw_data_root_path = "../DATA/data_20200129/"
    #raw_data_root_path = "../DATA/data_before/"
    # output_dir = sys.argv[2]
    output_dir = mainArgs.outPath
    #output_dir = "./output2/"

    #rotation_angle = [0,45,90,135,180,225,270,315]
    #zoom_rate = [0.95, 1.0, 1.05]
    rotation_angle = [0]
    zoom_rate = [1.0]

    output_image_path = output_dir + 'output_image/'
    output_mask_path = output_dir + 'output_mask/'
    output_image_with_mask_path = output_dir + 'output_image_with_mask/'
    output_json_path = output_dir + 'output_json/'

    try:
        os.makedirs(output_image_path)
    except:
        pass
    try:
        os.makedirs(output_mask_path)
    except:
        pass
    try:
        os.makedirs(output_image_with_mask_path)
    except:
        pass
    try:
        os.makedirs(output_json_path)
    except:
        pass


    json_list, image_list = get_images_with_json(raw_data_root_path)

    counter = 0

    could_not_transformed = []
    total_data_info = []

    for js, im in zip(json_list, image_list):
        if counter % 10 == 0:
            print('processed %d of %d' % (counter, len(json_list)))

        try:
            type1(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
            print('ok -> type 1 -> '+im)
            total_data_info.append(['type_1', im])
        except:

            try:
                type2(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                print('ok -> type 2 -> '+im)
                total_data_info.append(['type_2', im])
            except:
                try:
                    type3(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                    print('ok -> type 3 -> '+im)
                    total_data_info.append(['type_3', im])
                except:
                    print('could not transformed %s due to new json type' % im)
                    could_not_transformed.append(im)
        counter += 1

    print('could not transformed below %d files' % len(could_not_transformed))
    print(could_not_transformed)
    total_data_info = pd.DataFrame(total_data_info, columns = ['type', 'image_name'])
    total_data_info.to_csv('old_data.csv', index=False)

main()
