__author__ = 'croman'
# -*- coding: utf-8 -*-

from polyglot.detect import Detector
from polyglot.text import Text, Word
import rdflib
from lxml import etree
import subprocess
import tweetstotxt
import codecs
import re

def ner(datasetfile, format, language):

    tweetids = []
    tweets = ''
    tweetdict = {}



    if format == 'xml-collection':
        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//Tweet'):
            tweetText = tweet.xpath('./TweetText/text()')[0]
            tweets += ' '.join(re.findall(r"[\w:/!#$%&*+,\-:;?@^_`{|}~.]+|[\"'()[\]<=>]", tweetText))+"\n"
            tweetids.append(tweet.xpath('./TweetId/text()')[0])
        tweets = tweets.encode('utf-8')
        with codecs.open(datasetfile.split('.xml')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)


    elif format == 'xml-socialtv':
        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//tweet'):
            tweetText = tweet.xpath('./text()')[0]
            tweets += ' '.join(re.findall(r"[\w:/!#$%&*+,\-:;?@^_`{|}~.]+|[\"'()[\]<=>]", tweetText))+"\n"
            tweetids.append(tweet.get('id'))
        tweets = tweets.encode('utf-8')
        with codecs.open(datasetfile.split('.xml')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)


    elif format == "nif":

        a = rdflib.Graph()
        a.parse(datasetfile, format='n3')

        for s, p, o in a:
            if s.endswith(',') and p.endswith('isString'):
                tweetid = s.split('#')[0].split('.xml/')[1]
                tweetdict[tweetid] = ' '.join(re.findall(r"[\w:/!#$%&*+,\-:;?@^_`{|}~.]+|[\"'()[\]<=>]", o))

        for key in sorted(tweetdict):
            tweetids.append(key)
            tweets += tweetdict[key]+'\n'
        tweets = tweets.encode('utf-8')

        with codecs.open(datasetfile.split('.ttl')[0]+'.txt', 'wb', encoding='utf-8') as txt:
            tweets = tweets.decode('utf-8')
            txt.write(tweets)
    elif format == "text":
        filename = 'nerdy-input.txt'
        with codecs.open(filename, 'wb', encoding='utf-8') as txt:
            txt.write(datasetfile)
            datasetfile = 'nerdy-input.ttl'



    """for t in tweets.split('\n'):
        text = Text(t)
        detector = Detector(t.decode('utf-8'))
        print text.string.encode('utf-8')
        print (detector.language)"""
    p = subprocess.Popen(['polyglot', '--lang', language, 'ner', '--input', datasetfile.split('.ttl')[0]+'.txt'], stdout=subprocess.PIPE)
    output,err = p.communicate()
    results = ''
    tweetoutput = output.split('\n\n')
    tweetoutput.pop()
    for x in range(0, len(tweetoutput)):
        inEntity = False
        for line in tweetoutput[x].splitlines():
            if len(line.split()) < 2:
                word = line.split('O')[0].decode('utf-8')
                entity = u'O'
            else:
                word = line.split()[0].decode('utf-8')
                entity = line.split()[1].decode('utf-8')
            if entity != 'O' and inEntity:
                entity = 'I-'+entity.split('I-')[1]
            elif entity != 'O' and inEntity == False:
                entity = 'B-'+entity.split('I-')[1]
                inEntity = True
            else:
                inEntity = False
            results += word + u'/' + entity + u' '
        if tweetids:
            results += u"||"+tweetids[x]
        results += u"\n"
    return results

#print ner("Xavi marco un gol a Cristiano y Casillas es de Apple Inc", "text", "es")
#print ner("Barack Obama is the president of the United States of America and the leader of The Beatles", "text", "en")
#print ner('El gobierno de Brasil condecoro a Ronaldo en Rio de Janeiro', 'text', 'es')
#print ner('Messi scored three goals against Chelsea. Mourinho must be angry.', 'text', 'en')