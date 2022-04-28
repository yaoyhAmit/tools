# change the pic left and right trans and add json 
#   python3 transALL.py  gw/gw-o  gw/gw-m  1
#  python3 transALL.py  gw/gw-o  gw/gw-o-d 2
#  python3 transALL.py  gw/gw-m  gw/gw-m-d 2  
#  python3 transALL.py  gw/gw-o  gw/gw-o-r 3 
#   transALL.py  gw/gw-m  gw/gw-m-r 3 
#0609
import os
import pandas as pd
from PIL import ImageDraw
from PIL import Image,ImageEnhance
import math
import json
import matplotlib as plt
import sys
import os
import shutil 
#import shutil

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
                               
def ScaleImageTranslate(image, angle, center=None, new_center=None,
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
        #if center is None:
            #return image.rotate(angle, expand)
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


def Points_coordinate_LeftRight(point_list, angle, width,height,scale=None):
        '''
        experimental - not used yet
        '''
        #if center is None:
        #    return image.rotate(angle, expand)
        angle = -angle / 180.0 * math.pi
       # nx, ny = x, y = center
        #if new_center != center:
        #    (nx, ny) = new_center
        result_list = []

        #output (x,y) from original (a x + b y + c, d x + e y + f)

        for pairs in point_list:
            temp_x = width-pairs[0]
            temp_y = pairs[1]

            result_list.append([temp_x, temp_y])

        return result_list        
def getDepth(json_list):
    for js in json_list:
        data_json = json.load(open(js))
        #data_json_output = {'polygons':[]}
        depth=data_json['depth']
        print(depth)
    return depth   
def imgUniformSizeTranslate2(image,imgdepth,uniformdepth):
        

    newWidthLeft=0
    newWidthRight=0
    newHeight=0
    below33=None
    if(imgdepth<uniformdepth):
        print("imgdepth<uniformdepth")  
        newWidthLeft=round((1024-image.size[0])/2)
        newWidthRight=768-image.size[0]-newWidthLeft
        newHeight=768-image.size[1]
        newImg=Image.new("RGB",(1024,768),"#000000")
        newImg.paste(image, (newWidthLeft, 0))
        below33=True   
    if(imgdepth>uniformdepth):
        print("imgdepth>uniformdepth")
        newWidthLeft=round((image.size[0]-1024)/2)
        newHeight=(image.size[1]-768)/2 
        newWidthLeft=newWidthLeft+15
        newHeight=newHeight-20
        newImg=image.crop((newWidthLeft,newHeight,newWidthLeft+1024,newHeight+768))
        below33=False
    if(imgdepth==uniformdepth):
        print("imgdept==uniformdepth")
        newImg=image
        below33=None   
## print(image.size[1]) 
    return newImg,newWidthLeft,newHeight,below33
def Points_coordinate_uniformSize_copy(json,point_list,xoffset,yoffset,imgdepth,uniformdepth,scale=None):
        '''
        experimental - not used yet
        '''
       
        sx = sy = 1.0
        ratio=1.0
        if scale:
            (sx, sy) = scale
            ratio=sx/sy
        result_scalelist = []

        #output (x,y) from original (a x + b y + c, d x + e y + f)

        for pairs in point_list:
            temp_x = round(pairs[0]/ratio)
            temp_y = round(pairs[1]/ratio)

            result_scalelist.append([temp_x, temp_y])



        result_list = []
        for pairs in result_scalelist:
            if imgdepth<uniformdepth:# depth below 33， should add blackground
               temp_x = round(pairs[0]+xoffset)
               temp_y = round(pairs[1])
            if imgdepth>uniformdepth:
               temp_x = round(pairs[0]-xoffset)
               temp_y = round(pairs[1]-yoffset)
               if(temp_x>=0):
                  temp_x = round(pairs[0]-xoffset) 
               if(temp_x<0):
                   print("X wrong,imagename:")#,os.path.basename(json))
                   temp_x =0
                      
               if(temp_y>=0):
                   temp_y = round(pairs[1]-yoffset)
               if(temp_y<0):
                   temp_y = 0
                   print("Y wrong,,imagename:,")#,os.path.basename(json))
                   #break

            if imgdepth==uniformdepth:
               temp_x = pairs[0]
               temp_y = pairs[1]
                        
            result_list.append([temp_x, temp_y])

        return result_list
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
        ratio=1.0
        if scale:
            (sx, sy) = scale
            ratio=sx/sy
        print(image.size[1])    
        height=round(image.size[1]/ratio)
        ##width = img_raw.size[0]
        weight=round(image.size[0]/ratio)
        
        return image.resize((weight,height)) 
def Points_coordinate_scaletransformer(point_list, angle, center=None, new_center=None,
                             scale=None, expand=False, ):
        '''
        experimental - not used yet
        '''
        #if center is None:
            #return image.rotate(angle, expand)
        angle = -angle / 180.0 * math.pi
        nx, ny = x, y = center
        #if new_center != center:
        #    (nx, ny) = new_center
        sx = sy = 1.0
        ratio=1.0
        if scale:
            (sx, sy) = scale
            ratio=sx/sy
        result_list = []

        #output (x,y) from original (a x + b y + c, d x + e y + f)

        for pairs in point_list:
            temp_x = round(pairs[0]/ratio)
            temp_y = round(pairs[1]/ratio)

            result_list.append([temp_x, temp_y])

        return result_list  

def Points_coordinate_uniformSize(json,point_list,xoffset,yoffset,imgdepth,uniformdepth):
    
    #if center is None:
        #return image.rotate(angle, expand)
    #angle = -angle / 180.0 * math.pi
    #nx, ny = x, y = center
    #if new_center != center:
    #    (nx, ny) = new_cente

    #output (x,y) from original (a x + b y + c, d x + e y + f)
    result_list = []
    for pairs in point_list:
        if imgdepth<uniformdepth:# depth below 33， should add blackground
            temp_x = round(pairs[0]+xoffset)
            temp_y = round(pairs[1])
        if imgdepth>uniformdepth:
            temp_x = round(pairs[0]-xoffset)
            temp_y = round(pairs[1]-yoffset)
            if(temp_x>=0):
                temp_x = round(pairs[0]-xoffset) 
            if(temp_x<0):
                print("X wrong,imagename:")#,os.path.basename(json))
                temp_x =0
                    
            if(temp_y>=0):
                temp_y = round(pairs[1]-yoffset)
            if(temp_y<0):
                temp_y = 0
                print("Y wrong,,imagename:,")#,os.path.basename(json))
                #break

        if imgdepth==uniformdepth:
            temp_x = pairs[0]
            temp_y = pairs[1]
                    
        result_list.append([temp_x, temp_y])

    return result_list                             
#LR#
def type1(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path):
    img_size_list = []

   
   
    for js, im in zip(json_list, image_list):
        print(js)
        #js=js.encoding="utf-8"
        #line=open(js)
        #line.decode(encoding, errors='ignore')
        #data_json = json.load(line)
        data_json = json.load(open(js))
        
        #height = data_json['clipH']
        #width = data_json['clipW']
        imgdepth=0

        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        img_raw = img_raw.transpose(Image.FLIP_LEFT_RIGHT)
        heigth = img_raw.size[1]
        width = img_raw.size[0]
        #print(heigth, width, img_raw.size)
        #imgdepth=getDepth(json_list)
        for ang in rotation_angle:
            for sc in zoom_rate:
                img_out = ScaleRotateTranslate(img_raw, ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                img_out = img_out.convert('RGB')
                img_out_with_label = img_out.copy()
                img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
                data_json_output = {'polygons':[],'params':{'params':{}},'depth':0}
                for temp in data_json['polygons']:
                    #transformed_coordinates = Points_coordinate_transformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(sc,sc))
                    transformed_coordinates=Points_coordinate_LeftRight(temp['points'], ang,img_raw.size[0],img_raw.size[1])
                    d = ImageDraw.Draw(img_mask)
                    #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                    #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                    #d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                    #temp_out['points'] = transformed_coordinates
                    data_json_output['polygons'].append({'points':transformed_coordinates,'type':temp['type']})#'depth':data_json['depth'])
                    data_json_output['params']=data_json['params']
                    #data_json_output['depth']=data_json['depth']
                   # data_json_output['params'].append({data_json['params']})
                    #data_json_output.update({data_json['params']})
                    d1 = ImageDraw.Draw(img_out_with_label)
                    d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')

                #data_json_output['depth']=data_json['depth']
                save_name_common_part = ("-m")
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')



                img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
                img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
                #img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')


                f2 = open(output_image_path+read_name + save_name_common_part+'.json', 'w')
                json.dump(data_json_output, f2)

def typeUniformSize(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path,inputdepth,errorpath):#2
    img_size_list = []

    for js, im in zip(json_list, image_list):
        #line=open(js)
        #line.decode("gbk","ignore")
        #data_json = json.load(line) 
        data_json = json.load(open(js))

        #height = data_json['clipH']
        #width = data_json['clipW']
        imgdepth=0
        
        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        #img_raw = img_raw.transpose(Image.FLIP_LEFT_RIGHT)
        #heigth = img_raw.size[1]
        #width = img_raw.size[0]
        #print(heigth, width, img_raw.size)
        imgdepth=getDepth(json_list)
        if imgdepth==0:
           try:
                os.makedirs(errorpath)
           except:
                pass
                        
           shutil.move(js, errorpath)
                       
           shutil.move(im, errorpath)
           continue
                       
        print("the img depth is ",imgdepth)           
        for ang in rotation_angle:
            #for sc in inputdepth:
            
            img_outscale = ScaleRotateTranslate(img_raw, ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(inputdepth,imgdepth))
            img_outscale = img_outscale.convert('RGB')
            img_out_with_label = img_outscale.copy()
            img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
            data_json_outputscale = {'polygons':[],'params':{'params':{}},'depth':0}
            for temp in data_json['polygons']:
                transformed_coordinatesscale = Points_coordinate_scaletransformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2),  scale=(inputdepth,imgdepth))
                #transformed_coordinates=Points_coordinate_LeftRight(temp['points'], ang,img_raw.size[0],img_raw.size[1])
                d = ImageDraw.Draw(img_mask)
                #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                #####d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                #temp_out['points'] = transformed_coordinates
                data_json_outputscale['polygons'].append({'points':transformed_coordinatesscale,'type':temp['type']})#'depth':data_json['depth'])
                data_json_outputscale['params']=data_json['params']
                data_json_outputscale['depth']=data_json['depth']

                #d1 = ImageDraw.Draw(img_out_with_label)
                #d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')

            img_out,imgLeftoffset,imgHeightoffset,below33 = imgUniformSizeTranslate2(img_outscale,imgdepth,inputdepth)
            img_out = img_out.convert('RGB')
            img_out_with_label = img_out.copy()
            img_mask = Image.new('RGB', img_outscale.size, (0, 0, 0))
            data_json_output = {'polygons':[],'params':{'params':{}},'depth':0}
            for temp in data_json_outputscale['polygons']:
                transformed_coordinates = Points_coordinate_uniformSize(data_json_outputscale,temp['points'],imgLeftoffset,imgHeightoffset,imgdepth,inputdepth)
                #transformed_coordinates=Points_coordinate_LeftRight(temp['points'], ang,img_raw.size[0],img_raw.size[1])
                d = ImageDraw.Draw(img_mask)
                #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                #####d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                #temp_out['points'] = transformed_coordinates
                data_json_output['polygons'].append({'points':transformed_coordinates,'type':temp['type']})#'depth':data_json['depth'])
                data_json_output['params']=data_json_outputscale['params']
                data_json_output['depth']=data_json_outputscale['depth']

                d1 = ImageDraw.Draw(img_out_with_label)
                d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')

            data_json_output['depth']=data_json_outputscale['depth']
            save_name_common_part = ("-d"+str(int(inputdepth*10)))
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')



            img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
            img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
            #img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')


            f2 = open(output_image_path+read_name + save_name_common_part+'.json', 'w')
            json.dump(data_json_output, f2)
    #return imgdepth                   



              
def type3(rotation_angle, zoom_rate, json_list,image_list, output_image_path, output_mask_path, output_image_with_mask_path, output_json_path):## rotate the pic\

    img_size_list = []

    for js, im in zip(json_list, image_list):
        data_json = json.load(open(js))

       # height = data_json['imageHeight']
       # width = data_json['imageWidth']

        read_name = js.split('/')[-1].split('.')[0]

        img_raw = Image.open(im)
        #heigth = img_raw.size[1]
        #width = img_raw.size[0]
        #print(heigth, width, img_raw.size)
        #for ang in rotation_angle:
        ang=rotation_angle
        print(ang)
        for sc in zoom_rate:
                img_out = ScaleRotateTranslate(img_raw, ang, center = None,  scale=(sc,sc))
                img_out = img_out.convert('RGB')
                img_out_with_label = img_out.copy()
                img_mask = Image.new('RGB', img_raw.size, (0, 0, 0))
                data_json_output = {'polygons':[]}
                for temp in data_json['polygons']:
                    transformed_coordinates = Points_coordinate_transformer(temp['points'], ang, center = (img_raw.size[0]/2,img_raw.size[1]/2), scale=(sc,sc))
                    d = ImageDraw.Draw(img_mask)
                    #d.point(list(map(tuple, transformed_coordinates)), fill='white')
                    #d.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='black')
                    #d.polygon(list(map(tuple, transformed_coordinates)), fill='white')
                    #temp_out['points'] = transformed_coordinates
                    #data_json_output['polygons'].append({'label':temp['label'], 'points':transformed_coordinates})
                    data_json_output['polygons'].append({'points':transformed_coordinates,'type':temp['type']})#'depth':data_json['depth'])
                    data_json_output['params']=data_json['params']
                    
                    d1 = ImageDraw.Draw(img_out_with_label)
                    d1.line(list(map(tuple, transformed_coordinates + [transformed_coordinates[0]])), fill='white')

                data_json_output['depth']=data_json['depth']

                if ang==0 or ang==-5 :
                    ang1=abs( ang )
                    save_name_common_part = ('-r10'+str(ang1))
                if ang==-10 or ang==-15 or ang==-20:
                    ang1=abs( ang )
                    save_name_common_part = ('-r1'+str(ang1)) 
                if  ang==5 :
                    ang1=abs( ang )
                    save_name_common_part = ('-r00'+str(ang1))
                if ang==10 or ang==15 or ang==20:
                    ang1=abs( ang )
                    save_name_common_part = ('-r0'+str(ang1))        
                #print(output_image_path+read_name + save_name_common_part+'.jpg')
                #print(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')
                #print(save_path+read_name + save_name_common_part+'.json')



                img_out.save(output_image_path+read_name + save_name_common_part+'.jpg')
                img_out_with_label.save(output_image_with_mask_path+read_name +'_WITHMASK' + save_name_common_part+'.jpg')
                #img_mask.save(output_mask_path+read_name + '_MASK' + save_name_common_part+'.jpg')


                f2 = open(output_image_path+read_name + save_name_common_part+'.json', 'w')
                json.dump(data_json_output, f2)
def main():# 
    raw_data_root_path = sys.argv[1]
    #raw_data_root_path = "../DATA/data_20200129/"
    #raw_data_root_path = "../DATA/data_before/"
    output_dir = sys.argv[2]
    #output_dir = "./output2/"
    typemode=sys.argv[3]
    #rotation_angle = [0,45,90,135,180,225,270,315]
    #zoom_rate = [0.95, 1.0, 1.05]
    print(typemode)
    rotation_angle = [0]
    zoom_rate = [1.0]
    depthlist= [2.5,3.0,3.5,4,4.5,5]
    print(depthlist)
    countNum=0
   

    
    #current_folder = os.listdir('/'+raw_data_root_path)
    if typemode == "1": #LR To Mirror
        print("here is 1 type")
        for patientdir in os.listdir(raw_data_root_path):
            json_list, image_list = get_images_with_json(raw_data_root_path+'/'+patientdir)
            print(raw_data_root_path+'/'+patientdir)
            output_image_path = output_dir + '/'+patientdir+"-m"+'/'
            print(output_image_path)
            output_mask_path = output_dir + 'output_mask/'
            output_image_with_mask_path = output_dir + 'output_image_with_mask/'
            output_json_path = output_dir + 'output_json/'
            counter = 0
            try:
                os.makedirs(output_image_path)
            except:
                pass
           
            try:
                os.makedirs(output_image_with_mask_path)
            except:
                pass
            
            could_not_transformed = []
            
            total_data_info = []

            for js, im in zip(json_list, image_list):
                if counter % 10 == 0:
                    print('processed %d of %d' % (counter, len(json_list)))

                #try:
                #typeLeftRight(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                    print('ok -> type 1 ----> '+js)
                    try:
                       # print("move :",js)
                       # print("moveim :",im)
                       # print("###########")
                       # print("###########")
                       # print("###########")
                       # print("dst :",raw_data_root_path+'/'+'ERROR'+'/'+patientdir)
                        errorpath=output_dir+'/'+'ERROR'+'/'+patientdir+'/'
                        type1(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                    except :
                        print("move :",js)
                        print("moveimg",im)
                        print("###########")
                        print("###########")
                        print("###########")
                        print("dst :",raw_data_root_path+'/'+'ERROR'+'/'+patientdir)
                        #shutil.move (js, output_dir+'/'+'ERROR'+'/'+patientdir+'/')
                        
                        try:
                            os.makedirs(errorpath)
                        except:
                            pass
                        
                        shutil.copy(js, output_dir+'/'+'ERROR'+'/'+patientdir+'/')
                        os.remove(js)
                        shutil.copy(im, output_dir+'/'+'ERROR'+'/'+patientdir+'/')
                        os.remove(im)
                    else:
                    
                        print('ok -> type 1 -> '+im)
                        total_data_info.append(['type_1', im])
            print(output_dir+'/'+patientdir+'/'+"patient-info.json")            
            if os.path.exists(raw_data_root_path+'/'+patientdir+'/'+"patient-info.json"):
                shutil.copy(raw_data_root_path+'/'+patientdir+'/'+"patient-info.json",output_image_path)             
    elif typemode == "2": #To uniform depth
        print("here is 2 type")
        for redepth in depthlist:
           # redepthpath=output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
            print("kaishi",redepth)
            for patientdir in os.listdir(raw_data_root_path): #raw_data_root_path gw/gw-o;  patientdir patient/patient-m
                json_list, image_list = get_images_with_json(raw_data_root_path+'/'+patientdir)
                print(raw_data_root_path+'/'+patientdir)
                backdirlist = raw_data_root_path.rsplit('/',1)
                backdir=backdirlist[-1]
                output_image_path = output_dir + '/'+backdir+'-d'+str(int(redepth*10))+'/'+patientdir+'-d'+str(int(redepth*10))+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                print(str(float(redepth)))
                print(output_dir)
                print(output_dir)
                output_mask_path = output_dir + 'output_mask/'
                output_image_with_mask_path = output_dir + 'output_image_with_mask/'
                output_json_path = output_dir + 'output_json/'
                counter = 0
                try:
                    os.makedirs(output_image_path)
                except:
                    pass
                
                try:
                    os.makedirs(output_image_with_mask_path)
                except:
                    pass
                
                could_not_transformed = []
                total_data_info = []

                for js, im in zip(json_list, image_list):
                    if counter % 10 == 0:
                        print('processed %d of %d' % (counter, len(json_list)))

                        print('ok -> type 1 ----> '+js)
                        errorpath=output_dir+'/'+'ERROR'+'/'+patientdir+'/'
                        typeUniformSize(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path,float(redepth),errorpath)
                        print('ok -> type 1 -> '+im)
                        total_data_info.append(['type_1', im]) 
                print(output_dir+'/'+patientdir+'/'+"patient-info.json")
                if os.path.exists(raw_data_root_path+'/'+patientdir+'/'+"patient-info.json"):
                    shutil.copy(raw_data_root_path+'/'+patientdir+'/'+"patient-info.json",output_image_path)  
                 

    elif typemode == "3":# 
         print("here is 3 type")
         anglelist = [-20,-15,-10,-5,0,5,10,15,20]
         # findsubdir="patient"
         for reangle in anglelist:
        #for patientdir in os.listdir(raw_data_root_path): #raw_data_root_path gw/gw-o;  patientdir patient/patient-m
            for sub_root_path in os.listdir(raw_data_root_path):
                print("sub_root_path=  ",sub_root_path)#sub_root_path=   patient3018  
                print("+++++++++++++++++")
                
                subdir=raw_data_root_path+'/'+sub_root_path+'/'
                print("subdir is =========",subdir)#test/gw-d/gw-m-d45/patient3020-m-d45
                countNum=countNum+1
                print("countNum is ",countNum)
                json_list, image_list = get_images_with_json(subdir)# patientdir is :     gw-o-d50
                #print("raw_data_root_path+'/'+patientdir:  ",subdir+'/'+subpatientdir) #out:raw_data_root_path+'/'+patientdir:   gw/gw-d/gw-o-d50
                #backdirlist = subdir.rsplit('/',1)
                #backdir=backdirlist[-1]
                ang1=reangle
                ang=abs( ang1 )
                
                if  ang1==-5 :
                
                    #output_image_path = output_dir + '/'+backdir+'-r10'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                    output_image_path = output_dir + '/'+sub_root_path+'-r10'+str(ang)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                    #dir_r='-r10'
                if ang1==-10 or ang1==-15 or ang1==-20:
                    #ang=abs( ang1 )
                    #output_image_path = output_dir + '/'+backdir+'-r1'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                    output_image_path = output_dir + '/'+sub_root_path+'-r1'+str(ang)+'/'
                    #dir_r='-r1'
                if  ang1==0 or ang1==5 :
                    #ang=abs( ang1 )
                    #output_image_path = output_dir + '/'+backdir+'-r00'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                    output_image_path = output_dir + '/'+sub_root_path+'-r00'+str(ang)+'/'
                    #dir_r='-r00'
                if ang1==10 or ang1==15 or ang1==20:
                    #ang=abs( ang1 )
                    #dir_r='-r0'
                    #output_image_path = output_dir + '/'+backdir+'-r0'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/' #output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                    output_image_path = output_dir + '/'+sub_root_path+'-r0'+str(ang)+'/'
                    
                print(output_image_path)
                #if reangle<0:
                #  reangle=abs( reangle )
                # output_image_path = output_dir + '/'+backdir+'-r1'+str(reangle)+'/'+patientdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                #if reangle>=0:
                #  output_image_path = output_dir + '/'+backdir+'-r0'+str(reangle)+'/'+patientdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'   
                print(str(reangle))
                print(output_dir)
                print(output_dir)
                output_mask_path = output_dir + 'output_mask/'
                output_image_with_mask_path = output_dir + 'output_image_with_mask/'
                output_json_path = output_dir + 'output_json/'
                counter = 0
                try:
                    os.makedirs(output_image_path)
                except:
                    pass
                                
                try:
                    os.makedirs(output_image_with_mask_path)
                except:
                    pass
                
                could_not_transformed = []
                total_data_info = []

                for js, im in zip(json_list, image_list):
                    if counter % 10 == 0:
                        print('processed %d of %d' % (counter, len(json_list)))

                        print('ok -> type 1 ----> '+js)
                        #typeUniformSize(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path,float(redepth))
                        type3(reangle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                        print('ok -> type 1 -> '+im)
                        total_data_info.append(['type_1', im])  
                #print(raw_data_root_path+'/'+subpatientdir+'/'+"patient-info.json")
                if os.path.exists(subdir+'/'+"patient-info.json"):
                    shutil.copy(subdir+'/'+"patient-info.json",output_image_path)         
        
    elif typemode == "4":#d-r
        print("here is 4 type")
        anglelist = [-20,-15,-10,-5,0,5,10,15,20]
        
        #findsubdir="patient"
        for reangle in anglelist:
    #for patientdir in os.listdir(raw_data_root_path): #raw_data_root_path gw/gw-o;  patientdir patient/patient-m
            for sub_root_path in os.listdir(raw_data_root_path):
                print("sub_root_path=  ",sub_root_path)#sub_root_path=   gw-m-d45
                print("+++++++++++++++++")
                            
                for subdirf1 in os.listdir(raw_data_root_path+'/'+sub_root_path):
                    countNum=countNum+1
                    print("countNum is ",countNum)

                    print("subdirf1=  ",subdirf1)# out :subdirf1=   patient3020-m-d45
                    print("+++++======++++++++")   
                    subdir=raw_data_root_path+'/'+sub_root_path+'/'+subdirf1
                    print("subdir=raw_data_root_path+'/'+patientdirtuple+'/'+subdirf1 is =========",subdir)#test/gw-d/gw-m-d45/patient3020-m-d45
                       
                    json_list, image_list = get_images_with_json(subdir)# patientdir is :     gw-o-d50
                    #print("raw_data_root_path+'/'+patientdir:  ",subdir+'/'+subpatientdir) #out:raw_data_root_path+'/'+patientdir:   gw/gw-d/gw-o-d50
                    #backdirlist = subdir.rsplit('/',1)
                    #backdir=backdirlist[-1]
                    ang1=reangle
                    ang=abs( ang1 )
                                            
                    if  ang1==-5 :
                    
                        #output_image_path = output_dir + '/'+backdir+'-r10'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                        output_image_path = output_dir + '/'+sub_root_path+'-r10'+str(ang)+'/'+subdirf1+'-r10'+str(ang)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                        #dir_r='-r10'
                    if ang1==-10 or ang1==-15 or ang1==-20:
                        #ang=abs( ang1 )
                        #output_image_path = output_dir + '/'+backdir+'-r1'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                        output_image_path = output_dir + '/'+sub_root_path+'-r1'+str(ang)+'/'+subdirf1+'-r1'+str(ang)+'/'
                        #dir_r='-r1'
                    if  ang1==0 or ang1==5 :
                        #ang=abs( ang1 )
                        #output_image_path = output_dir + '/'+backdir+'-r00'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/'#output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                        output_image_path = output_dir + '/'+sub_root_path+'-r00'+str(ang)+'/'+subdirf1+'-r00'+str(ang)+'/'
                        #dir_r='-r00'
                    if ang1==10 or ang1==15 or ang1==20:
                        #ang=abs( ang1 )
                        #dir_r='-r0'
                        #output_image_path = output_dir + '/'+backdir+'-r0'+str(ang)+'/'+subdir+'-r'+str(reangle)+'/' #output_dir + '/'+patientdir+'-d'+str(float(redepth)*10)+'/'
                        output_image_path = output_dir + '/'+sub_root_path+'-r0'+str(ang)+'/'+subdirf1+'-r0'+str(ang)+'/'
                        
                    print(output_image_path)
                    print(str(reangle))
                    print(output_dir)
                    
                    output_mask_path = output_dir + 'output_mask/'
                    output_image_with_mask_path = output_dir + 'output_image_with_mask/'
                    output_json_path = output_dir + 'output_json/'
                    counter = 0
                    try:
                        os.makedirs(output_image_path)
                    except:
                        pass
                                    
                    try:
                        os.makedirs(output_image_with_mask_path)
                    except:
                        pass
                    
                    could_not_transformed = []
                    total_data_info = []

                    for js, im in zip(json_list, image_list):
                        if counter % 10 == 0:
                            print('processed %d of %d' % (counter, len(json_list)))

                            print('ok -> type 1 ----> '+js)
                            #typeUniformSize(rotation_angle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path,float(redepth))
                            type3(reangle, zoom_rate, [js], [im], output_image_path, output_mask_path, output_image_with_mask_path, output_json_path)
                            print('ok -> type 1 -> '+im)
                            total_data_info.append(['type_1', im])  
                    #print(raw_data_root_path+'/'+subpatientdir+'/'+"patient-info.json")
                    if os.path.exists(subdir+'/'+"patient-info.json"):
               
                       shutil.copy(subdir+'/'+"patient-info.json",output_image_path)  

main()



