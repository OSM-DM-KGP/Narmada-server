const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const CircularJSON = require('circular-json');
const jaccard = require('jaccard');
const ObjectID = require('mongodb').ObjectID;
const requestM = require('request');

const Tweet = require('./tweet.js');
const TweetSchema = mongoose.model('Tweet').schema;
// from resource import resource
// Make sure to change this in client as well
const port = process.env.PORT | 3000;

// locally hosted python parsing app
const parseUrl = 'http://localhost:5000';

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
	console.log(new Date(), '+++--- /info');
	response.send('Info');
});

// basic landing page
app.get('/', (request, response) => {
	console.log(new Date(), '+++--- /');
	response.send('This is indeed the basic landing page');
});

// Get
app.get('/get', (request, response) => {
	// request.query contains filter
	// response.status(200).send(request.query);
	console.log(new Date(), '+++--- /get', request.query);
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
			console.log('wat are results ', results)		 // remove temporarily plz
		
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
	console.log(new Date(), '+++--- /match ' + request.query.id + ' of type ' + request.query.type);
	var fetchType = (request.query.type === "Need") ? "Availability" : "Need";
	try {
		var values = Object.Values(request.query.Locations)
		var latitude = values[0]['lat']
		var longitude = values[0]['long']
	} catch(err) {
		var latitude = 0
		var longitude = 0
	}

	console.log("_id is ",request.query.id)
	db.collection(collectionName).findOne({_id: ObjectID(request.query.id) }, function(err, resourceToMatch) {
		
		if(err) {
			console.log('Cannot fetch resource of id!', err);
			console.log('err is ', err)
			response.send([]);
		}
		// buckets approach -> go via tweets having those categories
		var categoriesToMatch = [];

		console.log("resourceToMatch", resourceToMatch)
		var searchParams = {
			"Classification": fetchType,
			"$text": { $search: resourceToMatch.ResourceWords.join(",")},
			// "$text": { $search: 'Beds,Oxygen' },
			// "Matched": -1
		}

		console.log('search Params before starting search ', searchParams)
		
		

		db.collection(collectionName).find(searchParams).sort({created: -1 }).toArray(function (err, results) {
			console.log("came inside ")
			if (err) {
				console.log('Error retrieving docs', err);
			}
			// console.log('Matches', results.length); => >20 results
			// keep array of size 20 to track results
			var scores = [];
			var matches = [];
			var minScore = 1, minIndex = 0;

			console.log("results.length ",results.length)
			results.forEach(result => {
				var jscore = jaccard.index(resourceToMatch.ResourceWords, result.ResourceWords);
				if(scores.length < 20 || minScore < jscore) {
					scores.push(jscore); matches.push(result);
					minScore = Math.min(...scores); minIndex = scores.indexOf(minScore);
				}
				// add the score
				result['score'] = jscore

				try {
				let loc_values = Object.values(result["Locations"])

				var result_lat = loc_values[0]['lat']
				var result_long = loc_values[0]['long']

				} catch(err) {
					var result_lat = 0
					var result_long = 0
				}

				let euclid_dist = Math.abs(result_lat - latitude) + Math.abs(result_long - longitude)
				result['euclid_dist'] = euclid_dist

			});

			sorted_results = results.sort((a,b) => b['score'] - a['score'])
			sorted_by_dist_results = sorted_results.sort((a,b) => a['euclid_dis'] - b['euclid_dist'])
			console.log('sending these many',sorted_results.length)
			response.send(sorted_by_dist_results)		
	
			
			// var keyvalues = [];
			// for(var i=0; i < scores.length; i++) {
			// 	keyvalues.push([matches[i], scores[i]]);
			// }

			// // sort by score
			// keyvalues.sort(function compare(kv1, kv2) { return kv2[1] - kv1[1] });
			// matches = [];
			// for(var i =0 ; i < keyvalues.length; i++) matches.push(keyvalues[i][0]);
			// console.log("response.send ", matches.length)
			// response.send(matches);
		});
	});
});

// new match
app.get('/newmatch', (request, response) => {
	console.log(new Date(), '+++--- /match ' + request.query.id + ' of type ' + request.query.type);
	var fetchType = (request.query.type === "Need") ? "Availability" : "Need";
	try {
		var values = Object.Values(request.query.Locations)
		var latitude = values[0]['lat']
		var longitude = values[0]['long']
	} catch(err) {
		var latitude = 0
		var longitude = 0
	}

	console.log("_id is ",request.query.id)
	db.collection(collectionName).findOne({_id: request.query.id}, function(err, resourceToMatch) {
		
		if(err) {
			console.log('Cannot fetch resource of id!', err);
			console.log('err is ', err)
			response.send([]);
		}
		// buckets approach -> go via tweets having those categories
		var categoriesToMatch = [];

		console.log("resourceToMatch", resourceToMatch)
		var searchParams = {
			"Classification": fetchType,
			"$text": { $search: resourceToMatch.ResourceWords.join(",")},
			// "$text": { $search: 'Beds,Oxygen' },
			// "Matched": -1
		}

		console.log('search Params before starting search ', searchParams)
		
		

		db.collection(collectionName).find(searchParams).sort({created: -1 }).toArray(function (err, results) {
			console.log("came inside ")
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
				if(scores.length < 20 || minScore < jscore) {
					scores.push(jscore); matches.push(result);
					minScore = Math.min(...scores); minIndex = scores.indexOf(minScore);
				}
				// add the score
				result['score'] = jscore

				try {
				let loc_values = Object.values(result["Locations"])

				var result_lat = loc_values[0]['lat']
				var result_long = loc_values[0]['long']

				} catch(err) {
					var result_lat = 0
					var result_long = 0
				}

				let euclid_dist = Math.abs(result_lat - latitude) + Math.abs(result_long - longitude)
				result['euclid_dist'] = euclid_dist

			});

			sorted_results = results.sort((a,b) => b['score'] - a['score'])
			sorted_by_dist_results = sorted_results.sort((a,b) => a['euclid_dis'] - b['euclid_dist'])
			console.log('sending these many',sorted_results.length)
			response.send(sorted_by_dist_results)		
	
			
			// var keyvalues = [];
			// for(var i=0; i < scores.length; i++) {
			// 	keyvalues.push([matches[i], scores[i]]);
			// }

			// // sort by score
			// keyvalues.sort(function compare(kv1, kv2) { return kv2[1] - kv1[1] });
			// matches = [];
			// for(var i =0 ; i < keyvalues.length; i++) matches.push(keyvalues[i][0]);
			// console.log("response.send ", matches.length)
			// response.send(matches);
		});
	});
});

// Make match
app.put('/makeMatch', (request, response) => {
	console.log(new Date(), '+++--- /makeMatch ', request.body);
	db.collection(collectionName).findOneAndUpdate({_id: request.body.id1}, {$set: {Matched: request.body.id2 }});
	db.collection(collectionName).findOneAndUpdate({ _id: request.body.id2 }, {$set: {Matched: request.body.id1 }});

	response.status(201).send("Made match of" + request.body.id1 + " and " + request.body.id2);
});

// Mark need and availability as completed
app.put('/markCompleted', (request, response) => {
	console.log(new Date(), '+++--- /markCompleted ', request.body);
	db.collection(collectionName).findOneAndUpdate({ _id: request.body.id1 }, { $set: { isCompleted: true } });
	db.collection(collectionName).findOneAndUpdate({ _id: request.body.id2 }, { $set: { isCompleted: true } });

	response.status(201).send("Completed " + request.body.id1 + " and " + request.body.id2);
});


// out of order
app.post('/parse', (request, response, next) => {
	console.log(new Date(), '+++--- /parse', request.body);
	console.log(encodeURIComponent(JSON.stringify(request.body)));

	requestM('http://localhost:5000/parse?' + encodeURIComponent( JSON.stringify(request.body) ), (error, resp, body) => {
		if(error) {
			console.log(error);
			error['error'] = 1;
			response.send(CircularJSON.stringify(error));
		}
		else {
			console.log('Parsed info', CircularJSON.stringify(resp.body));
			resp.body.error = 0;
			response.send(JSON.parse(resp.body));
		}
	});
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
	insertTweet["isCompleted"] = true
	console.log('Before inserting tweet')
	db.collection(collectionName).insertOne(insertTweet, function(err, res) {
		if(err) {
			console.log("err ", err)
		}
		console.log('res is ',res.insertedId)
		response.status(201).send({'msg': 'Created resource', '_id': res.insertedId });
	});
	
});

app.listen(port, () => {
	console.log("Server listening on port " + port);
});