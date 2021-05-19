import os
import flask
from flask import Flask
app = Flask(__name__)


import re
import json
from urllib.parse import unquote
import location
import pudb

## CORS
from flask_cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

tel_no="([+]?[0]?[1-9][0-9\s]*[-]?[0-9\s]+)"
email="([a-zA-Z0-9]?[a-zA-Z0-9_.]+[@][a-zA-Z]+[.](com|net|edu|in|org|en))"
http_url='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def get_contact(text):
	contacts=[]
	numbers=re.findall(tel_no,text)
	temp=set()
	for i in numbers:
		if len(i.replace(' ',''))>=7:
			temp.add(i)
	contacts.append(temp)		
	temp=set()
	mails= re.findall(email,text)
	for i in mails:
		temp.add(i)
	contacts.append(temp)	
	temp=set()	
	urls= re.findall(http_url,text)	
	for i in urls:
		temp.add(i)
	contacts.append(temp)
	return contacts	

def get_classification(text, resource_list):
    if "need" in text or "require" in text:
        label = 0
    elif "availab" in text or len(resource_list) != 0:
        label = 1
    else:
        label = 2
    return (label)

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
def get_location_covid(text):
    text = text.lower()
    places = location.return_location_list(text)
    each_loc = [place[0] for place in places]
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
    return resource_text, places

@app.route('/parse', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def parseResources():
    resource, line = {}, ''
    print(flask.request.json)
    print(unquote(flask.request.query_string.decode('utf-8')))
    if flask.request and flask.request.json and'text' in flask.request.json:
        line = flask.request.json['text']
    else:
        line = json.loads(unquote(flask.request.query_string.decode('utf-8')))['text']
    print('Received for parsing: ', line)
    contacts = get_contact(line)
    resource_text, locations = get_location_covid(line)
    print(resource_text,locations)
    resource['Contact'] = {'Phone number': list(contacts[0]), "Email": list(contacts[1])}
    resource['Sources'] = {}
    resource['ResourceWords'] = resource_text.strip(" ").split(" ")
    resource['Locations'], resource['Resources'] = dict(), {}
    resource['Resources'] = {"resources": resource['ResourceWords']}
    for each in locations:
        resource['Locations'][each[0]] = {"long": float(each[1][0][1]), "lat": float(each[1][0][0])}
    resource['Classification'] = int(get_classification(line, resource['ResourceWords']))
    print('Returning', resource)
    return flask.jsonify(resource)

# add routes for nodejs backend via here as well
@app.route('/', methods=['GET', 'OPTIONS'])
@cross_origin()
def base():
	with open('index.html', 'r') as f:
		txt = f.readlines()
	return ''.join(txt)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
