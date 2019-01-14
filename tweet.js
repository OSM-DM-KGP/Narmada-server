const mongoose = require('mongoose');

const locationSchema = new mongoose.Schema({
});
// can't have variable keys
// "rieti" : {
//     "lat" : 42.404366,
//     "long" : 12.868538
// }

//     Resources: [{
// resource: String,
//     quantity: String,
//     }],

const tweetSchema = new mongoose.Schema({
    _id: { // id for tweet
        type: String,
        unique: true,
        required: true,
    },
    lang:  String,
    text: { // tweet text
        type: String,
        required: true,
    },
    Classification: { // Classification according to system
        type: String,
        enum: ['Need','Availability'],
    },
    isCompleted: { // only after status is full
        type: Boolean,
        default: false,
    },
    username:  {
        type: String,
        default: '',
    },
    Matched: { // id of matched tweet
        type: String,
        default: '',
    },
    Locations: {}, // all possible detected locations
    Sources: [{ // sources - names of people, NGO's, etc
        type: String
    }],
    Resources: {}, // detected json of jsons - each json has resource and quantity
    ResourceWords: {
        type: Array,
        default: [],
    },
    status: {
        type: Number,
        default: 0,
    },
    Contact: { // straight forwarsd
        Email: [{
            type: String,
        }],
        "Phone number": [{
            type: String,
        }],     
    },
    created: { // created time - used for matching
        type: Date, 
        default: Date.now,
    },
    url: { // tweet url in case we want to reply to them
        type: String,
        default: ''
    }

}, { collection: 'tweets'});

module.exports = exports = mongoose.model('Tweet', tweetSchema);


