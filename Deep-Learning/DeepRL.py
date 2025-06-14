import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torchvision.transforms as transform
from torch.autograd import Variable
import torch.nn.functional as F
from tqdm import tqdm
from sklearn import preprocessing
import os.path
import pickle
import math
import matplotlib.pyplot as plt
from sys import stdin, stdout
import io
from time import time

torch.set_printoptions(threshold=10000)
np.set_printoptions(threshold=np.inf)

# torch.set_default_tensor_type('torch.cuda.FloatTensor')

# batch_size = 5
input_dim = 15
hidden_dim = 26
num_layers = 2
output_dim = 100

learning_rate = 0.00001

seq_dim = 1 
PATH = './model2/'

no_of_hosts = 100
no_of_vms = 100


class DeepRL(nn.Module):
	def __init__(self, input_dim, hidden_dim, num_layers, output_dim, batch_size):
		super(DeepRL, self).__init__()

		file_path = PATH + 'running_model.pth'

		if not(os.path.isdir(PATH)):
			# print("here")
			os.mkdir(PATH)
		self.input_dim = input_dim
		self.hidden_dim = hidden_dim
		self.num_layers = num_layers
		self.batch_size = batch_size
		self.output_dim = output_dim
		self.hidden = []
		self.iter = 1
		self.loss_backprop = []
		self.loss_map = []
		self.output = []
		# self.scheduler = lr_scheduler.CosineAnnealingLR(optimizer, 5*24*12, eta_min=learning_rate)

		for i in range(no_of_hosts):
			self.hidden += [self.init_hidden()]

		self.relu = nn.ELU()

		self.fc1 = nn.Linear(24200, 5000)
		self.fc2 = nn.Linear(5000, 2500)
		self.fc3 = nn.Linear(2500, 2500)
		self.fc4 = nn.Linear(2500, 2500)
		self.fc5 = nn.Linear(2500, 2500)
		self.fc6 = nn.Linear(2500, 10000)

		if os.path.isfile(file_path):
			self.load_state_dict(torch.load(file_path))
			
			file = open(PATH + 'hidden_state.pickle','rb')
			self.hidden = pickle.load(file)

			file = open(PATH + 'loss_backprop.pickle','rb')
			self.loss_backprop = pickle.load(file)

			file = open(PATH + 'loss_map.pickle','rb')
			self.loss_map = pickle.load(file)

	def init_hidden(self):
		return (torch.zeros(self.num_layers,self.batch_size, self.hidden_dim),
				torch.zeros(self.num_layers,self.batch_size, self.hidden_dim))

	def forward(self, cnn_data, lstm_data):
		start = time()
		cnn_data = cnn_data.reshape(-1,cnn_data.shape[1]*cnn_data.shape[2])
		lstm_data = lstm_data.reshape(-1,lstm_data.shape[1]*lstm_data.shape[2])
		data = torch.cat((cnn_data, lstm_data),1)

		data = self.relu(self.fc1(data))
		data = self.relu(self.fc2(data))
		data = self.relu(self.fc3(data))
		data = self.relu(self.fc4(data))
		data = self.relu(self.fc5(data))
		data = self.relu(self.fc6(data))

		data = data.reshape(-1,self.output_dim,self.output_dim)
		data = F.softmax(data, dim=2)
		# print('Time = '+str(time()-start))
		return data

	def setInput(self, cnn_data, lstm_data):
		# for name, param in self.named_parameters():
		#     if param.requires_grad:
		#         print(name, param.data)
		self.vm_map = []
		# print(cnn_data.shape)
		for i in range(cnn_data.shape[1]):
			for j in range(cnn_data.shape[2]):
				if cnn_data[0][i][j] == 1:
					self.vm_map += [j]
					break
		# print(self.vm_map)

		train_cnn  = Variable(torch.from_numpy(cnn_data).type(torch.FloatTensor))
		train_lstm = Variable(torch.from_numpy(lstm_data).type(torch.FloatTensor))

		train_cnn
		train_lstm
		# print(train_lstm.shape)
		out = self.forward(train_cnn, train_lstm)
		out = out.reshape(out.shape[1],out.shape[2])
		# self.output = self.output.view(self.output.shape[1],self.output.shape[2])
		self.output += [out]

		for out in self.output:
			file = open(PATH+"DLoutput.txt", "w+")
			file.write(str(out))
			file.close()

			plt.imshow(out.detach().numpy(),cmap='gnuplot')
			ax = plt.gca();
			ax.set_xticks(np.arange(-0.5, 100, 1), minor=True);
			ax.set_yticks(np.arange(-0.5, 100, 1), minor=True);
			ax.grid(which='minor', color='w', linestyle='-', linewidth=0.1)
			plt.savefig(PATH + 'DLoutput.pdf', bbox_inches='tight')
			plt.close()
		# file = open(PATH + 'output.pickle','wb')
		# pickle.dump(self.output, file)
		# print(self.output)


	def backprop(self, data_input):
		# if self.iter == 1:
		# 	return("Init Loss")
		total_loss = 0
		index = 0
		for data in data_input:
			# vmMap = np.zeros((100,100), dtype=int)
			# print(vmMap.shape)

			# file = open('output.pickle','rb')
			# self.output = pickle.load(file)
			file = open(PATH+"BackpropLoss.txt", "a")
			file.write(str(data)+ "\n")
			file.close()

			loss_value = 5000*data[6] + data[8]/10000 + data[9]/100
			loss_value = torch.Tensor(np.array(loss_value)).type(torch.FloatTensor)

			loss = loss_value.clone().detach().requires_grad_(True)

			# plt.imshow(vmMap,cmap='gray')
			# plt.savefig(PATH + 'sendMap.jpg')
			# plt.close()

			# file = open(PATH+"sendMap.txt", "w+")
			# file.write(str(vmMap))
			# file.close()
			index += 1
			loss = loss / len(data)
			total_loss += loss
		
		total_loss /= len(data_input)
		# print(loss)
		# total_loss
		total_loss.backward()
		
		# loss_value = loss_parameters[3]/1000000 + loss_parameters[7] + loss_parameters[8]
		# loss_value = torch.Tensor(np.array(loss_value)).type(torch.FloatTensor)

		# file = open('output.pickle','rb')
		# self.output = pickle.load(file)

		# loss = self.output.min()
		# loss.data = loss_value

		#update parameters
		optimizer.step()

		# self.output = []

		if self.iter%6 == 0: 
			torch.save(model.state_dict(), PATH + 'running_model.pth')
			
			file = open(PATH + 'hidden_state.pickle','wb')
			pickle.dump(self.hidden, file)

			file = open(PATH + 'loss_backprop.pickle','wb')
			pickle.dump(self.loss_backprop, file)

			file = open(PATH + 'loss_map.pickle','wb')
			pickle.dump(self.loss_map, file)

			# globalFile.writeline(str(len(self.loss_map)))
			# globalFile.flush()
			plt.plot(self.loss_backprop)
			plt.savefig(PATH + 'loss_backprop.jpg')
			plt.clf()

			plt.plot(self.loss_map)
			plt.savefig(PATH + 'loss_map.jpg')
			plt.clf()


		self.iter += 1
		
		self.loss_backprop += [total_loss.item()]
		return str(total_loss.item())

	def host_rank(self, vm):
		# print(self.output.shape)	

		# file = open('output.pickle','rb')
		# self.output = pickle.load(file)

		host_list_tensor = self.output[-1].data[vm]
		host_list= host_list_tensor.numpy()
		# print(host_list)
		indices = np.flip(np.argsort(host_list))
		# print(indices)
		s = ''
		for index in indices:
			s += str(index) + ' '
		return s.rstrip()

	def migratableVMs(self):
		# file = open('output.pickle','rb')
		# self.output = pickle.load(file)

		# file = open('vm_map.pickle','rb')
		# self.vm_map = pickle.load(file)

		# print(self.output[0].data)
		output_index = np.argmax(self.output[-1].data, axis=1)
		# print(output_index)
		
		migratableIndex = []
		for i in range(len(self.vm_map)):
			if self.vm_map[i] != output_index[i].item():
				migratableIndex += [i]
		# print(migratableIndex)
		s = ''
		for index in migratableIndex:
			s += str(index) + ' '
		return s.rstrip()

	def sendMap(self, data_input):

		total_loss = 0
		index = 0
		for data in data_input:
			vmMap = np.zeros((100,100), dtype=int)
			# print(vmMap.shape)

			# file = open('output.pickle','rb')
			# self.output = pickle.load(file)

			loss = 0
			for i in range(len(data)):
				# l = data[i].split()
				y = data[i][1]
				vmMap[i][y] = 1
				# print(self.output[i][y])
				loss -= torch.log(self.output[index][i][y])

			plt.imshow(vmMap,cmap='gray')
			plt.savefig(PATH + 'sendMap.jpg')
			plt.close()

			file = open(PATH+"sendMap.txt", "w+")
			file.write(str(vmMap))
			file.close()
			index += 1
			loss /= len(data)
			total_loss += loss
		
		total_loss /= len(data_input)
		# print(loss)
		total_loss
		total_loss.backward()

		#update parameters
		optimizer.step()

		# self.output = []

		if self.iter%6 == 0: 
			torch.save(model.state_dict(), PATH + 'running_model.pth')
			
			file = open(PATH + 'hidden_state.pickle','wb')
			pickle.dump(self.hidden, file)

			file = open(PATH + 'loss_backprop.pickle','wb')
			pickle.dump(self.loss_backprop, file)

			file = open(PATH + 'loss_map.pickle','wb')
			pickle.dump(self.loss_map, file)

			# globalFile.writeline(str(len(self.loss_map)))
			# globalFile.flush()
			plt.plot(self.loss_backprop)
			plt.savefig(PATH + 'loss_backprop.jpg')
			plt.clf()

			plt.plot(self.loss_map)
			plt.savefig(PATH + 'loss_map.jpg')
			plt.clf()


		self.iter += 1
		
		self.loss_map += [total_loss.item()]
		return str(total_loss.item())


def preprocess(data, mean_old, std_old, flag):
	alpha = 0.5
	beta = 0.5
	for i in range(data.shape[2]):
		l = data[:,:,i]
		mean_new = np.mean(l)
		std_new = np.std(l)
		if flag == 0:
			mean_new = alpha*mean_new + (1-alpha)*mean_old
			std_new = beta*std_new + (1-beta)*std_old
		if std_new!=0:
			data[:,:,i] = (data[:,:,i] - mean_new) / std_new
		else:
			data[:,:,i] = 0
	return (data, mean_new, std_new)

def normalize(data, min_max):
	for i in range(data.shape[2]):
		if min_max[i][1] == min_max[i][0]:
			data[:,:,i] = 0
		else:
			data[:,:,i] = (data[:,:,i] - min_max[i][0]) / (min_max[i][1] - min_max[i][0])
	return data

def normalize_loss(data, min_max):
	# print(data)
	for i in range(10):
		if min_max[i][1] == min_max[i][0]:
			data[:,i] = 0
		else:
			data[:,i] = (data[:,i] - min_max[i][0]) / (min_max[i][1] - min_max[i][0])
	
	data[data == float('inf')] = 1
	data[data < 0] = 0
	return data


if __name__ == '__main__':
	global optimizer

	file = open('../Deep-Learning/cnn_min_max.pickle','rb')
	cnn_min_max = pickle.load(file)

	file = open('../Deep-Learning/lstm_min_max.pickle','rb')
	lstm_min_max = pickle.load(file)

	file = open('../Deep-Learning/loss_min_max.pickle','rb')
	loss_min_max = pickle.load(file)


	batch_size = 1
	model = DeepRL(input_dim, hidden_dim, num_layers, output_dim, batch_size)
	model
	# inp = "backprop,CurrentTime 300.1;LastTime 0.0;TimeDiff 300.1;TotalEnergy 105358.10624075294;NumVsEnded 1.0;AverageResponseTime 0.0;AverageMigrationTime 0.0;TotalCost 0.3317772222222221;SLAOverall NaN"
	# inp = "setInput,CNN data;1 2 3;4 5 6;LSTM data;7 8 9;1 2 3"
	# inp = "host_rank,4"
	inp = "sendMap,1 0;2 0;3 1;4 2;5 2;6 3"
	# inp = 'migratableVMs,'
	inp = []
	globalFile = open(PATH+"logs.txt", "a")

	batch_count_forward = 0
	batch_count_backward = 0
	cnn_input = []
	lstm_input = []
	loss_input = []
	hostVm_input = []
	mean = 0
	std = 0
	data_flag = 0
	output_flag = 0

	optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)	

	# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	# print(device)

	while(True):
		while(True):
			line = stdin.readline()
			if "END" in line:
				break
			inp.append(line)
		if inp[0] == 'exit':
			break
		funcName = inp[0]
		data = inp[1:]
		inp = []
		# print(funcName, data[0])

		if 'setInput' in funcName:
			file = open(PATH+"DLinput.txt", "w+")
			file.writelines(data)
			file.close()
			flag = 0
			cnn_data = np.zeros((100, 126), dtype=float)
			lstm_data = np.zeros((100, 116), dtype=float)
			cnn_count = 0
			lstm_count = 0
			for val in data:
				val = val.replace('false','0')
				val = val.replace('true','1')
				val = val.replace('NaN','0')
				x = val.split(' ')
				if x[0] == 'CNN':
					flag = 1
					continue
				
				elif x[0] == "LSTM":
					flag = 2
					continue

				if flag == 1:
					for i in range(len(x)):
						cnn_data[cnn_count][i] = float(x[i])
					cnn_count += 1

				elif flag == 2:
					for i in range(len(x)):
						lstm_data[lstm_count][i] = float(x[i])
					lstm_count += 1

			# cnn_data = preprocessing.normalize(cnn_data)
			# lstm_data = preprocessing.normalize(lstm_data)
			
			# cnn_input += [cnn_data]
			# lstm_input += [lstm_data]
			# batch_count_forward += 1

			# if batch_count_forward == batch_size:
			cnn_data = np.array(cnn_data).reshape(1,cnn_data.shape[0],cnn_data.shape[1])
			lstm_data = np.array(lstm_data).reshape(1,lstm_data.shape[0],lstm_data.shape[1])

			# print(cnn_data)

			# cnn_data, mean, std = preprocess(cnn_data,mean,std,data_flag)
			# lstm_data, mean, std = preprocess(lstm_data,mean,std,data_flag)
			# data_flag = 1

			cnn_data = normalize(cnn_data, cnn_min_max)
			lstm_data = normalize(lstm_data, lstm_min_max)

			# print(cnn_data.shape, lstm_data.shape)
			model.setInput(cnn_data, lstm_data)
			# cnn_input = []
			# lstm_input = []
			# batch_count_forward = 0

		elif 'backprop' in funcName:
			file = open(PATH+"DLbackprop.txt", "w+")
			file.writelines(data)
			file.close()
			if model.iter == 1:
				stdout.write("Init Loss\n")
				stdout.flush()
				model.iter += 1
				continue
			loss_data = []
			for val in data:
				val = val.replace('false','0')
				val = val.replace('true','1')
				val = val.replace('NaN','0')
				# print(val)
				val = val.split()
				loss_data += [float(val[1])]

			loss_input += [loss_data]
			batch_count_backward += 1

			if batch_count_backward == batch_size:
				loss_data = np.array(loss_input)
				loss_data = normalize_loss(loss_data, loss_min_max)
				# print(loss_data)
				ans = model.backprop(loss_data)
				stdout.write(ans+"\n")
				stdout.flush()
				loss_input = []
				batch_count_backward = 0
				# if output_flag == 1:
				model.output = []

			else:
				stdout.write(str(0.1)+"\n")
				stdout.flush()

			# stdout.write(model.backprop(loss_data))
			# stdout.flush()

		elif 'getSortedHost' in funcName:
			vm = int(data[0])
			stdout.write(model.host_rank(vm) + '\n')
			stdout.flush()

			# if output_flag == 1:
			# 	model.output = []
			# 	output_flag = 0

		elif 'getVmsToMigrate' in funcName:
			stdout.write(model.migratableVMs() + '\n')
			stdout.flush()

		elif 'sendMap' in funcName:
			if model.iter == 1:
				stdout.write("Init Loss\n")
				stdout.flush()
				model.iter += 1
				continue


			file = open(PATH+"DLsendMap.txt", "w+")
			file.writelines(data)
			file.close()

			hostVmMap = []
			for val in data:
				val = val.split()
				l = [int(val[0]), int(val[1])]
				hostVmMap += [l]

			hostVm_input += [hostVmMap]
			
			batch_count_backward += 1
			# print(hostVmMap)
			if batch_count_backward == batch_size:
				ans = model.sendMap(hostVm_input)
				stdout.write(ans+"\n")
				stdout.flush()
				hostVm_input = []
				batch_count_backward = 0
				model.output = []

			else:
				stdout.write(str(0.1)+"\n")
				stdout.flush()