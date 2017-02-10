__author__ = 'croman'
# -*- coding: utf-8 -*-

import codecs
from lxml import etree
import rdflib
import subprocess
import os
BASEPATH = os.path.dirname(os.path.abspath(__file__))

def ner(datasetfile, format, language):
    tweets = ""
    tweetids = []

    if format == 'xml':

        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//Tweet'):
            tweetText = tweet.xpath('./TweetText/text()')[0]
            tweets += tweetText+"\n"
            tweetids.append(tweet.xpath('./TweetId/text()')[0])

        tweets = tweets.encode('utf-8')

    elif format == "nif":

        tweetdict = {}
        a = rdflib.Graph()
        a.parse(datasetfile, format='n3')

        for s, p, o in a:
            if s.endswith(',') and p.endswith('isString'):
                tweetid = s.split('#')[0].split('.xml/')[1]
                tweetdict[tweetid] = o

        for key in sorted(tweetdict):
            tweetids.append(key)
            tweets += tweetdict[key]+'\n'
        tweets = tweets.encode('utf-8')
        print tweets

    elif format == "text":
        tweets = datasetfile

    if format == "text":
        txtname = 'nerdy-input.txt'
    else:
        txtname = datasetfile.split('.ttl')[0]+'.txt'
    with codecs.open(BASEPATH+'/'+txtname, 'wb', encoding='utf-8') as txt:
        txt.write(tweets)
    os.chdir(BASEPATH+'/classifiers/CitiusTools')
    citius = subprocess.Popen(['./nec.sh', language, BASEPATH+'/'+txtname],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    results, err = citius.communicate()
    subprocess.Popen(['rm', BASEPATH+'/'+txtname])
    print results
    print "ERROR: ",err
    finalresults = ''
    entities = []
    y = 0
    for x in range(0,len(results.splitlines()[1:])):
        words = results.splitlines()[1:][x].split()
        if len(words)<1:
            entities.append('||'+str(y)+'\n')
            continue
        entity = ''
        if len(words)<3 or not words[2].startswith('NP'):
            entity = 'O'
        elif words[2][4]=='S':
            entity = 'PERSON'
        elif words[2][4]=='G':
            entity = 'LOCATION'
        elif words[2][4]=='O':
            entity = 'ORGANIZATION'
        elif words[2][4]=='V':
            entity = 'OTHER'
        first = True
        for w in words[0].split('_'):
            if entity == 'O':
                type = entity
            elif first:
                type = 'B-'+entity
                first = False
            else:
                type = 'I-'+entity
            entities.append(w+'/'+type)
    finalresults = ' '.join(entities)

    return finalresults

    #print len(results)
    #print results.splitlines()

#print ner('Microposts2014_Collection_train.ttl', 'nif', 'es')
#print ner('El gobierno de Brasil condecoro a Ronaldo en Rio de Janeiro', 'text', 'es')
#print ner('Messi scored three goals against Chelsea. Mourinho must be angry.', 'text', 'en')