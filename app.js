const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const CircularJSON = require('circular-json');
const jaccard = require('jaccard');
const ObjectID = require('mongodb').ObjectID;

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
	response.header("Access-Control-Allow-Methods", "GET,POST,PUT,OPTIONS")
	response.header('Access-Control-Allow-Headers', 'Content-Type');
	next();
});

// Info only
app.get('/info', (request, response) => {
	response.send('Info');
});

// basic landing page
app.get('/', (request, response) => {
	response.send('This is indeed the basic landing page');
});

// Get
app.get('/get', (request, response) => {
	// request.query contains filter
	// response.status(200).send(request.query);
	var options = {
		"limit": 20,
		"skip": 0,
	};

	var matching = false;
	if(request.query.skip) {
		options.skip = Number(request.query.skip);
		delete request.query.skip;
	}
	if(request.query.isCompleted) request.query.isCompleted = (request.query.isCompleted == 'true');
	if(request.query.text) request.query.text = JSON.parse(request.query.text);
	if(request.query.Matched) {request.query.Matched = {$ne: "-1"}; matching = true;}
	// console.log('Query', request.query);
	
	db.collection(collectionName).find(request.query, options).sort({ created: -1 }).toArray(function(err, results) {
		if(results) {
			if(matching===true) {
				var partners = [];
				results.forEach(result => {partners.push(result.Matched)});
				console.log('partners', partners);
				db.collection(collectionName).find({"_id": {$in: partners}}).toArray(function(err, resultpartners) {
					if(err) console.log('Error retrieving partners', err);
					
					// fetched matches, fetched their partners. Now tie them in holy matrimony
					var partnerid = {};
					// setting additional field - isPartner as true for later ease
					for(var i=0; i < resultpartners.length; i++) {partnerid[resultpartners[i]._id] = i; resultpartners[i].isPartner = true;}


					for(var i=0; i < results.length; i++) {
						var availId = results[i].Matched;
						results[i].partner = resultpartners[ partnerid[availId] ];
					}
					response.send(results);
				});
			}
			// console.log(results);
			else response.send(results);
		}
		if(err) console.log('Error retrieving docs', err);
	});
	// response.status(200).send(CircularJSON.stringify(out));
});

// find matches for particular tweet
app.get('/match', (request, response) => {
	console.log('Matching for id ' + request.query.id + ' of type ' + request.query.type);
	var fetchType = (request.query.type === "Need") ? "Availability" : "Need";

	db.collection(collectionName).findOne({_id: request.query.id}, function(err, resourceToMatch) {
		if(err) {
			console.log('Cannot fetch resource of id!', err);
			response.send([]);
		}
		// buckets approach -> go via tweets having those categories
		var categoriesToMatch = [];

		var searchParams = {
			"Classification": fetchType,
			"$text": { $search: resourceToMatch.ResourceWords.join(",")},
			"Matched": '-1'
		}
		db.collection(collectionName).find(searchParams).sort({ created: -1 }).toArray(function (err, results) {
			if (err) {
				console.log('Error retrieving docs', err);
			}
			// console.log('Matches', results.length); => >20 results
			// keep array of size 20 to track results
			var scores = [];
			var matches = [];
			var minScore = 1, minIndex = 0;
			results.forEach(result => {
				var jscore = jaccard.index(resourceToMatch.ResourceWords, result.ResourceWords);
				
				if(scores.length < 20 || scores.length == 20 && minScore < jscore) {
					if(scores.length == 20) {
						// remove min element
						scores.splice(minIndex, 1); matches.splice(minIndex, 1); 
					}
					scores.push(jscore); matches.push(result);
					minScore = Math.min(...scores); minIndex = scores.indexOf(minScore);
				}
			});

			var keyvalues = [];
			for(var i=0; i < scores.length; i++) {
				keyvalues.push([matches[i], scores[i]]);
			}

			// sort by score
			keyvalues.sort(function compare(kv1, kv2) { return kv2[1] - kv1[1] });
			matches = [];
			for(var i =0 ; i < keyvalues.length; i++) matches.push(keyvalues[i][0]);
			
			response.send(matches);
		});
	});
});

// Make match
app.put('/makeMatch', (request, response) => {
	console.log(request.body);
	db.collection(collectionName).findOneAndUpdate({_id: request.body.id1}, {$set: {Matched: request.body.id2 }});
	db.collection(collectionName).findOneAndUpdate({ _id: request.body.id2 }, {$set: {Matched: request.body.id1 }});

	response.status(201).send("Made match of" + request.body.id1 + " and " + request.body.id2);
});

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