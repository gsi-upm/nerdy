#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tokenizer.py: Tokenizers for lydia pipeline."""

from optparse import OptionParser
import logging
import sys
import command
from command import CommandLine
from time import time
import re
from io import TextIOWrapper, BytesIO

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"


class Error(Exception):
  """Basic excetion type for be extended for specific module exceptions."""

class Quex(CommandLine):
  def __init__(self, executable_path):
    super(Quex, self).__init__(executable_path)

  @staticmethod
  def _convert_to_unicode(text):
    start = time()
    fh = TextIOWrapper(BytesIO(text), encoding='utf-8', errors='replace')
    logging.debug("Converting text to unicode took %f seconds", time()-start)
    return fh.read()
 
  def sentences(self, text):
    if isinstance(text, unicode):
      text = text.encode('utf-8')
    output = self.execute(text).strip()
    output = Quex._convert_to_unicode(output)
    start = time()
    lines = output.splitlines()
    sentences = [line.strip().split(' ') for line in lines[:-1]]
    logging.debug("Parsed output of the lexer in %f seconds", time()-start)
    return sentences


class WSpaceTokenizer(object):
  def __init__(self):
    self.line_splitter = re.compile('\n+')

  def sentences(self, text):
    lines = self.line_splitter.split(text)
    return [line.split() for line in lines]


def main(options, args):
  start = time()
  text = open(options.filename).read()
  logging.debug('Time spend in reading file is %f', time()-start)
  quex = Quex('/media/data/lydia2/lex/quex_tokenizer/C/conv/lexer.stable.1')
  quex.tokens(text)
  logging.debug('Time spent in tokenization is %f', time()-start)
  
  start = time()
  quex.sentences(text)
  logging.debug('Time spent in sentences splitting is %f', time()-start)

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="filename", help="Input file")
  parser.add_option("-l", "--log", dest="log", help="log verbosity level",
                    default="INFO")
  (options, args) = parser.parse_args()

  numeric_level = getattr(logging, options.log.upper(), None)
  logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
  main(options, args)

