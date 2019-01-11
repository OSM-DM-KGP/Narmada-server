// The mega uploader
// uploads all docs in compatible format to narmada/tweets
var MongoClient = require('mongodb').MongoClient;
const mongoose = require('mongoose');

const Tweet = require('./tweet.js');

const mongourl = 'mongodb://127.0.0.1:27017';
const dbName = 'narmada';
const collectionName = 'tweets';

var docs_in = require('./data/italy_needs.json');
var docs_io = require('./data/italy_offers.json');
var docs_nn = require('./data/nepal_needs.json');
var docs_no = require('./data/nepal_offers.json');

mongoose.Promise = global.Promise;
mongoose.connect(mongourl + '/' + dbName, { useMongoClient: true });
var db = mongoose.connection;


var docs_arr = [docs_in, docs_io, docs_nn, docs_no];
docs_arr.forEach(function (docs) {
    docs.forEach(function (doc) {
        console.log('Started', doc._id);
        var insertTweet = Tweet(doc);
        db.collection(collectionName).insert(insertTweet);
    });
});
