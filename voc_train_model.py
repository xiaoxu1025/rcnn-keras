from keras.optimizers import SGD
from model import get_model
from keras.layers import Input
import config as cfg
import time
from keras.utils import generic_utils
from voc_data import VocData
import tensorflow as tf
import numpy as np
from keras.callbacks import TensorBoard
import os


# tensorboard
def write_log(callback, names, logs, batch_no):
    for name, value in zip(names, logs):
        summary = tf.Summary()
        summary.value.add(tag=name, simple_value=value)
        callback.writer.add_summary(summary, batch_no)
        callback.writer.flush()


# load config
classes_num = cfg.CLASSES_NUM
im_size = cfg.IM_SIZE

# 得到训练数据生成器
voc_data = VocData('~/segment_data', 2007, 'train', './data/voc_classes.txt')
g_train = voc_data.data_generator_wrapper()


# get model
input_tensor = Input(shape=im_size + (3,))
model = get_model(input_tensor, classes_num)
optimizer = SGD(lr=1e-5)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy')

log_path = './logs'
callback = TensorBoard(os.path.join(log_path, '000'))
callback.set_model(model)

# define hyper parameters
epochs_num = 10
train_step = 0
iter_num = 0
epoch_length = voc_data.sample_nums
best_loss = np.Inf

for epoch_num in range(epochs_num):

    start_time = time.time()
    progbar = generic_utils.Progbar(epoch_length)  # keras progress bar
    print('Epoch {}/{}'.format(epoch_num + 1, epochs_num))
    while True:
        X, Y, _ = next(g_train)
        loss = model.train_on_batch(X, Y)

        write_log(callback, ['Elapsed time', 'loss'],
                  [time.time() - start_time, loss[0]], train_step)

        train_step += 1
        iter_num += 1
        progbar.update(iter_num, [('losses', loss[0])])

        if iter_num == epoch_length:
            if loss < best_loss:
                best_loss = loss
                model.save_weights('./weights/model_weights.h5')
                iter_num = 0
            break
