#! /usr/bin/env python3

import sys
import os
import os.path
import re
import commands

def syntax():
  sys.stderr.write("Syntax: %s [--e2e] [--key public_key_file] user@remote ...\n" % sys.argv[0])

exitStatus = 0
optind = 1

def locate(dir, filename):
  # print "seeking %s in %s" % (filename, dir)
  ret = None
  path = os.path.join(dir, filename)
  if os.path.islink(path) or os.path.islink(dir):
    ret = None
  elif os.path.isfile(path):
    ret = path
  elif os.path.isdir(dir):
    for child in os.listdir(dir):
      ret = locate(os.path.join(dir, child), filename)
      if ret:
        break

  return ret

def ownUser(target):
  ret = False

  for var in ["USER", "LOGNAME"]:
    if var in os.environ:
      ret = re.match("%s@." % os.environ[var], target) != None
      if ret:
        break

  return ret

authKeys=".ssh/authorized_keys"
if (len(sys.argv) < 2) or (sys.argv[1] in ["-h", "--help", "-?"]):
  syntax()
  exit(0)

if len(sys.argv) >= 1 and sys.argv[1] == "--e2e":
  e2ePublicKey = "beehive_id_dsa.pub"
  if "TOP" in os.environ:
    publicKey = locate("%(TOP)s/test/config" % os.environ, e2ePublicKey)
    assert publicKey, ("Could not find %%s in %(TOP)s/test/config" % os.environ) % e2ePublicKey
  else:
    publicKey = locate("%(HOME)s" % os.environ, e2ePublicKey)
    assert publicKey, ("Could not find %%s in %(HOME)s" % os.environ) % e2ePublicKey
  print("e2e key: %s" % publicKey)
  optind += 1
elif len(sys.argv) >= 2 and sys.argv[1] == "--key":
  if not sys.argv[2].endswuth(".pub"):
    sys.stderr.write("`%s` does not end in `.pub`.  Are you sure it's a public key??\n" % sys.argv[2])
    exit(1)
  publicKey=sys.argv[2]
  optind+=2
elif sys.argv[1].startswith("-"):
  syntax()
  exit(1)
else:
  # publicKey="/home/jp186030/svn/beehive/test/config/beehive_id_dsa.pub"
  # publicKey="%(HOME)s/.ssh/id_rsa.pub" % os.environ
  privatePublicKeys = ["id_dsa.pub", "id_rsa.pub"]
  publicKey = None
  for privatePublicKey in privatePublicKeys:
    publicKey = locate("%(HOME)s/.ssh" % os.environ, privatePublicKey)
    if publicKey:
      break

  assert publicKey, ("Could not find %%s in %(HOME)s/.ssh" % os.environ) % ' or '.join(privatePublicKeys)
  print("private key: %s" % publicKey)

privateKey = publicKey[:-4]
print("private key: %s" % privateKey)

for i in range(optind, len(sys.argv)):
   target = sys.argv[i]
   if re.match(".+@.", target):
      if i > 1:
         print("")
      #########################################################################################################################
      # cmd = "cat /home/jp186030/svn/beehive/test/config/beehive_id_dsa.pub | ssh %s cat \>\> .ssh/authorized_keys \; chmod 600 .ssh/authorized_keys" % target
      #########################################################################################################################
      (status, output) = commands.getstatusoutput("ssh -i %s -o IdentitiesOnly=yes -o PasswordAuthentication=no -o NumberOfPasswordPrompts=0 %s true" % (privateKey, target))
      if status == 0:
        print("Key is already in place for %s" % target)
      else:
        cmd = "cat %s | ssh %s mkdir -pv .ssh \; chmod -v 700 .ssh \; cat \>\> %s \; chmod -v 600 %s" % (publicKey, target, authKeys, authKeys)
        print(cmd)
        (status, output) = commands.getstatusoutput(cmd)
        if status == 0:
           print(output)
        else:
           print(>> sys.stderr, output)
           exitStatus = 1
   else:
      print(>> sys.stderr, target + " does not look good")
      exitStatus = 1

exit(exitStatus)
