import os
import xlrd
import math
import vector
import quaternion

def OPMaker(row, v_tG, v_left, v_face):
	v_acc = vector.Vector(row[1:4])
	new_accx = v_acc.dot_product(v_tG)
	new_accy = v_acc.dot_product(v_face)
	new_accz = v_acc.dot_product(v_left)
	v_acc_new = vector.Vector([new_accx,new_accy,new_accz])
	list_acc_new = list(v_acc_new.coordinates)

	rx = row[4] * (1 / target_rate)
	ry = row[5] * (1 / target_rate)
	rz = row[6] * (1 / target_rate)
	cos = math.cos(math.pi * (rx/360))
	sin = math.sin(math.pi * (rx/360))
	qx = quaternion.Quaternion(cos, sin, 0, 0)
	cos = math.cos(math.pi * (ry/360))
	sin = math.sin(math.pi * (ry/360))
	qy = quaternion.Quaternion(cos, 0, sin, 0)
	cos = math.cos(math.pi * (rz/360))
	sin = math.sin(math.pi * (rz/360))
	qz = quaternion.Quaternion(cos, 0, 0, sin)
	qf = (qx*qz*qy).normalize()
	
	deg_half = math.acos(qf.s)
	sin_deg_half = math.sin(deg_half)
	ux = qf.x / sin_deg_half
	uy = qf.y / sin_deg_half
	uz = qf.z / sin_deg_half
	v_axis = vector.Vector([ux, uy, uz])
	new_axisx = v_axis.dot_product(v_tG)
	new_axisy = v_axis.dot_product(v_face)
	new_axisz = v_axis.dot_product(v_left)
	v_axis_new = vector.Vector([new_axisx, new_axisy, new_axisz]).direction()
	list_axis_new = list(v_axis_new.coordinates)
	
	if list_axis_new[0] < 0:
		for m in range(len(list_axis_new)):
			list_axis_new[m] *= -1
		deg_half *= -1

	return list_acc_new + list_axis_new + [deg_half]



sys_sep = os.sep
target_rate = 50

path = '.' + sys_sep + 'DATA'
file_list = os.listdir(path)
file_list.sort()

total_list = []

for file in file_list:
	temp1 = file[:-4].split('_')
	temp2 = temp1[1].split('While')
	time = temp1[0]
	ac_name = temp2[0]
	bg_name = temp2[1]
	
	if ac_name == 'INIT1' and bg_name == 'INIT1':
		workbook = xlrd.open_workbook(path + sys_sep + file)
		sheet = workbook.sheet_by_index(0)
		count = 0
		z_imu = [0, 0, 0]
		for i in range(2, sheet.nrows):
			row = sheet.row_values(i)
			count += 1
			for j in range(3):
				z_imu[j] += row[j+4]
		for i in range(3):
			z_imu[i] /= count
	elif ac_name == 'INIT2' and bg_name == 'INIT2':
		workbook = xlrd.open_workbook(path + sys_sep + file)
		sheet = workbook.sheet_by_index(0)
		pos_count = 0
		neg_count = 0
		for i in range(2, sheet.nrows):
			row = sheet.row_values(i)
			if row[9] == 'off':
				pos_count += 1
			else:
				break
		for i in range(2+pos_count, sheet.nrows):
			row = sheet.row_values(i)
			if row[9] == 'on':
				neg_count += 1
			else:
				break
		count = 0
		v_tG = vector.Vector([0, 0, 0])
		for i in range(2+(int)(0.4*pos_count), 2+(int)(0.6*pos_count)):
			row = sheet.row_values(i)
			count += 1
			v_G = vector.Vector(row[1:4])
			v_tG = v_tG.plus(v_G)
		v_tG = v_tG.scalar_mult(1/count)
		v_tG = v_tG.direction()
		count = 0
		v_tG2 = vector.Vector([0, 0, 0])
		for i in range(2+pos_count+(int)(0.4*neg_count), 2+pos_count+(int)(0.6*neg_count)):
			row = sheet.row_values(i)
			count += 1
			v_G = vector.Vector(row[1:4])
			v_tG2 = v_tG2.plus(v_G)
		v_tG2 = v_tG2.scalar_mult(1/count)
		v_tG2 = v_tG2.direction()
		v_left = v_tG.cross_product(v_tG2)
		v_left = v_left.direction()
		v_face = v_tG.cross_product(v_left)
		v_face = v_face.direction()
	else:
		workbook = xlrd.open_workbook(path + sys_sep + file)
		sheet = workbook.sheet_by_index(0)
		
		label_dict = {'N/A':0, 'HeadShakingLeft':1, 'HeadShakingRight':2, 'HeadNodUp':3, 'HeadNodDown':4, 'HeadYawLeft':5, 'HeadYawRight':6}
		start_time = sheet.row_values(2)[0]
		total_st = start_time
		list_file = []
		list_1s = []	
		for i in range(2, sheet.nrows):
			row = sheet.row_values(i)
			for j in range(4,7):
				row[j] = row[j] - z_imu[j-4]
			output = OPMaker(row, v_tG, v_left, v_face)
			if row[9] == 'off':
				output.append(label_dict['N/A'])
			else:
				output.append(label_dict[ac_name])
			output.append(row[0])
		
			if row[0] - start_time < 1000:
				list_1s.append(output)
			else:
				n = (int)(target_rate - len(list_1s))
				if n > 0:
					for i in range(n):
						max_interval = -1
						max_index = -1
						for i in range(len(list_1s)-1):
							interval = list_1s[i+1][8] - list_1s[i][8]
							if interval > max_interval:
								max_interval = interval
								max_index = i
						temp = [list_1s[max_index][0] + (list_1s[max_index+1][0] - list_1s[max_index][0]) / 2,
								list_1s[max_index][1] + (list_1s[max_index+1][1] - list_1s[max_index][1]) / 2,
								list_1s[max_index][2] + (list_1s[max_index+1][2] - list_1s[max_index][2]) / 2,
								list_1s[max_index][3] + (list_1s[max_index+1][3] - list_1s[max_index][3]) / 2,
								list_1s[max_index][4] + (list_1s[max_index+1][4] - list_1s[max_index][4]) / 2,
								list_1s[max_index][5] + (list_1s[max_index+1][5] - list_1s[max_index][5]) / 2,
								list_1s[max_index][6] + (list_1s[max_index+1][6] - list_1s[max_index][6]) / 2,
								list_1s[max_index][7],
								list_1s[max_index][8] + (list_1s[max_index+1][8] - list_1s[max_index][8]) / 2]
						list_1s.insert(max_index+1, temp)
				for k in range(len(list_1s)):
					list_file.append(list_1s[k][0:8])
				start_time = list_1s[-1][8]
				list_1s = []
				list_1s.append(output)	
		n = (int)((list_1s[-1][8] - list_1s[0][8]) / 20) - len(list_1s)
		total_et = list_1s[-1][8]
		if n > 0:
			for i in range(n):
				max_interval = -1
				max_index = -1
				for i in range(len(list_1s)-1):
					interval = list_1s[i+1][8] - list_1s[i][8]
					if interval > max_interval:
						max_interval = interval
						max_index = i
				temp = [list_1s[max_index][0] + (list_1s[max_index+1][0] - list_1s[max_index][0]) / 2,
						list_1s[max_index][1] + (list_1s[max_index+1][1] - list_1s[max_index][1]) / 2,
						list_1s[max_index][2] + (list_1s[max_index+1][2] - list_1s[max_index][2]) / 2,
						list_1s[max_index][3] + (list_1s[max_index+1][3] - list_1s[max_index][3]) / 2,
						list_1s[max_index][4] + (list_1s[max_index+1][4] - list_1s[max_index][4]) / 2,
						list_1s[max_index][5] + (list_1s[max_index+1][5] - list_1s[max_index][5]) / 2,
						list_1s[max_index][6] + (list_1s[max_index+1][6] - list_1s[max_index][6]) / 2,
						list_1s[max_index][7],
						list_1s[max_index][8] + (list_1s[max_index+1][8] - list_1s[max_index][8]) / 2]
				list_1s.insert(max_index+1, temp)
		for k in range(len(list_1s)):
			list_file.append(list_1s[k][0:8])
		
		print(file + ' new SR: ' + str(len(list_file) / ((total_et - total_st)/1000)))
		
		output_list = list_file
		if ac_name != 'INIT2':
			count = 0
			state = 0
			cutpoint = []
			for i in range(len(output_list)):
				if state == 0 and output_list[i][7] != 0:
					state=1
				if state == 1 and output_list[i][7] == 0:
					state=2
					cutpoint.append(count)
				if state == 2 and output_list[i][7] != 0:
					state=1
					cutpoint.append(count)	
				count += 1
			n = 0
			cutpointer_left = 0
			cutpointer_right = 0
			while 2*n+1 < len(cutpoint):
				cutpointer_right = cutpoint[2*n] + (int)((cutpoint[2*n+1]-cutpoint[2*n])/2)
				temp = output_list[cutpointer_left+1 : cutpointer_right+1]
				total_list.append(['.' + sys_sep + 'Vecs' + sys_sep + file + '_' + str(n) + '.dt' , temp])
				cutpointer_left = cutpointer_right
				n += 1
			temp = output_list[cutpointer_left : len(output_list)]
			total_list.append(['.' + sys_sep + 'Vecs' + sys_sep + file + '_' + str(n) + '.dt' , temp])
		else:
			total_list.append(['.' + sys_sep + 'Seps' + sys_sep + file + '.dt' , output_list])

max_acc = -1
max_deg = -1

for item in total_list:
	for row in item[1]:
		for acc in row[0:3]:
			if abs(acc) > max_acc:
				max_acc = abs(acc)
		if abs(row[6]) > max_deg:
			max_deg = abs(row[6])

for i in range(len(total_list)):
	for j in range(len(total_list[i][1])):
		total_list[i][1][j][0] /= max_acc
		total_list[i][1][j][1] /= max_acc
		total_list[i][1][j][2] /= max_acc
		total_list[i][1][j][6] /= max_deg

for file_item in total_list:
	with open(file_item[0], 'w', encoding='UTF-8') as f:
		for row in file_item[1]:
			outstr = map(str, row)
			f.write(','.join(outstr) + '\n')

with open('Data_Config', 'w', encoding='UTF-8') as f:
	f.write(str(max_acc) + '\n')
	f.write(str(max_deg))




