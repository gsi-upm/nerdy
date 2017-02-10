#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""document.py: The abstractio of the web articles."""

from optparse import OptionParser
import logging
from tokenizer import Quex, WSpaceTokenizer
from pos import POSTagger
from ner import NERTagger
from time import time
import json as json
from io import open, StringIO

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

TAB = u'\t'
LINE = u'\n'
DLINE = u'\n\n'

class Error(Exception):
  """Basic error exception to be extended by the other exceptions"""


class Document(object):
  def __init__(self, text, settings):
    self.text = text
    self.settings = settings
    self.sentences = []
    self.pos_tags = []
    self.ner_tags = []
    self.entities = []

  @staticmethod
  def _to_utf8(utext):
    return utext.encode('utf-8')

  @staticmethod
  def _load_json_resource(path):
    fh = open(path, 'rb')
    obj = json.load(fh)
    fh.close()
    return obj

  def get_sentences(self):
    if not self.sentences:
      if self.settings.TOKENIZER == 'QUEX':
        quex = Quex(self.settings.LEXER_PATH)
        self.sentences = quex.sentences(self.text)
      elif self.settings.TOKENIZER == 'WHITESPACE':
        self.sentences = WSpaceTokenizer().sentences(self.text)
    return self.sentences

  def get_pos_tags(self):
    if not self.pos_tags:
      self.pos_tags = self.settings.pos_tagger.batch_tag(self.get_sentences())
    return self.pos_tags

  def get_ner_tags(self):
    if not self.ner_tags:
      self.ner_tags = self.settings.ner_tagger.batch_tag(self.get_sentences())
    return self.ner_tags

  def get_bytes(self):
    return Document._to_utf8(self.string())

  def slashtags(self):
    pass
        

  def string(self):
    start = time()
    features = filter(lambda x: x,
                      [self.sentences, self.pos_tags, self.ner_tags])
    buf = StringIO()
    for i in range(len(self.sentences)):
      for j in range(len(self.sentences[i])):
        for feature in features:
          try:
            buf.write(unicode(feature[i][j]))
          except:
            import pdb
            pdb.set_trace()
          buf.write(TAB)
        buf.write(LINE)
      buf.write(DLINE)
    repr_str = buf.getvalue()
    buf.close()
    logging.debug('Document string representation is caculated in %f seconds', time()-start)
    return repr_str

    sentences_combined = zip(*features)
    tokens_combined = [zip(*sent_fs) for sent_fs in sentences_combined]
    text = '\n\n'.join(['\n'.join(['\t'.join(token) for token in sent]) for sent in tokens_combined])
    return text 
           

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

