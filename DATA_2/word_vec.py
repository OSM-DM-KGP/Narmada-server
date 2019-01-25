import pickle
import gensim
from gensim import *
import nltk
import time
import stop_words
import re
import sys
import emoji
from nltk.tokenize import TweetTokenizer


tknzr=TweetTokenizer(strip_handles=True,reduce_len=True)
stemmer=nltk.stem.porter.PorterStemmer()

stop_words=stop_words.get_stop_words('en')
stop_words_2=['i','me','we','us','you','u','she','her','his','he','him','it','they','them','who','which','whom','whose','that','this','these','those','anyone','someone','some','all','most','himself','herself','myself','itself','hers','ours','yours','theirs','to','in','at','for','from','etc',' ',',']
stop_words.extend(stop_words_2)
stop_words.extend(['with', 'at', 'from', 'into', 'during', 'including', 'until', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'of', 'to', 'in', 'for', 'on', 'by', 'about', 'like', 'through', 'over', 'before', 'between', 'after', 'since', 'without', 'under', 'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'out', 'around', 'down', 'off', 'above', 'near', 'and', 'or', 'but', 'nor', 'so', 'for', 'yet', 'after', 'although', 'as', 'as', 'if', 'long', 'because', 'before', 'even', 'if', 'even though', 'once', 'since', 'so', 'that', 'though', 'till', 'unless', 'until', 'what', 'when', 'whenever', 'wherever', 'whether', 'while', 'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'yours', 'his', 'her', 'its', 'ours', 'their', 'few', 'many', 'little', 'much', 'many', 'lot', 'most', 'some', 'any', 'enough', 'all', 'both', 'half', 'either', 'neither', 'each', 'every', 'other', 'another', 'such', 'what', 'rather', 'quite'])
stop_words=list(set(stop_words))
stopword_file=open("Process_resources/stopword.txt",'r')
stop_words.extend([line.rstrip() for line in stopword_file])

remove_puncts="[\{\};,.[!@#$%^&*()_+=?/\'\"\]]"
apostrophe_file=open('Process_resources/apostrophe.txt')
apostrophe_dict={}

for line in apostrophe_file:
	line=line.rstrip().split('\t')
	poss_vals=line[1].split(',')
	if line[0] not in apostrophe_dict:
		apostrophe_dict[line[0]]=poss_vals

try:
	# Wide UCS-4 build
	myre = re.compile(u'['
		u'\U0001F300-\U0001F64F'
		u'\U0001F680-\U0001F6FF'
		u'\u2600-\u26FF\u2700-\u27BF]+', 
		re.UNICODE)
except re.error:
	# Narrow UCS-2 build
	myre = re.compile(u'('
		u'\ud83c[\udf00-\udfff]|'
		u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
		u'[\u2600-\u26FF\u2700-\u27BF])+', 
		re.UNICODE)		

emojis_list = map(lambda x: ''.join(x.split()), emoji.UNICODE_EMOJI.keys())
remoji = re.compile('|'.join(re.escape(p) for p in emojis_list))


web_url="http[s]?:[a-zA-Z._0-9/]+[a-zA-Z0-9]"
replacables="RT\s|-\s|\s-|#|@|[|}|]|{|(|)"
prop_name="([A-Z][a-z]+)"
num="([0-9]+)"
name="([A-Za-z]+)"
and_rate="([&][a][m][p][;])"
ellipses="([A-Za-z0-9]+[…])"
hashtags_2="([#][a-zA-z0-9]+[\s\n])"


entity_type_list=['NORP','ORG','GPE','PERSON']

def tweet_preprocess2(text):
	text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
	text = re.sub('http://', '', text)
	text = re.sub('https://', '', text)
	#print urls
	text = re.sub('@(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',text)
	text = re.sub('@', '',text)

	text=re.sub(and_rate,'and',text)
	text=re.sub(replacables,'',text)
	text=" ".join(tknzr.tokenize(text))

	prev_text=''
	while text!=prev_text:
		prev_text=str(text)
		text=re.sub(str(num)+''+name,"\\1 \\2",text)
		text=re.sub(name+''+str(num),"\\1 \\2",text)
		text=re.sub(prop_name+''+prop_name,"\\1 \\2",text)

	text = myre.sub('',text)
	return text.strip()	

try:
	region_name=sys.argv[1]
except Exception as e:
	region_name='italy'

file=open('INPUT/ALL/'+region_name+ '_all.txt','r')

sentence_list=[]

for line in file:
	line=line.split('<||>')
	if len(line)!=2:
		continue
	sentence_list.append(tweet_preprocess2(line[1]).lower())


stopset=set(stop_words)

qtexts=[[word for word in document.split() if word not in stopset ] for document in sentence_list]

print("Texts built")

starttime=time.time()

word_vec_model=gensim.models.Word2Vec(qtexts,size=2000,window=5,workers=2,alpha=0.05)
word_vec_model.save('WordVec/local_'+region_name+'_w2vec_model')

print(time.time()- starttime)
## xmeans
## louvian

'''
dictionary=corpora.Dictionary(qtexts)
print(1)
dictionary.save('WordVec/local_'+region_name+'_dictionary.dict')
print(2)
corpus=[dictionary.doc2bow(text) for text in qtexts]
print(3)
corpora.MmCorpus.serialize('WordVec/local_'+region_name+'_corpus.mm',corpus)
print(4)
tfidf_model = models.TfidfModel(corpus)
print(5)
corpus_tfidf = tfidf_model[corpus]
print(6)
print(time.time()-starttime)
'''