import json
import glob
import argparse
import pandas as pd
import shutil
import os
from sklearn.model_selection import train_test_split

def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)

def merge(root, out):

    json_files = glob.glob('{}/**/*.json'.format(root), recursive=True)
    img_files = glob.glob('{}/**/*.jpg'.format(root), recursive=True)

    img_size = {os.path.basename(img):os.path.getsize(img) for img in img_files}
    
    annos = {}
    for fname in json_files:
        with open(fname) as f:
            try:
                data = json.load(f)
                anno = data['_via_img_metadata']
                anno = {k:v for k, v in anno.items() if len(v['regions']) > 0}
                annos.update(anno)
            except:
                print(fname)
    
    annos = {k:v for k, v in annos.items() if v['filename'] in img_size and v['size'] == img_size[v['filename']]}
    annotated_img = {v['filename']:v['size'] for k, v in annos.items()}
    
    img_files = [img for img in img_files if os.path.basename(img) in annotated_img and os.path.getsize(img) == annotated_img[os.path.basename(img)]]
    
    annos = list(annos.items())
    ## create new train/test json
    train_data, test_data=  train_test_split(annos, test_size=0.1, random_state=2020)
    
    # copy img file
    img_folder = '{}/img'.format(out)
    os.makedirs(img_folder, exist_ok=True)
    for fname in img_files:
        copy(fname, img_folder)
    
    with open('{}/train_annotation.json'.format(out) , 'w') as f:
        data['_via_img_metadata'] = dict(train_data)
        json.dump(data, f)

    with open('{}/test_annotation.json'.format(out), 'w') as f:
        data['_via_img_metadata'] = dict(test_data)
        json.dump(data, f)

    with open('{}/full_annotation.json'.format(out), 'w') as f:
        data['_via_img_metadata'] = dict(annos)
        json.dump(data, f)

    print('json file: {}'.format(len(json_files)))
    print('image file: {}'.format(len(annos)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, help='foo help')
    parser.add_argument('--out', default='.', help='foo help')

    args = parser.parse_args()
    
    merge(args.root, args.out)

if __name__ == '__main__':
    main()
