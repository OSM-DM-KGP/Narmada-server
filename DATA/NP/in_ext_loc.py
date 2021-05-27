import pudb
import pickle
f = open("IN.txt", "r")
all_poses = {}

count = 0
while True:
	count += 1
	print(count)
	line = f.readline()
	if not line: break
	names = [line.split("\t")[2]]
	more_names = line.split("\t")[3]
	names.extend(more_names.split(","))
	names.append(line.split("\t")[1])
	lat = line.split("\t")[4]
	lon = line.split("\t")[5]
	names = [x.lower() for x in names]
	names = list(set(names))
	for name in names:
		# if "haora" in name:
		# 	pu.db
		if name not in all_poses:
			all_poses[name] = []
		all_poses[name].append((lat,lon))

f.close()
with open('IN_loc.p', 'wb') as handle:
   pickle.dump(all_poses, handle)