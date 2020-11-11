from keras.callbacks import TensorBoard
import tensorflow as tf


class CustomTensorBoard(TensorBoard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = tf.summary.create_file_writer(self.log_dir)

    def set_model(self, model):
        pass

    def log(self, step, **stats):
        print(1)