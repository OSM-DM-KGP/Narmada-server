# Narmada-server
Backend server for Narmada calls. Refer to https://osm-dm-kgp.github.io/Narmada-server/ for API description.

Other repositories associated with this project:
* Frontend - [OSM-DM-KGP/Narmada](https://github.com/OSM-DM-KGP/Narmada)

Currently sends only 20 resources at a time, offset to be used to send more than certain resources

## Servers

We have one server: which runs nodejs, and flask api in the same place. The Node server handles all incoming requests, and redirects requests for NLP tasks to the flask api.

Digitalocean is used to host this. The webite (refer [OSM-DM-KGP/Narmada](https://github.com/OSM-DM-KGP/Narmada)) accesses the backend via ngrok.

## Setup

Install the following:
* nodejs
* npm
* mongodb
* python3
* pip3
* ngrok (ngrok needs auth token, get from their dashboard)
* git

### ToDo: Add instructions for BERT

```sh
# both needed
$ pip3 install -r requirements.txt
$ npm install
$ python3 -m spacy download en
## setup data
$ node uploader.js # upload all the tweets into mongodb
#
$ mongo
> use narmada
# for text searchability
> db.tweets.ensureIndex({ text: "text" })
```

Once everything is setup, in three separate terminals, we have the following:

```
# T1
$ npm start
# T2
$ python3 app.py
# T3
$ ./ngrok http 3000 # expose backend
```

The url generate by ngrok must be added in front-end config.

### Useful debugging commands

* db.getCollection('tweets').find({Classification: 'Need', isCompleted: false}).sort({created: -1})
* db.tweets.ensureIndex({ text: "text" })
* db.tweets.createIndex({ text: "text" })

Other mongodb commands can be found here: [OSM-DM-KGP/Savitr](https://github.com/OSM-DM-KGP/Savitr/blob/master/data/README.md)