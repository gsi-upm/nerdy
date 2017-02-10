__author__ = 'croman'

from pipeline import pipe
from lxml import etree
import rdflib

def ner(datasetfile, format):
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
    indexes = []
    tweetlines = tweets.split('\n')
    for t in tweetlines:
        tweetlength = 0
        for word in t.split():
            tweetlength += len(word)
        print tweetlength
        indexes.append(tweetlength)
    options = {'log':'DEBUG', 'conf': 'pipeline/settings.py', 'text': tweets}
    results = pipe.main(options, [])
    print 'results: ' + results
    x = 0
    finalresults = ''
    resultslines = results.splitlines()
    finalresults = ''

    for i in indexes:
        print i
        length = 0
        tweetresult = ''
        print x
        print resultslines[x]
        while length < i:
            if resultslines[x] != '':
                entity = resultslines[x].split('\t')
                print entity
                length += len(entity[0])
                tweetresult += entity[0]+'/'+entity[1]+' '
                x += 1
                #print 'x=', x
                print 'length: ', length
            else:
                print 'ok'
                x += 1
        print tweetresult
        finalresults += tweetresult[:-1]+' END\n'
    print finalresults

ner("Mena Collection.ttl", "nif")



"""__author__ = 'croman'

from pipeline import pipe
from lxml import etree
import rdflib

def ner(datasetfile, format):
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
    indexes = []
    tweetlines = tweets.split('\n')
    for t in tweetlines:
        tweetlength = 0
        for word in t.split():
            tweetlength += len(word)
        indexes.append(tweetlength)
    options = {'log':'DEBUG', 'conf': 'pipeline/settings.py', 'text': tweets}

    results = pipe.main(options, [])
    print results
    x = 0
    finalresults = ''
    for i in indexes:
        print i
        resultslines = results.split('\n')
        length = 0
        while length < i:
            entity = resultslines[x].split('\t')
            print resultslines[x]
            length += len(entity[0])
            if len(entity)>1:
                finalresults += entity[0]+'/'+entity[1]+' '
                x += 1
                print 'x=', x
                print 'length: ', length
        finalresults = finalresults[:-1]+' END\n'
    print finalresults

ner("Mena Collection.ttl", "nif")"""