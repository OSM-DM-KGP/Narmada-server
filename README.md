# Narmada-server
Backend server for Narmada calls

Currently sends only 20 resources at a time, offset to be used to send more than certain resources

* db.getCollection('tweets').find({Classification: 'Need', isCompleted: false}).sort({created: -1})
  
* db.tweets.ensureIndex({ text: "text" })

## Servers

We have one server: which runs nodejs, and flask api in the same place.

We are using Digitalocean for this

### Setup

Install: nodejs, npm, mongodb, python, pip, ngrok, git
 (ngrok needs auth token, get from their dashboard)


```
# both needed
$ pip3 install -r requirements.txt
$ npm install
$ python3 -m spacy download en
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