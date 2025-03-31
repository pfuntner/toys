#! /usr/bin/env python3

import re
import sys
import logging
import argparse

from table import Table

class Task(object):
  def __init__(self, task_type, role, name, item):
    self.type = task_type.lower()
    self.role = re.sub('\s:\s$', '', role or '')
    self.name = name
    self.item = item or ''
    self.hosts = {}
    self.elapsed = None

  def __str__(self):
    if self.item:
      return '{self.type} {self.name!r} {self.item!r} {self.hosts}'.format(**locals())
    else:
      return '{self.type} {self.name!r} {self.hosts}'.format(**locals())

  def __eq__(self, other):
    return (self.type == other.type) and (self.role == other.role) and (self.name == other.name) and (self.item == other.item)

def remove_packer_overhead(s):
  match = packer_regexp.search(str(s))
  if match:
    return match.group(1)
  else:
    return s

def simplify_host(host):
  match = host_simplifier_regexp.search(str(host))
  if match:
    host = match.group(1)
  return host

def get_task(args):
  global tasks
  log.debug(f'get_task({args})')
  task = Task(*args)
  for curr in tasks:
    if curr == task:
      task = curr
      break
  else:
    tasks.append(task)
  return task

def process(filename=None):
  global eof, hosts

  stream = open(filename) if filename else sys.stdin
  host_prefix = (filename + ' ') if filename else ''

  eof.append(False)

  task_groups = list()
  task_names = dict()
  lines = stream.read().splitlines()
  for (pos, line) in enumerate(lines):
    line = remove_packer_overhead(line)

    if end_regexp.search(line):
      eof[-1] = True

    match = task_regexp.search(str(line))
    log.debug('task match: {groups} {line!r}'.format(groups=match.groups() if match else None, **locals()))
    if match:
      # check if we can backfill the timing information for the last task
      if task_groups and pos+1 < len(lines):
        timing_match = timing_regexp.search(lines[pos+1])
        if timing_match:
          for task in tasks:
            if task.type == task_groups[0].lower() and task.role == (task_groups[1] or '') and task.name == task_groups[2] and task.elapsed is None:
              task.elapsed = timing_match.groups()[-2]
              log.info(f'After backfilling: {task!s}')
      # check if last task didn't have items that applied to any host
      if task_groups:
        task_check = [task for task in tasks if task.type == task_groups[0].lower() and task.role == (task_groups[1] or '') and task.name == task_groups[2]]
        log.info(f'Checking for dummy task: {task_groups} {task_check}')
        if not task_check:
          for task in tasks:
            log.info(f'Need dummy task: {task}')
          get_task(task_groups + [''])

      eof[-1] = False
      task_groups = list(match.groups())
      count = task_names.get(task_groups[2], 0) + 1
      task_names[task_groups[2]] = count
      if count > 1:
        # handle tasks with the same name
        task_groups[2] += ' [{}]'.format(count)
    elif task_groups:
      host_match = host_regexp.search(str(line))
      log.debug('host match: {groups} {line!r}'.format(groups=host_match.groups() if host_match else None, **locals()))
      if host_match:
        eof[-1] = False
        task = get_task(task_groups + [host_match.group(3)])
        key = host_prefix + simplify_host(host_match.group(2))
        hosts.add(key)
        if key not in task.hosts:
          task.hosts[key] = host_match.group(1) + (' - {}'.format(pos+1) if args.locate else '')
        else:
          log.warning('Line {pos} had duplicate status for {key!r} {task!r} {item!r}'.format(
            pos=pos+1,
            key=key,
            task=task.name,
            item=host_match.group(3),
          ))

  if filename:
    stream.close()

parser = argparse.ArgumentParser(description='Scrape info from Ansible playbook task output')
parser.add_argument('files', metavar='file', nargs='*', help='Zero or more Ansible output files')
parser.add_argument('-l', '--locate', action='store_true', help='Identify line numbers from whence status was obtained')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable debugging')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

task_regexp = re.compile(r'^(?:RUNNING\s+)?(\S+)\s+\[([^:]*\s:\s)?\s*(.*)\]\s+\*{2,}$')

"""
host_regexp needs to be able to process all of these possibilities:

  ok: [localhost]
  ok: [localhost] => (item=[u'item1.1', u'item2.1', u'item3.1']) => {
  skipping: [aws-centos6] => (item=2.8.0)
  failed: [centos7] (item=OUTPUT) => {"ansible_loop_var": "item", "changed": false, "cmd": "/sbin/iptables -t filter -L OUTPUT", "item": "OUTPUT", "msg": "iptables v1.4.21: can\'t initialize iptables table `filter\': Permission denied (you must be root)\\nPerhaps iptables or your kernel needs to be upgraded.", "rc": 3, "stderr": "iptables v1.4.21: can\'t initialize iptables table `filter\': Permission denied (you must be root)\\nPerhaps iptables or your kernel needs to be upgraded.\\n", "stderr_lines": ["iptables v1.4.21: can\'t initialize iptables table `filter\': Permission denied (you must be root)", "Perhaps iptables or your kernel needs to be upgraded."], "stdout": "", "stdout_lines": []}
  fatal: [aws-rh8]: FAILED! => {"changed": true, "cmd": "cat '/home/ec2-user/repos/toys/misc/.bash_rc' >> '/home/ec2-user/.bashrc'", "delta": "0:00:00.005289", "end": "2020-10-18 13:42:04.813624", "msg": "non-zero return code", "rc": 1, "start": "2020-10-18 13:42:04.808335", "stderr": "cat: /home/ec2-user/repos/toys/misc/.bash_rc: No such file or directory", "stderr_lines": ["cat: /home/ec2-user/repos/toys/misc/.bash_rc: No such file or directory"], "stdout": "", "stdout_lines": []}
"""
host_regexp = re.compile(r'^([a-z]+):\s+\[([^\]]*)\](?:)?(?: FAILED!)?(?: =>)?(?: \(item=([^)]+)\))?(?: =>)?(?: \{.*$)?')

# Remove packer overhead if necessary
packer_regexp = re.compile(r'^\x1b\[\d+;\d+2m\s+\S+:\s(.*)\x1b\[\d+m$')

# Simplify host: [foo -> bar] => [foo]
host_simplifier_regexp = re.compile(r'^(\S+)\s+->\s+\S+$')

end_regexp = re.compile(r'^PLAY RECAP')

# Saturday 09 March 2024  10:11:40 -0500 (0:00:00.027)       0:00:01.216 ********
timing_regexp = re.compile(r'^(\w+)\s+(\d{2})\s+(\w+)\s+(\d{4})\s+(\d{2}:\d{2}:\d{2})\s+(-?\d{4})\s+\((\d+:\d{2}:\d{2}\.\d{3})\)\s+(\d+:\d{2}:\d{2}\.\d{3})\s+\*+')

tasks = []
eof = []
hosts = set()

if args.files:
  list(map(process, args.files))
else:
  if sys.stdin.isatty():
    parser.error('stdin must be redirected if no files are specified')
  process()

if tasks:
  log.info(tasks[-1])

hosts = sorted(list(hosts))

columns = ['Task type', 'Role', 'Task']
if any([bool(task.elapsed) for task in tasks]):
  has_elapsed = True
  columns.append('Elapsed')
else:
  has_elapsed = False

columns += ['Items']
columns += hosts

table = Table(*columns)
for task in tasks:
  row = [task.type, task.role, task.name]
  if has_elapsed:
    row.append(task.elapsed or '')
  row.append(task.item)
  for host in hosts:
    row.append(task.hosts.get(host, ''))
  table.add(row)
sys.stdout.write(str(table))

log.info(f'eof: {eof}')
if all(eof):
  log.warning('Ansible playbooks have ended')
