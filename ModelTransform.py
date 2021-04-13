import os
import random
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential


keras_model_path = '.' + os.sep + 'Models' + os.sep + 'fsw_best_model' + os.sep
model = tf.keras.models.load_model(keras_model_path)


run_model = tf.function(lambda x: model(x))
# This is important, let's fix the input size.
concrete_func = run_model.get_concrete_function(
    tf.TensorSpec([1, 60, 7, 1], model.inputs[0].dtype))

# model directory.
MODEL_DIR = '.' + os.sep + 'Models' + os.sep + 'Saved_Model' + os.sep
model.save(MODEL_DIR, save_format="tf", signatures=concrete_func)

converter = tf.lite.TFLiteConverter.from_saved_model(MODEL_DIR)
tflite_model = converter.convert()

if not os.path.exists('./tflite_models'):
    os.mkdir('./tflite_models')

with open('./tflite_models/keras_tflite', 'wb') as f:
    f.write(tflite_model)
	
interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(input_details)
print(output_details)