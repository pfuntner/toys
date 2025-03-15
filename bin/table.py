#! /usr/bin/env python3

import re
import sys
import csv
import json
import string
import signal
import logging
import argparse
import platform
import io
import xml.etree.ElementTree as ET


class MethodBase(object):
  """
  Base class for the I/O methods.  Contains some common methods.
  """
  name = None
  method_exclusions = list()

  def normalize(self, s):
    """
    Normalize a string by replacing non-alphanumerics with underscores
    :param s: The input string
    :return: The normalized string
    """
    s = normalizing_regexp.sub('_', s)
    if s[0:1] in string.digits:
      s = '_' + s
    return s


  def validate(self, root):
    """
    Validate a table after it's read.  Since JSON and YAML files could have arbitrary structure, the method ensures
    the following after reading such formats:

      1) The root object is a list
      2) Either:
         a) each element is a list
         b) each element is a dictionary
      3) Each element of the lists/dictionaries from step 2 is a simple type such as string, int, etc.
    :param root: The root object to consider
    :return: None
    """
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


  def stringify(self, root):
    """
    Replace unicode strings with regular strings
    :param root: A list of lists or dictionaries
    :return: The list of lists or dictionaries with unicode elements replaced with regular strings
    """
    for item in root:
      if isinstance(item, dict):
        kvs = list(item.items())
        for (key, value) in kvs:
          del item[key]
          item[str(key)] = str(value)
      else:
        for (pos, value) in enumerate(item):
          item[pos] = str(value)
    return root

  def get_key(self, pattern, actual_keys):
    """
    Get a key from a list of keys.
    :param pattern: An input regular expression pattern that should map to a single key
    :param actual_keys: The actual keys from which to choose
    :return:
    """
    regexp = re.compile(pattern, flags=re.IGNORECASE)
    keys = [key for key in actual_keys if regexp.search(key)]
    if len(keys) == 1:
      return keys[0]
    elif keys:
      parser.error('{pattern!r} is an ambiguous column: select {keys}'.format(**locals()))
    else:
      parser.error('{pattern!r} matches no columns: {actual_keys}'.format(**locals()))

  def make_order(self, root):
    """
    Create a ordered list of dictionary keys to be used in outputing the column when order is significant.  The list
    favors the user-specified order and completes the list with remaining columns in alphabetical order.
    :param root: A list of lists or dictionaries.
    :return: A list of column names when given a list of dictionaries.  The return is an empty list when given a list
    of lists
    """
    order = []
    if root and isinstance(root[0], dict):
      if args.no_sort:
        for item in root:
          for key in item.keys():
            if not key in order:
              order.append(key)
      else:
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
    """
    Emit a heading or data row using markup tags.
    :param stream: The output stream (eg sys.stdout)
    :param row: A list of the heading names or columnar data.
    :param prefix: The tag(s) that should begin the row
    :param separator: The tag(s) that will separate columns
    :param suffix: The tg(s) that should end the row
    :return:
    """
    stream.write(prefix)
    stream.write(separator.join(row))
    stream.write(suffix + '\n')

  def justify(self, s, width):
    return s.rjust(width) if (numeric_regexp.search(s) and args.numeric_justify) else s.ljust(width)

class XmlMethod(MethodBase):
  """
  Handle I/O for XML format
  """
  name = 'xml'

  def read(self, stream):
    """
    Read a list dictionaries in XML format - it is not possible to produce a list of lists
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of dictionaries, a list of named column headings)
    """
    ret = []
    order = []

    row_tag = None

    tree = ET.parse(stream)
    root = tree.getroot()
    for row in root:
      if row_tag and row_tag != row.tag:
        parser.error('Expected row tag <{row_tag}> but got <{row.tag}> instead'.format(**locals()))
      row_tag = row.tag
      ret.append({})

      for column in row:
        ret[-1][column.tag] = column.text or ''

    return (ret, self.make_order(ret))

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in XML format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of dictionaries
    :param order: The order of named columns - ignored for this method
    :return: None
    """

    if root:
      tree = ET.Element('table')
      for row in root:
        tree_row = ET.SubElement(tree, 'row')
        if isinstance(row, list):
          for (pos, col) in enumerate(row):
            tree_col = ET.SubElement(tree_row, 'col{pos:>08}'.format(**locals()))
            tree_col.text = col
        else:
          for (key, col) in row.items():
            tree_col = ET.SubElement(tree_row, self.normalize(key))
            tree_col.text = col

      stream.write(ET.tostring(tree).decode('utf-8') + '\n')

class CsvMethod(MethodBase):
  """
  Handle I/O for CSV format
  """
  name = 'csv'

  def read(self, stream):
    """
    Read a list of lists or dictionaries in CSV format
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    rows = [row for row in csv.reader(stream)]
    if args.degunk and len(rows) > 0 and len(rows[0]) >= 1 and len(rows[0][0]) > 0 and rows[0][0][0] == '\ufeff':
      rows[0][0] = rows[0][0][1:]
    if args.headings and rows:
      """
        Turn the list of lists into a list of dictionaries making use of the heading row
      """
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
    """
    Write the list of lists or dictionaries in CSV format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
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


class FlatMethod(MethodBase):
  """
  Handle I/O for "flat" format
  """
  name = 'flat'

  def read(self, stream):
    """
    Read a list of lists or dictionaries in flat format:
       datum1-1
       datum1-2
       .
       .
       datum1-n

       datum2-1
       datum2-2
       .
       .
       datum2-n
       .
       .

    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    lines = [line.rstrip() for line in stream.read().splitlines()]
    log.info('{count} lines read'.format(count=len(lines)))
    ret = []
    order = []
    pos = 0
    if args.headings:
      while pos < len(lines) and ((pos < args.columns) if args.columns is not None else lines[pos]):
        order.append(lines[pos])
        pos += 1
    log.info(f'order: {order}')

    if not args.columns:
      pos += 1
    while pos < len(lines):
      row = {} if args.headings else []
      ret.append(row)
      log.info('Starting to read data row at line {pos}'.format(**locals()))
      while (pos < len(lines)) and ((len(row) < args.columns) if args.columns else lines[pos]):
        log.info('{pos}: {line!r}'.format(pos=pos, line=lines[pos]))
        if args.headings:
          inner_pos = len(row)
          if inner_pos >= len(order):
            parser.error('Column {inner_pos} encountered when only {count} headings'.format(inner_pos=inner_pos, count=len(order)))
          row[order[inner_pos]] = lines[pos]
        else:
          row.append(lines[pos])
        pos += 1
      if not args.columns:
        pos += 1

    return (ret, order)

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in flat format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    need_newline = False
    for row in root:
      if need_newline:
        stream.write('\n')
      need_newline = True
      if isinstance(row, list):
        stream.write('\n'.join(row) + '\n')
      else:
        for column in order:
          stream.write(row[column] + '\n')

class FormMethod(MethodBase):
  """
  Handle I/O for "form" format
  """
  name = 'form'

  def read(self, stream):
    """
    Read a dictionary for a single row:
       key1
       value1
       key2
       value2
       .
       .
       .
       keyN
       valueN

    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    lines = [line.rstrip() for line in stream.read().splitlines()]
    log.info('{count} lines read'.format(count=len(lines)))
    ret = [{}]
    order = []
    pos = 0
    while pos < len(lines):
      key = lines[pos]
      order.append(key)
      pos += 1
      if pos >= len(lines):
        parser.error('Read key {key!r} without a value'.format(**locals()))
      ret[0][key] = lines[pos]
      pos += 1

    return (ret, order)

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in form format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    if not isinstance(root, dict):
      parser.error('Form format requires a dictionary')
    if len(root) != 1:
      parser.error('A {count} element dictionary cannot be processed in form format'.format(count=len(root)))
    for column in order:
      stream.write(column + '\n')
      stream.write(root[0][column] + '\n')

class JsonMethod(MethodBase):
  """
  Handle I/O for JSON format
  """
  name = 'json'

  def read(self, stream):
    """
    Read a list of lists of dictionaries in JSON format
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    ret = json.load(stream)
    self.validate(ret)
    self.stringify(ret)
    return (ret, self.make_order(ret))

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in JSON format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    json.dump(root, stream, indent=2)
    stream.write('\n')


class YamlMethod(MethodBase):
  """
  Handle I/O for YAML format
  """
  name = 'yaml'

  def read(self, stream):
    """
    Read a list of lists of dictionaries in YAML format
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    ret = yaml.load(stream)
    self.validate(ret)
    return (ret, self.make_order(ret))

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in YAML format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    yaml.dump(root, stream, default_flow_style=False if args.style == 'block' else None)


class SeparatorMethod(MethodBase):
  """
  Handle I/O for a free-form format where columns are separated by some set of characters (whitespace, a vertical bar,
  etc.)
  """
  name = 'separator'

  def read(self, stream):
    """
    Read a list of lists of dictionaries in free format where columns are separated by a set of characters
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    root = []
    headings = []
    leading_sep = False
    trailing_sep = False
    for (pos, line) in enumerate(stream.read().splitlines()):
      tokens = args.regexp.split(line)
      log.debug('tokens: {tokens}'.format(**locals()))

      if pos == 0:
        """
        Strip off empty beginning and trailing tokens in case the separator is used as a border
        """
        leading_sep = not tokens[0]
        trailing_sep = (tokens[-1] == '') and (len(tokens) > 1)

      if leading_sep:
        if tokens[0]:
          # parser.error('Unexpected token under empty leading heading')
          pass
        # del tokens[0]
        pass

      if trailing_sep:
        if tokens[-1]:
          # parser.error('Unexpected token under empty trailing heading')
          pass
        # del tokens[-1]
        pass

      if args.headings and (pos == 0):
        if not tokens:
          parser.error('No headings')
        headings = tokens
      else:
        if headings:
          if len(tokens) > len(headings):
            parser.error('Column without heading: {tokens} > {headings}'.format(**locals()))
          root.append({heading: tokens[heading_pos] if heading_pos < len(tokens) else ''
                       for (heading_pos, heading) in enumerate(headings)})
        else:
          root.append(tokens)

    return (root, headings)


  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in free format with a separator
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """

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
  """
  Handle I/O of a fixed column format
  """
  name = 'fixed'

  def read(self, stream):
    """
    Read a list of lists of dictionaries in fixed column format
    :param stream: The input stream (eg sys.stdin)
    :return: A two-element tuple: (the list of lists or dictionaries, a list of named column headings)
    """
    root = []
    headings = []
    columns = []

    lines = [line.rstrip() for line in stream.read().splitlines()]

    if (not args.headings) or args.loose_headings:
      """
      Most columns are probably left-justified but some (like numeric data) might be right-justified.  We need to
      examine all the lines to see where each column begins and ends.  We'll consider a column complete when we reach
      the end of a column where the same position is whitespace on all of the lines.
      """

      c = 0
      start = 0
      while any([c < len(line) for line in lines]):
        if all([line[c:c+1].ljust(1) in string.whitespace for line in lines]) and \
            any([line[start:c].strip() for line in lines]):
          """
          Remember the beginning and end of this column
          """
          columns.append((start, c))
          start = c
        c += 1

      """
      Complete the trailing column
      """
      if any([line[start:].strip() for line in lines]):
        columns.append((start, sys.maxsize))
    else:
      if lines:
        maxlen = max([len(line) for line in lines])
        delimiters = list(re.finditer(r'(\s{2,})', lines[0]))
        if delimiters:
          if delimiters[0].start(1) > 0:
            log.debug('First delimiter: {}:{} {!r}'.format(delimiters[0].start(1), delimiters[0].end(1), delimiters[0].group(1)))
            columns.append((0, delimiters[0].end(1)))
          else:
            parser.error('Leading columns in heading row no allowed')
          for (pos, delimiter) in enumerate(delimiters):
            columns.append((delimiter.end(1), maxlen if pos + 1 == len(delimiters) else delimiters[pos + 1].end(1)))
        else:
          columns = [(0, maxlen)]
      else:
        parser.error('No heading row')

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
    """
    Write the list of lists or dictionaries in fixed column format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """

    log.info('args.rotate: {}, order: {}'.format(args.rotate, order))
    if args.rotate and order:
      new_root = []
      if order:
        for heading in order:
          new_root.append([heading])
          for row in root:
            new_root[-1].append(row.get(heading, ''))
      root = new_root

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

    if isinstance(self, BannerMethod):
      (prolog, epilog) = ('| ', '|')
      pad_width = sum(widths) + 3 * len(widths)
      border = '+' + ('+'.join(['-' * (width+2) for width in widths])) + '+'
    else:
      (prolog, epilog) = ('', '')
      pad_width = 0
      border = None

    for (row_num, row) in enumerate(root):
      if isinstance(row, dict):
        if row_num == 0:
          if border:
            stream.write(border + '\n')
          stream.write((prolog + (args.separator.join([col.ljust(widths[col_num]) for (col_num, col) in enumerate(order)]).rstrip())).ljust(pad_width) + epilog)
          stream.write('\n')
          if border:
            stream.write(border + '\n')
        stream.write((prolog + (args.separator.join([self.justify(row.get(col, ''), widths[col_num])
                                          for (col_num, col) in enumerate(order)]).rstrip())).ljust(pad_width) + epilog)
      else:
        border = None
        stream.write(args.separator.join([self.justify(row[col_num] if col_num < len(row) else '', width)
                                          for (col_num, width) in enumerate(widths)]).rstrip())
      stream.write('\n')

    if border:
      stream.write(border + '\n')



class BannerMethod(FixedMethod):
  """
  Handle output in banner format.  This is similar to fixed format but will include pretty borders around the columns

  This class does not support reading data in banner format.
  """
  name = 'banner'
  method_exclusions = ['read']

  pass


class HtmlMethod(MethodBase):
  """
  Handle output in the HTML format.

  This class does not support reading data in HTML format.
  """
  name = 'html'

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in HTML format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
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
  """
  Handle output in the Markdown format.

  This method does not support reading data in HTML format.
  """
  name = 'markdown'

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in Markdown format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    if root and isinstance(root[0], dict):
      self.markup(stream, order, '| ', ' | ', ' |')
      self.markup(stream, ['-'] * len(order), '| ', ' | ', ' |')
      for row in root:
        self.markup(stream, [row.get(col, '') for col in order], '| ', ' | ', ' |')
    else:
      for row in root:
        self.markup(stream, row, '| ', ' | ', ' |')


class BbcodeMethod(MethodBase):
  """
  Handle output in the BBCode format.

  This method does not support reading data in HTML format.
  """
  name = 'bbcode'

  def write(self, stream, root, order):
    """
    Write the list of lists or dictionaries in BBCode format.
    :param stream: The output stream (eg. sys.stdout)
    :param root: The list of lists or dictionaries
    :param order: The order of named columns if order is important
    :return: None
    """
    stream.write('[table]\n')
    if root and isinstance(root[0], dict):
      self.markup(stream, order, '[tr][th]', '[/th][th]', '[/th][/tr]')
      for row in root:
        self.markup(stream, [row.get(col, '') for col in order], '[tr][td]', '[/td][td]', '[/td][/tr]')
    else:
      for row in root:
        self.markup(stream, row, '[tr][td]', '[/td][td]', '[/td][/tr]')
    stream.write('[/table]\n')


class Table(object):
  """
  This class can be used by other scripts to produce fixed column output.  It provides an add() method so the caller
  can provide input in a different way
  """
  # def __init__(self, headings=None, desiredSep=None, numeric_justify=False):
  def __init__(self, *arg_list, **kwargs):
    """
    The constructor prepares the caller to provide data.
    :param arg_list: The list of headings.  This could be:
      - One element consisting of a list of strings to be used as headings
      - No elements => no headings
    :param kwargs: A dictionary supporting these keys:
      desiredSep: The optional desired separator - the default separator is used if one is not specified by the caller
      numeric_justify: Boolean indicating whether to right-justify numeric columns
    """
    self.root = []
    if (len(arg_list) == 1) and isinstance(arg_list[0], list):
      self.headings = arg_list[0]
    else:
      self.headings = arg_list
    args.separator = kwargs.get('desiredSep') or args.separator
    args.numeric_justify = kwargs.get('numeric_justify', False)

  def append(self, *args):
    """
    This method performs the same function as add().  I added it because I can't
    remember if the method is add() or append() so this will allow either to work.
    """
    self.add(*args)

  def add(self, *args):
    """
    This method is used by the caller to add a new row to the table
    :param args: The row: if there is one element and it is an Iterable, the elements of the first element are the
    columns.  Otherwise, each element is a column.
    :return: None
    """
    if (len(args) == 1) and type(args[0]) in [list, tuple]:
      row = args[0]
    else:
      row = args
    if self.headings:
      assert len(row) == len(self.headings), 'Expected {} columns but got {}'.format(len(self.headings), len(row))
      self.root.append({name: str(row[pos]) for (pos, name) in enumerate(self.headings)})
    else:
      self.root.append([col for col in row])

  def reverse(self):
    """
    Used by the caller to reverse the rows in the table, typically after all rows have been added.
    :return: None
    """
    self.root.reverse()

  def __str__(self):
    """
    Convert the table into fixed column format.
    :return: A single string with newlines to present the table with fixed columns
    """
    buf = io.StringIO()
    args.output.write(buf, self.root, self.headings)
    return buf.getvalue()


def method_names(method_type):
  """
  Generate a list of names for the input or output methods
  :param method_type: Either "read" or "write" which specifies the method that the I/O method must support
  :return: A list of names of I/O methods that have the specified method_type
  """
  global methods
  ret = []
  for (name, value) in globals().items():
    if method_name_regexp.match(name) and type(value) == type:
      method = value()
      if isinstance(method, MethodBase):
        if method.name not in [curr.name for curr in methods]:
          methods.append(method)
        if hasattr(method, method_type) and method_type not in method.method_exclusions:
          ret.append(value.name)
  return ret


def get_method(name):
  """
  Get a method based on a I/O method name
  :param name: The name of the I/O method to locate
  :return: An instance of the specified I/O method class
  """
  for method in methods:
    if method.name == name:
      return method
  parser.error('{name!r} is an unsupported I/O method'.format(**locals()))


def order_splitter(arg):
  """
  Called from argparse.parse_args()
  :param arg: The --order argument specified by the user
  :return: A list of strings, seperating the --order argument at commas
  """
  return arg.split(',')


def method_abbreviator(arg):
  """
  Return the name of an I/O method based on a potential abbreviated name.  For example, "sep" should be sufficient
  to specify the separator I/O method
  :param arg: The I/O method name specified by the user
  :return: The name of the I/O method that uniquely matches the user argument.  If the argument does not uniquely
  match a single I/O method, the original argument is returned by the method - argparse.parse_args() will likely
  refuse to accept it because it won't match any of the exact I/O method names.
  """
  regexp = re.compile(arg)
  matches = []
  for method in methods:
    if regexp.match(method.name):
      matches.append(method.name)

  return matches[0] if len(matches) == 1 else arg


def to_numeric(s):
  """
  Convert a string to numeric if possible
  :param s: A string
  :return: The string interpreted as a numeric if possible.  Otherwise, it is simply the input string.
  """

  try:
    s = float(s)
  except Exception as e:
    log.debug('Caught `{e!s}` trying to cast {s!r} to numeric'.format(**locals()))
    pass
  return s


def sorter(a, b):
  """
  Sort two rows of a table as specified by args.sort.  If two or more columns are specified, they are examined in
  sequence until two unequal columns are found.
  :param a: First row
  :param b: Second row
  :return: -1 if a < b, 1 if a > b, 0 if a == b
  """
  ret = 0
  if isinstance(a, list):
    for key in args.sort:
      if key >= len(a):
        ret = -1
        break
      elif key >= len(b):
        ret = 1
        break
      elif a[key] != b[key]:
        ret = cmp(to_numeric(a[key]), to_numeric(b[key]))
        break
  else:
    for key in args.sort:
      if (key not in a) and (key in b):
        ret = -1
        break
      elif (key in a) and (key not in b):
        ret = 1
        break
      elif (key in a) and (key in b) and (a[key] != b[key]):
        ret = cmp(to_numeric(a[key]), to_numeric(b[key]))
        break
  return ret


logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
log = logging.getLogger()

normalizing_regexp = re.compile('[^a-zA-Z0-9]')
numeric_regexp = re.compile(r'^((\d+(\.\d+)?)|(\d*\.\d+))%?$')

method_name_regexp = re.compile('[A-Z][a-z]+Method$')
methods = []

parser = argparse.ArgumentParser(description='Process tabulur data in several input and output formats')
parser.add_argument('-H', '--headings', dest='headings', action='store_true', help='Treat row 1 as headings')
parser.add_argument('-l', '--loose-headings', dest='loose_headings', action='store_true', help='Use all rows to determine column widths')
parser.add_argument('-i', '--input', dest='input', help='Input method', type=method_abbreviator,
                    choices=method_names('read'), required=True)
parser.add_argument('-o', '--output', dest='output', help='Output method', type=method_abbreviator,
                    choices=method_names('write'), required=True)
parser.add_argument('-c', '--columns', type=int, help='Number of columns for the flat format')
parser.add_argument('--order', dest='order', type=order_splitter, help='Specify the order of columns')
parser.add_argument('-r', '--regexp', help='Regular expression to be used as an input separator', default=r'\s+')
parser.add_argument('-s', '--separator', help='Output separator')
parser.add_argument('--sort', help='Sort rows by one or more columns')
parser.add_argument('-n', '--numeric_justify', action='store_true',
                    help='Right-justify numeric columns during fixed format output')
parser.add_argument('--style', choices=['flow', 'block'], help='Specify an yaml output style')
parser.add_argument('--rotate', action='store_true', help='Rotate so rows are columns, columns are rows')
parser.add_argument('-f', '--file', help='File from which to read, instead of stdin')
parser.add_argument('--no-sort', action='store_true', help='Do not sort columns')
parser.add_argument('--degunk', action='store_true', help='''Remove '\\ufeff' from beginning of CSV data''')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable debugging')

args = parser.parse_args() if __name__ == '__main__' else parser.parse_args(['-i', 'separator', '-o', 'fixed'])

log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

if 'win' not in platform.platform().lower():
  signal.signal(signal.SIGPIPE, lambda signum, stack_frame: exit(0))

if args.loose_headings:
  args.headings = True

if args.separator is None:
  if args.output == 'fixed':
    args.separator = '  '
  elif args.output == 'banner':
    args.separator = ' | '
  else:
    args.separator = '|'

if args.separator == '\\t':
  args.separator = '\t'

args.input = get_method(args.input)
args.output = get_method(args.output)

if args.regexp:
  args.regexp = re.compile(args.regexp)

if 'yaml' in [args.input.name, args.output.name]:
  yaml = __import__('yaml')

if __name__ == '__main__':
  (root, order) = (None, None)
  if args.file:
    with open(args.file) as stream:
      (root, order) = args.input.read(stream)
  else:
    if sys.stdin.isatty():
      parser.error('stdin must be redirected if --file is not specified')
    (root, order) = args.input.read(sys.stdin)

  log.debug('order: {order}'.format(**locals()))
  log.debug('root: {root}'.format(**locals()))

  if args.sort:
    if root:
      if isinstance(root[0], list):
        args.sort = [int(key) for key in args.sort.split(',')]
      else:
        sort_list = []
        keys = set()
        for row in root:
          log.debug('keys available to sort with: {keys}'.format(**locals()))
          log.debug('row keys: {}'.format(row.keys()))
          keys = keys.union(set(row.keys()))
        for arg in args.sort.split(','):
          sort_list.append(args.input.get_key(arg, keys))
          keys.remove(sort_list[-1])
        args.sort = sort_list
      root.sort(cmp=sorter)

  args.output.write(sys.stdout, root, order)
