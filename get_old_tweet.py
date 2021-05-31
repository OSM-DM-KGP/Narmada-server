import gzip
import json
import os, sys
import twint
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import nest_asyncio

nest_asyncio.apply()


def fetch_all(keywords, outfile = 'tw.txt.gz', STARTDATE = None, ENDDATE = None, user = None, english = False, idset = None):
        print("\n##########################################")
        print("FETCHING BETWEEN", STARTDATE, "and", ENDDATE, "user:", user)
        print("##########################################\n")
        
        current_time_object = datetime.now() - timedelta(hours=5.5)
        hour_before_time_object = current_time_object - timedelta(hours=1)

        ENDDATE = current_time_object.strftime("%Y-%m-%d %H:%M:%S")
        STARTDATE = hour_before_time_object.strftime("%Y-%m-%d %H:%M:%S")

        print('START DATE ', STARTDATE)
        print('END DATE', ENDDATE)
        for _retry in range(3):
                try:
                        if not idset: 
                                idset = set()
                                fileopt = 'w'
                        else:
                                fileopt = 'a'

                        with gzip.open(os.path.join(outfile), fileopt) as fout:
        
                                size = 15
                                for kstart in range(0, len(keywords), size):
                                        #time.sleep(1)
                                        print('Fetching set: %d'%(kstart / size), flush = True)
                                        keys = ' OR '.join(keywords[kstart : kstart + size])
                                        #print(keys, flush = True)
                
                                        # keys = ' OR '.join(keywords)
                                        # print(keys, flush = True)
                                        c = twint.Config()
                                        if STARTDATE:
                                                c.Since = STARTDATE
                                        if ENDDATE:
                                                c.Until = ENDDATE
                                
                                        if user:
                                                c.Username = user
                                        
                                        
                                        c.Store_object = True
                                        c.Hide_output = True
                                        
                                        tweets = []
                                        c.Store_object_tweets_list = tweets              
                                        c.Search = keys
                                        twint.run.Search(c)
                
                                        print(len(tweets), '\n')
                
                                        for tweet in tweets:
                                                if tweet.id not in idset and (not english or tweet.lang == 'en'):
                                                        idset.add(tweet.id)
                                                        fout.write(json.dumps(tweet.__dict__).encode('utf8') + b'\n')
                                                #         fout.write(json.dumps(tweet.__dict__) + '\n')
                        break
                # except KeyboardInterrupt: raise KeyboardInterrupt 
                except Exception as e:
                        print('Waiting...', _retry + 1)
                        print('error is ',e)
                        time.sleep(300)

        #if fout: fout.close()
        return idset



def fetch_between(keywords, start, end, outdir):
        s = datetime.strptime(start, '%Y-%m-%d')
        e = datetime.strptime(end, '%Y-%m-%d')
        try: os.mkdir(os.path.join(outdir, 'live'))
        except: pass

        while s < e:
                nxt = s + timedelta(days = 1)
                nxtstr = nxt.strftime('%Y-%m-%d')
                currstr = s.strftime('%Y-%m-%d')
                s = nxt
                
                fetch_all(keywords, os.path.join(outdir, 'live',  '%s.json.gz'%currstr), STARTDATE= currstr, ENDDATE=nxtstr)



def fetch_hourly(keywords, outdir, start = None):
        if start is None: s = datetime.utcnow()
        else: s = datetime.strptime(start, '%Y-%m-%d')

        try: os.mkdir(os.path.join(outdir, 'live'))
        except: pass

        ids = set()
        try:
                tmpstdout = sys.stdout
                
                while True:
                        nxt = s + timedelta(days = 1)
                        nxtstr = nxt.strftime('%Y-%m-%d')
                        currstr = s.strftime('%Y-%m-%d')
                        
                        nowstr = datetime.utcnow().strftime('%Y-%m-%d')
                        outfile = os.path.join(outdir, 'live',  '%s.json.gz'%currstr)
                        
                        # uncomment line below to suppress logs, and comment the line after
                        # with open('DUMP.txt', 'w') as sys.stdout:
                        with open('DUMP.txt', 'w') as fo:
                                ids = fetch_all(keywords, outfile, STARTDATE= currstr, ENDDATE=nxtstr, idset = ids)
                                time.sleep(60)
                                
                                if nxtstr <= nowstr:
                                        s = nxt
                                        ids = set()

                                        print("####Completed", currstr, file = tmpstdout)

                                else:
                                        print('\n\n########### Recollecting %s #############\n\n'%currstr)
                                        time.sleep(3600)

        except KeyboardInterrupt:
                print('\nINCOMPLETE FILE: ' + outfile, file = tmpstdout)
        
        finally:
                sys.stdout = tmpstdout


        

############# READ KEYS
with open('keywords.txt') as fp:
        cities = fp.readline().split()
        keywords1 = fp.read().split() + ['corona '+ x.lower() for x in cities] + ['covid ' + x.lower() for x in cities]+ ['lockdown ' + x.lower() for x in cities]
        keywords1 = ['(' + key.strip() + ')' for key in keywords1]



if __name__ == '__main__':
        # y = 2021
        # output_dir = 'covind_tweets/'
        keys = keywords1
        
        print(keys)

        
        # for m in range(1,4):
        #         s = '%04d-%02d-01'%(y, m)
        #         e = '%04d-%02d-01'%(y, m+1)
        #         fetch_all(keys, os.path.join(output_dir, '%04d-%02d.jsonl.gz'%(y, m)), STARTDATE= s, ENDDATE=e)
        #         time.sleep(60)
       
        
        fetch_all(keys, 'latest_tweets.jsonl.gz', STARTDATE = '2021-05-19 03:00:00', ENDDATE = '2021-05-19 23:00:00', english = True)
        #fetch_between(keys, '2021-03-01', '2021-04-24', output_dir)
        # fetch_hourly(keys, output_dir, '2021-04-26')
