import yaml
import argparse
import json
import cv2
import os
import time
import torch

from predictor import DL, DC, TextDetector, Cropper
from layouttree.dtree import DocTree

#from translate.translator import Translator

class Pipeline():
    def __init__(self, config):
        device = config['device']
        log = config['log']

        self.classifier = DC(config['resnet'], device, log)

        self.cropper = Cropper(config['crop'], device, log)
        self.detector = DL(config['detectron'], device, log)

        self.doc_tree = DocTree(config, log)
        self.text_detector = TextDetector(config['vietocr'], device, log)
#        self.translator = Translator(config)        

        self.log = config['log']
        if self.log:
            os.makedirs(self.log, exist_ok=True)


    def predict(self, origin):
        areas = self.cropper.crop(origin)

        layouts = []

        for area in areas:
            meta_confidence = {}
            meta_value = {}

            img = area['img']
            side_clazz = area['class']
            side_prob = area['prob']

            card_side = side_clazz.split('_')[1]
            card_type, card_prob = self.classifier.predict(img)
            
            meta_confidence = {
                    'card_type':card_prob,
                    'side': side_prob
                    }
            meta_value = {
                    'card_type':card_type,
                    'side': card_side
                    }
            
            if self.log:
                cv2.imwrite('{}/{}.jpg'.format(self.log, card_side), img)

            start_time = time.time()
            print('classify: {}'.format(time.time() - start_time))

            start_time = time.time()
            rs = self.detector.predict(img)
            print('layout: {}'.format(time.time() - start_time))
            leaves_idx = self.doc_tree.get_leaves(rs)
            
            start_time = time.time()
            for idx in leaves_idx:
                r = rs[idx]
                x, y, w, h = int(r['x']), int(r['y']), int(r['w']), int(r['h'])
                crop_img = img[y:y+h,x:x+w]
                text, prob = self.text_detector.predict(crop_img)
                r['text'] = text
            print('text: {}'.format(time.time() - start_time))

            layout = self.doc_tree.build_layout(rs)
            layout['confidence'].update(meta_confidence)
            layout['value'].update(meta_value)

            layouts.append(layout)

#        layouts = self.translator.translate(layouts)
#        torch.cuda.empty_cache() 

        return layouts

def init(cfg):
    config = yaml.safe_load(open(cfg, 'r'))
    if config['log']:
        os.makedirs(config['log'], exist_ok=True)

    start_time = time.time()
    model =  Pipeline(config)
    print('load {}'.format(time.time() - start_time))

    return model, config

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', required=True, help='config')
    parser.add_argument('--img', required=True, help='img')

    args = parser.parse_args() 
    
    model, config = init(args.config)

    rs = model.predict(args.img)
    print(json.dumps(rs, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

