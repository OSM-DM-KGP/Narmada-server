# Narmada-server
Backend server for Narmada webapp.

This is the repository for the paper titled "NARMADA: Need and Available Resource Managing Assistant for Disasters and Adversities" which is to be presented at the [ACL Workshop on Natural Language Processing for Social Media (SocialNLP)](https://sites.google.com/site/socialnlp2020/) 2020.

Please refer to our website https://osm-dm-kgp.github.io/Narmada/ for up-to-date information (contains API description).

Other repositories associated with this project:
* Frontend app - [OSM-DM-KGP/Narmada](https://github.com/OSM-DM-KGP/Narmada)

## Citation

If you use the codes, please cite the following paper:
```
 @inproceedings{hiware-socialnlp20,
   author = {Hiware, Kaustubh and Dutt, Ritam and Sinha, Sayan and Patro, Sohan and Ghosh, Kripabandhu and Ghosh, Saptarshi},
   title = {{NARMADA: Need and Available Resource Managing Assistant for Disasters and Adversities}},
   booktitle = {{Proceedings of ACL Workshop on Natural Language Processing for Social Media (SocialNLP)}},
   year = {2020}
  }
```

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