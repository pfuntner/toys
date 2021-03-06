#! /usr/bin/env python3

"""
  Print git branches

  By default, only the branches which are not `master` are printed.
  If you want `master` included too, use the `--all` option.
"""

import sys
import re
import subprocess

if ("--help" in sys.argv) or ("--?" in sys.argv) or ("-help" in sys.argv) or ("-?" in sys.argv):
  sys.stderr.write("Syntax: %s [--all]\n" % sys.argv[0])
  exit(1)

cmd = "git branch".split()

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(stdout, stderr) = p.communicate()
stdout = stdout.decode('utf-8')
stderr = stderr.decode('utf-8')
rc = p.wait()
assert (rc == 0) and (not stderr), "%s failed: %d, %s, %s" % (cmd, rc, repr(stdout), repr(stderr))

for line in stdout.splitlines():
  branch = line.split()[-1]
  if ("--all" in sys.argv) or (branch != "master"):
    print(branch)
