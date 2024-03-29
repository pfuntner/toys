#! /usr/bin/env python3

"""
  This solves the problem of pushing commits to a git server when the
  branch doesn't exist on the git server yet.  git helpfully gives you
  a command that will create the branch and push it but you have to
  copy and paste it.  This script simplifies that use case by simply
  parsing out the suggestion and running it.
"""

import re
import sys
import subprocess

nastygram = re.compile("fatal: The current branch \S+ has no upstream branch")
suggestion = re.compile("(git push --set-upstream origin \S+)", re.DOTALL)

p = subprocess.Popen(["git", "push"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(stdout, stderr) = p.communicate()
stdout = stdout.decode('utf-8')
stderr = stderr.decode('utf-8')
rc = p.wait()
sys.stdout.write(stdout)
sys.stderr.write(stderr)
if (rc != 0) and (not stdout) and nastygram.search(stderr):
  match = suggestion.search(stderr)
  if match:
    print("Trying to push with git's suggestion...")
    cmd = match.group(1)
    # print "  " + cmd
    p = subprocess.Popen(cmd.split())
    exit(p.wait())
  else:
    sys.stderr.write("There appears to be no upstream branch but could not extract git's suggested push command\n")

exit(rc)
