// The mega uploader
// uploads all docs in compatible format to narmada/tweets
var MongoClient = require('mongodb').MongoClient;
const mongoose = require('mongoose');

const Tweet = require('./tweet.js');

const mongourl = 'mongodb://127.0.0.1:27017';
const dbName = 'narmada';
const collectionName = 'tweets';

var docs = require('./data/italy_needs.json');

mongoose.Promise = global.Promise;
mongoose.connect(mongourl + '/' + dbName, { useMongoClient: true });
var db = mongoose.connection;

        
docs.forEach(function (doc) {
    console.log('Started', doc._id);
    var insertTweet = Tweet(doc);
    db.collection(collectionName).insert(insertTweet);
})
