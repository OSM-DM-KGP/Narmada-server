import json

file = "nepal-quake-2015-tweets.jsonl"
data = {}

with open(file, 'r') as f:
    text = f.readlines()

for line in text:
    j = json.loads(line.strip())
    if len(j['entities']) == 0 or len(j['entities']['urls']) == 0:
        continue
    data[j['id']] = j['entities']['urls'][0]['url']

with open('tweet_urls.json', 'w') as fp:
    json.dump(data, fp)