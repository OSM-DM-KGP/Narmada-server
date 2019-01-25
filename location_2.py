import json
import os 
import time
import csv
import io
import pickle
import subprocess
import sys
from datetime import date
import datetime
import emoji
import re
from nltk.tokenize import TweetTokenizer
from collections import defaultdict
import pickle
import stop_words
from nltk.corpus import wordnet as wn
from itertools import product
from spacy.symbols import *
from nltk import Tree
import nltk
from nltk.stem import *
from nltk.stem import *
import spacy
import random
import wordsegment
import jellyfish
# from para_sentence import split_into_sentences
import networkx as nx
import geocoder

ps_stemmer=porter.PorterStemmer()

wordsegment.load()

dep_parse_dist=0
a=0
orth_dist=0

nlp=spacy.load('en')
tknzr=TweetTokenizer(strip_handles=True,reduce_len=True)
# import CMUTweetTagger

stop_words=stop_words.get_stop_words('en')
# stopwords=stopwords.words('english')

stop_words_2=['i','me','we','us','you','u','she','her','his','he','him','it','they','them','who','which','whom','whose','that','this','these','those','anyone','someone','some','all','most','himself','herself','myself','itself','hers','ours','yours','theirs','to','in','at','for','from','etc',' ',',']
stop_words.extend(stop_words_2)
stop_words.extend(['with', 'at', 'from', 'into', 'during', 'including', 'until', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'of', 'to', 'in', 'for', 'on', 'by', 'about', 'like', 'through', 'over', 'before', 'between', 'after', 'since', 'without', 'under', 'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'out', 'around', 'down', 'off', 'above', 'near', 'and', 'or', 'but', 'nor', 'so', 'for', 'yet', 'after', 'although', 'as', 'as', 'if', 'long', 'because', 'before', 'even', 'if', 'even though', 'once', 'since', 'so', 'that', 'though', 'till', 'unless', 'until', 'what', 'when', 'whenever', 'wherever', 'whether', 'while', 'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'yours', 'his', 'her', 'its', 'ours', 'their', 'few', 'many', 'little', 'much', 'many', 'lot', 'most', 'some', 'any', 'enough', 'all', 'both', 'half', 'either', 'neither', 'each', 'every', 'other', 'another', 'such', 'what', 'rather', 'quite'])
stop_words=list(set(stop_words))
stopword_file=open("DATA/Process_resources/stopword.txt",'r')
stop_words.extend([line.rstrip() for line in stopword_file])

need_word_file=open('DATA/Process_resources/need.txt','r')
need_offer_words=[]
for line in need_word_file:
	line=line.strip()
	need_offer_words.append(line)

offer_word_file=open('DATA/Process_resources/offer.txt','r')
for line in offer_word_file:
	line=line.strip()
	need_offer_words.append(line)

temp_stem_arr=[]	

remove_puncts="[\{\};,.[!@#$%^&*()_+=?/\'\"\]]"
apostrophe_file=open('DATA/Process_resources/apostrophe.txt')
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

count=0
# need_text=[]
# offer_text=[]
# location_list=[]
# id_need_list={}
# global_need_resource_list=[]
# id_offer_list=[]
# global_offer_resource_list=[]

web_url="http[s]?:[a-zA-Z._0-9/]+[a-zA-Z0-9]"
replacables="RT\s|-\s|\s-|#|@|[|}|]|{|(|)"
prop_name="([A-Z][a-z]+)"
num="([0-9]+)"
name="([A-Za-z]+)"
and_rate="([&][a][m][p][;])"
ellipses="([A-Za-z0-9]+[…])"
hashtags_2="([#][a-zA-z0-9]+[\s\n])"

# def camel_case_split(identifier):
#     matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
#     return [m.group(0) for m in matches]

entity_type_list=['NORP','ORG','GPE','PERSON']

def tweet_preprocess(text):
	#text=" ".join(tknzr.tokenize(text))
	text=re.sub(web_url,'',text)
	text=re.sub(mentions,'',text)
	text=re.sub(ellipses,'',text)
	text=re.sub(and_rate,'and',text)
	text=re.sub(str(num)+''+name,"\\1 \\2",text)
	text=re.sub(name+''+str(num),"\\1 \\2",text)
	text=re.sub(prop_name+''+prop_name,"\\1 \\2",text)
	return text.lstrip().rstrip()

def tweet_preprocess2(text,hashtag_list):
	# print(text,hashtag_list)
	# for i in hashtag_list:
	# 	text=text.replace(i,'')

	text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
	text = re.sub('http://', '', text)
	text = re.sub('https://', '', text)
	#print urls
	text = re.sub('@(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',text)
	text = re.sub('@', '',text)
	# text = re.sub(u"(\u2018|\u2019)", "'", text)
	# text = re.sub(u"(\u201d|\u201c)", "\"", text)
	# text = re.sub(u"(\xb0|\xba|\u02da)", "", text)

	# text = re.sub('#(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',text)
	# text=re.sub(web_url,'',text)
	# text=re.sub(mentions,'',text)
	#text=re.sub(ellipses,'',text)	
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
	# text =" ".join(re.sub('(?!^)([A-Z][a-z]+)', r' \1', text).split())

	# print(text)
	return text.strip()	


common_words= ['understandings', 'understanding', 'conversations', 'disappearing', 'informations', 'grandmothers', 'grandfathers', 'questionings', 'conversation', 'information', 'approaching', 'understands', 'immediately', 'positioning', 'questioning', 'grandmother', 'travellings', 'questioners', 'recognizing', 'recognizers', 'televisions', 'remembering', 'rememberers', 'expressions', 'discovering', 'disappeared', 'interesting', 'grandfather', 'straightest', 'controllers', 'controlling', 'considering', 'remembered', 'cigarettes', 'companying', 'completely', 'spreadings', 'considered', 'continuing', 'controlled', 'stationing', 'controller', 'straighter', 'stretching', 'businesses', 'somebodies', 'soldiering', 'countering', 'darknesses', 'situations', 'directions', 'disappears', 'younglings', 'suggesting', 'afternoons', 'breathings', 'distancing', 'screenings', 'schoolings', 'especially', 'everything', 'everywhere', 'explaining', 'explainers', 'expression', 'branchings', 'revealings', 'repeatings', 'surprising', 'rememberer', 'somewheres', 'television', 'themselves', 'recognizer', 'recognizes', 'recognized', 'belongings', 'finishings', 'travelling', 'questioner', 'beginnings', 'travelings', 'questioned', 'followings', 'pretending', 'forgetting', 'forgetters', 'forwarding', 'positioned', 'travellers', 'gatherings', 'perfecting', 'understand', 'understood', 'weightings', 'approaches', 'officering', 'numberings', 'happenings', 'mentioning', 'letterings', 'husbanding', 'imaginings', 'approached', 'apartments', 'whispering', 'interested', 'discovered', 'spinnings', 'clearings', 'climbings', 'spendings', 'clothings', 'colorings', 'soundings', 'truckings', 'somewhere', 'troubling', 'companies', 'companied', 'beautiful', 'computers', 'confusing', 'considers', 'travelers', 'youngling', 'continues', 'continued', 'traveller', 'traveling', 'yellowing', 'apartment', 'beginning', 'wheelings', 'travelled', 'sometimes', 'something', 'appearing', 'cornering', 'believing', 'countered', 'believers', 'countries', 'soldiered', 'coverings', 'creatures', 'crossings', 'accepting', 'daughters', 'belonging', 'situation', 'silvering', 'different', 'silencing', 'touchings', 'bettering', 'tomorrows', 'disappear', 'thinkings', 'boardings', 'discovers', 'admitting', 'wrappings', 'distances', 'distanced', 'sightings', 'shrugging', 'doctoring', 'showering', 'shoulders', 'shoppings', 'shootings', 'dressings', 'sheetings', 'shadowing', 'settlings', 'servicing', 'seriously', 'seconding', 'searching', 'weighting', 'screening', 'screaming', 'schooling', 'teachings', 'bothering', 'everybody', 'botherers', 'bottoming', 'excepting', 'expecting', 'explained', 'direction', 'explainer', 'surprised', 'surprises', 'waterings', 'branching', 'revealing', 'returning', 'surfacing', 'familiars', 'repeating', 'fathering', 'reminding', 'supposing', 'breasting', 'attacking', 'remembers', 'breathing', 'remaining', 'breathers', 'brightest', 'brownings', 'suggested', 'recognize', 'fightings', 'attention', 'figurings', 'receiving', 'reasoning', 'realizing', 'fingering', 'buildings', 'finishing', 'stupidest', 'stuffings', 'questions', 'watchings', 'flashings', 'strongest', 'strikings', 'flighting', 'flowering', 'promisers', 'promising', 'following', 'bathrooms', 'prettiest', 'pretended', 'stretched', 'foreheads', 'foresting', 'stretches', 'forgotten', 'pressings', 'forgetter', 'strangest', 'preparing', 'forwarded', 'strangers', 'possibles', 'positions', 'afternoon', 'straights', 'pocketing', 'gardening', 'pleasings', 'wondering', 'gathering', 'picturing', 'personals', 'perfected', 'stomaches', 'stomached', 'carefully', 'stationed', 'catchings', 'parenting', 'paintings', 'orderings', 'groupings', 'wintering', 'officered', 'offerings', 'centering', 'numbering', 'neighbors', 'certainly', 'happening', 'narrowing', 'narrowest', 'mountains', 'mothering', 'mirroring', 'middlings', 'messaging', 'standings', 'mentioned', 'mattering', 'marriages', 'histories', 'machining', 'hospitals', 'listening', 'lightings', 'springing', 'lettering', 'husbanded', 'spreaders', 'whispered', 'imagining', 'imaginers', 'spreading', 'important', 'languages', 'answering', 'cigarette', 'interests', 'spiriting', 'cleanings', 'knockings', 'soundest', 'coatings', 'sounders', 'sounding', 'colleges', 'coloring', 'colorful', "wouldn't", 'training', 'colorers', 'sorriest', 'worrying', 'belonged', 'approach', 'tracking', 'touchers', 'touching', 'computer', 'whatever', 'toppings', 'confused', 'confuses', 'workings', 'consider', 'bettered', 'teething', 'tonights', 'tonguers', 'tonguing', 'continue', 'arriving', 'tomorrow', 'controls', 'together', 'blacking', 'blackest', 'throwers', 'blocking', 'throwing', 'coolings', 'someones', 'blockers', 'somebody', 'thirties', 'soldiers', 'cornered', 'weighted', 'counting', 'thoughts', 'counters', 'thinking', 'thinners', 'thinning', 'coursing', 'covering', 'thinnest', 'craziest', 'snapping', 'creating', 'creature', 'thickest', 'boarding', 'crossing', 'smokings', 'crowding', 'smelling', 'smallest', 'cuttings', 'slipping', 'slightly', 'dancings', 'sleepers', 'sleeping', 'slamming', 'wordings', 'darkness', 'daughter', 'boatings', 'skinning', 'weddings', 'thanking', 'sittings', 'deciding', 'deciders', 'singling', 'singings', 'despites', 'simplest', 'terrible', 'silvered', 'tellings', 'wearings', 'youngest', 'watering', 'silences', 'teachers', 'bookings', 'agreeing', 'teaching', 'discover', 'attacked', 'bothered', 'botherer', 'watching', 'swingers', 'bottling', 'distance', 'silenced', 'signings', 'bottomed', 'sighting', 'shutting', 'shrugged', 'wondered', 'swinging', 'doctored', 'sweetest', 'showered', 'showings', 'doorways', 'shouting', 'shoulder', 'wronging', 'shortest', 'surprise', 'dragging', 'shopping', 'shooters', 'drawings', 'actually', 'shooting', 'dreaming', 'dressing', 'avoiding', 'shitting', 'shirting', 'shipping', 'drinking', 'drinkers', 'braining', 'sheeting', 'sharpest', 'drivings', 'sharpers', 'dropping', 'droppers', 'shadowed', 'surfaced', 'settling', 'washings', 'settings', 'services', 'serviced', 'earliest', 'backings', 'earthing', 'servings', 'branches', 'branched', 'seconded', 'seatings', 'surfaces', 'searched', 'searches', 'walkings', 'screened', 'waitings', 'screamed', 'supposed', 'emptiest', 'emptying', 'breaking', 'breakers', 'schooled', 'enjoying', 'enjoyers', 'entering', 'runnings', 'breasted', 'rounders', 'rounding', 'supposes', 'everyone', 'visitors', 'visiting', 'breathed', 'excepted', 'roofings', 'exciting', 'breathes', 'expected', 'rollings', 'bankings', 'breather', 'explains', 'villages', 'bridging', 'viewings', 'brighter', 'ringings', 'righting', 'suitings', 'bringing', 'revealed', 'bringers', 'returned', 'failings', 'repliers', 'replying', 'repeated', 'brothers', 'familiar', 'wintered', 'families', 'suggests', 'farthest', 'furthest', 'browning', 'fathered', 'removing', 'building', 'reminded', 'bathroom', 'allowing', 'suddenly', 'remember', 'allowers', 'feedings', 'builders', 'burnings', 'feelings', 'remained', 'refusing', 'stupider', 'windings', 'although', 'stuffing', 'studying', 'business', 'angriest', 'fighting', 'fighters', 'students', 'figuring', 'received', 'twenties', 'receives', 'fillings', 'reasoned', 'findings', 'stronger', 'turnings', 'realizes', 'realized', 'readiest', 'fingered', 'readying', 'striking', 'trusters', 'finishes', 'trusting', 'finished', 'readings', 'reachers', 'reaching', 'quieters', 'quietest', 'quieting', 'fittings', 'quickest', 'writings', 'beaching', 'question', 'trucking', 'callings', 'stranger', 'flashing', 'beatings', 'answered', 'flattest', 'flatting', 'flighted', 'straight', 'troubled', 'flowered', 'pullings', 'storming', 'promiser', "couldn't", 'promised', 'promises', 'couldn’t', 'followed', 'stoppers', 'problems', 'probably', 'prettier', 'stopping', 'pretends', 'stomachs', 'troubles', 'pressers', 'tripping', 'forehead', 'stickers', 'forested', 'pressing', 'whispers', 'carrying', 'sticking', 'carriers', 'stepping', 'stealers', 'forwards', 'stealing', 'becoming', 'prepares', 'prepared', 'powering', 'freeings', 'stations', 'possible', 'position', 'freshest', 'beddings', 'wrapping', 'fronting', 'catching', 'fuckings', 'policing', 'funniest', 'pointers', 'pointing', 'catchers', 'pocketed', 'gardened', 'starters', 'ceilings', 'pleasing', 'gathered', 'starting', 'centered', 'platings', 'plastics', 'planning', 'pictured', 'pictures', 'traveler', 'pickings', 'personal', 'glancing', 'yourself', 'chancing', 'perfects', 'changing', 'peopling', 'partying', 'partings', 'parented', 'grabbing', 'grabbers', 'changers', 'checking', 'starring', 'bedrooms', 'checkers', 'pairings', 'standing', 'painting', 'outsides', 'greatest', 'cheeking', 'greening', 'greenest', 'grouping', 'ordering', 'anything', 'openings', 'guarding', 'wheeling', 'officers', 'guessing', 'spreader', 'offering', 'children', 'anywhere', 'numbered', 'choicest', 'noticers', 'noticing', 'hallways', 'nothings', 'hangings', 'nobodies', 'admitted', 'neighbor', 'choosing', 'choosers', 'happened', 'neckings', 'happiest', 'narrowed', 'narrower', 'spotting', 'churches', 'mouthing', 'traveled', 'mountain', 'mothered', 'accepted', 'mornings', 'mirrored', 'headings', 'spirited', 'hearings', 'heatings', 'circling', 'middling', 'messaged', 'messages', 'heaviest', 'wouldn’t', 'spinners', 'mentions', 'helpings', 'cleanest', 'memories', 'meetings', 'meanings', 'appeared', 'mattered', 'marrieds', 'marrying', 'marriage', 'yellowed', 'markings', 'cleaning', 'managing', 'cleaners', 'holdings', 'machined', 'machines', 'lunching', 'luckiest', 'lowering', 'longings', 'clearest', 'hospital', 'lockings', 'littlest', 'clearing', 'listened', 'housings', 'lightest', 'lighting', 'lighters', 'spinning', 'hundreds', 'hurrying', 'believes', 'spenders', 'believed', 'climbing', 'husbands', 'lettered', 'lettings', 'learning', 'leadings', 'ignoring', 'laughing', 'ignorers', 'imagines', 'yellower', 'imagined', 'climbers', 'imaginer', 'spending', 'closings', 'specials', 'speakers', 'language', 'believer', 'clothing', 'clouding', 'speaking', 'interest', 'spacings', 'landings', 'knowings', 'southest', 'jacketed', 'knocking', 'kitchens', 'kissings', 'killings', 'keepings', 'dresses', 'biggest', 'sticker', 'careful', 'shirted', 'warmers', 'shipped', 'birding', 'drinker', 'carries', 'sheeted', 'warming', 'carried', 'carrier', 'driving', 'sharper', 'tonight', 'drivers', 'casings', 'sharers', 'sharing', 'stepped', 'dropped', 'dropper', 'whisper', 'shapers', 'shaping', 'shakers', 'shaking', 'tonguer', 'shadows', 'stealer', 'several', 'tongued', 'staying', 'settles', 'settled', 'dusting', 'setting', 'tongues', 'catting', 'backing', 'catches', 'earlier', 'warmest', 'earthed', 'service', 'serving', 'warring', 'wanters', 'catcher', 'serious', 'eastest', 'sensing', 'senders', 'easiest', 'sending', 'sellers', 'selling', 'seeming', 'seeings', 'tiniest', 'seconds', 'station', 'causing', 'seating', 'edgings', 'stating', 'timings', 'efforts', 'starter', 'causers', 'screens', 'blacker', 'ceiling', 'screams', 'centers', 'wanting', 'walling', 'walkers', 'certain', 'emptied', 'empties', 'emptier', 'thrower', 'endings', 'started', 'schools', 'scarers', 'scaring', 'sayings', 'engines', 'savings', 'sanding', 'enjoyed', 'starers', 'saddest', 'enjoyer', 'staring', 'enoughs', 'rushing', 'bagging', 'runners', 'entered', 'running', 'chances', 'entires', 'chancer', 'rubbing', 'rowings', 'rounder', 'chanced', 'rounded', 'starred', 'rooming', 'changed', 'changes', 'blocked', 'angrier', 'exactly', 'changer', 'blocker', 'excepts', 'checked', 'excited', 'walking', 'excites', 'roofing', 'through', 'expects', 'blooded', 'checker', 'cheeked', 'throats', 'explain', 'wakings', 'springs', 'thought', 'waiting', 'blowing', 'rolling', 'rocking', 'risings', 'ringing', 'baggers', 'animals', 'righter', 'righted', 'ridings', 'richest', 'facings', 'reveals', 'blowers', 'choicer', 'choices', 'returns', 'voicing', 'worries', 'resting', 'chooses', 'failing', 'spreads', 'replier', 'failers', 'falling', 'spotted', 'replies', 'replied', 'chooser', 'thinned', 'fallers', 'thinner', 'balling', 'boarded', 'repeats', 'visitor', 'farther', 'further', 'circles', 'another', 'removed', 'fastest', 'removes', 'fathers', 'thicker', 'circled', 'visited', 'reminds', 'fearing', 'spirits', 'classes', 'answers', 'banking', 'boating', 'cleaned', 'feeding', 'spinner', 'thanked', 'village', 'worried', 'feeling', 'cleaner', 'remains', 'cleared', 'refuses', 'refused', 'workers', 'reddest', 'telling', 'yellows', 'spender', 'working', 'clearer', 'clearly', 'climbed', 'tearing', 'fighter', 'teaming', 'figured', 'figures', 'booking', 'viewing', 'climber', 'usually', 'closest', 'receive', 'filling', 'teacher', 'reasons', 'closing', 'finally', 'closers', 'anybody', 'finding', 'anymore', 'realize', 'special', 'finders', 'booting', 'realest', 'clothed', 'readier', 'readies', 'readied', 'fingers', 'teaches', 'tallest', 'clothes', 'speaker', 'readers', 'talkers', 'clouded', 'talking', 'reading', 'firings', 'spacing', 'takings', 'reacher', 'reached', 'coating', 'reaches', 'raising', 'raining', 'fishing', 'quietly', 'fittest', 'fitting', 'systems', 'whether', 'bothers', 'wrapped', 'fitters', 'quieted', 'quieter', 'quickly', 'coffees', 'quicker', 'fixings', 'coldest', 'sounded', 'sounder', 'actings', 'anyways', 'college', 'flashed', 'flashes', 'bottles', 'flatter', 'flatted', 'colored', 'bottled', 'wording', 'turning', 'sorting', 'flights', 'colorer', 'putting', 'pushers', 'pushing', 'flowers', 'pullers', 'swinger', 'wonders', 'sorrier', 'pulling', 'proving', 'comings', 'bottoms', 'promise', 'truster', 'boxings', 'company', 'follows', 'younger', 'trusted', 'sweeter', 'yelling', 'problem', 'without', 'beached', 'footing', 'confuse', 'beaches', 'brained', 'bearing', 'pretend', 'trucked', 'forcing', 'presser', 'wishing', 'trouble', 'forests', 'appears', 'beating', 'airings', 'forever', 'surface', 'control', 'forgets', 'accepts', 'pressed', 'wronged', 'winters', 'forming', 'presses', 'prepare', 'beaters', 'breaker', 'wheeled', 'because', 'forward', 'coolers', 'cooling', 'allowed', 'powered', 'pourers', 'freeing', 'pouring', 'tripped', 'coolest', 'breasts', 'someone', 'fresher', 'suppose', 'somehow', 'friends', 'breaths', 'copping', 'fronted', 'becomes', 'porches', 'poppers', 'popping', 'poorest', 'treeing', 'fucking', 'fullest', 'pooling', 'breathe', 'polices', 'funnier', 'funnies', 'policed', 'bedding', 'corners', 'futures', 'pointer', 'pointed', 'gamings', 'counted', 'soldier', 'pockets', 'wetting', 'pleased', 'gardens', 'wetters', 'wettest', 'pleases', 'counter', 'sunning', 'players', 'westest', 'country', 'gathers', 'bridges', 'playing', 'plating', 'bridged', 'plastic', 'couples', 'softest', 'getting', 'planned', 'getters', 'placing', 'gifting', 'pinking', 'pilings', 'piecing', 'picture', 'coursed', 'courses', 'summers', 'picking', 'snowing', 'phoning', 'bedroom', 'glances', 'glanced', 'winging', 'snapped', 'glassed', 'glasses', 'perhaps', 'covered', 'crazies', 'crazier', 'perfect', 'peopled', 'persons', 'peoples', 'suiting', 'pausing', 'passing', 'goldest', 'partied', 'windows', 'parties', 'parting', 'creates', 'grabbed', 'smokers', 'created', 'grabber', 'brought', 'weights', 'bringer', 'arrives', 'crosser', 'crosses', 'grasses', 'parents', 'palming', 'graying', 'pairing', 'crossed', 'painted', 'arrived', 'greying', 'smoking', 'paining', 'outside', 'brother', 'greater', 'smilers', 'outings', 'greened', 'greener', 'crowded', 'travels', 'smiling', 'ordered', 'grounds', 'offings', 'smelled', 'openers', 'browner', 'grouped', 'opening', 'smaller', 'growing', 'okaying', 'officer', 'guarded', 'slowest', 'slowing', 'cupping', 'slipped', 'guessed', 'guesses', 'cutting', 'offices', 'gunning', 'offered', 'browned', 'allower', 'nursing', 'numbing', 'suggest', 'cutters', 'numbers', 'sliders', 'halving', 'sliding', 'noticer', 'wedding', 'notices', 'noticed', 'nothing', 'writers', 'hallway', 'handing', 'sleeper', 'normals', 'noising', 'hanging', 'nodding', 'dancing', 'wearing', 'writing', 'slammed', 'hangers', 'darkest', 'skinned', 'happens', 'trained', 'needing', 'builder', 'beliefs', 'happier', 'necking', 'nearest', 'hardest', 'nearing', 'burning', 'believe', 'winding', 'hatting', 'narrows', 'stupids', 'sitting', 'mouthed', 'deadest', 'watered', 'sisters', 'mothers', 'singled', 'winning', 'morning', 'mooning', 'moments', 'heading', 'missing', 'decides', 'decided', 'decider', 'mirrors', 'minutes', 'hearing', 'minings', 'already', 'minding', 'middled', 'heating', 'burners', 'singles', 'middles', 'deepest', 'stuffed', 'heaters', 'singing', 'simpler', 'heavier', 'heavies', 'belongs', 'message', 'despite', 'mention', 'simples', 'studies', 'studied', 'silvers', 'helping', 'helpers', 'members', 'meeting', 'willing', 'meanest', 'attacks', 'herself', 'meaning', 'dinners', 'student', 'hidings', 'matters', 'marries', 'married', 'busying', 'busiest', 'silence', 'against', 'highest', 'wildest', 'hilling', 'marking', 'mapping', 'manages', 'managed', 'himself', 'history', 'tracked', 'strikes', 'manning', 'hitting', 'makings', 'hitters', 'whiting', 'towards', 'watched', 'holding', 'toucher', 'machine', 'holders', 'lunches', 'lunched', 'watches', 'luckier', 'stretch', 'streets', 'lowered', 'loudest', 'lookers', 'looking', 'longing', 'calling', 'longest', 'locking', 'bending', 'washing', 'signing', 'hottest', 'littler', 'benders', 'strange', 'sighted', 'listens', 'linings', 'likings', 'housing', 'beneath', 'sighing', 'sicking', 'however', 'lighted', 'sickest', 'lighter', 'calming', 'lifters', 'hundred', 'calmest', 'hurried', 'hurries', 'lifting', 'touched', "doesn't", 'doesn’t', 'hurting', 'touches', 'showers', 'husband', 'doctors', 'letters', 'cameras', 'letting', 'tossing', 'leaving', 'learned', 'dogging', 'leaning', 'leafing', 'leaders', 'leading', 'whitest', 'layered', 'ignored', 'showing', 'ignores', 'stories', 'ignorer', 'shoving', 'laughed', 'lasting', 'largest', 'imaging', 'doorway', 'besting', 'imagine', 'shouted', 'stormed', 'downing', 'storing', 'topping', 'avoided', 'dragged', 'shorter', 'betters', 'stopper', 'landers', 'insides', 'instead', 'written', 'drawing', 'shopped', 'stopped', 'between', 'landing', 'shooter', 'knowing', 'jackets', 'dreamed', 'carding', 'toothed', 'knocked', 'knifing', 'kitchen', 'joining', 'teethed', 'stomach', 'joiners', 'kissing', 'kindest', 'killers', 'killing', 'shoeing', 'kidding', 'jumping', 'kickers', 'kicking', 'jumpers', 'keepers', 'dressed', 'keeping', 'enough', 'checks', 'kicked', 'jumper', 'kicker', 'kidded', 'jumped', 'killed', 'joking', 'killer', 'kinder', 'joiner', 'kisses', 'kissed', 'joined', 'knives', 'knifes', 'knifed', 'jacket', 'knocks', 'itself', 'ladies', 'landed', 'lander', 'inside', 'larger', 'images', 'lasted', 'imaged', 'laughs', 'ignore', 'aboves', 'laying', 'accept', 'layers', 'across', 'yellow', 'leaded', 'leader', 'leaved', 'leaned', 'learns', 'leaves', 'yelled', 'lesser', 'letter', 'living', 'lifted', 'lifter', 'humans', 'hugest', 'lights', 'wrongs', 'houses', 'liking', 'likers', 'lining', 'housed', 'acting', 'listen', 'hotels', 'little', 'hotter', 'locals', 'locked', 'horses', 'longer', 'longed', 'looked', 'hoping', 'looker', 'losing', 'adding', 'louder', 'loving', 'lovers', 'lowing', 'lowest', 'writer', 'lowers', 'homing', 'holing', 'holder', 'making', 'hitter', 'makers', 'manned', 'manage', 'writes', 'admits', 'mapped', 'marked', 'hilled', 'higher', 'afraid', 'hiding', 'hidden', 'matter', 'ageing', 'helper', 'member', 'helped', 'memory', 'hellos', 'heater', 'metals', 'middle', 'heated', 'mights', 'minded', 'hearts', 'mining', 'minute', 'headed', 'mirror', 'misses', 'missed', 'moment', 'moneys', 'monies', 'months', 'mooned', 'mostly', 'having', 'mother', 'worlds', 'hating', 'mouths', 'moving', 'movers', 'movies', 'musics', 'worker', 'myself', 'naming', 'namers', 'narrow', 'hatted', 'hardly', 'nearer', 'neared', 'nearly', 'harder', 'necked', 'needed', 'happen', 'hanger', 'newest', 'nicest', 'nights', 'worked', 'nobody', 'nodded', 'handed', 'noises', 'noised', 'worded', 'normal', 'norths', 'nosing', 'agrees', 'noting', 'notice', 'halves', 'halved', 'number', 'guying', 'numbed', 'nurses', 'nursed', 'agreed', 'wooden', 'offing', 'gunned', 'offers', 'office', 'guards', 'wonder', 'okayed', "okay'd", 'okay’d', "ok'ing", 'ok’ing', 'oldest', 'womens', 'opened', 'opener', 'groups', 'womans', 'within', 'ground', 'orders', 'others', 'outing', 'wished', 'greens', 'greats', 'owning', 'wishes', 'owners', 'paging', 'pained', 'paints', 'greyed', 'greyer', 'paired', 'palest', 'grayed', 'palmed', 'papers', 'grayer', 'parent', 'parted', 'passed', 'golder', 'passes', 'pauses', 'paused', 'paying', 'person', 'people', 'wipers', 'goings', 'glance', 'phones', 'phoned', 'photos', 'picked', 'giving', 'givens', 'pieces', 'pieced', 'piling', 'gifted', 'pinked', 'pinker', 'places', 'placed', 'getter', 'gotten', 'plated', 'plates', 'gently', 'played', 'gather', 'player', 'please', 'gating', 'garden', 'pocket', 'gamers', 'points', 'pointy', 'gaming', 'future', 'wiping', 'fuller', 'police', 'pooled', 'poorer', 'fucked', 'popped', 'popper', 'fronts', 'friend', 'freers', 'poured', 'pourer', 'freest', 'powers', 'formed', 'forget', 'forgot', 'forest', 'forces', 'forced', 'footed', 'pretty', 'follow', 'fliers', 'flyers', 'proven', 'airing', 'proves', 'proved', 'prover', 'pulled', 'flying', 'puller', 'flower', 'pushes', 'pushed', 'floors', 'pusher', 'flight', 'fixers', 'fixing', 'quicks', 'winter', 'fitted', 'quiets', 'fitter', 'winged', 'radios', 'rained', 'raises', 'raised', 'fishes', 'rather', 'fished', 'firsts', 'firing', 'reader', 'finish', 'finger', 'fining', 'finest', 'realer', 'finder', 'really', 'finals', 'reason', 'filled', 'figure', 'fought', 'fights', 'fields', 'fewest', 'redder', 'refuse', 'remain', 'feeing', 'remind', 'feared', 'father', 'faster', 'remove', 'repeat', 'family', 'faller', 'fallen', 'failer', 'failed', 'rested', 'fading', 'return', 'reveal', 'riches', 'richer', 'riding', 'ridden', 'window', 'riders', 'rights', 'facing', 'allows', 'ringed', 'rising', 'rivers', 'extras', 'rocked', 'rolled', 'expect', 'roofed', 'excite', 'except', 'rooves', 'roomed', 'events', 'rounds', 'rowing', 'evened', 'rubbed', 'almost', 'entire', 'runner', 'enters', 'keying', 'rushed', 'rushes', 'sadder', 'safest', 'sanded', 'enjoys', 'saving', 'engine', 'savers', 'winded', 'saying', 'enders', 'scared', 'scares', 'scarer', 'scenes', 'ending', 'school', 'scream', 'either', 'eights', 'screen', 'egging', 'effort', 'search', 'edging', 'seated', 'second', 'eaters', 'seeing', 'seemed', 'eating', 'seller', 'sender', 'senses', 'sensed', 'easier', 'easily', 'earths', 'serves', 'served', 'willed', 'dusted', 'settle', 'during', 'driers', 'sevens', 'sexing', 'shadow', 'shakes', 'shaken', 'dryers', 'shaker', 'always', 'shaped', 'driest', 'shapes', 'shaper', 'drying', 'shares', 'shared', 'sharer', 'sharps', 'driver', 'drives', 'driven', 'sheets', 'droves', 'drinks', 'shirts', 'drunks', 'shoots', 'dreams', 'shorts', 'dozens', 'should', 'downed', 'shouts', 'shoved', 'shoves', 'showed', 'wilder', 'shower', 'dogged', 'doctor', 'shrugs', 'didn’t', 'sicker', 'sicked', "didn't", 'siding', 'sighed', 'doings', 'sights', 'signed', 'dinner', 'silent', 'silver', 'dyings', 'widest', 'simple', 'simply', 'deeper', 'single', 'decide', 'deaths', 'sister', 'deader', 'sizing', 'darker', 'wholes', 'sleeps', 'dances', 'danced', 'slides', 'slider', 'cutter', 'slower', 'slowed', 'slowly', 'smalls', 'cupped', 'smells', 'smelly', 'crying', 'smiles', 'smiled', 'smiler', 'crowds', 'smokes', 'smoked', 'smoker', 'create', 'covers', 'snowed', 'whited', 'softer', 'course', 'softly', 'couple', 'counts', 'corner', 'whiter', 'copped', 'cooled', 'cooler', 'coming', 'whites', 'sorted', 'colors', 'colder', 'sounds', 'coffee', 'coated', 'spaces', 'clouds', 'spaced', 'spoken', 'speaks', 'clothe', 'closed', 'closes', 'closer', 'spends', 'climbs', 'clears', 'cleans', 'spirit', 'cities', 'circle', 'church', 'choose', 'spread', 'chosen', 'choice', 'chests', 'sprung', 'spring', 'sprang', 'stages', 'stairs', 'cheeks', 'stands', 'keeper', 'change', 'chance', 'stared', 'stares', 'starer', 'chairs', 'starts', 'center', 'causer', 'caused', 'states', 'stated', 'causes', 'caught', 'catted', 'stayed', 'steals', 'stolen', 'casing', 'sticks', 'caring', 'carded', 'stones', 'animal', 'cannot', 'stored', 'stores', 'storms', 'answer', 'camera', 'calmer', 'calmed', 'called', 'street', 'buyers', 'bought', 'strike', 'struck', 'buying', 'anyone', 'strong', 'busier', 'busied', 'busing', 'burner', 'stuffs', 'burned', 'stupid', 'builds', 'browns', 'suites', 'suited', 'brings', 'summer', 'bright', 'sunned', 'bridge', 'breath', 'breast', 'breaks', 'broken', 'surest', 'branch', 'brains', 'anyway', 'boxing', 'wheels', 'sweets', 'swings', 'bottom', 'bottle', 'system', 'bother', 'tables', 'taking', 'takers', 'talked', 'talker', 'boring', 'taller', 'booted', 'taught', 'booked', 'teamed', 'teared', 'boning', 'appear', 'bodies', 'thanks', 'boated', 'thicks', 'boards', 'bluest', 'things', 'thinks', 'blower', 'thirds', 'thirty', 'though', 'threes', 'throat', 'bloods', 'thrown', 'throws', 'blocks', 'timing', 'blacks', 'timers', 'tinier', 'biters', 'tiring', 'todays', 'biting', 'toning', 'tongue', 'arming', 'birded', 'bigger', 'wetter', 'toothy', 'beyond', 'better', 'topped', 'tossed', 'bested', 'tosses', 'beside', 'bender', 'toward', 'bended', 'tracks', 'belong', 'trains', 'belief', 'travel', 'behind', 'begins', 'before', 'bedded', 'became', 'become', 'beater', 'beaten', 'trucks', 'truest', 'aren’t', "aren't", 'trusts', 'truths', 'trying', 'turned', 'twenty', 'around', 'uncles', 'weight', 'wasn’t', "wasn't", 'arrive', 'unless', 'upping', 'wedded', 'viewed', 'barely', 'visits', 'banked', 'balled', 'voices', 'voiced', 'waited', 'bagger', 'waking', 'walked', 'bagged', 'walker', 'walled', 'asking', 'wanted', 'wanter', 'warred', 'waring', 'backed', 'warmed', 'warmer', 'babies', 'washed', 'washes', 'avoids', 'attack', 'waters', 'asleep', 'watery', 'waving', 'wavers', 'seems', 'party', 'minds', 'eaten', 'sells', 'sends', 'known', 'sense', 'hours', 'pasts', 'paths', 'easts', 'pause', 'mined', 'layer', 'payed', 'serve', 'earth', 'early', 'wills', 'aired', 'heard', 'hears', 'dusts', 'kills', 'goers', 'hotel', 'seven', 'dried', 'ideas', 'sexed', 'sexes', 'going', 'drier', 'dries', 'dryer', 'glass', 'heads', 'shake', 'leads', 'shook', 'aging', 'gives', 'phone', 'local', 'photo', 'shape', 'picks', 'above', 'locks', 'money', 'drops', 'share', 'given', 'wrong', 'girls', 'month', 'sharp', 'piece', 'wilds', 'sheet', 'drove', 'drive', 'moons', 'lands', 'piles', 'ships', 'drink', 'piled', 'drank', 'drunk', 'shirt', 'pinks', 'shits', 'dress', 'shoes', 'mores', 'shoot', 'longs', 'shots', 'dream', 'drawn', 'draws', 'drags', 'shops', 'haves', 'horse', 'short', 'gifts', 'dozen', 'place', 'downs', 'shout', 'hopes', 'shove', 'hoped', 'plans', 'wiper', 'doors', 'shown', 'shows', 'wiped', 'plate', 'world', 'mouth', 'doers', 'joins', 'shrug', 'shuts', 'leafs', 'moved', 'plays', 'moves', 'sicks', 'don’t', 'pleas', 'sided', 'sides', 'sighs', "don't", 'gated', 'sight', 'looks', 'gates', 'wives', 'mover', 'signs', 'doing', 'dirts', 'knees', 'movie', 'learn', 'gamer', 'games', 'gamed', 'dying', 'music', 'since', 'desks', 'sings', 'singe', 'deeps', 'point', 'acted', 'musts', 'yells', 'funny', 'death', 'wider', 'loses', 'sixes', 'whose', 'names', 'sizes', 'sized', 'skins', 'keyed', 'skies', 'pools', 'slams', 'darks', 'named', 'slept', 'namer', 'sleep', 'leave', 'dance', 'slide', 'hated', 'young', 'whole', 'fucks', 'who’s', 'slips', "who's", 'slows', 'front', 'porch', 'loved', 'hates', 'small', 'fresh', 'cries', 'cried', 'smell', 'white', 'nears', 'loves', 'smile', 'freer', 'pours', 'lover', 'freed', 'power', 'smoke', 'frees', 'yeses', 'crowd', 'cross', 'jokes', 'fours', 'snaps', 'crazy', 'forms', 'cover', 'homed', 'snows', 'among', 'necks', 'happy', 'least', 'press', 'force', 'homes', 'count', 'needs', 'wipes', 'years', 'cools', 'foots', 'joked', 'foods', 'never', 'songs', 'comes', 'sorry', 'flier', 'color', 'sorts', 'souls', 'lower', 'newer', 'flyer', 'colds', 'sound', 'flown', 'south', 'works', 'coats', 'space', 'nicer', 'prove', 'lucky', 'spoke', 'night', 'speak', 'cloud', 'hurts', 'yards', 'pulls', 'holed', 'flies', 'close', 'climb', 'spent', 'spend', 'words', 'holes', 'hangs', 'clear', 'lunch', 'spins', 'clean', 'class', 'liars', 'floor', 'holds', 'spots', 'alive', 'noise', 'flats', 'chose', 'flash', 'nones', 'child', 'fixer', 'fixed', 'fixes', 'chest', 'cheek', 'mains', 'stage', 'hands', 'makes', 'stair', 'quick', 'stood', 'check', 'fiver', 'stand', 'stars', 'fives', 'north', 'wrote', 'stare', 'lying', 'quiet', 'noses', 'quite', 'start', 'chair', 'nosed', 'radio', 'lived', 'rains', 'notes', 'state', 'large', 'cause', 'raise', 'catch', 'noted', 'maker', 'stays', 'halls', 'angry', 'stole', 'steal', 'reach', 'first', 'cased', 'cases', 'steps', 'lives', 'fires', 'stuck', 'carry', 'stick', 'cares', 'still', 'cared', 'fired', 'cards', 'added', 'stone', 'reads', 'halve', 'stops', 'write', 'can’t', 'ready', 'hairy', 'store', 'hairs', "can't", 'storm', 'numbs', 'story', 'could', 'finer', 'knife', 'fines', 'calms', 'fined', 'calls', 'hurry', 'while', 'buyer', 'finds', 'nurse', 'found', 'which', 'lifts', 'admit', 'final', 'fills', 'lasts', 'keeps', 'where', 'buses', 'bused', 'study', 'offed', 'stuff', 'fight', 'woods', 'burnt', 'burns', 'field', 'human', 'build', 'built', 'wings', 'offer', 'brown', 'allow', 'guyed', 'suite', 'suits', 'bring', 'marks', 'fewer', 'feels', 'hills', 'wines', 'later', 'feeds', 'agree', 'guess', 'surer', 'fears', 'broke', 'break', 'guard', 'brain', 'highs', 'often', 'marry', 'ahead', 'knock', 'boxes', 'sweet', 'boxed', 'okays', 'swing', 'swung', 'falls', 'reply', 'hides', 'fails', 'huger', 'table', 'takes', 'taken', 'laugh', 'taker', 'rests', 'house', 'talks', 'bored', 'women', 'faded', 'fades', 'wheel', 'facts', 'wraps', 'boots', 'teach', 'faces', 'teams', 'older', 'books', 'tears', 'bones', 'maybe', 'woman', 'faced', 'areas', 'boned', 'opens', 'tells', 'rides', 'grows', 'thank', 'their', 'boats', 'thens', 'there', 'these', 'thick', 'rider', 'after', 'board', 'right', 'bluer', 'thins', 'blues', 'blued', 'grown', 'thing', 'again', 'rings', 'think', 'blows', 'blown', 'third', 'would', 'means', 'those', 'risen', 'three', 'rises', 'blood', 'eying', 'heres', 'throw', 'block', 'threw', 'roses', 'group', 'river', 'black', 'tying', 'times', 'timed', 'roads', 'rocks', 'order', 'timer', 'meant', 'green', 'tired', 'tires', 'extra', 'meets', 'today', 'rolls', 'biter', 'bitey', 'other', 'toned', 'tones', 'light', 'bites', 'worry', 'birds', 'roofs', 'armed', 'outer', 'rooms', 'outed', 'every', 'tooth', 'teeth', 'round', 'image', 'bests', 'event', 'liked', 'evens', 'rowed', 'likes', 'touch', 'bends', 'windy', 'bents', 'towns', 'winds', 'great', 'below', 'track', 'overs', 'owned', 'liker', 'train', 'enter', 'wound', 'begun', 'helps', 'began', 'begin', 'owner', 'beers', 'kinds', 'wests', 'paged', 'trees', 'treed', 'tripe', 'trips', 'pages', 'alone', 'hello', 'beats', 'enjoy', 'bears', 'truck', 'beach', 'safer', 'trues', 'truer', 'trued', 'safes', 'hells', 'sames', 'trust', 'truth', 'pains', 'wells', 'sands', 'tried', 'tries', 'greys', 'turns', 'isn’t', "isn't", 'heavy', 'twice', 'saves', 'uncle', 'saved', 'under', 'kicks', 'saver', 'paint', 'lines', 'grays', 'until', 'weeks', 'upped', 'pairs', 'using', 'asked', 'usual', 'scare', 'being', 'ender', 'metal', 'views', 'paled', 'banks', 'visit', 'pales', 'paler', 'voice', 'scene', 'heats', 'waits', 'balls', 'ended', 'empty', 'woken', 'palms', 'wakes', 'waked', 'walks', 'lined', 'knows', 'pants', 'worse', 'paper', 'walls', 'worst', 'wants', 'eight', 'heart', 'along', 'backs', 'egged', 'jumps', 'warms', 'grass', 'might', 'edges', 'grabs', 'seats', 'avoid', 'parts', 'edged', 'aunts', 'watch', 'about', 'eater', 'won’t', 'water', "won't", 'waved', 'waves', 'goods', 'waver', 'golds', 'wears', 'ears', 'grab', 'fits', 'each', 'sets', 'knee', 'lots', 'part', 'dust', 'noes', 'fish', 'stay', 'good', 'rain', 'cats', 'work', 'wild', 'laid', 'hang', 'gold', 'pass', 'step', 'loud', 'case', 'help', 'your', 'past', 'nods', 'home', 'care', 'path', 'hell', 'read', 'love', 'fire', 'gods', 'lift', 'card', 'stop', 'pays', 'keys', 'cars', 'paid', 'idea', 'fine', 'none', 'real', 'into', 'drop', 'heat', 'wish', 'cans', 'kids', 'find', 'goer', 'goes', 'went', 'calm', 'just', 'lead', 'gone', 'call', 'fill', 'nose', 'ship', 'huge', 'acts', 'lows', 'buys', 'some', 'note', 'kind', 'shit', 'shat', 'mind', 'ices', 'busy', 'pick', 'hand', 'shod', 'shoe', 'gave', 'reds', 'shot', 'hall', 'fews', 'ours', 'feel', 'burn', 'drew', 'such', 'draw', 'shop', 'give', 'felt', 'wing', 'suit', 'drag', 'hear', 'feed', 'mine', 'girl', 'feds', 'iced', 'down', 'when', 'fees', 'half', 'suns', 'able', 'word', 'fear', 'nows', 'door', 'fast', 'sure', 'leaf', 'pile', 'jobs', 'show', 'wine', 'boys', 'dogs', 'yell', 'hair', 'guys', 'kept', 'doer', 'fall', 'fell', 'head', 'shut', 'gift', 'hole', 'rest', 'numb', 'kick', 'lean', 'take', 'both', 'sick', 'fail', 'fade', 'took', 'miss', 'side', 'sigh', 'held', 'talk', 'last', 'plan', 'bore', 'hold', 'done', 'tall', 'teas', 'fact', 'boot', 'like', 'wife', 'rich', 'sign', 'book', 'wood', 'team', 'does', 'main', 'offs', 'tear', 'tore', 'torn', 'rode', 'dirt', 'gets', 'bone', 'joke', 'ride', 'make', 'told', 'play', 'died', 'tell', 'dies', 'tens', 'area', 'body', 'than', 'boat', 'line', 'guns', 'desk', 'that', 'what', 'kiss', 'them', 'they', 'gate', 'sang', 'then', 'plea', 'kill', 'face', 'sing', 'sung', 'eyes', 'thin', 'blue', 'deep', 'made', 'rung', 'ring', 'sirs', 'wide', 'he’s', 'rang', 'moon', 'blow', 'eyed', 'sits', 'more', 'whys', 'dead', 'blew', 'days', 'this', 'left', 'grew', "he's", 'size', 'rise', 'rose', 'whom', 'have', 'skin', 'most', 'late', 'grow', 'slam', 'road', 'game', 'tied', 'ties', 'arms', 'time', 'dark', 'rock', 'okay', 'ages', 'mens', 'roll', 'mans', 'tiny', 'slid', 'dads', 'airs', "ok'd", 'tire', 'wets', 'ok’d', 'i’ll', 'roof', 'slip', 'full', 'cuts', 'pool', 'slow', 'tone', 'bite', 'lips', 'cups', 'bits', 'room', 'olds', 'poor', 'bird', 'adds', 'ever', 'knew', 'hate', 'fuck', 'pops', 'even', 'tops', 'wipe', 'hits', 'once', 'west', 'hour', 'rows', 'rubs', 'toss', 'best', 'ones', 'only', 'from', 'runs', 'bend', 'bent', 'onto', 'open', 'move', 'town', 'free', 'pour', 'legs', 'rush', 'jump', 'snap', 'many', 'hill', 'less', 'maps', 'snow', 'keep', 'safe', 'much', 'soft', 'join', 'beer', "i'll", 'beds', 'four', 'tree', 'same', 'sand', 'form', 'cops', 'must', 'year', 'cool', 'trip', 'lets', 'beat', 'mark', 'born', 'bear', 'with', 'come', 'save', 'know', 'true', 'sons', 'lock', 'song', 'soon', 'laws', 'came', 'outs', 'name', 'well', 'been', 'says', 'said', 'sort', 'feet', 'soul', 'high', 'yeah', 'were', 'hide', 'foot', 'turn', 'cold', 'wind', 'yard', 'twos', 'coat', 'food', 'over', 'hats', 'owns', 'ends', 'lady', 'aged', 'arts', 'else', 'long', 'flew', 'hurt', 'page', 'week', 'upon', 'lays', 'used', 'uses', 'hard', 'eggs', 'wins', 'very', 'mays', 'seas', 'pain', 'near', 'view', 'bars', 'weds', 'pull', 'edge', 'wrap', 'lies', 'bank', 'spin', 'ball', 'grey', 'seat', 'spun', 'lied', 'neck', 'push', 'wait', 'hope', 'bags', 'city', 'look', 'wake', 'spot', 'saws', 'woke', 'wear', 'pink', 'liar', 'eats', 'walk', 'need', 'sees', 'seen', 'puts', 'seem', 'wall', 'want', 'pair', 'gray', 'sell', 'will', 'flat', 'back', 'pale', 'sold', 'asks', 'wars', 'land', 'send', 'mean', 'warm', 'baby', 'sent', 'also', 'wash', 'away', 'here', 'easy', 'hung', 'sens', 'star', 'hers', 'aunt', 'palm', 'worn', 'life', 'meet', 'wore', 'east', 'live', 'news', 'five', 'wave', 'next', 'lost', 'lose', 'nice', 'ways', 'far', 'few', 'war', 'bad', 'bag', 'bar', 'wed', 'use', 'ups', 'art', 'was', 'two', 'try', 'are', 'bed', 'top', 'arm', 'wet', 'big', 'too', 'bit', 'tie', 'the', 'ten', 'tvs', 'tea', 'box', 'boy', 'sun', 'bus', 'but', 'buy', 'any', 'can', 'car', 'cat', 'and', 'son', 'cop', 'sos', 'cry', 'cup', 'cut', 'who', 'dad', 'sky', 'day', 'six', 'why', 'sit', 'sat', 'sir', 'die', 'did', 'dog', 'she', 'dry', 'sex', 'set', 'ear', 'ate', 'eat', 'see', 'saw', 'win', 'won', 'sea', 'egg', 'end', 'say', 'sad', 'ran', 'run', 'rub', 'row', 'eye', 'rid', 'ask', 'fed', 'fee', 'red', 'way', 'fit', 'fix', 'all', 'put', 'fly', 'for', 'pop', 'fun', 'get', 'got', 'god', 'pay', 'own', 'out', 'our', 'air', 'ors', 'one', 'old', 'ohs', 'gun', 'key', 'off', 'guy', 'now', 'not', 'nor', 'nod', 'nos', 'ago', 'new', 'hat', 'age', 'had', 'has', 'her', 'met', 'hey', 'may', 'hid', 'map', 'him', 'add', 'his', 'man', 'men', 'hit', 'mad', 'low', 'lot', 'hot', 'lip', 'how', 'lit', 'lie', 'kid', "i'm", 'let', 'i’m', 'leg', "i'd", 'i’d', 'ice', 'led', 'act', 'lay', 'law', 'ins', 'yes', 'yet', 'you', 'its', 'job', 'no', 'at', 'by', 'my', 'on', 'ha', 'do', 'ok', 'he', 'oh', 'is', 'tv', 'me', 'us', 'as', 'hi', 'go', 'if', 'of', 'am', 'up', 'to', 'we', 'so', 'in', 'or', 'it', 'be', 'an', 'i', 'a']

loc_preposition_list=['in','from','at','on','to','from','for','near', 'nearby']
dir_list=['north','south','east','west','upper','lower','greater','lesser','se','nw','ne','sw','northern','southern','eastern','western','new','old','north east', 'south west', 'south east', 'north west']
after_place_list=['building','house','road','rd','street','hospital','park','town','lake','city','village','college','school','bank','nagar','gram','kund','beach','railway','river','hill','district','river','island']
of_dir_list=['north','south','east','west','se','nw','ne','sw','north east','south east','north west','south west','northern','southern','eastern','western']
of_place_list=['village','town','city','region','outskirts']
of_people_list=['people','victims','survivors','president','PM','prime minister','CM','minister','doctor','soldier','volunteer','refugee','mayor']

verbs = {x.name().split('.', 1)[0] for x in wn.all_synsets('v')}
nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}


false_names=['malaria','twitter','city','name','park','city','town','the','ma','beach','',"",'"',"'",',','.',' ',';','?','!',' ']

# false_names.extend(list(nouns))
# false_names.extend(list(verbs))
# false_names.extend(common_words)
false_names.extend(stop_words)
false_names=set(false_names)

overall_location_dict={}

events_set={'hepatitis b', 'typhu', 'hepatitis ', 'yellow fev', 'rainfal', 'h1n1', 'limnic erupt', 'plagu', 'poliomyel', 'tornado', 'mening', 'ebola virus diseas', 'aid', 'malaria', 'dengu', 'cholera', 'landslid', 'sars coronaviru', 'leishmaniasi', 'flood', 'tsunami', 'cyclonic storm', 'dengue fev', 'japanese enceph', 'solar flar', 'avalanch', 'zika viru', 'measl', 'hurrican', 'ebola virus virion', 'polio', 'typhoon', 'influenza', 'zika', 'trypanosomiasi', 'storm', 'thunderstorm', 'earthquak', 'smallpox', 'middle east respiratory syndrom', 'hiv', 'wildfir', 'volcanic erupt', 'hand,foot and mouth diseas', 'mump', 'epidemic typhu', 'hand, foot and mouth diseas', 'chikungunya', 'drought', 'hailstorm', 'sinkhol', 'bubonic plagu', 'ebola', 'heat wav', 'blizzard', 'hepatitis e,', 'hepatitis a', 'relapsing fev'}
road_names_2={'vale', ' garden', 'avenue', 'place', 'asian highway', 'expressway', 'tunnel', 'ave', 'national highway', 'wharf', 'junction', 'state highway', 'cross', 'mead', 'lane', 'st', 'AH', 'square', 'bridge', 'NH', 'street', 'row', 'flyover', 'blvd', 'grove', 'dr', 'road', 'rise', 'parkway', 'drive', 'rd', 'mews', 'pl', 'ln', 'SH', 'highway', 'boulevard', 'Hw', 'way', 'underpass', 'lodge'}
building_names_2={'cafe','bank','office','water tower', 'metro', 'brewery', 'missile launch facility', 'city hall', 'parking lot', 'condominium', 'storage silo', 'market', 'shopping mall', 'archive', 'hairdressers', 'shrine', 'cinema', 'blockhouse', 'power plant', 'boathouse', 'garage', 'theater', 'arcade', 'concert hall', 'warehouse', 'barracks', 'citadel', 'pagoda', 'courthouse', 'prison', 'imambargah', 'museum', 'doctors office', 'foundry', 'embassy', 'mill', 'drugstore', 'college', 'house', 'elementary schools', 'parliament house', 'mandir', 'mosque', 'school', 'winery', 'makan', 'hangar', 'mihrab', 'monastery', 'consulate', 'villa', 'lighthouse', 'railway station', 'duplex', 'psychiatric hospital', 'bunker', 'pharmacy', 'orthodontist', 'masjid', 'arsenal', 'refinery', 'flat', 'chapel', 'forum', 'apartment', 'hospital', 'office', 'fire station', 'surau', 'martyrium', 'airport terminal', 'block', 'mithraeum', 'cathedral', 'duomo', 'temple', 'supermarket', 'parking garage', 'hall', 'dentist', 'car wash', 'oratory', 'mall', 'university', 'amphitheater', 'internet cafe', 'police station', 'townhouse', 'post office', 'synagogue', 'bus station', 'church', 'library', 'quarantine', 'shop', 'signal box', 'hotel', 'factory', 'meeting house', 'bungalow', 'convention center', 'art gallery', 'assembly', 'restaurant', 'orphanage', 'taxi station', 'nursing home', 'basilica', 'skyscraper', 'gurdwara', 'asylum', 'unit','dam','reservoir'}
landforms_2={'doab', 'islet', 'tower karst', 'hogback', 'glacial horn', 'thalweg', 'headland', 'mesa', 'lavaka', 'machair', 'stack', 'dune', 'lava dome', 'oxbow lake', 'mountain pass', 'submarine volcano', 'complex volcano', 'volcanic dam', 'horst', 'valley and vale', 'hillock', 'hill', 'wave-cut platform', 'complex crater', 'erg', 'stream', 'structural bench', 'lacustrine terrace', 'loess', 'natural arch', 'alluvial fan', 'flat landforms[edit]', 'scree', 'volcanic arc', 'cave', 'rock shelter', 'somma volcano', 'foiba', 'atoll', 'abîme', 'strike ridge', 'kame delta', 'malpais', 'shore', 'point bar', 'wadi', 'crevasse', 'diatreme', 'malpaís', 'lacustrine plain', 'polje', 'faceted spur', 'stream pool', 'salt pan (salt flat)', 'salt pan', 'moraine and ribbed moraines', 'gulch', 'stratocone', 'mountain range', 'submarine canyon', 'volcanic crater', 'plain', 'channel', 'parallel roads of glen roy', 'spatter cone', 'cove (mountain)', 'plateau', 'river island', 'proglacial lake', 'anabranch', 'ribbed moraines', 'gorge', 'outwash plain', 'estuary', 'abyssal fan', 'kipuka', 'tunnel valley', 'karst fenster', 'doline', 'earth hummocks', 'drainage divide', 'moulin', 'lacustrine terraces', 'terrace', 'side valley', 'turlough', 'strath', 'outwash fan', 'dreikanter', 'paleoplain', 'kettle', 'endorheic basin', 'honeycomb weathering', 'volcanic field', 'dike', 'playa lake', 'pyroclastic shield', 'drumlin field', 'inlet', 'strait', 'outwash fan and outwash plain', 'ejecta blanket', 'structural terrace', 'rock formations', 'peneplain', 'inselberg plain', 'shoal', 'sea cave', 'drainage basin', 'cryoplanation terrace', 'plunge pool', 'waterfall', 'paleosurface', 'riffle', 'bluff', 'volcanic island', 'beach ridge', 'lagoon', 'entrenched meander', 'towhead', 'defile', 'tepuy', 'barrier bar', 'panhole (weathering pit)', 'cenote', 'solifluction sheet', 'arroyo and (wash)', 'lake', 'rock-cut basin', 'impact crater', 'beach cusps', 'watershed', 'pit crater', 'tor', 'caldera', 'levee, natural', 'landforms', 'nunatak', 'dome', 'bar', 'island', 'tuff cone', 'tepui', 'planation surface', 'rock glacier', 'raised beach', 'dirt cone', 'guyot', 'roche moutonnée', 'nivation hollow', 'geyser', 'crater lake', 'volcanic group', 'karst', 'peninsula', 'u-shaped valley', 'drumlin and drumlin field', 'lava plain', 'hanging valley', 'geo', 'dry lake', 'marsh', 'etchplain', 'marine terrace', 'foibe', 'oceanic ridge', 'spit', 'quarry', 'oceanic plateau', 'mogote', 'oasis', 'truncated spur', 'monadnock', 'continental shelf', 'stratovolcano', 'tidal marsh', 'tuya', 'homoclinal ridge', 'confluence', 'gorge and canyon', 'archipelago', 'sinkhole', 'desert pavement', 'tessellated pavement', 'granite dome', 'cove', 'flatiron', 'yardang', 'trim line', 'cryptodome', 'yazoo stream', 'exhumed river channel', 'backswamp', 'mud volcano', 'sandhill', 'wave cut platform', 'ria', 'lava lake', 'panhole', 'epigenetic valley', 'glacier foreland', 'rapid', 'lava coulee', 'table', 'depressions[edit]', 'gully', 'esker', 'supervolcano', 'thermokarst', 'carolina bay', 'oceanic basin', 'permafrost plateau', 'dissected plateau', 'karst valley', 'salt marsh', 'cirque', 'ridge', 'pull-apart basin', 'crevasse splay', 'swamp', 'dune system', 'pingo', 'beach', 'calanque', 'lava flow', 'lava spine', 'volcanic plug', 'sand volcano', 'ait', 'volcano', 'coral reef', 'floodplain', 'draw', 'beach and raised beach', 'sandur', 'terracettes', 'flute', 'valley shoulder', 'badlands', 'cinder cone', 'flat (landform)', 'col', 'abyssal plain', 'ravine', 'seamount chains', 'barchan', 'pediment', 'glacier cave', 'ventifact', 'subglacial mound', 'pseudocrater', 'cut bank', 'bayou', 'river', 'tafoni', 'bench', 'ayre', 'surge channel', 'lava tube', 'glen', 'volcanic cone', 'bay', 'hornito', 'mamelon', 'flyggberg', 'pond', 'rift valley', 'natural levee', 'bornhardt', 'braided channel', 'cuesta', 'fault scarp', 'blowhole', 'fissure vent', 'dale', 'firth', 'delta, river', 'cuspate foreland', 'bight', 'coast', 'palsa', 'stump', 'dell', 'tea table', 'gulf', 'arête', 'summit', 'cape', 'mid-ocean ridge', 'fluvial terrace', 'escarpment (scarp)', 'arch', 'asymmetric valley', 'nubbin', 'butte', 'knoll', 'maar', 'interfluve', 'flat', 'tombolo', 'kame', 'spring', 'volcanic plateau', 'cryovolcano', 'oceanic trench', 'limestone pavement', 'glacier', 'uvala', 'lithalsa', 'fjord', 'graben', 'solifluction lobe', 'stack and stump', 'scowle', 'seamount', 'meander', 'cliff', 'moraine', 'mountain', 'canyon', 'vale', 'tide pool', 'shield volcano', 'potrero', 'flared slope', 'vent', 'river delta', 'shut-in', 'valley', 'inselberg', 'inverted relief', 'barrier island', 'sound', 'hoodoo', 'pediplain', 'isthmus', 'baymouth bar', 'fjard', 'strandflat', 'corrie or cwm', 'resurgent dome', 'fluvial island', 'blowout', 'drumlin'}
town_names_2={'city','town','nagar','place','district','village','gram'}
road_names={'mew', 'row', 'mead', 'flyover', 'junction', 'blvd', 'ln', 'vale', 'sh', 'hw', 'lodg', 'pl', 'highway', 'wharf', 'parkway', 'boulevard', 'garden', 'national highway', 'dr', 'state highway', 'drive', 'ah', 'avenu', 'lane', 'underpass', 'squar', 'road', 'tunnel', 'place', 'st', 'ave', 'nh', 'expressway', 'rise', 'grove', 'street', 'way', 'rd', 'asian highway', 'bridg', 'cross'}
building_names={'martyrium', 'univers', 'bungalow', 'asylum', 'oratori', 'mill', 'airport termin', 'psychiatric hospit', 'mithraeum', 'offic', 'police st', 'concert hal', 'signal box', 'hous', 'quarantin', 'shop', 'pharmaci', 'courthous', 'duplex', 'garag', 'pagoda', 'wineri', 'hospit', 'bunker', 'boathous', 'shrine', 'refineri', 'supermarket', 'gurdwara', 'nursing hom', 'cinema', 'missile launch facil', 'prison', 'chapel', 'elementary school', 'apart', 'masjid', 'power pl', 'mall', 'parliament hous', 'archiv', 'car wash', 'convention cent', 'citadel', 'dentist', 'surau', 'meeting hous', 'school', 'hall', 'foundri', 'synagogu', 'duomo', 'drugstor', 'fire st', 'condominium', 'internet caf', 'breweri', 'librari', 'storage silo', 'embassi', 'arcad', 'barrack', 'amphitheat', 'museum', 'cathedr', 'mandir', 'post offic', 'flat', 'bus stat', 'metro', 'water tow', 'warehous', 'monasteri', 'parking lot', 'block', 'makan', 'imambargah', 'art galleri', 'mihrab', 'townhous', 'shopping mal', 'cafe', 'forum', 'assembl', 'bank', 'villa', 'lighthous', 'unit', 'blockhous', 'factori', 'consul', 'railway st', 'doctors offic', 'restaur', 'church', 'arsen', 'taxi st', 'templ', 'hangar', 'hairdress', 'orphanag', 'parking garag', 'mosqu', 'orthodontist', 'theater', 'market', 'basilica', 'skyscrap', 'city hal', 'hotel', 'colleg'}
landforms={'marine terrac', 'pit crat', 'seamount', 'blowhol', 'complex volcano', 'glacial horn', 'escarpment','scarp', 'peninsula', 'bornhardt', 'coral reef', 'atol', 'geo', 'tide pool', 'natural leve', 'dome', 'floodplain', 'firth', 'cove', 'plateau', 'lacustrine terrac', 'mogot', 'stream', 'hanging valley', 'rock form', 'graben', 'volcanic field', 'paleoplain', 'gulli', 'nunatak', 'erg', 'lavaka', 'kame', 'interfluv', 'lava spin', 'beach and raised beach', 'waterfal', 'parallel roads of glen roy', 'tuff con', 'scowl', 'kettl', 'dell', 'complex crat', 'bight', 'uvala', 'oceanic ridg', 'river island', 'meander', 'endorheic basin', 'salt pan', 'homoclinal ridg', 'river delta', 'marsh', 'dune system', 'sand volcano', 'tidal marsh', 'volcanic dam', 'valley should', 'barrier bar', 'submarine volcano', 'yardang', 'terracett', 'braided channel', 'defil', 'salt pan (salt flat)', 'strike ridg', 'cliff', 'hillock', 'towhead', 'cuesta', 'bluff', 'volcanic con', 'headland', 'bay', 'flat landforms[edit]', 'rock shelt', 'cave', 'ventifact', 'knoll', 'panhol', 'hornito', 'dissected plateau', 'side valley', 'strandflat', 'inlet', 'glen', 'flat (landform)', 'beach', 'continental shelf', 'permafrost plateau', 'tepui', 'pull-apart basin', 'inverted relief', 'lithalsa', 'carolina bay', 'ejecta blanket', 'delta, riv', 'hogback', 'tombolo', 'tabl', 'outwash plain', 'thermokarst', 'fault scarp', 'archipelago', 'lacustrine plain', 'thalweg', 'pseudocrat', 'tafoni', 'blowout', 'mesa', 'peneplain', 'stack and stump', 'summit', 'abîm', 'polj', 'ridg', 'nivation hollow', 'plunge pool', 'arroyo and (wash)', 'ait', 'abyssal fan', 'col', 'mamelon', 'fluvial island', 'cape', 'coast', 'landform', 'salt marsh', 'oceanic plateau', 'supervolcano', 'outwash fan and outwash plain', 'canyon', 'raised beach', 'cuspate foreland', 'tunnel valley', 'gorg', 'bar', 'cinder con', 'strait', 'tessellated pav', 'shoal', 'islet', 'spring', 'kipuka', 'flat', 'mountain', 'cryovolcano', 'flyggberg', 'scree', 'malpai', 'baymouth bar', 'potrero', 'flared slop', 'pond', 'surge channel', 'kame delta', 'plain', 'volcanic crat', 'solifluction lob', 'faceted spur', 'vent', 'draw', 'dolin', 'shield volcano', 'trim lin', 'morain', 'oasi', 'stack', 'cove (mountain)', 'crevasse splay', 'badland', 'natural arch', 'exhumed river channel', 'lava tub', 'anabranch', 'island', 'epigenetic valley', 'playa lak', 'wave-cut platform', 'structural bench', 'watersh', 'drumlin field', 'drumlin', 'moulin', 'gulch', 'solifluction sheet', 'truncated spur', 'tepuy', 'crevass', 'dike', 'outwash fan', 'lava dom', 'valley', 'entrenched meand', 'u-shaped valley', 'stratocon', 'spatter con', 'fissure v', 'guyot', 'pediplain', 'mid-ocean ridg', 'lava lak', 'fjard', 'sound', 'arêt', 'horst', 'karst', 'geyser', 'alluvial fan', 'volcanic plug', 'maar', 'vale', 'turlough', 'dune', 'sea cav', 'oceanic basin', 'volcanic island', 'flute', 'subglacial mound', 'drumlin and drumlin field', 'cenot', 'fluvial terrac', 'abyssal plain', 'caldera', 'granite dom', 'gulf', 'beach ridg', 'bayou', 'sinkhol', 'inselberg', 'backswamp', 'impact crat', 'sandur', 'strath', 'stratovolcano', 'rock-cut basin', 'tea tabl', 'corrie or cwm', 'mud volcano', 'stump', 'dale', 'foib', 'pediment', 'cut bank', 'confluenc', 'mountain rang', 'valley and val', 'volcanic arc', 'doab', 'barrier island', 'rift valley', 'roche moutonné', 'pyroclastic shield', 'barchan', 'shore', 'ria', 'calanqu', 'pingo', 'cryptodom', 'mountain pass', 'proglacial lak', 'wave cut platform', 'monadnock', 'volcano', 'karst fenst', 'riffl', 'hoodoo', 'cryoplanation terrac', 'ayr', 'submarine canyon', 'tower karst', 'desert pav', 'honeycomb weath', 'oceanic trench', 'malpaí', 'lagoon', 'palsa', 'asymmetric valley', 'point bar', 'dreikant', 'lava plain', 'nubbin', 'levee, natur', 'glacier foreland', 'fjord', 'gorge and canyon', 'beach cusp', 'ravin', 'lava flow', 'drainage basin', 'bench', 'stream pool', 'esker', 'volcanic group', 'seamount chain', 'river', 'resurgent dom', 'glacier cav', 'arch', 'spit', 'limestone pav', 'crater lak', 'earth hummock', 'flatiron', 'volcanic plateau', 'hill', 'paleosurfac', 'lake', 'panhole (weathering pit)', 'foiba', 'karst valley', 'wadi', 'dry lak', 'inselberg plain', 'etchplain', 'yazoo stream', 'oxbow lak', 'butt', 'tor', 'estuari', 'lava coule', 'structural terrac', 'planation surfac', 'somma volcano', 'channel', 'swamp', 'machair', 'sandhil', 'shut-in', 'rapid', 'quarri', 'loess', 'drainage divid', 'diatrem', 'moraine and ribbed morain', 'rock glaci', 'glacier', 'cirqu', 'ribbed morain', 'tuya', 'isthmu', 'dirt con', 'terrac'}
town_names={'district', 'town', 'citi', 'nagar', 'gram', 'place', 'villag'}


regex_names=road_names|building_names|landforms|town_names|road_names_2|building_names_2|landforms_2|town_names_2



# false_names=false_names|events_set|regex_names
# false_names=false_names|set([ps_stemmer.stem(i) for i in false_names])


def hash_tag_segment(hashtag_list):

	poss_places=[elem.replace('#','') for elem in hashtag_list]
	for elem in hashtag_list:
		# print(elem)
		# print(wordsegment.segment(elem.replace('#','')))
		poss_places.extend(wordsegment.segment(elem.replace('#','')))

	poss_places=[i for i in poss_places if i not in common_words]	
	# print('Hashtags',poss_places)	

	return poss_places

def give_location_2(tags):
	return_name_list=[]
	old_j=0
	l=len(tags)
	for i in range(0,l):
		if i<old_j:
			continue

		if tags[i][1]=='PROPN':

			add_val=""
			place_flag=0
			j=i+1
			# print()
			# print("new iterate")
			# print(tags[i][0], tags[i][1])

			while j<(len(tags)-1):
				tag_name=tags[j][0].lower()
				stem_tag_name=ps_stemmer.stem(tag_name)
				# print(tags[j][0],tags[j][1])
				if tags[j][1]==',' or tags[j][1]=='ADJ':
					j+=1
				elif tags[j][1]=='CONJ' or tags[j][1]=='CCONJ' or tags[j][1]=='PUNCT':	
					j+=1
					add_val=add_val+","

				elif tags[j][1]=='PROPN' or tags[j][0]==',':
					add_val=add_val+" "+tags[j][0]
					j+=1	

				elif stem_tag_name in regex_names:
					add_val=add_val+" "+tags[j][0]
					place_flag=1
					j+=1

				elif max([jellyfish.jaro_distance(stem_tag_name,k) for k in regex_names])>0.75 and tag_name not in stop_words and (tags[j][1]=='PROPN' or tags[j][1]=='NOUN'):
					place_flag=1
					j+=1					
				else:	
					break		
			old_j=j		

			loc_name=tags[i][0].replace('#','')+add_val
			# print(loc_name)
			if place_flag==1:
				# print('Already has a place flag')
				if ',' in loc_name:
					return_name_list.extend([i.strip() for i in loc_name.split(',')])
				else:	
					return_name_list.append(loc_name)
				# print(return_name_list)	

				continue
			if tags[i-1][0].lower() in loc_preposition_list :
				#return_name_list.append(loc_name)
				# print('In loc preposition list')

				if ',' in loc_name:
					return_name_list.extend(loc_name.split(','))
				else:
					return_name_list.append(loc_name)
				place_flag=1
				# print(return_name_list)

			if tags[i-1][0].lower() in dir_list	:
				# print('In dir name list')
				loc_name= tags[i-1][0]+" "+ loc_name
				if ',' in loc_name:
					return_name_list.extend(loc_name.split(','))
				else:
					return_name_list.append(loc_name)
				place_flag=1	
					
				# print(return_name_list)	

			if tags[i-1][0].lower()=='of':
				try:
					prev_word=tags[i-2][0].lower()
					#print(prev_word)
					if prev_word in of_place_list: 
						return_name_list.append(loc_name)
						continue

					if prev_word in of_dir_list:
						return_name_list.append(loc_name)		
						continue

					if prev_word in of_people_list:
						return_name_list.append(loc_name)
						continue

					prev_word_list=wn.synsets(prev_word)
					both_set=set(of_place_list)|set(of_people_list)
					for item in both_set:
						possible_items=wn.synsets(item)
						for a,b in product(possible_items,prev_word_list):
							d= wn.wup_similarity(a,b)
							try:
								if d>0.8:
									#print(a,b)
									place_flag=1
									return_name_list.append(loc_name)
									break			
							except:
								continue
						if place_flag==1:
							break				
				except:	
					continue	

	for names in return_name_list:
		names=re.sub('#','',names)

	return_name_list=[i.strip() for i in return_name_list]	
	# print('in location seq',return_name_list)	
	return return_name_list				

'''
simple naming conventions for roads and streets in UK and India according to 
https://wiki.waze.com/wiki/India/Editing/Roads and 
http://www.haringey.gov.uk/parking-roads-and-travel/roads-and-streets/street-and-building-naming-and-numbering/guidelines-street-and-building-naming-and-numbering
https://www.ura.gov.sg/uol/-/media/User%20Defined/URA%20Online/development-control/sbnb/SBNB_handbook_streets.pdf
https://en.wikipedia.org/wiki/List_of_building_types
https://en.wikipedia.org/wiki/List_of_landforms

'''

def regex_matches(text):
	return_name_list=[]
	words=text.replace('.',' ').lower().split()
	L=len(words)
	for i in range(0,L):
		if words[i] in stop_words:
			continue
		w=ps_stemmer.stem(words[i])	
		if w in regex_names:			
			return_name_list.append(words[i-1]+' '+ words[i])
			if words[i-1]==stop_words:
				continue
			if i>2 and words[i] not in stop_words: 
				return_name_list.append(words[i-2]+' '+ words[i-1]+' '+ words[i])

		# print(words[i])		
		if words[i] in of_dir_list:
			return_name_list.append(words[i]+' '+ words[i+1])
			if i+2<L and words[i+2] not in stop_words:
				return_name_list.append(words[i]+' '+ words[i+1]+' '+words[i+2])			


	# print('Regex_matches',return_name_list)
	return return_name_list			

# def to_nltk_tree(node):
# ...     if node.n_lefts + node.n_rights > 0:
# ...         return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
# ...     else:
# ...         return node.orth_

def tok_format(tok):
	return "_".join([tok.orth_, tok.pos_])

def to_nltk_tree(node):
	if node.n_lefts + node.n_rights > 0:
		return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
	else:
		return tok_format(node)
		

def NP_chunk(doc,text):
	chunks=[]
	dep_places=[]
	#global gt_count,dep_parse_dist,a,act_gt_count,diff_gt,orth_dist

	for np in doc.noun_chunks:
		dep_places.append(np.text)

	# print('Noun Phrases', dep_places)	
	#print(text)	
	edges=[]

	source_list=[]
	target_list=[]
	

	for token in doc:

		if ps_stemmer.stem(token.lower_) in need_offer_words: #or token.tag_=='ROOT' or token.tag_=='VERB':
			# print(ps_stemmer.stem(token.lower_))
			source_list.append('{0}-{1}'.format(token.lower_,token.i))

		if token.pos_ =='PROPN' or token.pos_=='NOUN' or token.pos_=="ADJ"  and token.lower_ not in stop_words:# 
			# print(token.lower_)
			target_list.append('{0}-{1}'.format(token.lower_,token.i))
			
		for child in token.children:
			edges.append(('{0}-{1}'.format(token.lower_,token.i),'{0}-{1}'.format(child.lower_,child.i)))
			# edges.append(('{0}-{1}'.format(child.lower_,child.i),'{0}-{1}'.format(token.lower_,token.i)))

		# print(token.text, token.pos_ ,token.dep_, token.head.text, token.head.pos_,[child for child in token.children])

	graph=nx.Graph(edges)	

	for i in source_list:
		for j in target_list:
			try:
				if i!=j and nx.shortest_path_length(graph,source=i,target=j)<=4:
					# print(i,j,nx.shortest_path_length(graph,source=i,target=j))
					dep_places.append(j.split('-')[0])
			except:
				continue		

	new_target_set=set()
	new_target_list=[]

	for i in target_list:
		for j in target_list:
			spec_i=i.split('-')[0].lower().strip()
			spec_j=j.split('-')[0].lower().strip()
			if spec_i+' '+spec_j in text.lower():
				new_target_set.add(spec_i+' '+spec_j)
				new_target_list.append(i+'_'+j+'_'+spec_i+' '+spec_j)
	
	for i in source_list:
		for j in new_target_list:
			try:
				v2=j.split('_')	
				if v2[-1] not in gt:
					continue
				v=min(nx.shortest_path_length(graph,source=i,target=v2[0]),nx.shortest_path_length(graph,source=i,target=v2[1]))
				if v<=4:
					dep_places.append(v2[-1])
			except:
				continue	

	# print('Dependency parsing', dep_places)			
	return dep_places


with open('DATA_2/IT/IT_loc.p','rb') as handle:
	curr_loc_dict=pickle.load(handle)

# false_names=false_names-set([i for i in curr_loc_dict])

input_file='DATA_2/INPUT/chennai_needs.txt'
#input_file='./Test_input/check_dir.csv'


eps=0
all_lines=0
exception_count=0
false_lines=0

f=open(input_file,'r')
starttime=time.time()

def return_location_list(text):
	lat_long=[]
	reg_poss_places=[]
	try:
		
		try:
			hashtag_list=[i for i in text.split() if i.startswith("#")]
		except:
			hashtag_list=[]	

		poss_places=hash_tag_segment(hashtag_list)
		text=tweet_preprocess2(text,hashtag_list)		
		# print(text)
		need_spacy_tags=[]
		doc=nlp(text)
		for word in doc:
			temp=(word.text,word.pos_)
			need_spacy_tags.append(temp)	

		loc_list_spacy=give_location_2(need_spacy_tags)		

		reg_poss_places.extend(regex_matches(text))
		poss_places.extend(NP_chunk(doc,text))
		

		org_list=[]
		prev_word=""
		prev_word_type=""
		
		for word in doc:
			if word.ent_type_ in entity_type_list:
				org_list.append(word.orth_+"<_>"+word.ent_type_)
			else:
				org_list.append("<_>")
		# print('NER List', org_list)		

		for i in org_list:
			index=i.index("<_>")
			if i[index+3:]=='GPE' or i[index+3:]=='FACILITY' or i[index+3:]=='LOC':
				poss_places.append(i[:index])

		poss_places=set([i.lower().strip() for i in poss_places])
		refined_poss_place_list=[]	
		for i in poss_places:
			if i not in false_names:
				refined_poss_place_list.append(i)

		refined_poss_place_list.extend([i.lower().strip() for i in loc_list_spacy])
		refined_poss_place_list=set([re.sub('[^A-Za-z\s]+', '', i).strip() for i in refined_poss_place_list])#-set(stop_words)
		
		
		del_poss_list=set()
		
		
		for i in refined_poss_place_list:
			for k in town_names|town_names_2:
				if ' '+k in i:
					del_poss_list.add(i)
					i=i.replace(' '+ k,'').strip()
					i=i.replace(k+' ','').strip()

		# print(refined_poss_place_list)
		# temp_file.write(str(refined_poss_place_list)+'\n')

		for i in refined_poss_place_list:		
			try:
				if i =='' or i in false_names or ps_stemmer.stem(i) in false_names:
					continue
				if i.endswith('hospital') and len(i.split())>=3:
					g=geocoder.osm(i+', Italy')
					# print(g)
					if g.json!=None:
						lat_long.append((i,(g.json['lat'],g.json['lng'])))

						
				lat_long.append((i,curr_loc_dict[i]))
			except Exception as e:
				continue	

		# for i in reg_poss_places:
		# 	try:
		# 		if i =='' or i in false_names or ps_stemmer.stem(i) in false_names:
		# 			continue

		# 		tryflag=False
		# 		for j in regex_names:
		# 			if i.endswith(j) or i.startswith(j):
		# 				tryflag=True		
		# 				break

		# 		if tryflag==False:
		# 			continue		
					
				
		# 		g=geocoder.osm(i+', Chennai')
		# 		# print(g)
		# 		if g.json!=None:
		# 			lat_long.append((i,(g.json['lat'],g.json['lng'])))
				
		# 	except Exception as e:
		# 		continue		
				
		# print(lat_long)			
		
	except Exception as e:
		print("EXCEPTION")
		print(e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		# print(obj,obj2)
		# exception_count+=1
		pass
		

	return lat_long

# temp_file=open('temp.txt','w')

# c=0
# for line in f:
# 	line=line.rstrip().split('<||>')		
# 	text=line[1]
# 	org_text=text
# 	temp_file.write(text+'\n')
# 	temp_file.write(str(return_location_list(org_text))+'\n')
# 	temp_file.write('\n')
# 	all_lines+=1
# 	print(all_lines)
	

