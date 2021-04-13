import os




#path = '.' + os.sep + '10fold' + os.sep + 'cnn' + os.sep + 'Output0.txt'
path = '.' + os.sep + 'Output7.txt'

list_pre = []
list_lbl = []
flag = 0
with open(path, 'r', encoding='UTF-8') as f:
	for line in f.readlines():
		if flag == 0:
			flag = 1
			continue
		line = line.strip()
		if len(line) > 0 :
			templist = line.split('\t')
			list_pre.append(int(templist[0]))
			list_lbl.append(int(templist[1]))
			
flt_size_1 = 3
header_1 = int(flt_size_1/2)

for i in range(header_1, len(list_pre)-header_1):
	if list_pre[i-1]!=0 and list_pre[i+1]!=0 and (list_pre[i-1]==list_pre[i+1] or list_pre[i] == 0) :
		list_pre[i] = list_pre[i-1]
	

flag_pre = 0
flag_lbl = 0
count = [0,0,0,0,0,0]
start_pre = 0
start_lbl = 0
temp_pre = []
temp_lbl = 0
list_lbl_windowed = []
list_pre_windowed = []

for i in range(len(list_lbl)):
	if flag_lbl==0 and list_lbl[i]!=0:
		flag_lbl = 1
		count[list_lbl[i]-1] += 1
		start_lbl = i
		temp_lbl = list_lbl[i]
	elif flag_lbl==1 and (list_lbl[i]==0 or i==len(list_lbl)-1):
		flag_lbl = 0
		list_lbl_windowed.append([temp_lbl, [start_lbl, i-1]])
	
	if flag_pre==0 and list_pre[i]!=0:
		flag_pre = 1
		start_pre = i
		temp_pre.append(list_pre[i])
	elif flag_pre==1 and list_pre[i]!=0:
		temp_pre.append(list_pre[i])
	elif flag_pre==1 and (list_pre[i]==0 or i==len(list_lbl)-1):
		flag_pre = 0
		list_pre_windowed.append([temp_pre, [start_pre, i-1]])
		temp_pre = []




def get_action(lst):
	window_counter = [0,0,0,0,0,0]
	for item in lst:
		window_counter[item-1] += 1
	big = max(window_counter)
	if window_counter.count(big) == 1:
		return window_counter.index(big)+1
	else:
		big_list = []
		for i in range(len(window_counter)):
			if window_counter[i] == big:
				big_list.append(i+1)
		flag = 0
		count = 0
		max_count = 0
		max_label = 0
		for i in range(len(lst)):
			if flag==0 and big_list.count(lst[i])!=0:
				flag = lst[i]
				count += 1
			elif flag!=0 and lst[i]==flag:
				count += 1
			elif flag!=0 and lst[i]!=flag:
				if count > max_count:
					max_count = count
					max_label = flag
				if big_list.count(lst[i])==0:
					flag = 0
					count = 0
				else:
					flag = lst[i]
					count = 1
		return max_label

def findpos(n):
	for i in range(len(list_lbl_windowed)):
		if n>=list_lbl_windowed[i][1][0] and n<=list_lbl_windowed[i][1][1]:
			return i
		elif n>list_lbl_windowed[i][1][1] and (i==len(list_lbl_windowed)-1 or n<list_lbl_windowed[i+1][1][0]):
			return i+0.5
		elif n<list_lbl_windowed[i][1][0] and (i==0 or n>list_lbl_windowed[i-1][1][1]):
			return i-0.5

def isint(x):
	if x-int(x)==0:
		return True
	else:
		return False

def findcross(x):
	rtn = []
	for i in range(len(judge_list)):
		if judge_list[i][1] <= x and judge_list[i][2] >= x:
			rtn.append(i)
	return rtn




judge_list = []
for i in range(len(list_pre_windowed)):
	if len(list_pre_windowed[i][0])<4:
		continue
	action = get_action(list_pre_windowed[i][0])
	start = findpos(list_pre_windowed[i][1][0])
	end = findpos(list_pre_windowed[i][1][1])
	judge_list.append([action, start, end])


err = 0
rcl = 0
registered = -1
last_registered = -1
last_passed = True

for i in range(len(list_lbl_windowed)):
	temp = findcross(i)
	
	if len(temp) == 0:											#预测队列中没有有效的匹配，说明本动作被完全跳过了，ERR+1
		err += 1
		print("Err+1, {}, Motion was skipped.".format(list_lbl_windowed[i]))
	else:															#预测队列中有有效的匹配
		if temp[0] - registered > 1:									#跳过了预测队列中的某些序列，RCL+n，注册新起点位置
			rcl += temp[0]-registered-1
			print("Rcl+{}, {}, Prediction was skipped.".format(temp[0]-registered-1, list_lbl_windowed[i]))
			last_registered = registered
			registered = temp[0]-1
		temp_start = 0
		use = -1
		if last_passed == True:
			use = registered
		else:
			use = last_registered
		for j in range(len(temp)):
			if temp[j] <= use:
				temp_start += 1
		if len(temp[temp_start:]) == 0:
			err += 1
			print("Err+1, {}, Motion was skipped.".format(list_lbl_windowed[i]))
		else:
			flag = 0
			for item in temp[temp_start:]:									#从上一次注册位置开始检查
				if judge_list[item][0] == list_lbl_windowed[i][0]:				#成功匹配，注册新起点位置，设置flag
					flag = 1
					last_registered = registered
					registered = item
					last_passed = True
					if len(temp) != 1:
						rcl += len(temp) - 1
						print("Rcl+{}, {}, Prediction Success, but there are multiple predictions.".format(len(temp) - 1, list_lbl_windowed[i]))
					break
			if flag == 0:														#没有任何一个成功匹配，ERR+1，设置falg
				err += 1
				print("Err+1, {}, all corresponding predictions are wrong.".format(list_lbl_windowed[i]))
				
				registered = temp[-1]
				last_passed = False
				
print("ERR = {} in total of {} Motions.".format(err, len(list_lbl_windowed)))		
print("Accuracy = {}%".format((1-(1.0*err)/len(list_lbl_windowed))*100))
print("RCL = {}.".format(rcl))












