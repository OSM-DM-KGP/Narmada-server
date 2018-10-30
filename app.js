const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const CircularJSON = require('circular-json');

const Tweet = require('./tweet.js');
const TweetSchema = mongoose.model('Tweet').schema;
// from resource import resource
// Make sure to change this in client as well
const port = process.env.PORT | 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Connect to Mongoose
const mongourl = 'mongodb://127.0.0.1:27017';
const dbName = 'narmada';
const collectionName = 'tweets';

mongoose.Promise = global.Promise;
mongoose.connect(mongourl + '/' + dbName, { useMongoClient: true });
var db = mongoose.connection;

//Bind connection to error event (to get notification of connection errors)
db.on('error', console.error.bind(console, 'MongoDB connection error:'));

// Allow CORS
app.all('/*', function (request, response, next) {
    response.header("Access-Control-Allow-Origin", "*");
    response.header("Access-Control-Allow-Headers", "X-Requested-With");
    response.header("Access-Control-Allow-Methods", "GET")
    response.header('Access-Control-Allow-Headers', 'Content-Type');
    next();
});

// Info only
app.get('/info', (request, response) => {
    response.send('Info');
});

// Get
app.get('/', (request, response) => {
    // request.query contains filter
    // response.status(200).send(request.query);
    var options = {
        "limit": 20,
        "skip": 0,
    };
    if(request.query.skip) {
        options.skip = Number(request.query.skip);
        delete request.query.skip;
    }
    if(request.query.isCompleted) request.query.isCompleted = (request.query.isCompleted == 'true');
    if(request.query.text) request.query.text = JSON.parse(request.query.text);
    // console.log('Query', request.query);
    db.collection(collectionName).find(request.query, options).sort({ created: -1 }).toArray(function(err, results) {
        if(results) {
            // console.log('results', results);
            response.send(results);
        }
        if(err) {
            console.log('Error retrieving docs', err);
        }
    });
    // response.status(200).send(CircularJSON.stringify(out));
});

// get details of tweet
// update tweet statuses

// Create new resource
app.post('/new', (request, response) => {
    // console.log(request.body);
    var tweet = request.body;
    // assign _id, time, 
    if(!tweet._id) {
        tweet._id = mongoose.Types.ObjectId().toString();
    }

    var insertTweet = Tweet(tweet);
    db.collection(collectionName).insert(insertTweet);
    response.status(201).send('Created resource');
});

app.listen(port, () => {
    console.log("Server listening on port " + port);
});