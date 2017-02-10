#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ner.py: Name Entity Extractor."""

from optparse import OptionParser
import logging
from time import time
from pos import POSTagger
import json
import re
from math import log
import numpy as np
from itertools import izip

from lists.lists import WEEK_MONTHS, CAPITALS
from lists.sports import SPORTS
from lists.jobs import JOBS
from lists.demonyms import DEMONYMS

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

UNIFY = {'I-MISC': 'MISC', 'B-MISC': 'MISC', 'I-ORG': 'ORG', 'B-ORG': 'ORG',
         'I-LOC': 'LOC', 'B-LOC': 'LOC', 'I-PER': 'PER', 'B-PER': 'PER'}

COMBINED  = WEEK_MONTHS.union(SPORTS).union(JOBS).union(CAPITALS)

class NERTagger(object):
  def __init__(self, words, contexts, postagger, coef_file):
    self.words = words
    self.contexts = contexts
    self.tags = ['LOC', 'PER', 'ORG', 'MISC']
    self.num_classes = len(self.tags)
    self.defaultprob = self.default_prob()
    self.map = dict(zip(self.tags, range(len(self.tags))))
    self.reversed_map = dict(zip(range(len(self.tags)), self.tags))
    self.numeric = re.compile(r'(.*?|)([0-9]+[.,-]*)+(.*?|)', flags=re.U|re.I)
    self.pos_tagger = postagger
    try:
      f = open(coef_file, 'r')
      self.coef, self.intercept = json.load(f)
      self.coef, self.intercept = np.array(self.coef), np.array(self.intercept)
      f.close()
    except IOError:
      pass
    self.words[1].extend(self.default_prob())
    self.contexts[1].extend(self.default_prob())

  def batch_tag(self, sents, chunks=None):
    if not chunks:
      sents_pos = self.pos_tagger.batch_tag(sents)
      chunks = self.batch_detect(sents, sents_pos)
    return self.batch_classify(sents, chunks)

  def batch_classify(self, sents, chunks):
    return [self.classify(sent, chunk) for sent,chunk in izip(sents, chunks)]

  def batch_detect(self, sents, sents_pos):
    return [self.detect(sent,pos) for sent,pos in izip(sents, sents_pos)]

  def tag(self, sent):
    return self.batch_tag([sent])[0]

  def detect(self, words, postags):
    sent = []
    tags = {'NNP', 'NNPS'}
    connectors = {'&', 'de', 'of'}
#    connectors = {}
    sent_len = len(words)
    for i in range(sent_len):
      found = False
      word = words[i]
      if word.isupper():
        word = word.capitalize()
      tag = postags[i]
      if tag in tags and not word in COMBINED:
        sent.append("I")
        found = True
      elif word in connectors:
        if i > 0 and i < sent_len-1 and (postags[i-1] in tags) and (postags[i+1] in tags):
            sent.append("I")
            found = True
      elif word in DEMONYMS:
        sent.append("I")
        found = True
      if not found:
        sent.append("O")
    if len(sent) != len(words):
      pdb.set_trace()
    return sent

  def classify(self, sent, tags):
#    cleaned_sent = [self.numeric.sub('\g<1>0\g<3>', w) for w in sent]
    cleaned_sent = sent
    chunks = self._extract_chunks(tags)
    for chunk in chunks:
      start, end = chunk
      scores = self.segment_scores(cleaned_sent, tags, chunk)
      numeric_tag = self.predict(scores)
      tag = self.reversed_map.get(numeric_tag, numeric_tag) 
      for i in range(start, end+1):
        tags[i] = tag
    return tags

  def predict(self, scores):
    return np.argmax(np.dot([scores], self.coef) + self.intercept, axis=1)[0]

  def segment_scores(self, sent, tags, chunk):
    start, end = chunk
    prev_, next_ = '<E>', '<E>'
    if start != 0:
      prev_ = sent[start-1]
    if end != len(sent)-1:
      next_ = sent[end+1]
    context = (prev_, next_)
    words = sent[start:end+1]
    chunk_scores = self.get_scores(words, self.words)
    context_scores = self.get_scores(context, self.contexts)
    scores = chunk_scores + context_scores
    return scores

  def _extract_chunks(self, sequence):
    chunks = []
    entity = False
    for i in range(len(sequence)):
      if sequence[i] != 'O' and not entity:
        start = i
        entity = True
      if sequence[i] == 'O' and entity:
        end = i-1
        chunks.append((start, end))
        entity = False
      if i == len(sequence)-1 and entity:
        end = i  
        chunks.append((start, end))
        entity = False
    return chunks

  def get_prob_dist(self, dist):
    counts = self.get_counts(dist)
    return self.get_prob(counts)

  def get_prob(self, counts):
    total = sum(counts)
    return [log((c+1.0)/(total+len(self.tags)), 2.0) for c in counts]
  
  def get_counts(self, dist):
    return [dist.get(tag, 0.0) for tag in self.tags]

  def get_prob_unigram(self, dists, unigram):
    try:
      return self.get_prob_dist(dists[unigram])
    except:
      return self.default_prob()

  def default_prob(self):
      return [log(1.0/len(self.tags), 2.0) for t in self.tags]

  def get_scores(self, sequence, dists):
    words, probs = dists
    default = len(probs) - self.num_classes
    scores = [0.0 for t in self.tags]
    i = 0
    for key in sequence:
      index = words.get(key, default)
      probs_ = probs[index : index+self.num_classes]
      scores = [x+y for (x,y) in zip(probs_, scores)]
      i += 1
    scores = [x/i for x in scores]
    return scores

  def _get_X_y(self, sent, tags):
#    cleaned_sent = [self.numeric.sub('\g<1>0\g<3>', w) for w in sent]
    cleaned_sent = sent
    X, y = [], []
    chunks = self._extract_chunks(tags)
    for chunk in chunks:
      scores = self.segment_scores(cleaned_sent, tags, chunk)
      X.append(scores)
      start, end = chunk
      tag_  = UNIFY.get(tags[start], tags[start])
      numerical_tag_ = self.map.get(tag_, -1)
      y.append(numerical_tag_)
    return X,y 

  def get_X_y(self, sents, iob_sents):
    X = []
    y = []
    for i in range(len(sents)):
      X_, y_ = self._get_X_y(sents[i], iob_sents[i])
      X.extend(X_)
      y.extend(y_)
    logging.debug("Calculated the features")
    return X, y


def main(options, args):
  pass

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="filename", help="Input file")
  parser.add_option("-l", "--log", dest="log", help="log verbosity level",
                    default="INFO")
  (options, args) = parser.parse_args()

  numeric_level = getattr(logging, options.log.upper(), None)
  logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
  main(options, args)

