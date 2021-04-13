import os
import random
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential




def load_Data(path, file_list):
	rtn = []
	
	for filename in file_list:
		full_path = path + os.sep + filename
		temp_list = []
		with open(full_path, 'r', encoding='UTF-8') as f:
			for line in f.readlines():
				line = line.strip()
				if len(line) > 0 :
					line = line.split(',')
					line = list(map(eval, line))
					temp_list.append(line)
		rtn.append(temp_list)
		
	return rtn


def make_Window_List(database, epoc, insert_flag, insert_rate, seps):
	EPOC_count = 0
	file_count = 0
	total_data_list = []
	total_label_list = []
	
	for i in range(epoc):
		random.shuffle(database)
		for file_data in database:
			for line in file_data:
				total_data_list.append(line[:-1])
				total_label_list.append(line[-1])
			if insert_flag:
				rd = random.randint(0,99)
				if rd < insert_rate:
					tgt = random.randint(0,len(seps)-1)
					starter = random.randint(0,(int)(len(seps[tgt])/2))
					ender = random.randint((int)(len(seps[tgt])/2), len(seps[tgt])-1)
					for line in (seps[tgt][starter:ender]):
						total_data_list.append(line[:-1])
						total_label_list.append(line[-1])
			file_count += 1
		EPOC_count += 1

	line_count = len(total_data_list)
	left_lenth = (line_count - WINDOW_SIZE) % WINDOW_STEP
	if left_lenth != 0:
		for i in range(WINDOW_STEP - left_lenth):
			total_data_list.append(total_data_list[-1])
			total_label_list.append(total_label_list[-1])
	line_count = len(total_data_list)
	
	data_window_list = []
	label_window_list = []
	window_start = 0
	while window_start+WINDOW_SIZE <= len(total_data_list):
		data_window_list.append(total_data_list[window_start : window_start+WINDOW_SIZE])
		temp_label = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		for i in range(window_start, window_start+WINDOW_SIZE):
			typ = total_label_list[i]
			temp_label[typ] += 1
		for i in range(len(temp_label)):
			temp_label[i] = temp_label[i] / WINDOW_SIZE
		label_window_list.append(temp_label)
		window_start += WINDOW_STEP

	window_count = len(data_window_list)
	X = np.array(data_window_list).reshape(window_count, WINDOW_SIZE, 7, 1)
	Y = np.array(label_window_list).reshape(window_count, 7)
	
	print("\n######################MAKING DATA######################")
	print("Making Data_List: ")
	print("----Total Epoc: {}.".format(EPOC_count))
	print("----Total File: {}.".format(file_count))
	print("----Total Line: {}.".format(line_count))
	print("----Total Window: {}.".format(window_count))
	print("######################MAKING DATA######################\n")

	return X, Y




#加载动作相关数据到内存
vec_path = '.' + os.sep + 'Vecs'
vec_list = os.listdir(vec_path)

test_file_list  = vec_list[(int)(0.7*len(vec_list)) : (int)(0.8*len(vec_list))]
valid_file_list = vec_list[(int)(0.7*len(vec_list)) : (int)(0.8*len(vec_list))]
train_file_list = vec_list[(int)(0.0*len(vec_list)) : (int)(0.7*len(vec_list))] + vec_list[(int)(0.8*len(vec_list)) : (int)(1.0*len(vec_list))]

train_base = load_Data(vec_path, train_file_list)
valid_base = load_Data(vec_path, valid_file_list)
test_base  = load_Data(vec_path, test_file_list)

#加载补间数据到内存
sep_path_train = '.' + os.sep + 'Seps' + os.sep + 'train'
sep_path_test = '.' + os.sep + 'Seps' + os.sep + 'test'
sep_list_train = os.listdir(sep_path_train)
sep_list_test = os.listdir(sep_path_test)
sep_base_train = load_Data(sep_path_train, sep_list_train)
sep_base_test = load_Data(sep_path_test, sep_list_test)

#超参数仓库，输出数据统计和超参数统计
EPOC = 5
WINDOW_SIZE = 60
WINDOW_STEP = 5
TRAIN_INSERT_RATE = 33
TEST_INSERT_RATE = 100

print("\n######################DATA ANALYZE######################")
print("Total Movements: {}.".format(len(vec_list)))
print("----Train Movements: {}.".format(len(train_file_list)))
print("----Test Movements: {}.".format(len(test_file_list)))
print("----Validation Movements: {}.\n".format(len(valid_file_list)))
print("Hyperparameters:")
print("----Epoc: {}.".format(EPOC))
print("----Window Size: {}.".format(WINDOW_SIZE))
print("----Window Step: {}.".format(WINDOW_STEP))
print("######################DATA ANALYZE######################\n")

#定义模型
def create_model():
	model = Sequential()
	model.add(layers.TimeDistributed(layers.Conv1D(64, 3, activation='tanh'), input_shape=(WINDOW_SIZE, 7, 1)))
	model.add(layers.TimeDistributed(layers.Conv1D(128, 3, activation='tanh')))
	model.add(layers.TimeDistributed(layers.Flatten()))
	model.add(layers.LSTM(64))
	model.add(layers.Dropout(0.5))
	model.add(layers.Dense(7, activation='softmax'))
	model.compile(optimizer='adam',
					loss=tf.keras.losses.CosineSimilarity(),
					metrics=['accuracy'])
	return model
	
model = create_model()
model.summary()

#生成固定数据集
test_data_list, test_label_list = make_Window_List(test_base, 1, True, TEST_INSERT_RATE, sep_base_train)
valid_data_list, valid_label_list = make_Window_List(valid_base, 1, True, TEST_INSERT_RATE, sep_base_test)


#单次训练
train_data_list, train_label_list = make_Window_List(train_base, EPOC, True, TRAIN_INSERT_RATE, sep_base_test)
history = model.fit(train_data_list, train_label_list, validation_data=(valid_data_list, valid_label_list), batch_size=128, epochs=5)
test_loss, test_acc = model.evaluate(test_data_list, test_label_list)

rtn_t = model.predict(test_data_list, batch_size=64)
rtn = rtn_t.tolist()

with open('Output7.txt', 'w', encoding='UTF-8') as f:
	f.write(str(test_loss) + '\t' + str(test_acc) + '\n')
	count = 0
	for i in range(len(rtn)):
		big = max(rtn[i])
		id1 = rtn[i].index(big)
		big = max(test_label_list[i])
		id2 = test_label_list[i].tolist().index(big)
		f.write(str(id1) + '\t' + str(id2) + '\n')
		if id1 == id2:
			count += 1
acc = count / len(test_data_list)
print(acc)

# Save tf.keras model in pb format
keras_model_path = '.' + os.sep + 'Models' + os.sep + 'Saved_Model' + os.sep
tf.saved_model.save(model, keras_model_path)