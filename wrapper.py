__author__ = 'croman'
# -*- coding: utf-8 -*-

import codecs
import ritter_ner, stanford_ner, validator, resultstonif, polyglot_ner, citius_ner

from sklearn.cross_validation import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier
from sklearn.feature_extraction.text import TfidfVectorizer


def nif(input, type, ner):
    print ner

    if ner == 'ritter':
        results = ritter_ner.ner(input, type)
    elif ner == 'stanford-en':
        results = stanford_ner.ner(input, type, 'english')
    elif ner == 'stanford-es':
        results = stanford_ner.ner(input, type, 'spanish')
    elif ner == 'polyglot-en':
        results = polyglot_ner.ner(input, type, 'en')
    elif ner == 'polyglot-es':
        results = polyglot_ner.ner(input, type, 'es')
    elif ner == 'citius-en':
        results = citius_ner.ner(input, type, 'en')
    elif ner == 'citius-es':
        results = citius_ner.ner(input, type, 'es')
    elif ner == 'voting':
        results = voting(input)
    print "NER completado"

    if type == 'text':
        filename = 'nifresults.ttl'
    elif type == 'file':
        filename = input

    nifresult = resultstonif.convert(results, filename+'.xml')
    print "Conversion a NIF completada"

    return nifresult

def score(corpus, ner):

    if ner == 'ritter':
        results = ritter_ner.ner(corpus+'.ttl', "nif")
        print "NER completado"
    elif ner == 'stanford-en':
        results = stanford_ner.ner(corpus+'.ttl', "nif", 'english')
        print "NER completado"
    elif ner == 'stanford-es':
        results = stanford_ner.ner(corpus+'.ttl', "nif", 'spanish')
        print "NER completado"
    elif ner == 'polyglot-en':
        results = polyglot_ner.ner(corpus+'.ttl', 'nif', 'en')
        print "NER completado"
    elif ner == 'polyglot-es':
        results = polyglot_ner.ner(corpus+'.ttl', 'nif', 'es')
        print "NER completado"
    elif ner == 'citius-en':
        results = citius_ner.ner(corpus+'.ttl', 'nif', 'en')
        print "NER completado"
    elif ner == 'citius-es':
        results = citius_ner.ner(corpus+'.ttl', 'nif', 'es')
        print "NER completado"
    elif ner == 'voting':
        results = voting(corpus)
        print "NER completado"

    nifresults = resultstonif.convert(results, corpus+'.xml')
    print "Conversion a NIF completada"

    resultspath = corpus+'-results.ttl'
    with codecs.open(resultspath, 'wb', encoding='utf-8') as resultsfile:
        resultsfile.write(nifresults)
    print "NIF guardado"

    scores = validator.validate(corpus+'.ttl', resultspath)
    print "Validacion completada"

    return scores

def voting(corpus):
    ner_results = []
    ner_results.append(ritter_ner.ner(corpus+'.ttl', 'nif'))
    ner_results.append(stanford_ner.ner(corpus+'.ttl', 'nif', 'english'))
    ner_results.append(polyglot_ner.ner(corpus+'.ttl', 'nif', 'en'))
    #Ordenar por ids?

    for x in range(0, len(ner_results[0].splitlines())):
        if len(ner_results[0].splitlines()[x].split())!=len(ner_results[1].splitlines()[x].split()):
            print 'CONFLICT: ', len(ner_results[0].splitlines()[x].split()), len(ner_results[1].splitlines()[x].split())
            print ner_results[0].splitlines()[x]
            print ner_results[1].splitlines()[x]

    voting_results = ''
    for x in range(0, len(ner_results[0].splitlines())):
        inEntity = False
        print 'tweet: ',x, len(ner_results[0].splitlines())
        print ner_results[0].splitlines()[x].split('||')[0]
        for y in range(0, len(ner_results[0].splitlines()[x].split('||')[0].split())):
            vote = 0
            for z in range(0, len(ner_results)):
                print 'word: ',y, len(ner_results[z].splitlines()[x].split('||')[0].split())
                print ner_results[z].splitlines()[x].split('||')[0].split()[y]
                entities = ner_results[z].splitlines()[x].split('||')[0].split()[y]
                if not entities.endswith('/O'):
                    vote += 1
            if vote > 1:
                if not inEntity:
                    vote = 'B-ENTITY'
                    inEntity = True
                else:
                    vote = 'I-ENTITY'
            else:
                vote = 'O'
                inEntity = False
            voting_results += ner_results[0].splitlines()[x].split()[y].rsplit('/', 1)[0]+'/'+vote+' '
        voting_results += '||'+ner_results[0].splitlines()[x].split('||')[1]+'\n'

    print voting_results
    return voting_results

def service(input, classifier):
    print classifier
    if classifier == 'ritter':
        results = ritter_ner.ner(input, 'text')
    elif classifier == 'stanford-en':
        results = stanford_ner.ner(input, 'text', 'english')
    elif classifier == 'stanford-es':
        results = stanford_ner.ner(input, 'text', 'spanish')
    elif classifier == 'polyglot-en':
        results = polyglot_ner.ner(input, 'text', 'en')
    elif classifier == 'polyglot-es':
        results = polyglot_ner.ner(input, 'text', 'es')
    elif classifier == 'citius-en':
        results = citius_ner.ner(input, 'text', 'en')
    elif classifier == 'citius-es':
        results = citius_ner.ner(input, 'text', 'es')
    #print results
    entities = []
    types = []
    startIndexes = []
    endIndexes = []

    words = results.split()
    inEntity = False
    entity = ''
    index = 0

    for word in words:

        if "/B-" in word:
            #print "WORD: ", word
            w = word.split("/B-")[0]
            type = word.split("/B-")[1]
            if inEntity == True:
                endIndexes.append(index-1)
                entities.append(entity)
                types.append(type)
                entity = ''
                inEntity = False

            startIndexes.append(index)
            index += len(w) + 1
            entity += w
            inEntity = True

        elif "/I-" in word:
            w = word.split("/I-",1)[0]
            index += len(w) + 1
            entity += ' '
            entity += w

        elif inEntity == True:
            endIndexes.append(index-1)
            if not word.startswith('||'):
                w = word.split("/O",1)[0]
                index += len(w) + 1
            entities.append(entity)
            types.append(type)
            entity = ''
            inEntity = False

        elif "/O" in word:
            w = word.split("/O",1)[0]
            index += len(w) + 1
    if inEntity == True:
        endIndexes.append(index)
        types.append(type)
        entities.append(entity)
        entity = ''
        inEntity = False

    return (entities, types, startIndexes, endIndexes)





#print 'Brian: \n'+score('Brian Collection')
#print '\nMena: \n'+score('Mena Collection')
#print '\nMicroposts2014: \n'+score('Microposts2014_Collection_train')
#print 'Test: \n'+score('testingcorpus')
#print voting('testingcorpus')
#print score('Microposts2014_Collection_train', 'polyglot-en')
"""with codecs.open("datasets/esp.testa.out", "rb", encoding="utf-8") as inputfile:
    i = inputfile.read()
    print service(i, 'citius-es')"""

#print 'Brian: \n'+nif('Mena Collection')
#print nif('Brian Collection', 'stanford')
#print adaboost('Brian Collection')
#print nif('datasets/Mena Collection', 'file', 'polyglot-en')

