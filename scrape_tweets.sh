#!/bin/bash

cd /home/narmada/Narmada-server
source env/bin/activate
echo "running old_tweet"
python3 get_old_tweet.py
gunzip latest_tweets.jsonl.gz
python3 parseTweetsAndAdd2DB.py
rm -f latest_tweets.jsonl
