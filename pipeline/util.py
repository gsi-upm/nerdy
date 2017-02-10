#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""util.py: Common utilities for the pipeline."""

from optparse import OptionParser
import logging
import os

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

LOG_FORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}


class Serialized(object):
  """Decorator that serliazes a function's return value each time it is called.
  If called later with the same arguments, the cached value is returned, and
  not re-evaluated.
  """

  def __init__(self, func):
    self.func = func

  def _path(self):
    filename = '.'.join([self.func.__module__, self.func.__name__, 'ser'])
    return os.path.join(CACHE_FOLDER, filename)

  def __call__(self, *args):
    data = None
    filename = self._path()
    try:
      if not CACHE:
        raise Exception
      fh = open(filename, 'rb')
      data = cPickle.load(fh)
      fh.close()
    except:
      data = self.func(*args)
      if CACHE:
        fh = open(filename, 'wb')
        cPickle.dump(data, fh)
        fh.close()
    return data

  def __get__(self, obj, objtype):
    """Support instance methods."""
    return functools.partial(self.__call__, obj)


class Memoized(object):
  """Decorator that caches a function's return value each time it is called.
  If called later with the same arguments, the cached value is returned, and
  not re-evaluated.
  """

  __cache = {}

  def __init__(self, func):
    self.func = func
    self.key = (func.__module__, func.__name__)

  def __call__(self, *args):
    try:
      return Memoized.__cache[self.key][args]
    except KeyError:
      value = self.func(*args)
      if self.key in Memoized.__cache:
        Memoized.__cache[self.key][args] = value
      else:
        Memoized.__cache[self.key] = {args : value}
      return value
    except TypeError:
      # uncachable -- for instance, passing a list as an argument.
      # Better to not cache than to blow up entirely.
      return self.func(*args)

  def __get__(self, obj, objtype):
    """Support instance methods."""
    return functools.partial(self.__call__, obj)

  @staticmethod
  def reset():
    Memoized.__cache = {}


class MemoryProfiler():
  def __init__(self):
    self.resident_size = self.resident()
    self.stacksize_size = self.stacksize()
    self.memory_size = self.memory()

  def _VmB(self, VmKey):
    '''Private.
    '''
    global _proc_status, _scale
    # get pseudo file  /proc/<pid>/status
    try:
      t = open(_proc_status)
      v = t.read()
      t.close()
    except:
      return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
      return 0.0  # invalid format?
      # convert Vm value to bytes
    return (float(v[1]) * _scale[v[2]])/_scale['MB']

  def memory(self, since=0.0):
    '''Return memory usage in bytes.
    '''
    return self._VmB('VmSize:') - since

  def resident(self, since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return self._VmB('VmRSS:') - since

  def stacksize(self, since=0.0):
    '''Return stack size in bytes.
    '''
    return self._VmB('VmStk:') - since

  def report(self):
    result = (self.memory(), self.resident(), self.stacksize())
    logging.debug("Memory: %f, Resident: %f, Stack: %f" % result)
    return result

  def change(self):
    result = (self.memory(self.memory_size), self.resident(self.resident_size),
            self.stacksize(self.stacksize_size))
    logging.debug("Memory: %f, Resident: %f, Stack: %f" % result)
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

