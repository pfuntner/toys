#! /usr/bin/env python3

"""
   Print lines to identify the columns, keyed off the width of the screen.  Useful to know how long lines are, what column a character/field is in, etc.
"""

import re
import sys
import math
import getopt
import subprocess

def syntax(msg=None):
  if msg:
    sys.stderr.write('{msg}\n'.format(**locals()))
  sys.stderr.write('Syntax: {pgm} [-v|--verbose|-a|--all] [INT]\n'.format(pgm=sys.argv[0]))
  exit(1)

def debug(msg, loud=False):
  if verbose or loud:
    sys.stderr.write('{msg}\n'.format(**locals()))

cols = 80

p = subprocess.Popen(["stty", "size"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(stdout, stderr) = p.communicate()
stdout = stdout.decode('utf-8')
stderr = stderr.decode('utf-8')
rc = p.wait()

verbose = False
(opts,args) = ([],[])
try:
  (opts,args) = getopt.getopt(sys.argv[1:], 'va', ['verbose', 'all'])
except Exception as e:
  syntax('Caught: {e!s}'.format(**locals()))

for (opt,arg) in opts:
  if opt in ['-v', '--verbose', '-a', '--all']:
    verbose = not verbose
  else:
    syntax('Unexpected option: {opt!r}'.format(**locals()))

if len(args) == 1:
  cols = int(args[0])
  assert cols > 0
  debug('Overriding columns with {cols}'.format(**locals()))
elif len(args) > 1:
  syntax('Unexpected arguments: {remain}'.format(remain=args[1:]))
else:
  if stdout and (not stderr) and (rc == 0):
    match = re.search('\d+\s+(\d+)', str(stdout))
    if stdout:
      cols = int(match.group(1))
      debug('cols={cols}, `stty size` returned {rc}, {stdout!r}, {stderr!r}'.format(**locals()))
    else:
      debug('defaulting to cols={cols} because `stty size` could not be parsed: {stdout!r}\n'.format(**locals()), loud=True)
  elif not all:
    debug('defaulting to cols={cols} because `stty size` returned {rc}, {stdout!r}, {stderr!r}\n'.format(**locals()), loud=True)

digits = math.log10(cols)
debug('cols={cols}, digits={digits}, int(digits)={int_digits}'.format(int_digits=int(digits), **locals()))
if digits == int(digits):
  debug('power of 10!')
  digits = int(digits)+1
else:
  digits = int(math.ceil(digits))
debug('digits: {digits}'.format(**locals()))

"""
if digits >= 4:
  print(''.join([str(num)*1000 for num in range(10)] * int(math.ceil(cols/10000+1)))[1:cols+1])
if digits >= 3:
  print(''.join([str(num)*100 for num in range(10)] * int(math.ceil(cols/1000+1)))[1:cols+1])
if digits >= 2:
  print(''.join([str(num)*10 for num in range(10)] * int(math.ceil(cols/100+1)))[1:cols+1])
print ('1234567890' * int(math.ceil(cols/10+1)))[:cols]
"""

for digit in range(digits, 0, -1):
  print(''.join([str(num)*int(math.pow(10, digit-1)) for num in range(10)] * int(math.ceil(cols/math.pow(10, digit)+1)))[1:cols+1])
