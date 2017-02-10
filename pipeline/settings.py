#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""template.py: Description of what the module does."""

from optparse import OptionParser
import logging


__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

LEXER_PATH =    'resources/lexer'
UNIGRAMS_PATH = 'resources/unigrams.json'
BIGRAMS_PATH =  'resources/bigrams.json'
TRIGRAMS_PATH = 'resources/trigrams.json'

ENTITIES_PATH = 'resources/entities.json'
CONTEXTS_PATH = 'resources/contexts.json'

NER_COEF = 'resources/NERClassifierCoefs.json'

TOKENIZER = 'QUEX'
#TOKENIZER = 'WHITESPACE'

pos_tagger = None
ner_tagger = None

