
#-*- coding: utf-8 -*-
import math
import os
import tensorflow as tf
import numpy as np
import cPickle
import skimage
import pprint
import tensorflow.python.platform
from keras.preprocessing import sequence
from data_loader import *
import vgg19
import question_generator

flags = tf.app.flags
pp = pprint.PrettyPrinter().pprint

tf.app.flags.DEFINE_string('input_img_h5', './data_img.h5', 'path to the h5file containing the image feature')
tf.app.flags.DEFINE_string('input_ques_h5', './data_prepro.h5', 'path to the h5file containing the preprocessed dataset')
tf.app.flags.DEFINE_string('input_json', './data_prepro.json', 'path to the json file containing additional info and vocab')
tf.app.flags.DEFINE_string('model_path', './models/', 'where should we save')
tf.app.flags.DEFINE_string('vgg_path', './vgg16.tfmodel', 'momentum for adam')
tf.app.flags.DEFINE_string('gpu_fraction', '2/3', 'define the gpu fraction used')
tf.app.flags.DEFINE_string('test_image_path', './assets/demo.jpg', 'the image you want to generate question')
tf.app.flags.DEFINE_string('test_model_path', './temp/model-7', 'model we saved')

tf.app.flags.DEFINE_integer('batch_size', 256, 'tch_size for each iterations') # 256
tf.app.flags.DEFINE_integer('dim_embed', 512, 'word embedding size')
tf.app.flags.DEFINE_integer('dim_hidden', 512, 'hidden size')
tf.app.flags.DEFINE_integer('dim_image', 4096, 'dimension of output from fc7')
tf.app.flags.DEFINE_integer('img_norm', 1, 'do normalization on image or not')
tf.app.flags.DEFINE_integer('maxlen', 26, 'max length of question')
tf.app.flags.DEFINE_integer('n_epochs', 250, 'how many epochs are we going to train') # 250
tf.app.flags.DEFINE_float('learning_rate', '0.001', 'learning rate for adam')
tf.app.flags.DEFINE_float('momentum', 0.9, 'momentum for adam')
tf.app.flags.DEFINE_boolean('is_train', 'False', 'momentum for adam')

conf = flags.FLAGS

api_request_image = ''

def calc_gpu_fraction(fraction_string):
  idx, num = fraction_string.split('/')
  idx, num = float(idx), float(num)

  fraction = 1 / (num - idx + 1)
  print " [*] GPU : %.4f" % fraction
  return fraction

def main(api_request_image):

    # attrs = conf.__dict__['__flags']
    # pp(attrs)

    dataset, img_feature, train_data = get_data(conf.input_json, conf.input_img_h5, conf.input_ques_h5, conf.img_norm)

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=calc_gpu_fraction(conf.gpu_fraction))

    with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        model = question_generator.Question_Generator(sess, conf, dataset, img_feature, train_data)

        
        model.build_generator()
        print (api_request_image)
        return model.test(test_image_path=api_request_image, model_path=conf.test_model_path, maxlen=26)

import flask
from flask import jsonify, request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

dataset, img_feature, train_data = get_data(conf.input_json, conf.input_img_h5, conf.input_ques_h5, conf.img_norm)

@app.route('/', methods=['POST'])
def home():
    image_path_array = request.json['image_path_array']

    image_paths = [each_path[1:-1].replace('////','/') for each_path in image_path_array[1:-1].split(', ')]
    questions=[]

    
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=calc_gpu_fraction(conf.gpu_fraction))
    with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        model = question_generator.Question_Generator(sess, conf, dataset, img_feature, train_data)
        model.build_generator()
        
        for image_path in image_paths:
            question = model.test(test_image_path=image_path, model_path=conf.test_model_path, maxlen=26)
            questions.append(question)

    

    return jsonify({'result': questions}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=90)


