# -*- coding: utf-8 -*-
"""
Created on Thu May 30 21:42:07 2019

@author: cm
"""

import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
import numpy as np
import tensorflow as tf
from networks import NetworkAlbert
from classifier_utils import get_features,get_features_test
from hyperparameters import Hyperparamters as hp
from utils import select,shuffle_one,time_now_string


pwd = os.path.dirname(os.path.abspath(__file__))
print(pwd)
MODEL = NetworkAlbert(is_training=True)


# Get data features
input_ids,input_masks,segment_ids,label_ids = get_features()
num_train_samples = len(input_ids)
indexs = np.arange(num_train_samples)               
num_batchs = int((num_train_samples - 1) /hp.batch_size) + 1
print('Number of batch:',num_batchs)


# test  data
#test_input_ids,test_input_masks,test_segment_ids,test_label_ids = get_features_test()


# Set up the graph 
saver = tf.train.Saver(max_to_keep=hp.max_to_keep)
sess = tf.Session()
sess.run(tf.global_variables_initializer())



# Load model saved before
MODEL_SAVE_PATH = os.path.join(pwd, hp.file_save_model)
ckpt = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
if ckpt and ckpt.model_checkpoint_path:
     saver.restore(sess, ckpt.model_checkpoint_path)
     print('Restored model!')


with sess.as_default():
    # Tensorboard writer
    writer = tf.summary.FileWriter(hp.logdir, sess.graph)
    for i in range(hp.num_train_epochs):
        print(len(indexs))
        idns=indexs
        indexs=idns[:int(len(idns)*0.7)]
        test_indexs=idns[int(len(idns)*0.7):]
        np.random.shuffle(indexs)

        test_input_id_ = select(input_ids, test_indexs)
        test_input_mask_ = select(input_masks, test_indexs)
        test_segment_id_ = select(segment_ids, test_indexs)
        test_label_id_ = select(label_ids, test_indexs)
        print(num_batchs-1)
        for j in range(num_batchs-1):
            # Get ids selected
            i1 = indexs[j * hp.batch_size:min((j + 1) * hp.batch_size, num_train_samples)]
            
            # Get features
            input_id_ = select(input_ids,i1)
            input_mask_ = select(input_masks,i1)
            segment_id_ = select(segment_ids,i1)
            label_id_ = select(label_ids,i1)
            
            # Feed dict
            fd = {MODEL.input_ids: input_id_,
                  MODEL.input_masks: input_mask_,
                  MODEL.segment_ids:segment_id_,
                  MODEL.label_ids:label_id_}
            
            # Optimizer
            sess.run(MODEL.optimizer, feed_dict = fd)   
            
            # Tensorboard
            if j%hp.summary_step==0:
                summary,glolal_step = sess.run([MODEL.merged,MODEL.global_step], feed_dict = fd)
                writer.add_summary(summary, glolal_step) 
                
            # Save Model
            if j%(num_batchs//hp.num_saved_per_epoch)==0:
                if not os.path.exists(os.path.join(pwd, hp.file_save_model)):
                    os.makedirs(os.path.join(pwd, hp.file_save_model))                 
                saver.save(sess, os.path.join(pwd, hp.file_save_model, 'model'+'_%s_%s.ckpt'%(str(i),str(j))))            
            
            # Log
            if j % hp.print_step == 0:
                fd = {MODEL.input_ids: input_id_,
                      MODEL.input_masks: input_mask_,
                      MODEL.segment_ids:segment_id_,
                      MODEL.label_ids:label_id_}
                test_fd={MODEL.input_ids: test_input_id_,
                      MODEL.input_masks: test_input_mask_,
                      MODEL.segment_ids:test_segment_id_,
                      MODEL.label_ids:test_label_id_}
                loss = sess.run(MODEL.loss,feed_dict = fd)
                train_acc=sess.run(MODEL.accuracy,feed_dict = fd)
                test_acc=sess.run(MODEL.accuracy,feed_dict = test_fd)
                print('Time:%s, Epoch:%s, Batch number:%s/%s, Loss:%s,Train_Accuracy:%s,Test_Accuracy:%s'%(time_now_string(),str(i),str(j),str(num_batchs),str(loss),str(train_acc),str(test_acc)))
    print('Train finished')
    
    
    
    




