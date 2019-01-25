import os

file=open('INPUT/Chennai-availabilities.txt','r')
ofile=open('INPUT/chennai_offers.txt','w')

c=0
for line in file:
	line=line.rstrip().split('<||>')
	print(line)
	ofile.write(line[0]+'<||>'+line[-1]+'\n')
	c+=1

print(c)	