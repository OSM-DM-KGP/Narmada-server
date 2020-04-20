import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from pytorch_pretrained_bert import BertTokenizer, BertConfig, BertModel
from pytorch_pretrained_bert import BertAdam, BertForSequenceClassification
from tqdm import tqdm, trange
import pandas as pd
import io
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
import os
import torch.nn.functional as F
import pudb

from types import SimpleNamespace

import sys

try:
	dataset = sys.argv[1]
	if dataset not in ['nepal','italy']:
		dataset='nepal'
except Exception as e:
		dataset='nepal'

with open('DATA_2/INPUT/nepal_dict.p','rb') as handle:
	nepal_dict= pickle.load( handle)

with open('DATA_2/INPUT/italy_dict.p','rb') as handle:
	italy_dict= pickle.load(handle)


nepal_dict ={}

if dataset =='nepal':
	need_file = open('DATA_2/INPUT/nepal_needs.txt', encoding="utf-8")
	offer_file = open('DATA_2/INPUT/nepal_offers.txt', encoding="utf-8")
	all_file =open('DATA_2/INPUT/nepal-all.txt', encoding="utf-8")
else:
	need_file = open('./DATA_2/INPUT/italy_needs.txt', encoding="utf-8")
	offer_file = open('./DATA_2/INPUT/italy_offers.txt', encoding="utf-8")
	all_file =open('./DATA_2/INPUT/italy-all.txt', encoding="utf-8")

while(True):
	line = need_file.readline()
	if not line: break
	line=line.strip().split('<||>')
	nepal_dict[line[0]]=(line[1].lower(), 1)

while(True):
	line = offer_file.readline()
	if not line: break
	line=line.strip().split('<||>')
	nepal_dict[line[0]]=(line[1].lower(), 2)

while(True):
	line = all_file.readline()
	if not line: break
	line= line.strip().split('<||>')
	if line[0] not in nepal_dict:
		nepal_dict[line[0]]= (line[1].lower(),0)


def create_train_test_data(nepal_dict):
	X=[[],[],[]]
	
	for elem in nepal_dict:
		X[nepal_dict[elem][1]].append(nepal_dict[elem][0])
	
	random.shuffle(X[0])
	random.shuffle(X[1])
	random.shuffle(X[2])

	train = [(X[i][k],i) for i in range(0,3) for k in range(0,int(0.7*len(X[i]))) ]
	val   = [(X[i][k],i) for i in range(0,3) for k in range(int(0.7*len(X[i])),int(0.8*len(X[i])))] 
	test  = [(X[i][k],i) for i in range(0,3) for k in range(int(0.8*len(X[i])), len(X[i]))]
	
	random.shuffle(train)
	random.shuffle(val)
	random.shuffle(test)  
	
	return train, val,  test

if dataset=='nepal':
	train_nepal, val_nepal, test_nepal = create_train_test_data(nepal_dict)
else:
	train_nepal, val_nepal, test_nepal = create_train_test_data(italy_dict)

train_nepal_sentences = ["[CLS] "+ text[0]+ " [SEP]" for text in train_nepal]
val_nepal_sentences   = ["[CLS] "+ text[0]+ " [SEP]" for text in val_nepal]
test_nepal_sentences  = ["[CLS] "+ text[0]+ " [SEP]" for text in test_nepal]
# train_italy_sentences = ["[CLS] "+ text[0]+ " [SEP]" for text in train_italy]
# val_italy_sentences   = ["[CLS] "+ text[0]+ " [SEP]" for text in val_italy]
# test_italy_sentences  = ["[CLS] "+ text[0]+ " [SEP]" for text in test_italy]
print(len(test_nepal_sentences))

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)

tokenized_nepal_train = [tokenizer.tokenize(sent) for sent in train_nepal_sentences]
tokenized_nepal_val   = [tokenizer.tokenize(sent) for sent in val_nepal_sentences]
tokenized_nepal_test  = [tokenizer.tokenize(sent) for sent in test_nepal_sentences]

# tokenized_italy_train = [tokenizer.tokenize(sent) for sent in train_italy_sentences]
# tokenized_italy_val   = [tokenizer.tokenize(sent) for sent in val_nepal_sentences]
# tokenized_italy_test  = [tokenizer.tokenize(sent) for sent in test_italy_sentences]

train_nepal_labels    = [elem[1] for elem in train_nepal]
val_nepal_labels      = [elem[1] for elem in val_nepal]
test_nepal_labels     = [elem[1] for elem in test_nepal]
# train_italy_labels    = [elem[1] for elem in train_italy]
# val_italy_labels      = [elem[1] for elem in val_italy]
# test_italy_labels     = [elem[1] for elem in test_italy]

MAX_LEN = 64
train_nepal_ids = pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in tokenized_nepal_train], maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")
val_nepal_ids   = pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in tokenized_nepal_val], maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")
test_nepal_ids  = pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in tokenized_nepal_test], maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

train_nepal_masks = []
val_nepal_masks   = []
test_nepal_masks  = []

for seq in train_nepal_ids:
	seq_mask = [float(i>0) for i in seq]
	train_nepal_masks.append(seq_mask)
	
for seq in val_nepal_ids:
	seq_mask = [float(i>0) for i in seq]
	val_nepal_masks.append(seq_mask)

for seq in test_nepal_ids:
	seq_mask = [float(i>0) for i in seq]
	test_nepal_masks.append(seq_mask)

train_nepal_ids    =  torch.LongTensor(train_nepal_ids)
val_nepal_ids      =  torch.LongTensor(val_nepal_ids)
test_nepal_ids     =  torch.LongTensor(test_nepal_ids)

train_nepal_masks  =  torch.LongTensor(train_nepal_masks)
val_nepal_masks    =  torch.LongTensor(val_nepal_masks)
test_nepal_masks   =  torch.LongTensor(test_nepal_masks)

train_nepal_labels = torch.LongTensor(train_nepal_labels)
val_nepal_labels   = torch.LongTensor(val_nepal_labels)
test_nepal_labels  = torch.LongTensor(test_nepal_labels)

train_nepal_data   = TensorDataset(train_nepal_ids, train_nepal_masks, train_nepal_labels)
val_nepal_data     = TensorDataset(val_nepal_ids, val_nepal_masks, val_nepal_labels)
test_nepal_data    = TensorDataset(test_nepal_ids, test_nepal_masks, test_nepal_labels)



class BertSentClassifier(torch.nn.Module):

	def __init__(self, config):
		super(BertSentClassifier, self).__init__()
		self.num_labels = config.num_labels
		self.bert = BertModel.from_pretrained(config.model_name)
		self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
		self.classifier = torch.nn.Linear(config.hidden_size, config.num_labels)

	def forward(self, input_ids, token_type_ids =None, attention_mask= None):
		_, pooled_output = self.bert(input_ids, token_type_ids, attention_mask, output_all_encoded_layers=False)
		pooled_output = self.dropout(pooled_output)
		logits = self.classifier(pooled_output)
		return F.log_softmax(logits, dim=1)


config = {'hidden_dropout_prob':0.3, 'num_labels':3,'model_name':'bert-base-uncased', 'hidden_size':768, 'data_dir':'saved_models/',}
config = SimpleNamespace(**config)

# model = BertModel.from_pretrained('bert-base-uncased')

model = BertSentClassifier(config)
print("Loading Done")

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '2'
model

param_optimizer = list(model.named_parameters())
no_decay = ['bias', 'gamma', 'beta']
optimizer_grouped_parameters = [
	{'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
	 'weight_decay_rate': 0.01},
	{'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
	 'weight_decay_rate': 0.0}
]

optimizer = BertAdam(optimizer_grouped_parameters,
					 lr=2e-5,
					 warmup=.1)


from sklearn.metrics import classification_report, f1_score

epochs =10

BATCH_SIZE = 64

train_nepal_dataloader = DataLoader(train_nepal_data, shuffle = True, batch_size= BATCH_SIZE)
val_nepal_dataloader = DataLoader(val_nepal_data, shuffle = False, batch_size= BATCH_SIZE)
test_nepal_dataloader = DataLoader(test_nepal_data, shuffle = False, batch_size= BATCH_SIZE)

best_val=0

# for epoch in range(epochs):
# 	model.train()
# 	print(epoch)
	
# 	tr_loss=0
# 	batch_num=0
# 	for step, batch in enumerate(train_nepal_dataloader):
# 		print("Done for batch = {}".format(step), end='\r')
# 		b_ids, b_mask, b_labels = batch
# 		b_ids= b_ids
# 		b_mask = b_mask
# 		b_labels = b_labels        
# 		# weights  = torch.Tensor([0.004461883549047657, 0.557096078912092, 0.4384420375388603])
# 		# weights = torch.Tensor([0.01,0.55,0.44])

# 		optimizer.zero_grad()
		
# 		logits = model(b_ids, attention_mask=b_mask)
# 		# import pdb
# 		# pdb.set_trace()
# 		loss   = F.nll_loss(logits, b_labels.view(-1), reduction='sum')
# 		loss /= b_labels.view(-1).shape[0]
# 		loss.backward()
# 		optimizer.step()
		
# 		tr_loss += loss.item()
# 		batch_num+=1
# 	print("Train loss {}".format(tr_loss/batch_num))
	
# 	model.eval()
	
# 	y_true=[]
# 	y_pred=[]
	
# 	for step, batch in enumerate(val_nepal_dataloader):
# 		b_ids, b_mask, b_labels = batch
# 		b_ids= b_ids
# 		b_mask = b_mask
# 		with torch.no_grad():
# 			logits = model(b_ids, attention_mask=b_mask)
# 			logits = logits.detach().cpu().numpy()
# 			preds  = np.argmax(logits, axis=1).flatten()
# 			b_labels = b_labels.flatten()
# 			y_true.extend(b_labels)
# 			y_pred.extend(preds)
			

# 	print(classification_report(y_true, y_pred))
# 	f1= f1_score(y_true, y_pred, average='macro')
# 	if f1> best_val:
# 		best_val= f1
# 		model_path = '{}/{}.pt'.format(config.data_dir, dataset)
# 		torch.save(model, model_path)


model_path = '{}/{}.pt'.format(config.data_dir, dataset)
model = torch.load(model_path, map_location='cpu')

model = model

y_true=[]
y_pred=[]
for step, batch in tqdm(enumerate(test_nepal_dataloader)):
	b_ids, b_mask, b_labels = batch
	b_ids= b_ids
	b_mask = b_mask
	with torch.no_grad():
		logits = model(b_ids, attention_mask=b_mask)
		logits = logits.detach().cpu().numpy()
		preds  = np.argmax(logits, axis=1).flatten()
		b_labels = b_labels.flatten()
		y_true.extend(b_labels)
		y_pred.extend(preds)
		
print(classification_report(y_true, y_pred))




'''
No weights, processed text. 

precision    recall  f1-score   support

           0       0.99      0.99      0.99      9641
           1       0.73      0.65      0.68        99
           2       0.75      0.69      0.72       265

    accuracy                           0.98     10005
   macro avg       0.82      0.78      0.80     10005
weighted avg       0.98      0.98      0.98     10005


No weights, un-processed text. 


  precision    recall  f1-score   support

           0       1.00      0.99      0.99      9641
           1       0.61      0.75      0.67        97
           2       0.67      0.84      0.74       267

    accuracy                           0.98     10005
   macro avg       0.76      0.86      0.80     10005
weighted avg       0.98      0.98      0.98     10005


Weights un-processed [0.01, 0.55, 0.44]


'''
