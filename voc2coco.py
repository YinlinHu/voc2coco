#!/usr/bin/python

# pip install lxml

import sys
import os
import json
import shutil
import xml.etree.ElementTree as ET


START_BOUNDING_BOX_ID = 1

def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars


def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(filename)[0]
        return int(filename)
    except:
        raise NotImplementedError('Filename %s is supposed to be an integer.'%(filename))

def get_defined_categories(labels_file):
    results = {}
    current_id = 1
    list_fp = open(labels_file, 'r')
    for line in list_fp:
        line = line.strip()
        results[line] = current_id
        current_id += 1
    list_fp.close()
    return results

def convert(jpg_list, labels_file, out_dirname, kitti=False):
    list_fp = open(jpg_list, 'r')
    json_dict = {"images":[], "type": "instances", "annotations": [],
                 "categories": []}
    # categories = get_defined_categories(labels_file)
    categories = {}
    bnd_id = START_BOUNDING_BOX_ID

    for line in list_fp:
        line = line.strip()
        print("Processing %s"%(line))
        # if not os.path.exists(out_dirname):
        #     os.makedirs(out_dirname)
        # shutil.copy2(line, out_dirname + os.sep + os.path.basename(line))

        # xml_f = os.path.join(xml_dir, line)
        xml_f = line.replace('/JPEGImages/', '/Annotations/').replace('.jpg', '.xml').replace('.png', '.xml')
        tree = ET.parse(xml_f)
        root = tree.getroot()
        # path = get(root, 'path')
        # if len(path) == 1:
        #     filename = os.path.basename(path[0].text)
        # elif len(path) == 0:
        #     filename = get_and_check(root, 'filename', 1).text
        # else:
        #     raise NotImplementedError('%d paths found in %s'%(len(path), line))
        #
        filename = os.path.basename(line)
        ## The filename must be a number
        image_id = get_filename_as_int(filename)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        objcnt = 0
        for obj in get(root, 'object'):
            category = get_and_check(obj, 'name', 1).text
            if kitti:
                if category not in ['car', 'Truck', 'Van', 'bus', 'truck']:
                    continue
                category = 'car'
                category_id = 1
            else:
                if category not in categories:
                    continue # only for the desired categories !!!!!!!!!!
                    new_id = len(categories)
                    categories[category] = new_id
                category_id = categories[category]
            
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = float(get_and_check(bndbox, 'xmin', 1).text) - 1
            ymin = float(get_and_check(bndbox, 'ymin', 1).text) - 1
            xmax = float(get_and_check(bndbox, 'xmax', 1).text)
            ymax = float(get_and_check(bndbox, 'ymax', 1).text)
            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            ann = {'area': o_width*o_height, 'iscrowd': 0, 'image_id':
                   image_id, 'bbox':[xmin, ymin, o_width, o_height],
                   'category_id': category_id, 'id': bnd_id, 'ignore': 0,
                   'segmentation': []}
            json_dict['annotations'].append(ann)
            bnd_id = bnd_id + 1
            objcnt += 1
        #
        if objcnt > 0:
            size = get_and_check(root, 'size', 1)
            width = int(get_and_check(size, 'width', 1).text)
            height = int(get_and_check(size, 'height', 1).text)
            image = {'file_name': filename, 'height': height, 'width': width,
                    'id':image_id}
            json_dict['images'].append(image)

    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    json_file = out_dirname + '.json'
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()
    list_fp.close()

if __name__ == '__main__':
    # if len(sys.argv) <= 1:
    #     print('3 auguments are need.')
    #     print('Usage: %s XML_LIST.txt XML_DIR OUTPU_JSON.json'%(sys.argv[0]))
    #     exit(1)
    # convert(sys.argv[1], sys.argv[2], sys.argv[3])
    jpgListFile = "/data/Cityscapes_detection/train_200shots_5.txt"
    labelsFile = "/xx.txt"
    outDirName = "./train_200shots_5"
    convert(jpgListFile, labelsFile, outDirName, kitti=False)
