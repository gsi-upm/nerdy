#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pipeline.py: Pipeline is the main process that runs lydia2."""

from optparse import OptionParser
import logging
import os
import sys
from time import time
import json
from document import Document 
from util import MemoryProfiler
from pos import POSTagger
from ner import NERTagger
from io import open
import settings

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

def load_json_resource(path):
  fh = open(path, 'r')
  obj = json.load(fh)
  fh.close()
  return obj

def init_postagger():
  start = time()
  mem_prof = MemoryProfiler()
  unigrams = load_json_resource(settings.UNIGRAMS_PATH)
  bigrams = load_json_resource(settings.BIGRAMS_PATH)
  trigrams = load_json_resource(settings.TRIGRAMS_PATH)
  settings.pos_tagger = POSTagger(unigrams, bigrams, trigrams)
  logging.debug("Initialized the POSTagger in\t%f seconds", time()-start)
  mem_prof.change()

def init_nertagger():
  start = time()
  mem_prof = MemoryProfiler()
  entities = load_json_resource(settings.ENTITIES_PATH)
  contexts = load_json_resource(settings.CONTEXTS_PATH)
  settings.ner_tagger = NERTagger(entities, contexts, settings.pos_tagger, settings.NER_COEF)
  logging.debug("Initialized the NERTagger in\t%f seconds", time()-start)
  mem_prof.change()

def main(options, args):
  start = time()
  mem_prof = MemoryProfiler()
  logging.debug('Initialization ...')
  init_postagger()
  init_nertagger()
  logging.debug("Initialized the Taggers in\t%f seconds", time()-start)
  mem_prof.change()
  start = time()
  doc = Document(options['text'], settings)
  logging.debug('Time spent building the document is %f', time()-start) 
  start = time()
  doc.get_ner_tags()
  mem_prof.change()
  logging.debug('Time spent processing the file is %f', time()-start) 
  start = time()
  return doc.get_bytes()
  logging.debug('Time spent writing the file is %f', time()-start)
  mem_prof.change()


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="filename", help="Input file")
  parser.add_option("-c", "--conf", dest="conf", help="Configuration file")
  parser.add_option("-l", "--log", dest="log", help="log verbosity level",
                    default="INFO")
  (options, args) = parser.parse_args()

  conf_path = os.path.dirname(os.path.abspath(options.conf))
  sys.path.append(conf_path)
  import settings

  numeric_level = getattr(logging, options.log.upper(), None)
  logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
  main(options, args)

