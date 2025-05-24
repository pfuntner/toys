#! /usr/bin/env python

import os
import re
import sys
import json
import base64
import os.path
import hashlib
import getpass
import logging
import argparse
import datetime
import cryptography.fernet

def berate(s):
  global output

  if args.jsonOutput:
    if not ('errors' in output):
      output['errors'] = [s]
    else:
      output['errors'].append(s)
  else:
    log.info(s)

def announce(name, value, whisperName=False):
  if args.jsonOutput:
    output['pairs'][name] = value
  else:
    if whisperName:
      print(value)
    else:
      print(f'{name}: {value!r}')

class SecureKeyValues:
  """
  Manage a secure dictionary file
  """

  def __init__(self, filename, key=None, keyPromptForMissingFile=True, ssh=False, log=None):
    """
    Constructor

    Args:
      filename (str): Path to secure file.  If it has no directory component, `~/private/` is used as the parent directory
      key (str): Encryption key
      keyPromptForMissingFile (bool): Control whether the class will prompt for a key it not supplied
      ssh (bool): Control whether to use `~/.ssh/rsa_id` for the encryption key
      log (logging.RootLogger): The caller's Logger for debugging.  This can be `None` if the caller doesn't have a
                                logger or doesn't want to use its logger for some reason.  In that case, an internal
                                logger is used.

    """
    self.log = log if log else globals()['log']

    self.simpleFilename = filename
    self.store = {}
    self.exists = False
    self.fernet = None

    if '/' in filename:
      if filename[0] == '/':
        self.filename = filename
      else:
        self.filename = os.path.join(os.getcwd(), filename)
    else:
      self.filename = os.path.expanduser(os.path.join('~', '.private', filename))

    self.log.debug(f'store is {self.filename}')

    if ssh and (not key):
      sshFilename = os.path.expanduser('~/.ssh/id_rsa')
      if os.path.isfile(sshFilename):
        self.log.debug(f'Reading {sshFilename!r}')
        with open(sshFilename, 'r') as stream:
          key = ''.join([line for line in stream.read().splitlines() if not re.match('---', str(line))])
          self.log.debug('ssh private key is {bytes} bytes long'.format(bytes=len(key)))

    if keyPromptForMissingFile or os.path.exists(self.filename):
      done = False

      while not done:
        if key:
          self.simpleKey = key
        else:
          self.simpleKey = getpass.getpass(f'Enter key for {self.filename!r}: ')

        hash = hashlib.md5()
        hash.update(self.simpleKey.encode())
        self.key = base64.b64encode(hash.hexdigest().encode())

        self.fernet = cryptography.fernet.Fernet(self.key)

        if os.path.isfile(self.filename) and os.path.getsize(self.filename):
          with open(self.filename, 'rb') as f:
            self.store = json.loads(self.fernet.decrypt(f.read()))
            self.log.debug('Store is read')
            self.exists = True
            done = True
        else:
          """
            The lack of a store file is not a problem.  It will get created once
            the write() method is used on the object.  We have a key and will
            use it if and when we write.
          """
          done = True

  def get(self, key, root=None):
    """
    Get a value for a key in the store

    Args:
      key (str): Key for the value for extract.  This can be structured with slashes: `a/b/c` => ['a']['b']['c']
      root (dict): Portion of the store to process.  Typically, the caller leaves as `None`.  The method is recursive
                   and invokes itself overriding the root for structured keys

    Returns:
      value (str): The value for the key.  This could be `None` if the key does not exist in the store
    """
    if root == None:
      root = self.store

    if type(key) != list:
      key = key.split('/')

    if key[0] in root:
      return root[key[0]] if len(key) == 1 else self.get(key[1:], root[key[0]])
    else:
      return None

  def put(self, key, value, root=None):
    """
    Set a value for a key in the store

    Args:
      key (str): Key for the value to store.  This can be structured with slashes: `a/b/c` => ['a']['b']['c']
      value (str): Value for the key to store.
      root (dict): Portion of the store to process.  Typically, the caller leaves as `None`.  The method is recursive
                   and invokes itself overriding the root for structured keys
    Returns:
      None
    """
    if root == None:
      root = self.store

    if type(key) != list:
      key = key.split('/')

    if len(key) > 1:
      if key[0] not in root:
        root[key[0]] = {}
      self.put(key[1:], value, root[key[0]])
    else:
      root[key[0]] = value

  def keys(self):
    """
    Returns top-level keys of the store

    Returns:
      keys (list): A list of strings for the keys in the root of the store.

    To do:
      This method only list keys in the root, not structured keys.  If I get the ambition, I might fix this but
      I don't think I even use structured keys.
    """
    return self.store.keys()

  def remove(self, key):
    """
    Set a value for a key in the store

    Args:
      key (str): Key from the store root to remove.

    Returns:
      value (str): Value from the key removed.  This can be `None` if the key was not in the store.

    To do:
      This method only list keys in the root, not structured keys.  If I get the ambition, I might fix this but
      I don't think I even use structured keys.
    """
    if key in self.store:
      return self.store.pop(key)
    else:
      return None

  def write(self):
    """
    Commit a store to the file system
    """
    global log

    if os.path.isfile(self.filename):
      backup =  f'{self.filename}D{datetime.datetime.now().isoformat().replace(":", "")}'
      self.log.info(f'Backing up {self.filename!r} to {backup!r}')
      os.rename(self.filename, backup)
    else:
      dir = os.path.dirname(self.filename)
      if not os.path.isdir(dir):
        os.mkdir(dir, 0o700)
    self.log.info(f'Saving store to {self.filename}')
    with open(self.filename, 'wb') as f:
      os.chmod(self.filename, 0o600)
      f.write(self.fernet.encrypt(json.dumps(self.store).encode()))

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()

if __name__ == '__main__':
  output = {'pairs': {}}

  """
    `staticStringRegexp` is a regular expression that let's us
    identify when an argument is a "static string".  That is,
    the caller wants the string included in the result as-is
    and the store is not used.  This can be used to build
    calls like this:

      $ echo $(SecureKeyValues --store foobar --get \"-u\" user \"-p\" password)
      Key for 'ctc':
      -u fooar -p bar
      $
  """
  staticStringRegexp = re.compile('''^['"](.+)['"]$''')

  parser = argparse.ArgumentParser(description='A manager of secure stores')
  parser.add_argument('-o', '--operation', dest='operation', help='Secure store operation', choices=['read', 'list', 'get', 'set', 'remove', 'test'], required=True)
  parser.add_argument('-s', '--store', dest='storeName', help='Name of secure store')

  group = parser.add_mutually_exclusive_group()
  group.add_argument('-k', '--key', dest='key', help='Encryption key for secure store')
  group.add_argument('--ssh', dest='ssh', action='store_true', help='Use ssh private key for secure store encryption key')

  parser.add_argument('-j', '--json', dest='jsonOutput', action='store_true', help='Print output in JSON form')
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable debugging messages')
  parser.add_argument('args', metavar='arg', nargs='*', help='Additional arguments, dependent on operation')
  args = parser.parse_args()

  log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

  if args.operation != 'test' and (not args.storeName):
    parser.error('Use -s/--store to specify secure store')

  if args.operation == 'test':
    store = SecureKeyValues('test', 'this is a test')
    print(f'store file: {store.filename!r}')
    keys = store.keys()
    print(f'keys: {list(keys)}')
    now = str(datetime.datetime.now())
    if keys:
      for key in keys:
        print(f'{key}: {store.get(key)!r}')
      store.put('runs', [now] + store.get('runs'))
    else:
      store.put('one', 1)
      store.put('two', 2)
      store.put('one hundred', 100)
      store.put('runs', [now])
    store.write()
  else:
    store = SecureKeyValues(args.storeName, args.key, keyPromptForMissingFile=(args.operation != 'read'), ssh=args.ssh)
    keyvalue_regexp = re.compile('^([^=]+)=(.+)$')
    key_regexp = re.compile(r'^(\w[^=]*\w+)$')
    if args.operation == 'read':
      if not store.exists:
        berate(f'{store.filename!r} does not exist')
      for key in store.keys():
        announce(key, store.get(key))
    elif args.operation == 'set':
      if not args.args and sys.stdin.isatty():
        args.args = sys.stdin.read().strip('\n').split('\n')
      for arg in args.args:
        match = keyvalue_regexp.search(str(arg))
        if match:
          store.put(match.group(1), match.group(2))
        else:
          match = key_regexp.search(str(arg))
          if match:
            store.put(match.group(1), getpass.getpass('Enter value for {name!r}: '.format(name=match.group(1))))
          else:
            raise Exception(f'{arg!r} is neither a valid key nor key/value pair')
      store.write()
    elif args.operation == 'remove':
      for arg in args.args:
        store.remove(arg)
      store.write()
    elif args.operation == 'list':
      print(f'Keys: {list(store.keys())}')
    elif args.operation == 'get':
      if sys.stdout.isatty():
        log.fatal('Stdout must be redirected')
        exit(1)

      if args.args:
        for arg in args.args:
          match = staticStringRegexp.search(str(arg))
          if match:
            if (not args.jsonOutput):
              print(match.group(1))
          else:
            announce(arg, store.get(arg), whisperName=True)
      else:
        parser.error('At least one key is required for `get` operation')

  if args.jsonOutput:
    print(json.dumps(output, indent=2, sort_keys=True))
