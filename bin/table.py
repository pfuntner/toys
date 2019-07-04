#! /usr/bin/env python

import re
import sys
import csv
import json
import string
import logging
import argparse
import StringIO


class MethodBase(object):
  name = None

  def validate(self, root):
    if not isinstance(root, list):
      parser.error('Root object is not a list')
    if root:
      expected_type = type(root[0])
      if expected_type not in [list, dict]:
        parser.error('First row is a {}, not a list or dictionary'.format(expected_type))
      for item in root:
        if type(item) != expected_type:
          parser.error('Row type does not match first row')
          for col in item:
            if type(col) not in [str, unicode, int, float, bool]:
              parser.error('Row column is unexpected type')


  def get_key(self, pattern, actual_keys):
    regexp = re.compile(pattern)
    keys = [key for key in actual_keys if regexp.search(key)]
    if len(keys) == 1:
      return keys[0]
    elif keys:
      parser.error('{pattern!r} is an ambiguous column: select {keys}'.format(**locals()))
    else:
      parser.error('{pattern!r} matches no columns: {actual_keys}'.format(**locals()))

  def make_order(self, root):
    order = []
    if root and isinstance(root[0], dict):
      keys = set()
      for item in root:
        for key in item.keys():
          keys.add(key)
      for key in args.order or []:
        key = self.get_key(key, keys)
        keys.remove(key)
        order.append(key)
      order += sorted(list(keys))
    return order

  def markup(self, stream, row, prefix, separator, suffix):
    stream.write(prefix)
    stream.write(separator.join(row))
    stream.write(suffix + '\n')


class CsvMethod(MethodBase):
  name = 'csv'

  def read(self, stream):
    rows = [row for row in csv.reader(stream)]
    if args.headings and rows:
      ret = []
      order = rows[0]
      for row in rows[1:]:
        ret.append({name: row[pos] for (pos, name) in enumerate(order)})
    else:
      ret = rows
      order = []
    self.validate(ret)
    return (ret, order)

  def write(self, stream, root, order):
    writer = csv.writer(stream)
    if order:
      writer.writerow(order)
    for row in root:
      if isinstance(row, list):
        writer.writerow(row)
      else:
        if order:
          writer.writerow([row.get(name, '') for name in order])
        else:
          parser.error('Cannot write a dictionary without an order for columns')


class JsonMethod(MethodBase):
  name = 'json'

  def read(self, stream):
    ret = json.load(stream)
    self.validate(ret)
    return (ret, self.make_order(ret))

  def write(self, stream, root, order):
    json.dump(root, stream, indent=2, sort_keys=True)
    stream.write('\n')


class YamlMethod(MethodBase):
  name = 'yaml'

  def read(self, stream):
    ret = yaml.load(stream)
    self.validate(ret)
    return (ret, self.make_order(ret))

  def write(self, stream, root, order):
    yaml.dump(root, stream)


class SeparatorMethod(MethodBase):
  name = 'separator'

  def read(self, stream):
    root = []
    headings = []
    leading_sep = False
    trailing_sep = False
    for (pos, line) in enumerate(stream.read().splitlines()):
      tokens = args.regexp.split(line)
      log.debug('tokens: {tokens}'.format(**locals()))
      if args.headings and (pos == 0):
        if not tokens:
          parser.error('No headings')
        leading_sep = not tokens[0]
        trailing_sep = (tokens[-1] == '') and (len(tokens) > 1)

      if leading_sep:
        if tokens[0]:
          parser.error('Unexpected token under empty leading heading')
        del tokens[0]

      if trailing_sep:
        if tokens[-1]:
          parser.error('Unexpected token under empty trailing heading')
        del tokens[-1]

      if args.headings and (pos == 0):
        headings = tokens
      else:
        if headings:
          if len(tokens) > len(headings):
            parser.error('Column without heading')
          root.append({heading: tokens[pos] for (pos, heading) in enumerate(headings)})
        else:
          root.append(tokens)

    return (root, headings)


  def write(self, stream, root, order):
    for (pos, row) in enumerate(root):
      log.debug('{pos}: {row}'.format(**locals()))
      if isinstance(row, dict):
        if pos == 0:
          stream.write(args.separator.join(order))
          stream.write('\n')
        stream.write(args.separator.join([row[name] for name in order]))
      else:
        stream.write(args.separator.join(row))
      stream.write('\n')


class FixedMethod(MethodBase):
  name = 'fixed'

  def read(self, stream):
    root = []
    headings = []
    columns = []

    lines = stream.read().splitlines()
    c = 0
    start = 0
    while any([c < len(line) for line in lines]):
      if all([line[c:c+1] in string.whitespace for line in lines]) and any([line[start:c].strip() for line in lines]):
        columns.append((start, c))
        start = c
      c += 1

    if any([line[start:].strip() for line in lines]):
      columns.append((start, sys.maxint))

    log.debug('columns: {columns}'.format(**locals()))

    if args.headings and lines:
      headings = [lines[0][stops[0]:stops[1]].strip() for stops in columns]

    for line in lines[1 if args.headings else 0:]:
      if args.headings:
        root.append({headings[num]: line[start:stop].strip() for (num, (start, stop)) in enumerate(columns)})
      else:
        root.append([line[start:stop].strip() for (start, stop) in columns])

    return (root, headings)


  def write(self, stream, root, order):
    widths = []
    for (row_num, row) in enumerate(root):
      if isinstance(row, dict):
        if row_num == 0:
          for (col_num, col) in enumerate(order):
            widths.append(len(col))
        for (col_num, col) in enumerate(order):
          widths[col_num] = max(widths[col_num], len(row.get(col, '')))
      else:
        for (col_num, col) in enumerate(row):
          if col_num == len(widths):
            widths.append(len(col))
          else:
            widths[col_num] = max(widths[col_num], len(col))

    log.debug('widths: {widths}'.format(**locals()))

    for (row_num, row) in enumerate(root):
      if isinstance(row, dict):
        if row_num == 0:
          stream.write(args.separator.join([col.ljust(widths[col_num]) for (col_num, col) in enumerate(order)]))
          stream.write('\n')
        stream.write(args.separator.join([row.get(col, '').ljust(widths[col_num])
                                          for (col_num, col) in enumerate(order)]))
      else:
        stream.write(args.separator.join([(row[col_num] if col_num < len(row) else '').ljust(width)
                                          for (col_num, width) in enumerate(widths)]))

      stream.write('\n')


class HtmlMethod(MethodBase):
  name = 'html'

  def write(self, stream, root, order):
    stream.write('<table>\n')
    stream.write('<tbody>\n')
    if root and isinstance(root[0], dict):
      self.markup(stream, order, '<tr><th>', '</th><th>', '</th></tr>')
      for row in root:
        self.markup(stream, [row.get(col, '') for col in order], '<tr><td>', '</td><td>', '</td></tr>')
    else:
      for row in root:
        self.markup(stream, row, '<tr><td>', '</td></tr>', '</td><td>')
    stream.write('</tbody>\n')
    stream.write('</table>\n')


class MarkdownMethod(MethodBase):
  name = 'markdown'

  def write(self, stream, root, order):
    if root and isinstance(root[0], dict):
      self.markup(stream, order, '| ', ' | ', ' |')
      self.markup(stream, ['-'] * len(order), '| ', ' | ', ' |')
      for row in root:
        self.markup(stream, [row.get(col, '') for col in order], '| ', ' | ', ' |')
    else:
      for row in root:
        self.markup(stream, row, '| ', ' | ', ' |')


class BbcodeMethod(MethodBase):
  name = 'bbcode'

  def write(self, stream, root, order):
    stream.write('[table]\n')
    if root and isinstance(root[0], dict):
      self.markup(stream, order, '[tr][th]', '[/th][th]', '[/th][/tr]')
      for row in root:
        self.markup(stream, [row.get(col, '') for col in order], '[tr][td]', '[/td][td]', '[/td][/tr]')
    else:
      for row in root:
        self.markup(stream, row, '[tr][td]', '[/td][/tr]', '[/td][td]')
    stream.write('[/table]\n')


class Table(object):
  def __init__(self, headings, desiredSep=None):
    self.root = []
    self.headings = headings
    if desiredSep:
      args.separator = desiredSep

  def add(self, row):
    self.root.append({name: row[pos] for (pos, name) in enumerate(self.headings)})

  def reverse(self):
    self.root.reverse()

  def __str__(self):
    buf = StringIO.StringIO()
    args.output.write(buf, self.root, self.headings)
    return buf.getvalue()


def method_names(method_type):
  global methods
  ret = []
  for (name, value) in globals().items():
    if method_name_regexp.match(name) and type(value) == type:
      method = value()
      if isinstance(method, MethodBase):
        if method.name not in [curr.name for curr in methods]:
          methods.append(method)
        if hasattr(method, method_type):
          ret.append(value.name)
  return ret


def get_method(name):
  for method in methods:
    if method.name == name:
      return method
  parser.error('{name!r} is an unsupported I/O method'.format(**locals()))


def order_splitter(arg):
  return arg.split(',')


def method_abbreviator(arg):
  # log.debug('arg: {arg}'.format(**locals()))
  regexp = re.compile(arg)
  matches = []
  for method in methods:
    if regexp.match(method.name):
      matches.append(method.name)
  # log.debug('matches: {matches}'.format(**locals()))
  return matches[0] if len(matches) == 1 else arg


logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()

method_name_regexp = re.compile('[A-Z][a-z]+Method$')
methods = []

parser = argparse.ArgumentParser(description='Super Table - work in progress')
parser.add_argument('-H', '--headings', dest='headings', action='store_true', help='Treat row 1 as columns')
parser.add_argument('-i', '--input', dest='input', help='Input method', type=method_abbreviator,
                    choices=method_names('read'), required=True)
parser.add_argument('-o', '--output', dest='output', help='Output method', type=method_abbreviator,
                    choices=method_names('write'), required=True)
parser.add_argument('--order', dest='order', type=order_splitter, help='Specify the order of columns')
parser.add_argument('-r', '--regexp', help='Regular expression to be used as an input separator', default=r'\s+')
parser.add_argument('-s', '--separator', help='Output separator')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable debugging')

args = parser.parse_args() if __name__ == '__main__' else parser.parse_args(['-i', 'separator', '-o', 'fixed'])

log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

args.separator = args.separator or (' ' if args.output == 'fixed' else '|')

args.input = get_method(args.input)
args.output = get_method(args.output)

if args.regexp:
  args.regexp = re.compile(args.regexp)

if 'yaml' in [args.input.name, args.output.name]:
  yaml = __import__('yaml')

if __name__ == '__main__':
  if sys.stdin.isatty():
    parser.error('stdin must be redirected')

  (root, order) = args.input.read(sys.stdin)
  log.debug('order: {order}'.format(**locals()))
  log.debug('root: {root}'.format(**locals()))
  args.output.write(sys.stdout, root, order)