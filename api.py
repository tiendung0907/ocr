from flask import Flask, render_template, request, jsonify, current_app
import requests
import argparse
from pipeline import Pipeline, init

from PIL import Image, ImageOps
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import numpy as np
import yaml
import time
import os
from io import BytesIO

model, config = init(os.environ['CONFIG'])

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/nic_img", methods=['POST'])
def upload_img():
    fname = request.files['file'].filename
    img_bin = request.files['file'].read()
    img = Image.open(BytesIO(img_bin)).convert('RGB')
#    img.thumbnail((1024, 1024))

    if config['log']:
        localfile = os.path.join(config['log'], fname)
        img.save(localfile)
        print('img: {}'.format(fname))

    img = np.asarray(img)

    r = model.predict(img) 

    return jsonify(r)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000)
