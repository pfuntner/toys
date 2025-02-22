# `data-shell`

## Purpose
An interactive _shell-like_ tool to explore a JSON, YAML, or XML file.

I am often frustrated by large complicated structured objects and had this wild idea of treating an object like a Unix filesystem: there is a root, child nodes, and grandchildren, you can navigate with `cd` along with other familiar Unix commands. 

## Syntax
```
Syntax: data-shell [-v] filename
```

### Options
| Option | Description | Default                                |
| ------ | ----------- |----------------------------------------|
|  `-v`  | Enable verbose debugging | Debugging is not enabled  |

## Examples

Unlike a lot of my other tools, the examples are in the forms of interactive subcommands in the tool so I'll give examples of those.

Since there are so many subcommands and some of the help information is a little long, I'll provide a table of contents:

- [cat](#cat)
- [cd](#cd)
- [describe](#describe)
- [exit](#exit)
- [find](#find)
- [grep](#grep)
- [help](#help)
- [ls](#ls)
- [pwd](#pwd)

There's also [an example using an XML file](#XML-example).

### JSON file used in examples
I'll also use the following JSON file in most of the examples:
```json
{
  "bools": [true, false],
  "ints": [42, 32768, -1],
  "floats": [3.141592654, 2.7182818285, -0.000001],
  "strs": ["a", "b", "foo", "bar"],
  "none": null,
  "dict": {
    "1": [".", "one", "One", "ONE"],
    "2": ["..", "two", "Two", "TWO"]
  }
}
```
This is also available [from a Gist](https://gist.githubusercontent.com/pfuntner/cdf1e734371cafe904f78b6b836347e4/raw/195b0f0fdcb402bc8182081cbe984ac336800cd2/help-example.json).

Here's an example of downloading the smple on the fly without storing it in a file, even a conventional temporary file:
```commandline
$ data-shell <(curl https://gist.githubusercontent.com/pfuntner/cdf1e734371cafe904f78b6b836347e4/raw/195b0f0fdcb402bc8182081cbe984ac336800cd2/help-example.json 2>/dev/null)
Confoozed?  Try `help`
/> describe
/ is a dict with 6 elements
/> quit
$ 
```

I didn't do an example using YAML but there aren't really any surprises. 

### The prompt
The tool prompts for subcommands includes the _current location_ much like the current working directory as in a filesystem.
```commandline
$ data-shell sample.json
Confoozed?  Try `help`
/> 
```
The initial current location is `/` since you always begin in the root node.  The `> ` is asking for a subcommand to be entered.

### `cat`
`cat` will display the current or target node and all of its children.

```commandline
/> cat
{
  "bools": [
    true,
    false
  ],
  "ints": [
    42,
    32768,
    -1
  ],
  "floats": [
    3.141592654,
    2.7182818285,
    -1e-06
  ],
  "strs": [
    "a",
    "b",
    "foo",
    "bar"
  ],
  "none": null,
  "dict": {
    "1": [
      ".",
      "one",
      "One",
      "ONE"
    ],
    "2": [
      "..",
      "two",
      "Two",
      "TWO"
    ]
  }
}
/> cd dict
/dict> cat
{
  "1": [
    ".",
    "one",
    "One",
    "ONE"
  ],
  "2": [
    "..",
    "two",
    "Two",
    "TWO"
  ]
}
/dict> cat 1
[
  ".",
  "one",
  "One",
  "ONE"
]
/dict>
```

### `cd`
I'm taking great liberties with the name because we're not talking about a _current working directory_ but it's a similar concept.  You can `cd` into any child of the current node that's a list or dictionary:
```commandline
/> cd bools
/bools> cd ..
/> cd dict
/dict> cd 1
/dict/1> cd
/> 
```
The _keys_ you can `cd` into are based on the type of node you're currently in:
- If the current node is a dictionary, the keys of the dictionary are the keys you can cd into.
- If the current node is a list, the keys are integers from 0 to the length of the list minus one.

You don't have to treat the key differently based on whether you're in a list or dicitonary.  The tool knows what type of key is needed.

There are invalid `cd`s based on the current node:
```commandline
/> cd foo
'foo' is not a key
/> cd floats
/floats> cd 3
3 is out of range
/floats> cd -1
-1 is out of range
/floats> cd 0
0 is not a list or dictionary
/floats> cd foo
'foo' is not an integer: invalid literal for int() with base 10: 'foo'
/floats> 
```

### `describe`
The `describe` subcommand _describes_ the current or target node:
```commandline
/> describe
/ is a dict with 6 elements
/> describe ints
/ints is a list with 3 elements
/> cd ints
/ints> describe
/ints is a list with 3 elements
/ints> describe 0
/ints/0 is a int
/ints> 
```

### `exit`
The `exit` and `quit` subcommands terminate the tool and return you to the Unix shell.  The subcommands are synonymous.

### `find`
The `find` command list elements starting at the current node, one node per line, with no indentation:

```commandline
/> find
/
/bools/
/bools/0: True
/bools/1: False
/ints/
/ints/0: 42
/ints/1: 32768
/ints/2: -1
/floats/
/floats/0: 3.141592654
/floats/1: 2.7182818285
/floats/2: -1e-06
/strs/
/strs/0: 'a'
/strs/1: 'b'
/strs/2: 'foo'
/strs/3: 'bar'
/none: None
/dict/
/dict/1/
/dict/1/0: '.'
/dict/1/1: 'one'
/dict/1/2: 'One'
/dict/1/3: 'ONE'
/dict/2/
/dict/2/0: '..'
/dict/2/1: 'two'
/dict/2/2: 'Two'
/dict/2/3: 'TWO'
/> 
```

I find this kind of display very useful when I'm writing code to navigate through a structure to find specific elements.

### `grep`
The `grep` command list elements starting at the current node, one node per line, that either match or do not match the regular expression(s):

#### Simple search
```commandline
/> grep e
/bools/0: True
/bools/1: False
/floats/2: -1e-06
/none: None
/dict/1/1: 'one'
/dict/1/2: 'One'
/> 
```

#### Key-only search
```commandline
/> grep e=
/none: None
/> 
```

#### Value-only search
```commandline
/> grep =o
/strs/2: 'foo'
/none: None
/dict/1/1: 'one'
/dict/2/1: 'two'
/dict/2/2: 'Two'
/> 

```

#### Case-insensitive search
```commandline
/> grep -i =o
/strs/2: 'foo'
/none: None
/dict/1/1: 'one'
/dict/1/2: 'One'
/dict/1/3: 'ONE'
/dict/2/1: 'two'
/dict/2/2: 'Two'
/dict/2/3: 'TWO'
/> 
```

#### Negated search
```commandline
/> grep -vi =o
/
/bools/
/bools/0: True
/bools/1: False
/ints/
/ints/0: 42
/ints/1: 32768
/ints/2: -1
/floats/
/floats/0: 3.141592654
/floats/1: 2.7182818285
/floats/2: -1e-06
/strs/
/strs/0: 'a'
/strs/1: 'b'
/strs/3: 'bar'
/dict/
/dict/1/
/dict/1/0: '.'
/dict/2/
/dict/2/0: '..'
/> 
```

### `help`
You can get general help of all subcommands:

```commandline
/> help
Navigate around a JSON document, just like a shell, only different!

Commands:

  cat       Display the current node or a child
              `cat` by itself displays the current node
              `cat key` display child element `key` of the current node

  cd        Change the current node
              `cd` by itself goes to root node
              `cd ..` go to parent node as long as you're not already at the root
              `cd key` goes to a child node if the key exists and its node is a dictionary or list

  describe  Describe a node
              `describe` describes the current node
              `describe key` describes the child element `key` of the current node

  exit      Exit from data-shell

  find      List structure with each element on a separate line without indentation:
               key/key/.../key/key: value

  grep      Search structure for regular expressions
               grep re        # search for the regular expression in key or value
               grep re1=re2   # search for re1 in key and re2 in value
            
            Options:
               -i     perform case-insensitive search
               -v     show elements that do not match regular expression(s)
            
            Notes:
               Non-string values are cast to strings and then searched

  help      Display help

  ls        List keys in the current node

  pwd       Print the current node - note that this is included in each prompt

  quit      Exit from data-shell
/>
```

or you can get help on a specific subcommand:
```commandline
/> help cd
Change the current node
  `cd` by itself goes to root node
  `cd ..` go to parent node as long as you're not already at the root
  `cd key` goes to a child node if the key exists and its node is a dictionary or list
/> 
```

### `ls`
The `ls` subcommand displays the keys of the current node:
```commandline
/> ls
bools  ints  floats  strs  none  dict
/> cd dict
/dict> ls
1  2
/dict> cd 1
/dict/1> ls
0  1  2  3
/dict/1> 
```

### `pwd`
The `pwd` subcommand prompts the location of the current node - in a filesystem, you might think of this as the _current working directory_.  It's also part of each and every prompt but it's such a popular command and it was an easy thing to add so I added it. 

### XML example
I've extended the command to handle XML files but I had to reimagine the nodes since they are structured differently than simple lists and dictionaries.  I hope the restructuring makes sense.  The file is available at [example.xml](https://gist.githubusercontent.com/pfuntner/7f36b9d4b9f91b674945bd6bf6b32f3a/raw/2f6ddfd40b35ef77c7b4bc4a2658f771e061acb3/example.xml).

```commandline
$ cat foo.html
<html>
<title>Hello, world</title>
<body>
<h1>Table time</h1>
<table border='1'>
<tr>
<th>Cell</th>
<th>Value></th>
</tr>
<tr>
<td>One</td>
<td>1</td>
</tr>
</table>
<br/>
<p>Good bye</p>
</body>
</html>
$ data-shell foo.html
Confoozed?  Try `help`
/> find
/
/0/
/0/tag: 'html'
/0/text: '\n'
/0/children/
/0/children/0/
/0/children/0/tag: 'title'
/0/children/0/text: 'Hello, world'
/0/children/0/tail: '\n'
/0/children/1/
/0/children/1/tag: 'body'
/0/children/1/text: '\n'
/0/children/1/tail: '\n'
/0/children/1/children/
/0/children/1/children/0/
/0/children/1/children/0/tag: 'h1'
/0/children/1/children/0/text: 'Table time'
/0/children/1/children/0/tail: '\n'
/0/children/1/children/1/
/0/children/1/children/1/tag: 'table'
/0/children/1/children/1/attrib/
/0/children/1/children/1/attrib/border: '1'
/0/children/1/children/1/text: '\n'
/0/children/1/children/1/tail: '\n'
/0/children/1/children/1/children/
/0/children/1/children/1/children/0/
/0/children/1/children/1/children/0/tag: 'tr'
/0/children/1/children/1/children/0/text: '\n'
/0/children/1/children/1/children/0/tail: '\n'
/0/children/1/children/1/children/0/children/
/0/children/1/children/1/children/0/children/0/
/0/children/1/children/1/children/0/children/0/tag: 'th'
/0/children/1/children/1/children/0/children/0/text: 'Cell'
/0/children/1/children/1/children/0/children/0/tail: '\n'
/0/children/1/children/1/children/0/children/1/
/0/children/1/children/1/children/0/children/1/tag: 'th'
/0/children/1/children/1/children/0/children/1/text: 'Value>'
/0/children/1/children/1/children/0/children/1/tail: '\n'
/0/children/1/children/1/children/1/
/0/children/1/children/1/children/1/tag: 'tr'
/0/children/1/children/1/children/1/text: '\n'
/0/children/1/children/1/children/1/tail: '\n'
/0/children/1/children/1/children/1/children/
/0/children/1/children/1/children/1/children/0/
/0/children/1/children/1/children/1/children/0/tag: 'td'
/0/children/1/children/1/children/1/children/0/text: 'One'
/0/children/1/children/1/children/1/children/0/tail: '\n'
/0/children/1/children/1/children/1/children/1/
/0/children/1/children/1/children/1/children/1/tag: 'td'
/0/children/1/children/1/children/1/children/1/text: '1>'
/0/children/1/children/1/children/1/children/1/tail: '\n'
/0/children/1/children/2/
/0/children/1/children/2/tag: 'br'
/0/children/1/children/2/tail: '\n'
/0/children/1/children/3/
/0/children/1/children/3/tag: 'p'
/0/children/1/children/3/text: 'Good bye'
/0/children/1/children/3/tail: '\n'
/> 
```

## Notes

- The tool leans heavily on the Python [`cmd` module](https://docs.python.org/3/library/cmd.html) which does the following:
  - Tab-completion for subcommand verbs and potential arguments (keys)
  - Command history: Use the up and down arrows to go through subcommands previously issued
  - Command editing: use the left and right arrows to move around a subcommand to make changes
- Initially, the script only worked for JSON files and all the examples are using a JSON file.  I changed it to also handle YAML files which was a very easy extension but I didn't redo much of the doc. I added XML support next which was substantially more challenging than adding YAML but I like the results.
- I have ideas for improvements.  I was starting to list them hear but I've created [individual issues](https://github.com/pfuntner/toys/issues?q=is%3Aissue+is%3Aopen+data-shell%3A) for them.
