import pickle
import sys
import ast
import re
import json
from word2number import w2n
import os, sys

try:
	location=sys.argv[1]
except Exception as e:
	location='roma'	

try:
	type_=sys.argv[2]
except Exception as e:
	type_='needs'


with open('OUTPUT/'+location+'_'+type_+'.p','rb') as handle:
	need_dict=pickle.load(handle)


need_json=[]

for elem in need_dict:

	sample_dict={}	

	elem_id=elem

	tweet_text=need_dict[elem][0]

	resource_class_dict= need_dict[elem][-1]

	sample_dict['_id']=elem_id
	sample_dict['lang']='en'
	sample_dict['text']=tweet_text
	sample_dict['Classification']='Need'
	sample_dict['isCompleted']=False
	sample_dict['username']='@Username'
	sample_dict['Matched']=-1
	sample_dict['Locations']={}
	sample_dict['Sources']=[]
	sample_dict['Resources']=[]
	sample_dict['Contact']={}
	sample_dict['Contact']['Email']=[]
	sample_dict['Contact']['Phone Number']=[]

	source_list= list(set(need_dict[elem][1]))
	for i in source_list:
		sample_dict['Sources'].append(i)


	for i in list(set(need_dict[elem][3])):
		loc_name=i[0]
		lat=i[1][0]
		long_=i[1][1]
		sample_dict['Locations'][loc_name]={}
		sample_dict['Locations'][loc_name]['lat']=lat
		sample_dict['Locations'][loc_name]['long']=long_


	for i in list(set(need_dict[elem][4][0])):
		sample_dict['Contact']['Phone Number'].append(i)

	for i in list(set(need_dict[elem][4][1])):
		sample_dict['Contact']['Email'].append(i[0])


	resources=list(set(need_dict[elem][-2]))
	print(resources)
	print(resource_class_dict)
	# resource_list=",".join(list(set(need_dict[elem][-1])))

	
	split_text=tweet_text.split()

	quantity_list=[]			

	class_list={}

	for resource in resources:
		

		s={}

		try:
			res_class = resource_class_dict[resource][1]
		except Exception as e:
			res_class = 'ERROR'	
			continue

		if res_class not in class_list:
			class_list[res_class]={}	
		
		
		# s['resource']=resource	

		prev_words=[ split_text[i-1] for i in range(0,len(split_text)) if resource.startswith(split_text[i]) ]
		# prev_words_2=[ str(split_text[i-2])+' '+ str(split_text[i-1]) for i in range(0,len(split_text)) if i == resource ]

		qt='None'

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

				elems=resource.strip().split()	
				word=elems[0]
				resource2=" ".join(elems[1:])				

				word=word.replace(',','')
				if word.isnumeric()==True:
					qt=str(word)
				else:
					try:
						qt=str(w2n.word_to_num(word))
					except Exception as e:
						pass	

			if qt!='None' and qt in resource:
				print(resource, qt)
				continue


			if resource not in class_list[res_class]:
				class_list[res_class][resource]=qt
			else:
				continue				
			

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			qt='None'						

		
		
		class_list[res_class][resource]= qt
		# sample_dict['Resources'].append(s)


	sample_dict['Resources']= class_list

	need_json.append(sample_dict)	


with open(location+'_'+type_+'.json','w') as fp:
	json.dump(need_json,fp, indent= 3)


# offer_csv=open(location+'_offers.csv','w')
# with open('OUTPUT/'+location+'_offers.p','rb') as handle:
# 	need_dict=pickle.load(handle)

# offer_csv.write('Tweet ID	 Tweet text	 Source List	 Location list	 Resource list	 Phone number	 Email	 Url	 Quantity Dict\n')

# for elem in need_dict:
# 	elem_id=elem
# 	tweet_text=need_dict[elem][0]
# 	source_list= ",".join(list(set(need_dict[elem][1])))
# 	loc_list=",".join(list(set([i[0] for i in need_dict[elem][3]])))
# 	resources=list(set(need_dict[elem][-1]))
# 	resource_list=",".join(list(set(need_dict[elem][-1])))
# 	contact_list_0=','.join(list(set(need_dict[elem][4][0])))

# 	contact_list_1=','.join([i[0] for i in list(set(need_dict[elem][4][1]))])

# 	contact_list_2=','.join(list(set(need_dict[elem][4][2])))	
# 	split_text=tweet_text.split()
	
# 	quantity_list=[]			

# 	for resource in resources:
# 		prev_words=[ split_text[i-1] for i in range(0,len(split_text)) if resource.startswith(split_text[i])]
# 		for word in prev_words:
# 			try:
# 				word=word.replace(',','')
# 				if word.isnumeric()==True:
# 					quantity_list.append(str(resource)+'-'+str(word))
# 					# quantity_dict[resource]=word
# 				else:
# 					quantity_list.append(str(resource)+'-'+str(w2n.word_to_num(word)))
# 					# quantity_dict[resource]=w2n.word_to_num(word)

# 			except Exception as e:
# 				continue			


# 		elems=resource.split()		
# 		word=elems[0]
# 		resource=" ".join(elems[1:-1])
# 		try:
# 			word=word.replace(',','')
# 			if word.isnumeric()==True:
# 				quantity_list.append(str(resource)+'-'+str(word))
# 				# quantity_dict[resource]=word
# 			else:
# 				quantity_list.append(str(resource)+'-'+str(w2n.word_to_num(word)))
# 				# quantity_dict[resource]=w2n.word_to_num(word)

# 		except Exception as e:
# 			continue




# 	quantity_list=','.join(list(set(quantity_list)))	
	
# 	offer_csv.write(str(elem_id)+'	'+tweet_text+'	'+source_list+'	'+loc_list+'	'+ resource_list+'	'+ contact_list_0+'	'+ contact_list_1+'	'+ contact_list_2+"	"+ quantity_list+'\n')