#! /usr/bin/env python3

import re
import os
import sys
import glob
import signal
import logging
import argparse
import datetime

from table import Table


def human(s):
  if isinstance(s, datetime.timedelta):
    log.info(f'timedelta: {s!s}')
    secs = s.total_seconds()
    (days, secs) = divmod(secs, 24*60*60)
    (hours, secs) = divmod(secs, 60*60)
    (minutes, secs) = divmod(secs, 60)
    s = f'{int(hours):02}:{int(minutes):02}:{int(secs):02}'
    if days:
      s = f'{int(days)}-{s}'

  return s


def extract_name_name_and_network(path):
  components = path[1:].split('/')
  return [log_extension_regexp.sub('', components[-1]), components[-2]]


parser = argparse.ArgumentParser(description=sys.argv[0])
parser.add_argument('regexp', nargs='?', help='Regular expression to search log messages')
parser.add_argument('-a', '--age', type=float, help='Number of days old')
parser.add_argument('-n', '--name-regexp', help='Regular expression to search chat name')
parser.add_argument('-i', '--ignore-case', action='store_true', help='Perform case-insensitive regular expression matching')
parser.add_argument('-l', '--list', action='store_true', help='List users')
parser.add_argument('-v', '--verbose', action='count', help='Enable debugging')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()
log.setLevel(logging.WARNING - (args.verbose or 0)*10)

signal.signal(signal.SIGPIPE, lambda signum, stack_frame: exit(0))

"""
[mrbruno@bruno-meerkat ~]$ head -30 /home/mrbruno/.config/hexchat/logs/undernet/blah.log
**** BEGIN LOGGING AT Fri Mar 27 15:39:22 2020
.
.
.
**** ENDING LOGGING AT Fri Mar 27 16:38:56 2020
"""

now = datetime.datetime.now()
channel_regexp = re.compile('^#')
older = args.age is not None and args.age > 0
desired_age = datetime.timedelta(days=abs(args.age)) if args.age is not None else None
msg_regexp = re.compile(args.regexp, flags=re.IGNORECASE if args.ignore_case else 0) if args.regexp is not None else None
name_regexp = re.compile(args.name_regexp, flags=re.IGNORECASE) if args.name_regexp is not None else None # filenames are folded to lowercase

logging_regexp = re.compile(r'^\*\*\*\* (BEGIN|ENDING) LOGGING AT (\w{3}\s+\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})\s*$')
timestamp_regexp = re.compile('^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([<*].*)$')
log_extension_regexp = re.compile(r'\.log$')

start_time, start_pos = (None, None)
end_time, end_pos = (None, None)
last_time = None

table = Table('Name', 'Network', 'Start', 'Duration')

root = os.path.expanduser('~/.config/hexchat/logs')
paths = glob.glob(os.path.join(root, '*/*.log'))
log.info(f'{len(paths)} files from glob.glob()')
for path in paths:
  done = False
  basename = os.path.basename(path)
  if len(set(extract_name_name_and_network(path))) == 2 and \
      not channel_regexp.search(basename) and \
      (not args.name_regexp or name_regexp.search(basename)):
    log.debug(f'Reading {path}')
    with open(path) as stream:
      lines = stream.read().splitlines()
    for pos in range(len(lines)):
      line = lines[pos]
      match = logging_regexp.search(line)
      if match:
        timestamp = datetime.datetime.strptime(match.group(2), '%a %b %d %H:%M:%S %Y')
        if match.group(1) == 'BEGIN':
          start_time, start_pos = (timestamp, pos)
          end_time = timestamp
        elif start_time is not None:
          end_pos = pos
          if end_time is None:
            end_time = timestamp

          if args.age is None or \
              (older and now-start_time > desired_age) or \
              (not older and now-end_time < desired_age):
            log.info(f'{start_time!s} {end_time!s} {path}')
            for curr in range(start_pos+1, end_pos):
              line = lines[curr]
              if msg_regexp is None or msg_regexp.search(line):
                match = timestamp_regexp.search(line)
                if match:
                  timestamp = datetime.datetime.strptime(match.group(1) + f' {start_time.year}', '%b %d %H:%M:%S %Y')
                  end_time = timestamp
                else:
                  timestamp = None

                if args.list:
                  table.append(*(extract_name_name_and_network(path) + [str(start_time), human(end_time-start_time)]))
                  done = True
                else:
                  if timestamp:
                    line = f'{timestamp.year}-{timestamp.month:02}-{timestamp.day:02} {timestamp.hour:02}:{timestamp.minute:02}:{timestamp.second:02} {match.group(2)}'
                  print(f'{path}: {line}')
              if done:
                break

          start_time, start_pos = (None, None)
          end_time, end_pos = (None, None)
      else:
        # the did not denote start/end of logging
        match = timestamp_regexp.search(line)
        if match and start_time is not None:
          end_time = datetime.datetime.strptime(match.group(1) + f' {start_time.year}', '%b %d %H:%M:%S %Y')

      if done:
        break
  if done:
    continue

if args.list:
  table.root.sort(key=lambda row: row['Start'], reverse=True)
  print(str(table), end='')
