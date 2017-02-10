__author__ = 'croman'

import codecs
from lxml import etree
import rdflib

def convert(datasetfile, format):
    tweets = ''
    tweetids = []

    if format == 'xml-collection':
        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//Tweet'):
            tweetText = tweet.xpath('./TweetText/text()')[0]
            tweets += tweetText+"\n"
            tweetids.append(tweet.xpath('./TweetId/text()')[0])
        tweets = tweets.encode('utf-8')
        with codecs.open(datasetfile.split('.xml')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)

    elif format == 'xml-socialtv':
        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//tweet'):
            tweetText = tweet.xpath('./text()')[0]
            tweets += tweetText+'\n'
            tweetids.append(tweet.get('id'))
        tweets = tweets.encode('utf-8')
        with codecs.open(datasetfile.split('.xml')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)

    elif format == 'nif':
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

        with codecs.open(datasetfile.split('.ttl')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)