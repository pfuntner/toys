#! /usr/bin/env python3

import os
import sys
import grp
import pwd
import stat
import logging
import datetime

def mode_bits(mode, pos):
  bits = (mode / (8**pos)) % 8
  ret = '{read}{write}{execute}'.format(
    read='r' if bits & 4 else '-',
    write='w' if bits & 2 else '-',
    execute='x' if bits & 1 else '-',
  )

  return ret

def special_bits(mode):
  ret = ''

  if stat.S_ISUID & mode:
    ret += ', setuid bit is on'

  if stat.S_ISGID & mode:
    ret += ', setgid bit is on'

  if stat.S_ISVTX & mode:
    ret += ', sticky bit is on'

  return ret

def see_time(secs):
  return str(datetime.datetime.fromtimestamp(secs))

def emit(label, value):
  label += ':'
  print('  {label:<8} {value}'.format(**locals()))

def human_size(value):
  units = 'b'
  if value > 1000:
    value /= 1024.0
    units = 'K'
    if value > 1000:
      value /= 1024.0
      units = 'M'
      if value > 1000:
        value /= 1024.0
        units = 'G'
        if value > 1000:
          value /= 1024.0
          units = 'T'
    return '{value:.3f}{units}'.format(**locals())
  else:
    return '{value}{units}'.format(**locals())

def see_user(uid):
  try:
    user = pwd.getpwuid(uid)
  except:
    return '? ({uid})'.format(**locals())
  else:
    user = user.pw_name
    return '{user} ({uid})'.format(**locals())

def see_group(gid):
  try:
    group = grp.getgrgid(gid)
  except:
    return '? ({gid})'.format(**locals())
  else:
    group = group.gr_name
    return '{group} ({gid})'.format(**locals())

def process(filename):
  global log, count

  try:
    # stat attributes: ['n_fields', 'n_sequence_fields', 'n_unnamed_fields', 'st_atime', 'st_blksize', 'st_blocks', 'st_ctime', 'st_dev', 'st_gid', 'st_ino', 'st_mode', 'st_mtime', 'st_nlink', 'st_rdev', 'st_size', 'st_uid']
    stat_obj = os.stat(filename)
  except Exception as e:
    log.error('Could not stat() {filename!r}: `{e!s}`'.format(**locals()))
  else:
    print(os.path.abspath(filename))
    emit('mode', '{owner}{group}{other}{special_bits}'.format(
      owner=mode_bits(stat_obj.st_mode, 2),
      group=mode_bits(stat_obj.st_mode, 1),
      other=mode_bits(stat_obj.st_mode, 0),
      special_bits=special_bits(stat_obj.st_mode),
    ))
    emit('ctime', see_time(stat_obj.st_ctime))
    emit('mtime', see_time(stat_obj.st_mtime))
    emit('size',  '{size:,} bytes, {size:.2e}, {human_size}'.format(size= stat_obj.st_size, human_size=human_size(stat_obj.st_size)))
    emit('user',  see_user(stat_obj.st_uid))
    emit('group', see_group(stat_obj.st_gid))
    emit('inode', stat_obj.st_ino)
    emit('dev', stat_obj.st_dev)

  if count:
    print('')

  count += 1

count = 0

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()

list(map(process, sys.argv[1:]))
