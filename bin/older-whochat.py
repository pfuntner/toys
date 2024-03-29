#! /usr/bin/env python3

import re
import os
import logging
import datetime
import argparse

from BrunoUtils import TimezoneMagic

def desired_by_time(path):
  ret = False
  if args.age is None:
    log.debug(f'{path} is desired because --age is not specified')
    ret = True
  else:
    file_age = (now - timezone_magic.to_gmt(datetime.datetime.fromtimestamp(os.path.getmtime(path)))).total_seconds()
    if args.age < 0:
      age = -args.age
      ret = file_age <= age
      log.debug(f'{path} {file_age} < {age} => {ret}')
    else:
      ret = file_age > args.age
      log.debug(f'{path} {file_age} > {args.age} => {ret}')
  return ret

root = os.path.expanduser('~/.config/hexchat/logs')

parser = argparse.ArgumentParser(description='Search hexchat irc client logs')
parser.add_argument('pattern', help='Regular expression to search log file names and contents')
parser.add_argument('-r', '--root', required=False, default=root, help=f'Specify path to log file root: default: {root!r}')
parser.add_argument('-a', '--age', type=float, help='Specify age of file in days.  Older: positive, newer: negative')
parser.add_argument('-n', '--name-only', action='store_true', help='Search log file names only, not content')
parser.add_argument('-i', '--ignore-case', action='count', help='Toggle ignore case (default: ignore case)')
parser.add_argument('-v', '--verbose', action='count', help='Enable debugging')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()
log.setLevel(logging.WARNING - (args.verbose or 0)*10)

"""
/home/mrbruno/.config/hexchat/logs/undernet/foobar.log
"""

timezone_magic = TimezoneMagic()

root = args.root
regexp = re.compile(args.pattern, flags=re.IGNORECASE if bool((args.ignore_case or 0) % 2) else 0)
remove_log_suffix_regexp = re.compile(r'\.log$')

now = datetime.datetime.utcnow()
if args.age:
  args.age *= 24*60*60 # convert to seconds

if os.path.isdir(root):
  for network_name in os.listdir(root):
    for log_name in os.listdir(os.path.join(root, network_name)):
      path = os.path.join(root, network_name, log_name)
      if desired_by_time(path):
        hit = False
        if not args.name_only:
          with open(path) as stream:
            for line in stream.read().splitlines():
              if regexp.search(line):
                hit = True
                print(f'{path}: {line}')
        if not hit and regexp.search(remove_log_suffix_regexp.sub('', log_name)):
          print(f'{path}')
else:
  parser.error(f'Could not find: {root}')
