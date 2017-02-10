#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pos.py: Part Of Speech Tagger."""

from optparse import OptionParser
import logging
import re
from lists.lists import NUMERALS
from time import time

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

class RegexpTagger(object):
    """
    Regular Expression Tagger
    
    The RegexpTagger assigns tags to tokens by comparing their
    word strings to a series of regular expressions.  The following tagger
    uses word suffixes to make guesses about the correct Brown Corpus part
    of speech tag:
    
        >>> from nltk.corpus import brown
        >>> test_sent = brown.sents(categories='news')[0] 
        >>> regexp_tagger = RegexpTagger(
        ...     [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
        ...      (r'(The|the|A|a|An|an)$', 'AT'),   # articles
        ...      (r'.*able$', 'JJ'),                # adjectives
        ...      (r'.*ness$', 'NN'),                # nouns formed from adjectives
        ...      (r'.*ly$', 'RB'),                  # adverbs
        ...      (r'.*s$', 'NNS'),                  # plural nouns
        ...      (r'.*ing$', 'VBG'),                # gerunds
        ...      (r'.*ed$', 'VBD'),                 # past tense verbs
        ...      (r'.*', 'NN')                      # nouns (default)
        ... ])
        >>> regexp_tagger.tag(test_sent)
        [('The', 'AT'), ('Fulton', 'NN'), ('County', 'NN'), ('Grand', 'NN'), ('Jury', 'NN'),
        ('said', 'NN'), ('Friday', 'NN'), ('an', 'AT'), ('investigation', 'NN'), ('of', 'NN'),
        ("Atlanta's", 'NNS'), ('recent', 'NN'), ('primary', 'NN'), ('election', 'NN'),
        ('produced', 'VBD'), ('``', 'NN'), ('no', 'NN'), ('evidence', 'NN'), ("''", 'NN'),
        ('that', 'NN'), ('any', 'NN'), ('irregularities', 'NNS'), ('took', 'NN'),
        ('place', 'NN'), ('.', 'NN')]

    :type regexps: list(tuple(str, str))
    :param regexps: A list of ``(regexp, tag)`` pairs, each of
        which indicates that a word matching ``regexp`` should
        be tagged with ``tag``.  The pairs will be evalutated in
        order.  If none of the regexps match a word, then the
        optional backoff tagger is invoked, else it is
        assigned the tag None.
    """

    yaml_tag = '!nltk.RegexpTagger'

    def __init__(self, regexps):
        """
        """
        labels = ['g'+str(i) for i in range(len(regexps))]
        tags = [tag for regex, tag in regexps]
        self._map = dict(zip(labels, tags))
        regexps_labels = [(regex, label) for ((regex,tag),label) in zip(regexps,labels)]
        self._regexs = re.compile('|'.join(['(?P<%s>%s)' % (label, regex) for regex,label in regexps_labels]))

    def tag_one(self, token):
        m = self._regexs.match(token)
        if m:
          return self._map[m.lastgroup]
        return None

    def tag(self, tokens):
      return [self.tag_one(token) for token in tokens]

    def __repr__(self):
        return '<Regexp Tagger: size=%d>' % len(self._regexps)


def RegexTagger():
  patterns = [(r'^-?[0-9]+(\\/[0-9]+)?(.[0-9]+)?$', 'CD'),
              (r'.*ness$', 'NN'),
              (r'.*ment$', 'NN'),
              (r'^[A-Z].*s$', 'NNPS'),
              (r'^[A-Z].*$', 'NNP'),
              (r'.*ly$', 'RB'),
              (r'.*ing$', 'VBG'),
              (r'.*ed$', 'VBD'),
              (r'.*ould$', 'MD'),
              (r'.*able$', 'JJ'),
              (r'.*ful$', 'JJ'),
              (r'.*ious$', 'JJ'),
              (r'.*ble$', 'JJ'),
              (r'.*ic$', 'JJ'),
              (r'.*ive$', 'JJ'),
              (r'.*ic$', 'JJ'),
              (r'.*est$', 'JJ'),
              (r'^a$', 'PREP'),
              (r'.*s$', 'NNS'),
              (r'.*-.*', 'JJ'),
              (r'.*', 'NN')]
  return RegexpTagger(patterns)


class POSTagger(object):
  def __init__(self, unigrams, bigrams, trigrams):
    self.unigrams = unigrams
    self.update_unigrams()
    self.bigrams = bigrams
    self.trigrams = trigrams
    self.regex = RegexTagger()

  def update_unigrams(self):
    known = {".": ".", ":": ":", "...": ":", "(": "(", "``":"``",
             "-RRB-": "-RRB-", "-LRB-": "-LRB-", "-RCB-": "-RRB-",
             "-LCB-": "-LRB-", "--": ":", "''": "''"}
    for k,v in known.items():
      self.unigrams[k] = (v, 100)
    NUMERALS.update([str(x) for x in range(10)]) 
    for number in NUMERALS:
      self.unigrams[number] = ("CD", 100)
    

  def bi_uni_regex(self, words):
    tags = self.certain_tags(words, 90)
    for i in range(len(tags)):
      tag = tags[i]
      uni_tag = ""
      if tag is None:
        tag = self.regex.tag([words[i]])[0]
      elif tag == 0 and i >0:
        uni_tag, percentage = self.unigrams[words[i]]
        tag, percentage = self.bigrams[words[i]].get(tags[i-1], (uni_tag, 100))
      else:
        tag, percentage = self.unigrams[words[i]]
      tags[i] = tag
    return tags

  def tri_bi_uni_regex(self, words):
    tags = self.certain_tags(words, 95)
    tags_len = len(tags)
    for i in range(tags_len):
      tag = tags[i]
      word = words[i]
      if tag is None:
        tag = self.regex.tag([word])[0]
      elif tag==0 and i > 0 and tags[i-1]:
        try:
          if i < tags_len-1 and tags[i+1]:
            tag, percentage = self.trigrams[word][str((tags[i-1],tags[i+1]))]
          else:
            raise Exception
        except:
          try:
            tag, percentage = self.bigrams[word][tags[i-1]]
          except:
            tag, percentage = self.unigrams[word]
      else:
        tag, percentage = self.unigrams[word]
      tags[i] = tag
    return tags
  
  def tri_bi_uni_regex_2(self, words):
    tags = self.certain_tags(words, 95)
    tags2, percentages = zip(*self.most_frequent(words))
    for i in range(len(tags)):
      tag = tags[i]
      if tag is None:
        tag = self.regex.tag([words[i]])[0]
      elif tag==0 and i > 0 and tags2[i-1]:
        try:
          if i < len(tags)-1 and tags2[i+1]:
            tag, percentage = self.trigrams[words[i]][str((tags2[i-1],tags2[i+1]))]
          else:
            raise Exception
        except:
          try:
            tag, percentage = self.bigrams[words[i]][tags2[i-1]]
          except:
            tag, percentage = self.unigrams[words[i]]
      else:
        tag, percentage = self.unigrams[words[i]]
      tags[i] = tag
    return tags

  def uni_regex(self, words):
    tags = self.certain_tags(words, 0)
    for i in range(len(tags)):
      tag = tags[i]
      if not tag:
        tag = self.regex.tag([words[i]])[0]
      tags[i] = tag
    return tags

  def certain_tags(self, words, threshold):
    tags = self.most_frequent(words)
    for i in range(len(tags)):
      tag, percentage = tags[i]
      if percentage < threshold:
        tags[i] = 0
      else:
        tags[i] = tag
    return tags

  def most_frequent(self, words):
    result = []
    for word in words:
      tag, percentage = self.unigrams.get(word, (None, 100))
      result.append((tag, percentage))
    return result

  def tag(self, sent):
    return self.tri_bi_uni_regex(sent)

  def batch_tag(self, sents):
    start = time()
    result = [self.tag(sent) for sent in sents]
    logging.debug("POS tags calculated in %f seconds", time()-start)
    return result


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

