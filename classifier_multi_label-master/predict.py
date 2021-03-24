# -*- coding: utf-8 -*-
"""
Created on Thu May 30 17:12:37 2019

@author: cm
"""


import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
pwd = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import tensorflow as tf
from networks import NetworkAlbert
from classifier_utils import get_feature_test,id2label
from hyperparameters import Hyperparamters as hp
          

class Model(object,):
    """
    Load NetworkAlbert model
    """
    def __init__(self):
        self.albert, self.sess = self.load_model()
    @staticmethod
    def load_model():
        with tf.Graph().as_default():
            sess = tf.Session()
            with sess.as_default():
                albert =  NetworkAlbert(is_training=False)
                saver = tf.train.Saver()  
                sess.run(tf.global_variables_initializer())
                checkpoint_dir = os.path.abspath(os.path.join(pwd,hp.file_model))
                checkpoint_dir="E:/classifier_multi_label-master/model/model_01"
                print (checkpoint_dir)
                ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
                saver.restore(sess, ckpt.model_checkpoint_path)
        return albert,sess

MODEL = Model()
print('Load model finished!')


def get_label(sentence):
    """
    Prediction of the sentence's label.
    """
    feature = get_feature_test(sentence)
    print(feature)
    fd = {MODEL.albert.input_ids: [feature[0]],
          MODEL.albert.input_masks: [feature[1]],
          MODEL.albert.segment_ids:[feature[2]],
          }
    prediction = MODEL.sess.run(MODEL.albert.predictions, feed_dict=fd)[0]
    print(prediction)
    return [id2label(l) for l in np.where(prediction==1)[0] if l!=0]    
     

if __name__ == '__main__':
    import time
    start = time.time()
    sent = '当然自营快递时效也是相当的高效'
    print(get_label(sent))
    end = time.time()
    print(end-start)#57ms
    

    
    
    
