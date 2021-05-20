import location
import pudb
import json

from pymongo import MongoClient
client = MongoClient('mongodb://127.0.0.1:27017')
db = client["narmada"]
tweet = db['tweets']


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

    # make places in db format
    locations = {}
    for place in places:
        name_of_place = place[0]
        arr_of_co_ords = place[1]
        if len(arr_of_co_ords) == 1:
            locations[name_of_place] = {
                'lat': arr_of_co_ords[0][0],
                'long': arr_of_co_ords[0][1]
            }
        else:
            for i in range(len(arr_of_co_ords)):
                locations[name_of_place + '_' + str(i+1)] = {
                    'lat': arr_of_co_ords[i][0],
                    'long': arr_of_co_ords[i][1],
                }


    print('locations in DB ', locations)

    if "availab" in text:
        classification_type = 'Availability'
        print("\nType: Availability")
    elif "need" in text or "require" in text:
        classification_type = 'Need'
        print("\nType: Need")
    else:
        classification_type = 'Other'
        print("\nType: Other")

    # if "need" in text or "require" in text:
    #     print("\nType: Need")
    # elif "availab" in text or len(resource_text) != 0:
    #     print("\nType: Availability")
    # else:
    #     print("\nType: Other")
    
    # inserting in mongodb
    if classification_type != 'Other':
        try:
            db.tweets.insert_one({
                'text': text_org,
                'Classification': classification_type,
                'ResourceWords': resource_text.split(" "),
                "Locations": locations
            })
            print('successfully added in DB')
        except Exception as e:
            print('Error in adding to DB is ',e)

# For testing uncomment below
# parseTweet('I need oxygen and bed in goa and hyderabad')

with open('2021-05-10.jsonl') as f:
    json_lines = f.readlines()
    for json_line in json_lines:
        try:
            parsed_json_line = json.loads(json_line)
            tweet = parsed_json_line['tweet']
            print('============> parsing currently ', tweet)
            parseTweet(tweet)
        except Exception as e:
            print('Failed for some thing')
            
    
