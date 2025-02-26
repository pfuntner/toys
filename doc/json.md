# `json`

## Purpose
Read a JSON file and do magical stuff with it.  Really, this has morphed over the years and will probably continue to morph.  It probably started as just a simple script to reformat a JSON file in a pretty way, doing it mostly through the use of `json.dumps(indent=2)` - that can do **wonders** on raw JSON.

There are several styles of printers to present the output.  One of my favorites is the _flattener_ - that is, every single element is printed on a separate line, preceded by the _path_ to that element where the path is made up of the keys to get there.  _Flattening_ used to be taken care of in a completely separate script that only did flattening but one day I realized that it could be folded into my common `json` script.  And that's just one example of the printers!

Check out the examples and try it out yourself!

## Syntax
```
Syntax: json [--verbose] [--flatten] [--describe] [--file FILENAME] [--depth DEPTH] [--forgive] [--linear] [--string] [path ...]
```

### Options and arguments

The default _printer_ uses `json.dumps(indent=2, sort_keys=True)` to print the structure in a beautiful way with newlines.

| Option | Description | Default |
| ------ | ----------- | ------- |
|  `-v` or `--verbose`  | Enable verbose debugging | Debugging is not enabled and probably not recommended for average users |
| `--flat` or `--flatten` | Enables the _flatten_ printer.  I love using this when I'm writing code to deal with JSON and need to understand how to get to a particular element - the path to traverse through the structure | The default printer is used |
| `--linear` | Enables the _linear_ printer - each element of a list or dictionary is printed on a separate line.  If the root is not a list or dictionary, the output shouldn't change.  The output of a list or dictionary is probably no longer in JSON structure if there are multiple elements but maybe that's what you want to do | The default printer is used |
| `--string` | Enables the _string_ printer with `json.dumps(sort_keys=True)` that prints an entire JSON structure in one long string | The default printer is used |
| `--describe` | Describes the top level of the JSON input.  This can be thought of as yet another printer | The default printer is used |
| `--forgive` | Give errors in processing.  For example, if you specify a key in the path that doesn't exist, you can have the script forgive that error and continue processing. | The default is not to forgive errors |
| `--depth DEPTH` | Specifies the depth to which the tool will dive into the JSON | The default is to dive through the entire JSON, visiting all nodes |
| `--file FILENAME` | Specifies a filename to read as source | By default if no filename is specified, the script tries to read from stdin |
| `path ...` | Specifies a path of a single element to select out of the JSON - the element at which to start printing.  The path can be specified in a single string with components separated by slashes or they can be specified as separate strings.  Each element of the path expresses an index from a list (an integer) or a dictionary key, depending on what the current element in the JSON is. | The default is to start printing at the root |

## Examples


### Setup and default behavior

Note that this example makes use of my [`Data.py`](Data.py.md) tool.
```
$ Data.py > data.json
$ json < data.json
{
  "booleans": [
    false,
    false,
    false,
    false,
    true,
    false,
    true,
    false,
    false,
    false
  ],
  "dates": [
    "0566-08-13T02:54:42.786999",
    "0452-04-21T05:06:30.268000",
    "0044-11-26T16:12:03.626000",
    "1134-05-20T09:21:06.754997",
    "1383-12-17T09:37:12.151001",
    "1386-10-29T01:07:11.259003",
    "0567-05-14T19:03:24.080002",
    "2388-04-04T09:39:19.102005",
    "0523-09-24T00:42:09.995001",
    "0655-10-07T05:28:36.752998"
  ],
  "integers": [
    -1618560047,
    150180806,
    280125565,
    2031172952,
    -278304840,
    1998794971,
    -733818980,
    -241488755,
    -1178259463,
    -886702287
  ],
  "listOfDicts": [
    {
      "aanczw": "0701-09-21 14:23:35.125999",
      "bhkmrwnvuxaovij": "whtmfzglbe",
      "fnfiyvymfvb": "True",
      "iqcrhg": "1847-03-27 09:36:17.242996",
      "jvcwllrczblm": "True",
      "orlsghicztdz": "-1831379938",
      "tidmexbniop": "2132015487.51",
      "wsyybaysssfp": "7885dddc-7416-4a27-aade-d1ea108ecf7e",
      "xwolsbfzgiajpb": "1160643539"
    },
    {
      "aanczw": "2306-09-03 18:14:40.623001",
      "bhkmrwnvuxaovij": "oznkgffympghhfj",
      "fnfiyvymfvb": "False",
      "iqcrhg": "1410-05-21 03:08:04.087997",
      "jvcwllrczblm": "False",
      "orlsghicztdz": "1880706452",
      "tidmexbniop": "-1941883269.79",
      "wsyybaysssfp": "cff76cf4-06d5-4b7e-b6bc-1f0b5a7d75de",
      "xwolsbfzgiajpb": "283191153"
    },

    .
    .
    .

    {
      "aanczw": "2029-06-17 23:06:53.469002",
      "bhkmrwnvuxaovij": "ponnxha",
      "fnfiyvymfvb": "True",
      "iqcrhg": "1394-06-10 11:42:47.871002",
      "jvcwllrczblm": "False",
      "orlsghicztdz": "470312339",
      "tidmexbniop": "-1680785865.71",
      "wsyybaysssfp": "13754cf2-d433-4e19-ba59-c76bd67d4604",
      "xwolsbfzgiajpb": "-820960660"
    },
    {
      "aanczw": "2288-07-16 23:19:07.143005",
      "bhkmrwnvuxaovij": "fgtmjomuczgcsgsa",
      "fnfiyvymfvb": "False",
      "iqcrhg": "1496-02-07 15:33:47.416000",
      "jvcwllrczblm": "True",
      "orlsghicztdz": "-399553886",
      "tidmexbniop": "1923473993.95",
      "wsyybaysssfp": "735569c8-cd45-4c6f-a4cb-64d9305fe201",
      "xwolsbfzgiajpb": "-64910366"
    },
    {
      "aanczw": "0636-06-19 01:32:35.803001",
      "bhkmrwnvuxaovij": "sqimqok",
      "fnfiyvymfvb": "True",
      "iqcrhg": "1851-05-09 07:52:56.185997",
      "jvcwllrczblm": "True",
      "orlsghicztdz": "-1701651134",
      "tidmexbniop": "-1624144614.04",
      "wsyybaysssfp": "aae54bdd-65d0-4fde-9a27-c6be296ca0c5",
      "xwolsbfzgiajpb": "-1170977005"
    },
    {
      "aanczw": "1903-05-18 16:36:56.003998",
      "bhkmrwnvuxaovij": "bbifqhyktwzz",
      "fnfiyvymfvb": "False",
      "iqcrhg": "1509-05-12 18:50:34.949997",
      "jvcwllrczblm": "True",
      "orlsghicztdz": "706871771",
      "tidmexbniop": "1993274453.92",
      "wsyybaysssfp": "f50f58af-0c61-4fd0-8ac1-027b702da99b",
      "xwolsbfzgiajpb": "1469984191"
    }
  ],
  "names": [
    "fvgje",
    "gngubmv",
    "uyvnem",
    "uvpalplxrpathzq",
    "tnuciucbwz",
    "ajvgzdntiu",
    "zagp",
    "vbgtxgcfbylgs",
    "qpeboarhtckwed",
    "jqmbtecfycdq"
  ],
  "numbers": [
    -1629408594.3059185,
    509454225.4005561,
    -1027496266.6567712,
    888486952.576993,
    -1383236579.3851902,
    1731626912.759914,
    -1689106457.8079977,
    -1055553039.3306704,
    -1501380021.7274141,
    867860593.2310615
  ],
  "uids": [
    "bd8e4121-8ed0-470d-b3d2-6e4a920d27da",
    "5766b7a3-992f-4e39-8a02-a3ca93507a59",
    "b5403642-d4eb-4d38-a9b3-4030300bc27c",
    "a3eae2b5-8cf8-4592-ba2b-bbe7fec6ce2a",
    "e248f61d-1c57-4c88-ad08-b2102ce87332",
    "1db90160-1bd2-4b44-986f-1300a3a4a56d",
    "0d7537ab-3674-4002-8ea4-aff5ff1c1cad",
    "7eacf144-bb76-49d3-a090-e8633bcccc2b",
    "0aaa3eee-4cb8-4d17-ae2d-0293bfb62854",
    "b2d529c5-7a7b-4738-b88f-797994a696df"
  ]
}
$
```

### `--describe`
```
$ json --describe < data.json
A 7 element dictionary with keys: booleans, dates, integers, listOfDicts, names, numbers, uids
$
```

### `--flatten`
```
$ json --flatten < data.json
/booleans/0 False
/booleans/1 False
/booleans/2 False
/booleans/3 False
/booleans/4 True
/booleans/5 False
/booleans/6 True
/booleans/7 False
/booleans/8 False
/booleans/9 False
/dates/0 '0566-08-13T02:54:42.786999'
/dates/1 '0452-04-21T05:06:30.268000'
/dates/2 '0044-11-26T16:12:03.626000'
/dates/3 '1134-05-20T09:21:06.754997'
/dates/4 '1383-12-17T09:37:12.151001'
/dates/5 '1386-10-29T01:07:11.259003'
/dates/6 '0567-05-14T19:03:24.080002'
/dates/7 '2388-04-04T09:39:19.102005'
/dates/8 '0523-09-24T00:42:09.995001'
/dates/9 '0655-10-07T05:28:36.752998'
/integers/0 -1618560047
/integers/1 150180806
/integers/2 280125565
/integers/3 2031172952
/integers/4 -278304840
/integers/5 1998794971
/integers/6 -733818980
/integers/7 -241488755
/integers/8 -1178259463
/integers/9 -886702287
/listOfDicts/0/aanczw '0701-09-21 14:23:35.125999'
/listOfDicts/0/bhkmrwnvuxaovij 'whtmfzglbe'
/listOfDicts/0/fnfiyvymfvb 'True'
/listOfDicts/0/iqcrhg '1847-03-27 09:36:17.242996'
/listOfDicts/0/jvcwllrczblm 'True'
/listOfDicts/0/orlsghicztdz '-1831379938'
/listOfDicts/0/tidmexbniop '2132015487.51'
/listOfDicts/0/wsyybaysssfp '7885dddc-7416-4a27-aade-d1ea108ecf7e'
/listOfDicts/0/xwolsbfzgiajpb '1160643539'
/listOfDicts/1/aanczw '2306-09-03 18:14:40.623001'
/listOfDicts/1/bhkmrwnvuxaovij 'oznkgffympghhfj'
/listOfDicts/1/fnfiyvymfvb 'False'

.
.
.

/listOfDicts/5/orlsghicztdz '-1701651134'
/listOfDicts/5/tidmexbniop '-1624144614.04'
/listOfDicts/5/wsyybaysssfp 'aae54bdd-65d0-4fde-9a27-c6be296ca0c5'
/listOfDicts/5/xwolsbfzgiajpb '-1170977005'
/listOfDicts/6/aanczw '1903-05-18 16:36:56.003998'
/listOfDicts/6/bhkmrwnvuxaovij 'bbifqhyktwzz'
/listOfDicts/6/fnfiyvymfvb 'False'
/listOfDicts/6/iqcrhg '1509-05-12 18:50:34.949997'
/listOfDicts/6/jvcwllrczblm 'True'
/listOfDicts/6/orlsghicztdz '706871771'
/listOfDicts/6/tidmexbniop '1993274453.92'
/listOfDicts/6/wsyybaysssfp 'f50f58af-0c61-4fd0-8ac1-027b702da99b'
/listOfDicts/6/xwolsbfzgiajpb '1469984191'
/names/0 'fvgje'
/names/1 'gngubmv'
/names/2 'uyvnem'
/names/3 'uvpalplxrpathzq'
/names/4 'tnuciucbwz'
/names/5 'ajvgzdntiu'
/names/6 'zagp'
/names/7 'vbgtxgcfbylgs'
/names/8 'qpeboarhtckwed'
/names/9 'jqmbtecfycdq'
/numbers/0 -1629408594.3059185
/numbers/1 509454225.4005561
/numbers/2 -1027496266.6567712
/numbers/3 888486952.576993
/numbers/4 -1383236579.3851902
/numbers/5 1731626912.759914
/numbers/6 -1689106457.8079977
/numbers/7 -1055553039.3306704
/numbers/8 -1501380021.7274141
/numbers/9 867860593.2310615
/uids/0 'bd8e4121-8ed0-470d-b3d2-6e4a920d27da'
/uids/1 '5766b7a3-992f-4e39-8a02-a3ca93507a59'
/uids/2 'b5403642-d4eb-4d38-a9b3-4030300bc27c'
/uids/3 'a3eae2b5-8cf8-4592-ba2b-bbe7fec6ce2a'
/uids/4 'e248f61d-1c57-4c88-ad08-b2102ce87332'
/uids/5 '1db90160-1bd2-4b44-986f-1300a3a4a56d'
/uids/6 '0d7537ab-3674-4002-8ea4-aff5ff1c1cad'
/uids/7 '7eacf144-bb76-49d3-a090-e8633bcccc2b'
/uids/8 '0aaa3eee-4cb8-4d17-ae2d-0293bfb62854'
/uids/9 'b2d529c5-7a7b-4738-b88f-797994a696df'
$
```

### `--linear`
```
$ json --linear < data.json
{"booleans": [false, false, false, false, true, false, true, false, false, false]}
{"dates": ["0566-08-13T02:54:42.786999", "0452-04-21T05:06:30.268000", "0044-11-26T16:12:03.626000", "1134-05-20T09:21:06.754997", "1383-12-17T09:37:12.151001", "1386-10-29T01:07:11.259003", "0567-05-14T19:03:24.080002", "2388-04-04T09:39:19.102005", "0523-09-24T00:42:09.995001", "0655-10-07T05:28:36.752998"]}
{"integers": [-1618560047, 150180806, 280125565, 2031172952, -278304840, 1998794971, -733818980, -241488755, -1178259463, -886702287]}
{"listOfDicts": [{"aanczw": "0701-09-21 14:23:35.125999", "bhkmrwnvuxaovij": "whtmfzglbe", "fnfiyvymfvb": "True", "iqcrhg": "1847-03-27 09:36:17.242996", "jvcwllrczblm": "True", "orlsghicztdz": "-1831379938", "tidmexbniop": "2132015487.51", "wsyybaysssfp": "7885dddc-7416-4a27-aade-d1ea108ecf7e", "xwolsbfzgiajpb": "1160643539"}, {"aanczw": "2306-09-03 18:14:40.623001", "bhkmrwnvuxaovij": "oznkgffympghhfj", "fnfiyvymfvb": "False", "iqcrhg": "1410-05-21 03:08:04.087997", "jvcwllrczblm": "False", "orlsghicztdz": "1880706452", "tidmexbniop": "-1941883269.79", "wsyybaysssfp": "cff76cf4-06d5-4b7e-b6bc-1f0b5a7d75de", "xwolsbfzgiajpb": "283191153"},  ... {"aanczw": "0636-06-19 01:32:35.803001", "bhkmrwnvuxaovij": "sqimqok", "fnfiyvymfvb": "True", "iqcrhg": "1851-05-09 07:52:56.185997", "jvcwllrczblm": "True", "orlsghicztdz": "-1701651134", "tidmexbniop": "-1624144614.04", "wsyybaysssfp": "aae54bdd-65d0-4fde-9a27-c6be296ca0c5", "xwolsbfzgiajpb": "-1170977005"}, {"aanczw": "1903-05-18 16:36:56.003998", "bhkmrwnvuxaovij": "bbifqhyktwzz", "fnfiyvymfvb": "False", "iqcrhg": "1509-05-12 18:50:34.949997", "jvcwllrczblm": "True", "orlsghicztdz": "706871771", "tidmexbniop": "1993274453.92", "wsyybaysssfp": "f50f58af-0c61-4fd0-8ac1-027b702da99b", "xwolsbfzgiajpb": "1469984191"}]}
{"names": ["fvgje", "gngubmv", "uyvnem", "uvpalplxrpathzq", "tnuciucbwz", "ajvgzdntiu", "zagp", "vbgtxgcfbylgs", "qpeboarhtckwed", "jqmbtecfycdq"]}
{"numbers": [-1629408594.3059185, 509454225.4005561, -1027496266.6567712, 888486952.576993, -1383236579.3851902, 1731626912.759914, -1689106457.8079977, -1055553039.3306704, -1501380021.7274141, 867860593.2310615]}
{"uids": ["bd8e4121-8ed0-470d-b3d2-6e4a920d27da", "5766b7a3-992f-4e39-8a02-a3ca93507a59", "b5403642-d4eb-4d38-a9b3-4030300bc27c", "a3eae2b5-8cf8-4592-ba2b-bbe7fec6ce2a", "e248f61d-1c57-4c88-ad08-b2102ce87332", "1db90160-1bd2-4b44-986f-1300a3a4a56d", "0d7537ab-3674-4002-8ea4-aff5ff1c1cad", "7eacf144-bb76-49d3-a090-e8633bcccc2b", "0aaa3eee-4cb8-4d17-ae2d-0293bfb62854", "b2d529c5-7a7b-4738-b88f-797994a696df"]}
$
```

### `--file` and `path ...`
```
$ json --file data.json booleans
[
  false,
  false,
  false,
  false,
  true,
  false,
  true,
  false,
  false,
  false
]
$ json --file data.json booleans 4
true
$ json --file data.json booleans/4
true
$
```

### `--depth`
```
$ json --file data.json --depth 0
{
  "booleans": "[false, false, false, false, true, false, true, false, false, false]",
  "dates": "[\"0566-08-13T02:54:42.786999\", \"0452-04...995001\", \"0655-10-07T05:28:36.752998\"]",
  "integers": "[-1618560047, 150180806, 280125565, 203..., -241488755, -1178259463, -886702287]",
  "listOfDicts": "[{\"aanczw\": \"0701-09-21 14:23:35.125999...99b\", \"xwolsbfzgiajpb\": \"1469984191\"}]",
  "names": "[\"fvgje\", \"gngubmv\", \"uyvnem\", \"uvpalpl...gs\", \"qpeboarhtckwed\", \"jqmbtecfycdq\"]",
  "numbers": "[-1629408594.3059185, 509454225.4005561...1501380021.7274141, 867860593.2310615]",
  "uids": "[\"bd8e4121-8ed0-470d-b3d2-6e4a920d27da\"...b2d529c5-7a7b-4738-b88f-797994a696df\"]"
}
$ json --file data.json --depth 1
{
  "booleans": [
    "false",
    "false",
    "false",
    "false",
    "true",
    "false",
    "true",
    "false",
    "false",
    "false"
  ],
  "dates": [
    "\"0566-08-13T02:54:42.786999\"",
    "\"0452-04-21T05:06:30.268000\"",
    "\"0044-11-26T16:12:03.626000\"",
    "\"1134-05-20T09:21:06.754997\"",
    "\"1383-12-17T09:37:12.151001\"",
    "\"1386-10-29T01:07:11.259003\"",
    "\"0567-05-14T19:03:24.080002\"",
    "\"2388-04-04T09:39:19.102005\"",
    "\"0523-09-24T00:42:09.995001\"",
    "\"0655-10-07T05:28:36.752998\""
  ],
  "integers": [
    "-1618560047",
    "150180806",
    "280125565",
    "2031172952",
    "-278304840",
    "1998794971",
    "-733818980",
    "-241488755",
    "-1178259463",
    "-886702287"
  ],
  "listOfDicts": [
    "{\"aanczw\": \"0701-09-21 14:23:35.125999\"...cf7e\", \"xwolsbfzgiajpb\": \"1160643539\"}",
    "{\"aanczw\": \"2306-09-03 18:14:40.623001\"...d75de\", \"xwolsbfzgiajpb\": \"283191153\"}",
    "{\"aanczw\": \"1269-10-30 04:34:57.207001\"...69fc3\", \"xwolsbfzgiajpb\": \"536655900\"}",
    "{\"aanczw\": \"2029-06-17 23:06:53.469002\"...4604\", \"xwolsbfzgiajpb\": \"-820960660\"}",
    "{\"aanczw\": \"2288-07-16 23:19:07.143005\"...fe201\", \"xwolsbfzgiajpb\": \"-64910366\"}",
    "{\"aanczw\": \"0636-06-19 01:32:35.803001\"...0c5\", \"xwolsbfzgiajpb\": \"-1170977005\"}",
    "{\"aanczw\": \"1903-05-18 16:36:56.003998\"...a99b\", \"xwolsbfzgiajpb\": \"1469984191\"}"
  ],
  "names": [
    "\"fvgje\"",
    "\"gngubmv\"",
    "\"uyvnem\"",
    "\"uvpalplxrpathzq\"",
    "\"tnuciucbwz\"",
    "\"ajvgzdntiu\"",
    "\"zagp\"",
    "\"vbgtxgcfbylgs\"",
    "\"qpeboarhtckwed\"",
    "\"jqmbtecfycdq\""
  ],
  "numbers": [
    "-1629408594.3059185",
    "509454225.4005561",
    "-1027496266.6567712",
    "888486952.576993",
    "-1383236579.3851902",
    "1731626912.759914",
    "-1689106457.8079977",
    "-1055553039.3306704",
    "-1501380021.7274141",
    "867860593.2310615"
  ],
  "uids": [
    "\"bd8e4121-8ed0-470d-b3d2-6e4a920d27da\"",
    "\"5766b7a3-992f-4e39-8a02-a3ca93507a59\"",
    "\"b5403642-d4eb-4d38-a9b3-4030300bc27c\"",
    "\"a3eae2b5-8cf8-4592-ba2b-bbe7fec6ce2a\"",
    "\"e248f61d-1c57-4c88-ad08-b2102ce87332\"",
    "\"1db90160-1bd2-4b44-986f-1300a3a4a56d\"",
    "\"0d7537ab-3674-4002-8ea4-aff5ff1c1cad\"",
    "\"7eacf144-bb76-49d3-a090-e8633bcccc2b\"",
    "\"0aaa3eee-4cb8-4d17-ae2d-0293bfb62854\"",
    "\"b2d529c5-7a7b-4738-b88f-797994a696df\""
  ]
}
$
```

## Notes

- This script is continually evolving and I doubt I'll ever say it's _complete_ or _perfect_.  Indeed, it has some usage problems and may not be the most intuative in some ways.  If you have suggestions, please let me know!
- Regarding the `path ...` argument: when I was coming up with examples for the documentation, I hadn't used paths much recently and was a little confused that `booleans/0 booleans/1` or `booleans/{0..1}` didn't print out two elements.  The reason is that I designed the tool to print out a single root element.  If you specify multiple strings such as `booleans 0`, the script assumes you are not using slashes and indeed slashes are inappropriate any element of the path **unless** the slash actually appears in the key.  I was close to hacking the script up to allow for multiple paths/roots but decided against that when I thought about printing the root. Perhaps I should just throw each element in a list and then just print that list.  I think I might already have a script kind of like that.
- Frankly, I've been using [`jq`](https://jqlang.org/) a lot lately instead of this tool because of the this tool.  Although this tool does have an advantage over `jq` in that it will combine individual objects into a single list.
- A more recent tool of mine is [`data-shell`](../docs/data-shell.md) which has some good features.