const mongoose = require('mongoose');

const locationSchema = new mongoose.Schema({
});
// can't have variable keys
// "rieti" : {
//     "lat" : 42.404366,
//     "long" : 12.868538
// }

const tweetSchema = new mongoose.Schema({
    _id: {
        type: String,
        unique: true,
        required: true,
    },
    lang:  String,
    text: {
        type: String,
        required: true,
    },
    Classification: {
        type: String,
        enum: ['Need','Availability'],
    },
    isCompleted: {
        type: Boolean,
        default: false,
    },
    username:  String,
    Matched: Number,
    Locations: {},
    Sources: [{
        type: String
    }],
    Resources: [{
        resource: String,
        quantity: String,
    }],
    status: {
        type: Number,
        default: 0,
    },
    Contact: {
        Email: [{
            type: String,
        }],
        "Phone number": [{
            type: String,
        }],     
    },
    created: {
        type: Date, 
        default: Date.now,
    },

}, { collection: 'tweets'});

module.exports = exports = mongoose.model('Tweet', tweetSchema);


