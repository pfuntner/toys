#! /usr/bin/env python3

import re
import sys
import logging
import argparse

parser = argparse.ArgumentParser(description='Search for the failure at the end of output for Ansible playbook')
parser.add_argument('-v', '--verbose', action='count', help='Enable debugging')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()
# log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)
log.setLevel(logging.WARNING - (args.verbose or 0)*10)

if sys.stdin.isatty():
  parser.error('stdin must be redirected')

fatal_regexp = re.compile(r'failed|FAILED|fatal|FATAL')
fatal_summary_regexp = re.compile(r'failed=\d')

last_pos = None
lines = sys.stdin.read().splitlines()
for (pos, line) in enumerate(lines):
  if fatal_regexp.search(line) and not fatal_summary_regexp.search(line):
    last_pos = pos

log.info(f'last_pos = {last_pos}')
if last_pos:
  top = max(0, last_pos - 10)
  bottom = min(len(lines), last_pos + 10)

  for line in lines[top:bottom+1]:
    print(line)
