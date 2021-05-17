import os
import flask
from flask import Flask
app = Flask(__name__)

# get_resource_class.py's version as an api
import re
# import CMUTweetTagger
#import cPickle
from collections import defaultdict
import pickle
from nltk.corpus import wordnet as wn
from itertools import product
import spacy
from spacy.symbols import *
from nltk import Tree
from word2number import w2n
import nltk
import location_2 as location
import time
import sys
import json
from urllib.parse import unquote
from classify_tweets_covid_infer import BertSentClassifier
from classify_tweets_covid_infer import evaluate_bert
import location
import pudb
# model = load_model()
ps_stemmer= nltk.stem.porter.PorterStemmer()

## CORS
from flask_cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# import en_core_web_sm
# nlp = en_core_web_sm.load()
nlp=spacy.load('en')
np_labels=set(['nsubj','dobj','pobj','iobj','conj','nsubjpass','appos','nmod','poss','parataxis','advmod','advcl'])
subj_labels=set(['nsubj','nsubjpass','csubj','csubjpass'])
modifiers=['nummod','compound','amod','punct']
after_clause_modifier=['relcl','acl','ccomp','xcomp','acomp','punct','advcl','rcmod']
tel_no="([+]?[0]?[1-9][0-9\s]*[-]?[0-9\s]+)"
email="([a-zA-Z0-9]?[a-zA-Z0-9_.]+[@][a-zA-Z]+[.](com|net|edu|in|org|en))"
web_url="http:[a-zA-Z._0-9/]+[a-zA-Z0-9]"
http_url='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
entity_type_list=['NORP','ORG','GPE','PERSON']
quant_no="([0-9]*[,.]?[0-9]+[km]?)"
alphanum="[^0-9a-zA-Z ]"

stop_list=list(location.false_names)
#,'nn','quantmod','nmod','hmod','infmod']

need_file=open('DATA/Process_resources/need.txt')
offer_file=open('DATA/Process_resources/offer.txt')
shelter_file=open('DATA/Process_resources/shelter.txt')
food_file=open('DATA/Process_resources/food.txt')
medical_file=open('DATA/Process_resources/medical.txt')
cash_file=open('DATA/Process_resources/cash.txt')
logistics_file=open('DATA/Process_resources/logistics.txt')
disaster_events_file=open('DATA/Process_resources/disaster_events.txt')

basic_resource=['medical','water','sanitation','shelter','cloth','food','transport','infrastructure','volunteers','logistic']

need_verb_list=set()
for line in need_file:
	line=line.rstrip().lower()
	need_verb_list.add(line)
send_verb_list=set()	
for line in offer_file:
	line=line.rstrip().lower()
	send_verb_list.add(line)

need_send_verb_list=list(need_verb_list)
need_send_verb_list.extend(list(send_verb_list))	
common_resource=set()
dis_events=set()

resource_class_dict={}
resource_class_dict['shelter']=set()
resource_class_dict['food']=set()
resource_class_dict['medical']= set()
resource_class_dict['logistic']= set()
resource_classes=['shelter', 'food','medical','logistic']


for line in shelter_file:
	line=line.rstrip().lower()
	common_resource.add(line)
	resource_class_dict['shelter'].add(line)
	resource_class_dict['shelter'].add(ps_stemmer.stem(line))

for line in cash_file:
	line=line.rstrip().lower()
	common_resource.add(line)
	resource_class_dict['logistic'].add(line)
	resource_class_dict['logistic'].add(ps_stemmer.stem(line))

for line in food_file:
	line=line.rstrip().lower()
	common_resource.add(line)
	resource_class_dict['food'].add(line)
	resource_class_dict['food'].add(ps_stemmer.stem(line))

for line in medical_file:
	line=line.rstrip().lower()
	common_resource.add(line)
	resource_class_dict['medical'].add(line)
	resource_class_dict['medical'].add(ps_stemmer.stem(line))

for line in logistics_file:
	line=line.rstrip().lower()
	common_resource.add(line)
	resource_class_dict['logistic'].add(line)
	resource_class_dict['logistic'].add(ps_stemmer.stem(line))


for line in disaster_events_file:
	line=line.rstrip().lower()
	dis_events.add(line)

dis_events_stem=[ps_stemmer.stem(i) for i in list(dis_events)]

common_resource=list(common_resource)
common_resource.extend([ps_stemmer.stem(i) for i in common_resource])

try:
	input_name=sys.argv[1]
except:
	input_name='roma_needs'	

print(input_name)
input_file='DATA/INPUT/'+input_name+'.txt'
# print(tweet_preprocess2(text,[]))
stop_list.extend(need_send_verb_list)

def get_contact(text):
	contacts=[]
	flag=0
	numbers=re.findall(tel_no,text)
	temp=set()
	for i in numbers:
		if len(i.replace(' ',''))>=7:
			temp.add(i)
			# print("Contact information:" +i)
	contacts.append(temp)		
	temp=set()
	mails= re.findall(email,text)
	for i in mails:
		temp.add(i)
		# print("Mail: "+i[0])	
	
	contacts.append(temp)	
	temp=set()	
	urls= re.findall(http_url,text)	
	for i in urls:
		temp.add(i)
		# print("URL: "+i)	
		
	contacts.append(temp)
	return contacts	

def modifier_word(word):
	modified_word=word.orth_
	while word.n_lefts+word.n_rights==1 and word.dep_.lower() in modifiers:
		word=[child for child in word.children][0]
		modified_word=word.orth_+" "+modified_word
	return modified_word	

def tok_format(tok):
	return "_".join([tok.orth_, tok.dep_,tok.ent_type_])

def to_nltk_tree(node):
	if node.n_lefts + node.n_rights > 0:
		return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
	else:
		return tok_format(node)		

def get_verb_similarity_score(word,given_list,given_list_2):
	max_verb_similarity=0
	if word.lower() in given_list:
		max_verb_similarity=1
	else:	
		current_verb_list=wn.synsets(word.lower())
		for verb in given_list_2:
			related_verbs=wn.synsets(verb)
			for a,b in product(related_verbs,current_verb_list):
				d=wn.wup_similarity(a,b)
				try:
					if d> max_verb_similarity:
						max_verb_similarity=d
				except:
					continue
	return max_verb_similarity			

def resource_in_list(resource):
	
	related_resources=wn.synsets(resource)
	max_similarity=0
	chosen_word=""
	resource_class=""

	resource_stem=ps_stemmer.stem(resource.lower())

	for elem in resource_classes:
		if resource_stem in resource_class_dict[elem]:
			return 1,resource, elem

	for word in basic_resource:
		related_words=wn.synsets(word)
		for a,b in product(related_words,related_resources):
			d=wn.wup_similarity(a,b)
			try:
				if d> max_similarity:
					max_similarity=d
					chosen_word=word
			except:
				continue
	
	if chosen_word in ['medical','sanitation']:
		resource_class='medical'

	elif chosen_word in ['food','water']:
		resource_class = 'food'

	elif chosen_word in ['shelter','cloth']:
		resource_class= 'shelter'

	elif chosen_word in ['transport','infrastructure','volunteers','logistic']:	
		resource_class= 'logistic'
				
	return max_similarity, chosen_word, resource_class

def get_children(word,resource_array,modified_array):
	#print(word,word.dep_)

	for child in word.children:
		if child.dep_.lower() in modifiers:
			get_word=modifier_word(child)+" "+word.orth_+"<_>"+word.dep_
			modified_array.append(get_word)
		if child.dep_.lower()=='prep' or child.dep_.lower()=='punct':
			get_children(child,resource_array,modified_array)	
		if child.dep_.lower() in after_clause_modifier:	
			#print(child, child.dep_)
			get_children(child,resource_array,modified_array)	
		if child.dep_.lower() in np_labels:			
			get_children(child,resource_array,modified_array)
			resource_array.append(child.orth_+"<_>"+child.dep_)		
		else:
			if get_verb_similarity_score(child.orth_,common_resource,basic_resource)>0.9:
				get_children(child,resource_array,modified_array)

def get_resource(text):
	doc=nlp(text)
	# try:
	# 	[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
	# except:
	# 	print("Exception here")

	# print(time.time()-start_time,1)
	org_list=[]
	prev_word=""
	prev_word_type=""
	for word in doc:
		if word.ent_type_ in entity_type_list:
			org_list.append(word.orth_+"<_>"+word.ent_type_)
		else:
			org_list.append("<_>")

	resource_array=[]
	modified_array=[]
	for word in doc:
		if  get_verb_similarity_score(word.orth_,need_send_verb_list,need_send_verb_list)>0.9 or word.dep_=='ROOT':
			get_children(word,resource_array,modified_array)

		if word.dep_=='cc' and word.n_lefts+word.n_rights==0:
			ancestor=word.head.orth_
			#print(ancestor)
			if get_verb_similarity_score(ancestor,common_resource,basic_resource)>0.9:
				get_children(word.head,resource_array,modified_array)		
				
	last_word=[]
	final_resource={}
	modified_array_2=[]
	resource_array_2=[]
	n_subj_list=[]

	# print(time.time()-start_time,2)

	# print("Modified array", modified_array)
	# print("Resource array", resource_array)
	
	for i in modified_array:
		modified_array_2.append(i[:(i.index("<_>"))])

	for i in resource_array:
		resource_array_2.append(i[:(i.index("<_>"))])

	modified_array_2=[re.sub(alphanum,"",i.strip()) for i in modified_array_2]
	modified_array_2=list(set([i.strip() for i in modified_array_2]))
	resource_array_2=[re.sub(alphanum,"",i.strip()) for i in resource_array_2]
	resource_array_2=list(set([i.strip() for i in resource_array_2]))

	# print("Resource array: ",resource_array_2)	
	# print("Modified array: ", modified_array_2)

	for resources in modified_array_2:
		max_val_resource=-1
		val_type=""
		class_type=''

		resource_list=resources.strip().split(" ")
		for resource in resource_list:
			# print(resource)

			pres_res_val,pres_res_type,pres_res_class =resource_in_list(resource)

			if pres_res_val==-1:
				continue

			if pres_res_val>= max_val_resource:
				val_type=pres_res_type
				max_val_resource=pres_res_val		
				class_type= pres_res_class
				# print(resource, val_type, pres_res_val, class_type)

			if pres_res_val> 0.8:
				final_resource[resource]=(pres_res_type	, pres_res_class)
				# print(resource,pres_res_val,pres_res_type, pres_res_class)
				
		if max_val_resource > 0.9:
			final_resource[resources]=(val_type, class_type)

	# print(time.time()-start_time,3)
			
	for resource in resource_array_2:
		
		pres_res_val,pres_res_type, pres_res_class=resource_in_list(resource)
		# print(resource,pres_res_val,pres_res_type, pres_res_class )

		if pres_res_val> 0.8:
			if resource not in final_resource:
				final_resource[resource]=(pres_res_type, pres_res_class)

	final_resource_keys=list(final_resource.keys())
	
		
	prev_word_type=""
	prev_word=""
	org_list_2=[]
	
	for i in org_list:
		index=i.index("<_>")
		if i[index+3:]=="ORG" and prev_word_type=="ORG":
			prev_word=prev_word+" "+i[:index]
		elif i[index+3:]=="PERSON" and prev_word_type=="PERSON":	
			prev_word=prev_word+" "+i[:index]
		else:
			if prev_word !='':
				org_list_2.append(prev_word+"<_>"+prev_word_type)
			prev_word_type=i[index+3:]
			prev_word=i[:index]


	source_list=[]
	org_person_list=[]
	
	for i in org_list_2:
		tag=i[i.index("<_>")+3:]
		j=i[:i.index("<_>")]

		if tag=="ORG" or tag=="PERSON" or tag=='GPE' or tag=='LOC':
			if j.lower() not in stop_list:
				org_person_list.append(j)
		elif j.lower() not in stop_list :
			source_list.append(j)
		else:
			continue	
	
	for i in modified_array:
		pos_res=i[:i.index("<_>")]
		pos_tag=i[i.index("<_>")+3:]
		if pos_tag in subj_labels:
			if pos_res not in source_list and pos_res not in final_resource_keys and pos_res.lower() not in  stop_list:
				#print(pos_tag,pos_res)
				source_list.append(pos_res)

	for i in resource_array:
		pos_res=i[:i.index("<_>")]
		pos_tag=i[i.index("<_>")+3:]
		if pos_tag in subj_labels:
			if pos_res not in source_list and pos_res not in final_resource_keys and pos_res.lower() not in  stop_list:
				#print(pos_tag,pos_res)
				source_list.append(pos_res)				

	pos_tags_dict={}	
	doc2=nlp(text.lower())		

	for word in doc2:
		try:
			pos_tags_dict[word.orth_]=word.pos_
		except:
			continue	

	final_resource_keys_2=[]

	for elem in final_resource_keys:
		elem2=elem.split()
		poss=[]

		for i in elem2:
			try:
				poss.append(pos_tags_dict[i.lower()])
			except Exception as e:
				continue	
		# poss=[pos_tags_dict[i.lower()] for i in elem2]

		if poss==[]:
			continue
			
		if 'VERB' not in poss and( poss[-1]=='NOUN'):
			final_resource_keys_2.append(elem)	


	return final_resource_keys_2,source_list,org_person_list,modified_array, final_resource

def jumble(text,items):

	final_items=[]

	for item in items:
		if item in text:
			final_items.append(item)

	temp_list=[]
	for item1 in final_items:
		for item2 in final_items:
			if item1+' '+item2 in text:
				temp_list.append(item1+' '+item2)

	final_items.extend(temp_list)			

	items=list(set(items)-set(final_items))
	
	while True:
		add_list=[]
		rem_list=[]
		item_list=[]

		for item in items:		
			item_split=item.split()
			for elem in final_items:
				for k in item_split:
					if k+' '+elem in text:
						add_list.append(k+' '+elem)
						rem_list.append(elem)
						item_list.append(item)
					if elem+' '+k in text:	
						add_list.append(elem+' '+k)
						rem_list.append(elem)
						item_list.append(item)						

		if add_list==[]:
			break
		else:
			final_items.extend(add_list)
			items= list(set(items)-set(item_list))

	return final_items		

def post_process(text,final_resource_keys,source_list,loc_list):

	source_dis=set()
	resource_dis=set()

	for loc in loc_list:
		for elem in source_list:
			elem2=elem
			elem=elem.lower()
			if loc in elem or elem in loc or elem in stop_list:
				source_dis.add(elem2)
				continue

		for elem in final_resource_keys:
			elem2=elem
			elem=elem.lower()
			if loc in elem or elem in loc or elem in stop_list:
				resource_dis.add(elem2)
				continue


	source_list=list(set(source_list)- source_dis)
	final_resource_keys=list(set(final_resource_keys)- resource_dis)

	source_list_2=[]
	source_dis=set()
	
	for elem in source_list:	
		elem_split=[ps_stemmer.stem(i) for i in elem.lower().split()]
		flag=False
		for i in elem_split:
			if i in dis_events_stem:
				flag=True
				break
		if flag==True:
			source_dis.add(elem)
			continue

		for elem2 in source_list:
			if elem2 ==elem:
				continue

			if elem2 in source_dis:
				continue

			if elem2 in elem :
				source_dis.add(elem2)
			if elem in elem2:
				source_dis.add(elem)	

	source_list=list(set(source_list)- source_dis)	
	source_list=jumble(text,source_list)

	dup_final_resource_keys=list(final_resource_keys)

	final_resource_keys=jumble(text,final_resource_keys)


	source_dis=set()
	resource_dis=set()

	for elem in source_list:	
		for elem2 in source_list:
			if elem2 ==elem:
				continue
			if elem2 in source_dis:
				continue
			if elem2 in elem :
				source_dis.add(elem2)
			if elem in elem2:
				source_dis.add(elem)

		for elem3 in final_resource_keys:
			if elem in elem3 or elem3 in elem:
				source_dis.add(elem)		



	for elem in final_resource_keys:
		for elem2 in final_resource_keys:
			if elem2 ==elem:
				continue
			if elem2 in resource_dis:
				continue
			if elem2 in elem :
				resource_dis.add(elem2)
			if elem in elem2:
				resource_dis.add(elem)			

	source_list=list(set(source_list)- source_dis)			
	final_resource_keys=list(set(final_resource_keys)- resource_dis)

	return source_list,final_resource_keys,loc_list	,dup_final_resource_keys
	# print(source_list)
	# print(final_resource_keys)
	# print(loc_list)

def create_resource_list(text):
	count=0
	
	quantity_dict={}
	final_resource_keys=[]
	source_list=[]
	loc_list=[]
	org_person_list=[]

	loc_list_2=location.return_location_list(text)
	# print("Location list",loc_list_2)
	
	final_resource_keys,source_list,org_person_list,modified_array, final_resource_dict= get_resource(text)	


	# print("Final resource keys",final_resource_keys)
	# print("Final resources", final_resource_dict)

	doc=nlp(text)		
	

	for elem in source_list:
		if elem.lower() in location.curr_loc_dict and elem.lower() not in stop_list:
			loc_list_2.append((elem.lower(),location.curr_loc_dict[elem.lower()]))

	for elem in org_person_list:
		if elem.lower() in location.curr_loc_dict and elem.lower() not in stop_list:
			loc_list_2.append((elem.lower(),location.curr_loc_dict[elem.lower()]))

	loc_list=list(set([i[0] for i in loc_list_2]))

	source_list= [i for i in source_list if i.lower() not in loc_list] 
	org_person_list=[i for i in org_person_list if i.lower() not in loc_list] 

	source_list=list(set(source_list) | set(org_person_list))

	final_resource_keys=[i for i in final_resource_keys if i.lower() not in loc_list]

		
	a,b,c,d=post_process(text, final_resource_keys,source_list,loc_list)
	# print(text)
	# print(a)
	# print(b)
	# print(c)
	# print(d)

	'''
	a= source list
	b= final resource keys
	c= loc_list
	d= dup_final_resource keys
	'''
	return a,b,loc_list_2,modified_array,d, final_resource_dict

def get_classification(text):
	# global model
	return evaluate_bert(text)

bucket_classes=['shelter', 'food','medical','logistic']

@app.route('/parse', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def parseResources():
	global_resource_list={}
	# print(flask.request.body)
	resource, line = {}, ''
	print(flask.request.json)
	print(unquote(flask.request.query_string.decode('utf-8')))
	if flask.request and flask.request.json and'text' in flask.request.json:
		line = flask.request.json['text']
	else:
		line = json.loads(unquote(flask.request.query_string.decode('utf-8')))['text']

	print('Received for parsing: ', line)

	text = line.lower()

	places = location.return_location_list(text)
	each_loc = [place[0] for place in places]
	resources = {
		"oxygen": "Oxygen",
		"o2": "Oxygen",
		"ventilator": "Ventilator",
		"bed": "Beds",
		"icu": "Beds",
		"remdes": "Remdesivir",
		"plasma": "Plasma",
		"consultation": "Doctor",
		"ambulance": "Ambulance"
	}

	places_to_remove = []
	resource_text = ""
	for res in resources:
		if res in each_loc:
			places_to_remove.append(each_loc.index(res))
		if res in text:
			resource_text = resource_text+resources[res]+" "

	places_to_remove.sort(reverse=True)
	for ptr in places_to_remove:
		del places[ptr]

	# pu.db
	resource['ResourceWords'] = resource_text
	resource['Locations'] = places




	# contacts = get_contact(line)
	# t2 = location.tweet_preprocess2(line,[])
	# sources,b,locations,modified_array,rWords, final_resource_dict  =create_resource_list(line)
	# # source_list,final_resource_keys,loc_list	,dup_final_resource_keys => post_process

	# ## source_list, final_resource_keys, loc_list_2, modified_array?, dup_final_resource_keys, final_resource_dict?
	# # resource['x']=((line,a,b,c,modified_array,d, final_resource_dict))

	# resource['Contact'] = {'Phone number': list(contacts[0]), "Email": list(contacts[1])}
	# resource['Sources'] = sources
	# resource['ResourceWords'] = rWords
	# resource['Locations'], resource['Resources'] = dict(), {}
	# # resource['Locations'] = locations
	# for each in locations:
	# 	# print(each[0], "<>", each[1])
	# 	resource['Locations'][each[0]] = {"long": float(each[1][1]), "lat": float(each[1][0])}
	# # f is Resources type
	# resources_bucket = {}

	# for each_resource in final_resource_dict:
	# 	buckets = final_resource_dict[each_resource]
	# 	assigned = False
	# 	for bucket in buckets:
	# 		if bucket in bucket_classes and not assigned:
	# 			if bucket not in resource['Resources']:
	# 				resource['Resources'][bucket] = {}
	# 			resource['Resources'][bucket][each_resource] = 'None'
	# 			assigned = True
	# 			resources_bucket[each_resource] = bucket
		
	
	# split_text= line.split()
	# class_list={}

	# for rWord in rWords:
	# 	s = {}
	# 	prev_words = [ split_text[i-1] for i in range(0,len(split_text)) if rWord.startswith(split_text[i]) ]
	# 	qt = 'None'

	# 	try:
	# 		for word in prev_words:
	# 			word=word.replace(',','')
	# 			if word.isnumeric()==True:
	# 				qt=str(word)
	# 				break
	# 			else:
	# 				try:
	# 					qt=str(w2n.word_to_num(word))
	# 					break
	# 				except Exception as e:	
	# 					continue

	# 		if qt=='None':	
	# 			elems=rWord.strip().split()	
	# 			word=elems[0]
	# 			rWord2=" ".join(elems[1:])

	# 			word=word.replace(',','')
	# 			if word.isnumeric()==True:
	# 				qt=str(word)
	# 			else:
	# 				try:
	# 					qt=str(w2n.word_to_num(word))
	# 				except Exception as e:
	# 					pass

	# 		if qt != 'None' and qt in rWord:
	# 			print(rWord, qt)
	# 			continue


	# 	except Exception as e:
	# 		exc_type, exc_obj, exc_tb = sys.exc_info()
	# 		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	# 		print(exc_type, fname, exc_tb.tb_lineno)
	# 		qt='None'

	# 	# class_list[rWord]= qt
	# 	resource['Resources'][resources_bucket[rWord]][rWord] = qt

	# print(class_list)
	## Need to add quantity
	## Ritam yaha dekh
	classification = -1
	if "need" in text or "require" in text:
	    classification = 0
	elif "availab" in text or len(resource_text) != 0:
	    classification = 1
		
	resource['Classification'] = classification
	# print('=>', resource['contact'], '\na=>', a, '\nb=>', b, '\nc=>', c, '\nm=>', modified_array, '\nd=>', d, '\nf=>', final_resource_dict)
	# print(final_resource_dict)
	print('Returning', resource)
	return flask.jsonify(resource)


@app.route('/parseStream', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def parseResourcesStream():
	global_resource_list={}
	# resource, line = {}, ''
	resource_stream = []
	print(flask.request.json)
	# print(unquote(flask.request.query_string.decode('utf-8')))
	if flask.request and flask.request.json and'text' in flask.request.json:
		line_stream = flask.request.json['text']
	# else:
	# 	line = json.loads(unquote(flask.request.query_string.decode('utf-8')))['text']
	for line in line_stream:
		resource = {}
		print('Received for parsing: ', line)
		contacts = get_contact(line)
		t2 = location.tweet_preprocess2(line,[])
		sources,b,locations,modified_array,rWords, final_resource_dict  =create_resource_list(line)
		# source_list,final_resource_keys,loc_list	,dup_final_resource_keys => post_process

		## source_list, final_resource_keys, loc_list_2, modified_array?, dup_final_resource_keys, final_resource_dict?
		# resource['x']=((line,a,b,c,modified_array,d, final_resource_dict))
		resource["text"] = line
		resource['Contact'] = {'Phone number': list(contacts[0]), "Email": list(contacts[1])}
		resource['Sources'] = sources
		resource['ResourceWords'] = rWords
		resource['Locations'], resource['Resources'] = dict(), {}
		# resource['Locations'] = locations
		for each in locations:
			# print(each[0], "<>", each[1])
			resource['Locations'][each[0]] = {"long": float(each[1][1]), "lat": float(each[1][0])}
		# f is Resources type
		resources_bucket = {}

		for each_resource in final_resource_dict:
			buckets = final_resource_dict[each_resource]
			assigned = False
			for bucket in buckets:
				if bucket in bucket_classes and not assigned:
					if bucket not in resource['Resources']:
						resource['Resources'][bucket] = {}
					resource['Resources'][bucket][each_resource] = 'None'
					assigned = True
					resources_bucket[each_resource] = bucket
			

		split_text= line.split()
		class_list={}

		for rWord in rWords:
			s = {}
			prev_words = [ split_text[i-1] for i in range(0,len(split_text)) if rWord.startswith(split_text[i]) ]
			qt = 'None'

			try:
				for word in prev_words:
					word=word.replace(',','')
					if word.isnumeric()==True:
						qt=str(word)
						break
					else:
						try:
							qt=str(w2n.word_to_num(word))
							break
						except Exception as e:	
							continue

				if qt=='None':	
					elems=rWord.strip().split()	
					word=elems[0]
					rWord2=" ".join(elems[1:])

					word=word.replace(',','')
					if word.isnumeric()==True:
						qt=str(word)
					else:
						try:
							qt=str(w2n.word_to_num(word))
						except Exception as e:
							pass

				if qt != 'None' and qt in rWord:
					print(rWord, qt)
					continue


			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				qt='None'

			# class_list[rWord]= qt
			resource['Resources'][resources_bucket[rWord]][rWord] = qt
		resource_stream.append(resource)
		# print(class_list)
		## Need to add quantity
		## Ritam yaha dekh
		# resource['Classification'] = get_classification(line_stream)
	classification_stream = get_classification(line_stream)
	print(classification_stream)
	resource_stream_final = []
	for i, cl in enumerate(classification_stream):
		resource = resource_stream[i]
		resource["Classification"] = int(cl)
		resource_stream_final.append(resource)
			
		# print('=>', resource['contact'], '\na=>', a, '\nb=>', b, '\nc=>', c, '\nm=>', modified_array, '\nd=>', d, '\nf=>', final_resource_dict)
		# print(final_resource_dict)
	print('Returning', resource_stream_final)
	return flask.jsonify(resource_stream_final)

# add routes for nodejs backend via here as well

@app.route('/', methods=['GET', 'OPTIONS'])
@cross_origin()
def base():
	with open('index.html', 'r') as f:
		txt = f.readlines()
	return ''.join(txt)

# @app.route('/hello')
# def empty():
# 	return "Hello World!"


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
