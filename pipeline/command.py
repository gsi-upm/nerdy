#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""command.py: Interface to command line executables."""

from optparse import OptionParser
import logging
from os import path
from subprocess import PIPE, Popen
from time import time

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

class Error(Exception):
  """Basic excetion type for be extended for specific module exceptions."""

class ExecutionError(Error):
  """Raised if the command fails to execute."""

class CommandLine(object):
  def __init__(self, executable_path, args=None):
    self.executable_path = path.abspath(executable_path)
    self.args = args

  @property
  def cmd(self):
    if self.args:
      return '%s %s' % (self.exeutable_path, ' '.join(self.args))
    return self.executable_path

  def execute(self, input_):
    start = time()
    p = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate(input=input_)
    if p.returncode != 0:
      raise ExecutionError('Command failed!\nError Message:\n%s', stderr)
    logging.debug("Command: %s", self.cmd)
    logging.debug("Command executed in %f seconds", time()-start)
    return stdout

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

