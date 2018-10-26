import pickle
import csv

csv_file=open('NP.txt','r')

location_dict={}

count=0

def check_location_dict(name1,lat,longi):
	if name1 not in location_dict:
		location_dict[name1]=[]	
	location_dict[name1].append((lat,longi))	

	# else:
	# 	flag=False
	# 	for i in range(0,len(location_dict[name1])):
	# 		lat1=location_dict[name1][i][0]
	# 		long1=location_dict[name1][i][1]
	# 		if lat1==lat and long1==longi:
	# 			flag=True
	# 			break

	# 	if flag==False:
	# 		location_dict[name1].append((lat,longi))	


for line in csv_file:
	line=line.strip().split('\t')
	name1=line[1]
	name2=line[2]
	names=line[3].split(',')
	lat=line[4]
	longi=line[5]

	check_location_dict(name1.lower(),lat,longi)	
	check_location_dict(name2.lower(),lat,longi)

	for name in names:
		check_location_dict(name.lower(),lat,longi)

	count+=1	
	if count%10000==0:
		print(count/100)	

new_location_dict={}

lat_len=[]
long_len=[]

for name in location_dict:
	lat_len=[float(i[0]) for i in location_dict[name]]
	long_len=[float(i[1]) for i in location_dict[name]]

	lat_val=round(sum(lat_len)/len(lat_len),6)
	long_val=round(sum(long_len)/len(long_len),6)

	new_location_dict[name]=(lat_val,long_val)

with open('NP_loc.p','wb') as handle:
	pickle.dump(new_location_dict,handle)	


		
		




