import location
import pudb
import json

from pymongo import MongoClient
client = MongoClient('mongodb://127.0.0.1:27017')
db = client["narmada"]
tweets_collection = db['tweets']


def parseTweet(text_org):
    print('helo')
    text = text_org.lower()
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
    for resource in resources:
        if resource in each_loc:
            places_to_remove.append(each_loc.index(resource))
        if resource in text:
            resource_text = resource_text+resources[resource]+" "

    places_to_remove.sort(reverse=True)
    for ptr in places_to_remove:
        del places[ptr]

    # print("\n\n\nText: "+str(text_org))
    print("\nLocation: ",places)
    print("\nResources: "+resource_text)

    if "need" in text or "require" in text:
        print("\nType: Need")
    elif "availab" in text or len(resource_text) != 0:
        print("\nType: Availability")
    else:
        print("\nType: Other")
    
    # inserting in mongodb
    db.tweets_collection.insert_one({
        'text': text_org,
        # need to add resource
        # need to add type
        # need to add locations
    })

with open('2021-05-10.jsonl') as f:
    json_lines = f.readlines()
    for json_line in json_lines:
        parsed_json_line = json.loads(json_line)
        tweet = parsed_json_line['tweet']
        print('============> parsing currently ', tweet)
        parseTweet(tweet)
        break

