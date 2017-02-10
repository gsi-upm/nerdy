__author__ = 'croman'
# -*- coding: utf-8 -*-

import rdflib
from lxml import etree
from nltk.tag.stanford import StanfordNERTagger
import re
import os

java_path = "/usr/lib/jvm/java-8-oracle/jre/bin/java" # replace this
os.environ['JAVAHOME'] = java_path
BASEPATH = os.path.dirname(os.path.abspath(__file__))

def ner(datasetfile, format, language):

    tweets = ""
    tweetids = []
    if language == 'english':
        st = StanfordNERTagger(BASEPATH+'/classifiers/english.all.3class.distsim.crf.ser.gz', BASEPATH+'/classifiers/stanford-ner.jar', encoding='utf8')
    elif language == 'spanish':
        st = StanfordNERTagger(BASEPATH+'/classifiers/spanish.ancora.distsim.s512.crf.ser.gz', BASEPATH+'/classifiers/stanford-ner.jar', encoding='utf8')

    if format == 'xml':

        dataset = etree.parse(datasetfile)
        for tweet in dataset.xpath('//Tweet'):
            tweetText = tweet.xpath('./TweetText/text()')[0]
            tweets += ' '.join(re.findall(r"[\w:/!#$%&*+,\-:;?@^_`{|}~.]+|[\"'()[\]<=>]", tweetText))+"\n"
            tweetids.append(tweet.xpath('./TweetId/text()')[0])

        tweets = tweets.encode('utf-8')

    elif format == "nif":

        tweetdict = {}
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
        #print tweets

    elif format == "text":
        tweets = datasetfile

    tweetlist = []
    for t in tweets.splitlines():
        newtweet = []
        for word in t.split():
            newword = u''
            if word.endswith(",") or word.endswith(".") or word.endswith(")") or word.endswith("\'"):
                newtweet.append(word[:-1])
                newtweet.append(word[-1])
            else:
                newtweet.append(word)
        #print newtweet
        tweetlist.append(newtweet)


    results = ''
    tagged = []

    for tweet in tweetlist:
        tagged.append(st.tag(tweet))
        #print tagged[-1]
    #print len(tagged)

    inEntity = False
    for line in tagged:
        #print line
        for (word, entity) in line:
            if entity != 'O' and inEntity:
                entity = 'I-'+entity
            elif entity != 'O' and inEntity == False:
                entity = 'B-'+entity
                inEntity = True
            else:
                inEntity = False
            results += word + '/' + entity + ' '
    if tweetids:
        results += "||"+tweetids[x]
    results += "\n"

    #print results
    return results

#print ner("Xavi marco un gol a Cristiano y Casillas es de Apple Industries", "text", "spanish")
#print ner('El gobierno de Brasil condecoro a Ronaldo en Rio de Janeiro', 'text', 'spanish')
#print ner('Messi scored three goals against Chelsea. Mourinho must be angry.', 'text', 'english')
