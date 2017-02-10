__author__ = 'croman'
# -*- coding: utf-8 -*-


import codecs
import sys
import os

def convert(nerfile, corpusfile):

    ner = nerfile.splitlines()
    entities = []
    tweets = []
    tweetids = []
    startIndexes = []
    endIndexes = []

    for line in ner:
        words = line.split()
        inEntity = False
        tweet = ''
        tweetEntities = []
        starts = []
        ends = []
        entity = ''
        index = 0
        tweetids.append(line.split('||', 2)[1])

        for word in words:

            if word.__contains__('B-'):
                w = word.split("/B-",1)[0]
                tweet += w

                if inEntity == True:
                    ends.append(index-1)
                    tweetEntities.append(entity)
                    entity = ''
                    inEntity = False

                starts.append(index)
                index += len(w) + 1
                entity += w
                inEntity = True

            elif word.__contains__('I-'):
                w = word.split("/I-",1)[0]
                index += len(w) + 1
                tweet += w
                entity += ' '
                entity += w

            elif inEntity == True:
                ends.append(index-1)
                if not word.startswith('||'):
                    w = word.split("/O",1)[0]
                    index += len(w) + 1
                    tweet += w
                tweetEntities.append(entity)
                entity = ''
                inEntity = False


            elif word.__contains__("/O"):
                w = word.split("/O",1)[0]
                index += len(w) + 1
                tweet += w

            tweet += ' '

        if inEntity == True:
            endIndexes.append(ends)
            tweetEntities.append(entity)
            entity = ''
            inEntity = False

        tweets.append(tweet.split(' ||',1)[0][:-2])
        startIndexes.append(starts)
        endIndexes.append(ends)
        entities.append(tweetEntities)

    """nermentions = 0

    for entity in entities:
        print len(entity)
        nermentions += len(entity)

    print nermentions

    print len(entities)"""


    results = "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    results += "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    results += "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    results += "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    results += "@prefix nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> .\n"
    results += "@prefix itsrdf: <http://www.w3.org/2005/11/its/rdf#> .\n\n"

    results += "<"+corpusfile+"#char=0,>\n"
    results += "\ta nif:String , nif:Context , nif:RFC5147String ;\n"
    results += "\tnif:sourceUrl <"+corpusfile+"/> .\n\n"

    for x in range(0,len(tweets)):

        results += "<"+corpusfile+"/"+tweetids[x]+"#char=0,>\n"
        results += "\ta nif:String , nif:Context , nif:RFC5147String ;\n"
        results += "\tnif:isString \"\"\""+tweets[x]+"\"\"\" ;\n"
        results += "\tnif:beginIndex \"0\"^^xsd:nonNegativeInteger ;\n"
        results += "\tnif:endIndex \""+str(len(tweets[x]))+"\"^^xsd:nonNegativeInteger .\n\n"

        for y in range(0,len(entities[x])):
            #print startIndexes[x], endIndexes[x], entities[x]
            results += "<"+corpusfile+"/"+tweetids[x]+"#char="+str(startIndexes[x][y])+","+str(endIndexes[x][y])+">\n"
            results += "\ta nif:String , nif:RFC5147String ;\n"
            results += "\tnif:anchorOf \"\"\""+entities[x][y]+"\"\"\" ;\n"
            results += "\tnif:beginIndex \""+str(startIndexes[x][y])+"\"^^xsd:nonNegativeInteger ;\n"
            results += "\tnif:endIndex \""+str(endIndexes[x][y])+"\"^^xsd:nonNegativeInteger ;\n"
            results += "\ta nif:Phrase .\n\n"
            #results += "\titsrdf:taIdentRef "++" .\n\n"


    return results

