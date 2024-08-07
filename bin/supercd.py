#! /usr/bin/env python3

import re
import os
import json
import signal
import fnmatch
import logging
import datetime
import argparse

import bruno_tools

parser = argparse.ArgumentParser(description='`Super cd` Python code')
parser.add_argument('pat', help='Glob pattern to search for')
parser.add_argument('-b', '--bash', action='store_true', help='Generate output to set bash array')
parser.add_argument('-c', '--cache', action='store_true', help='Use cache for results')
parser.add_argument('-v', '--verbose', action='count', help='Enable debugging')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()
log.setLevel(logging.WARNING - (args.verbose or 0)*10)

signal.signal(signal.SIGPIPE, lambda signum, stack_frame: exit(0))

files = list()
now = datetime.datetime.now()
epoch = datetime.datetime.fromtimestamp(0)
cache_threshold = datetime.timedelta(days=7)
cache_file_name = os.path.expanduser('~/.supercd.json')

cache = dict()
cleanup = False

if args.cache:
  if os.path.exists(cache_file_name):
    with open(cache_file_name) as stream:
       cache = json.load(stream)
    if args.pat in cache:
      log.info(f'Found {args.pat!r} in {cache_file_name}')
      if datetime.datetime.fromtimestamp(cache[args.pat]['timestamp']) >= now - cache_threshold:
        log.info(f'Pattern was last used {datetime.datetime.fromtimestamp(cache[args.pat]["timestamp"])} and is elligible for reuse')
        files = [cache[args.pat]['file']]
      else:
        log.info(f'Pattern was last used {datetime.datetime.fromtimestamp(cache[args.pat]["timestamp"])} and is inelligible for reuse')
        del cache[args.pat]
        cleanup = True
  else:
    log.info(f'{cache_file_name} not found')
    with open(cache_file_name, 'w') as stream:
      json.dump(cache, stream)
    log.info(f'Rewrote {cache_file_name}')

if not files:
  files = bruno_tools.run([
    'find',
    os.path.expanduser('~'),
    '!', '-path', '*/.*',
    '-type', 'd',
    '-name', args.pat,
  ], log=log)[1].splitlines()

if args.cache and (len(files) == 1 or cleanup):
  if len(files) == 1:
    log.info(f'Equating {args.pat} with {files[0]} in {cache_file_name}')
    cache[args.pat] = {
      'file': files[0],
      'timestamp': (now - epoch).total_seconds(),
      'timestamp_human': str(now),
    }
  with open(cache_file_name, 'w') as stream:
    json.dump(cache, stream)
  log.info(f'Rewrote {cache_file_name}')

if args.bash:
  print(f'({" ".join([repr(file) for file in files])})')
else:
  print('\n'.join(files))
