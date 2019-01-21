# Narmada-server
Backend server for Narmada calls

* insert json to mongo: `mongoimport --db narmada --collection tweets --type json --file italy_needs.json --jsonArray`

Currently sends only 20 resources at a time, offset to be used to send more than certain resources

* db.getCollection('tweets').find({Classification: 'Need', isCompleted: false}).sort({created: -1})
  
* db.tweets.ensureIndex({ text: "text" })

## Servers

We have two servers: One for mongodb setup, and nodejs backend.

Another with simply a flask backend, which uses local files - nothing else.

```
# both needed
$ pip install -r requirements.txt
$ npm install
```