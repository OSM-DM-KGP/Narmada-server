import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
# from keras.preprocessing.sequence import pad_sequences
# from sklearn.model_selection import train_test_split
# from pytorch_pretrained_bert import BertTokenizer, BertConfig, BertModel
# from pytorch_pretrained_bert import BertAdam, BertForSequenceClassification
from tqdm import tqdm, trange
# import pandas as pd
import io
import numpy as np
# import matplotlib.pyplot as plt
import random
import pickle
import os
import torch.nn.functional as F

from types import SimpleNamespace
import pudb
import sys

class BertSentClassifier(torch.nn.Module):

	def __init__(self, config):
		super(BertSentClassifier, self).__init__()
		self.num_labels = config.num_labels
		# self.bert = BertModel.from_pretrained(config.model_name)
		# self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
		self.classifier = torch.nn.Linear(config.hidden_size, config.num_labels)

	def forward(self, input_ids, token_type_ids =None, attention_mask= None):
		# _, pooled_output = self.bert(input_ids, token_type_ids, attention_mask, output_all_encoded_layers=False)
		# pooled_output = self.dropout(pooled_output)
		logits = self.classifier(input_ids)
		return F.log_softmax(logits, dim=1)


def evaluate_bert(text):
	from bert_serving.client import BertClient
	print("Here 1")
	bc = BertClient()
	print("Here 2")
	test_nepal = [text]
	test_nepal_sentences  = ["[CLS] "+ text[0]+ " [SEP]" for text in test_nepal]
	
	MAX_LEN = 64
	test_nepal_ids  =  bc.encode(test_nepal_sentences)
	test_nepal_ids  =  torch.FloatTensor(test_nepal_ids)
	test_nepal_data =  TensorDataset(test_nepal_ids)

	bc.close()


	config = {'hidden_dropout_prob':0.3, 'num_labels':3,'model_name':'bert-base-uncased', 'hidden_size':768, 'data_dir':'saved_models/',}
	config = SimpleNamespace(**config)

	# model = BertModel.from_pretrained('bert-base-uncased')

	print("Here 3")
	model = BertSentClassifier(config)
	model = torch.load("/home/kaustubh/Narmada-server/saved_models/nepal_bert_service.pth", map_location='cpu')
	model.eval()
	print("Loading Done")

	print("Here 4")
	import os
	os.environ['CUDA_VISIBLE_DEVICES'] = '2'
	# model

	param_optimizer = list(model.named_parameters())
	no_decay = ['bias', 'gamma', 'beta']
	optimizer_grouped_parameters = [
		{'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
		 'weight_decay_rate': 0.01},
		{'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
		 'weight_decay_rate': 0.0}
	]

	optimizer = torch.optim.Adam(optimizer_grouped_parameters, lr=2e-5)


	# from sklearn.metrics import classification_report, f1_score

	# epochs = 100

	print("Here 5")
	BATCH_SIZE = 1

	test_nepal_dataloader = DataLoader(test_nepal_data, shuffle = False, batch_size= BATCH_SIZE)

	best_val=0

	for step, batch in enumerate(test_nepal_dataloader):
		print("Done for batch = {}".format(step), end='\r')
		b_ids = batch[0]
		# pu.db
		# b_sent = train_nepal_sentences[(step * BATCH_SIZE) : (step * BATCH_SIZE) + BATCH_SIZE]
		# pu.db
		# b_ids= b_ids
		# b_mask = b_mask
		# b_labels = b_labels        
		# weights  = torch.Tensor([0.004461883549047657, 0.557096078912092, 0.4384420375388603])
		# weights = torch.Tensor([0.01,0.55,0.44])

		optimizer.zero_grad()
		
		logits = model(b_ids)
		# import pdb

		logits = logits.detach().numpy()
		preds  = np.argmax(logits, axis=1).flatten()
		
		print(preds)

	del bc

	return int(preds[0])

if __name__ == '__main__':
	text = input("Text ploxx: ")
	evaluate_bert(text)