#! /usr/bin/env python3

import sys
import gzip
import os.path
import io
import traceback

def process(filename=None):
  zippedStream = None
  if not filename:
    zippedStream = sys.stdin
  else:
    if not os.path.exists(filename):
      sys.stderr.write("Could not find %s\n" % repr(filename))
    elif os.path.isdir(filename):
      sys.stderr.write("%s is a directory\n" % repr(filename))
    else:
      zippedStream = open(filename, 'r')

  if zippedStream:
    stringStream = io.StringIO(zippedStream.read())
    try:
      with gzip.GzipFile(fileobj=stringStream) as stream:
        sys.stdout.write(stream.read())
    except Exception as e:
      if e.message == "Not a gzipped file":
        zippedStream.seek(0)
        sys.stdout.write(zippedStream.read())
      else:
        sys.stderr.write("Problem uncompressing %s: %s\n" % (repr(filename) if filename else "stdin", e))
        # traceback.print_stack()
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)

    stringStream.close()

    if filename:
      zippedStream.close()

if len(sys.argv) == 1:
  assert not sys.stdin.isatty(), "stdin must be redirected if not filenames are specified"
  process()
else:
  for filename in sys.argv[1:]:
    process(filename)
