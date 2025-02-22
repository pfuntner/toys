# `argparse`

## Purpose
This is a tool for bash scripts to provide some of the same function as [Python's argparse module](https://docs.python.org/3/library/argparse.html), at least the features I use a lot in my Python scripts!  A lot of it should look very familiar if you're used to using the Python module.

## Syntax
```
Syntax: argparse [-h] [-p PARSER] [--args ARGS] [--name NAME] [-d DESCRIPTION] [--arguments argument] [-m METAVAR] [-n NARGS]
                 [--arg-action {store_true,count}] [--help-text HELP_TEXT] [-v]
                 {argument-parser,add-argument,parse-args,get}
```

### Positional arguments
| Argument | Description                                    | Choices                                                                                                                                                        |
|----------|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Action   | Select the `argparse` action</br></br>Required | `argument-parser`: initialize the parser</br>`add-argument`: add an argument</br>`parse-args`: parse the command line</br>`get`: get an argument after parsing |


### Options
| Option                            | Description                                                                                                                                                                                                                                                                                                                                                                                                                                          | Default                  |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| `-p`, `--parser` PARSER           | Parser payload.  This is where `argparse` stores all of the information provided in order to do parsing.  It gets created during initialization and is updated for adding each argument and parsing the command line.<br/><br/>It's not really of any use to the caller except passing into `argparse`.  It can be displayed but likely won't make any sense.  Just roll with it!</br></br>Required for the `add-argument` and `parse-args` actions. | None                     |
| `--args` ARGS                     | This is the cache after parsing a command line.  The value is created by the the `parse-args` action and specified in this option for the `get` action.  <br/><br/>It's not really of any use to the caller except passing into `argparse`.  It can be displayed but likely won't make any sense.  Just roll with it!</br></br>Required for the `get` action.                                                                                        | None                     |
| `--name` NAME                     | Name of the caller, used when the `--help` option is used in the caller script.</br></br>Required for the `argument-parser` action.                                                                                                                                                                                                                                                                                                                  | None                     |
| `-d`, `--description` DESCRIPTION | Description of the caller, used when the `--help` option is used in the caller script.</br></br>Required for the `argument-parser` action.                                                                                                                                                                                                                                                                                                           | None                     |
| `--arguments` ARGUMENT            | Specifies the keywords for a position or keyword argument, can be repeated for synonyms.</br></br>Required for the `add-argument` action.                                                                                                                                                                                                                                                                                                            | None                     |
| `--metavar` METAVAR               | Specifies a different name for the variable in help</br></br>Only allowed by the `add-argument` action.                                                                                                                                                                                                                                                                                                                                              | None                     |
| `-n`, `--nargs` *,+,?             | Specifies if a positional argument can be repeated or is optional:</br>   `*`: Zero or more occurrences</br>   `+`: One or more occurrences</br>   `?`: Optional</br></br>Only allowed by the `add-argument` action.                                                                                                                                                                                                                                 | None                     |
| `--arg-action` store_true,count   | Keyword-only option:</br> `store_true`: The option value is `True` if specified, `False` if not</br> `count`: The option value is a count of how many times it was specified</br></br>Only allowed by the `add-argument` action.                                                                                                                                                                                                                     | None                     |
| `--help` HELP_TEXT                | Help text for argument for automated help.</br></br>Only allowed by the `add-argument` action.                                                                                                                                                                                                                                                                                                                                                       | | `-v`                              | Enable verbose debugging                                                                                                                                                                                                                                                                                                                                                                                                           | Debugging is not enabled |


## Example
You really need to see an example of how to use this tool in a bash script. 

```commandline
$ cat example1.sh
parser=$(argparse argument-parser --name "$0" --description="Sample script with zero or more arguments, a store_true option, and a boolean option")
parser=$(argparse add-argument --parser "$parser" --argument=paths --metavar=path --nargs='*' --help-text="Zero or more paths")
parser=$(argparse add-argument --parser "$parser" --argument=-l --argument=--loud --arg-action=store_true --help-text="Long output")
parser=$(argparse add-argument --parser "$parser" --argument=-v --argument=--verbose --arg-action=count --help-text="Enable debugging")

args=$(argparse parse-args --parser "$parser" -- "$@")
if test -n "$args" && echo "$args" | base64 -d >/dev/null 2>&1
then
  echo paths=$(argparse get --args "$args" paths)
  echo loud=$(argparse get --args "$args" loud)
  echo verbose=$(argparse get --args "$args" verbose)
else
  echo "$args" >&2
  exit 1
fi
$ bash example1.sh
paths=
loud=false
verbose=0
$ bash example1.sh -v one two three
paths=one two three
loud=false
verbose=1
$ bash example1.sh -vv one two three
paths=one two three
loud=false
verbose=2
$ bash example1.sh -vv -l one two three
paths=one two three
loud=true
verbose=2
$ bash example1.sh --foo
usage: example1.sh [-h] [-l] [-v] [path ...]
example1.sh: error: unrecognized arguments: --foo
$
```
### So what's in the payload?!
Check this out:
```commandline
$ argparse argument-parser --name foo --description="Sample script with 1 or more arguments, a store_true option, and a boolean option"
eyJhcmd1bWVudHMiOiBbXSwgImRlc2NyaXB0aW9uIjogIlNhbXBsZSBzY3JpcHQgd2l0aCAxIG9yIG1vcmUgYXJndW1lbnRzLCBhIHN0b3JlX3RydWUgb3B0aW9uLCBhbmQgYSBib29sZWFuIG9wdGlvbiIsICJuYW1lIjogImZvbyJ9
$ argparse argument-parser --name foo --description="Sample script with 1 or more arguments, a store_true option, and a boolean option" | base64 -d
{"arguments": [], "description": "Sample script with 1 or more arguments, a store_true option, and a boolean option", "name": "foo"}$ 
$ argparse argument-parser --name foo --description="Sample script with 1 or more arguments, a store_true option, and a boolean option" | base64 -d | jq .
{
  "arguments": [],
  "description": "Sample script with 1 or more arguments, a store_true option, and a boolean option",
  "name": "foo"
}
$ 
```
The payload just contains the information that needs to be retained for parsing.  Every time you add an argument, it's just adding to the arguments list of this structure.  The tool doesn't use the information tocall `argparse.ArgumentParser()` or `argparse.add_argument()` (1 or more times, likely) until you use the `parse-args` action. 

## Notes

- The tool doesn't really support special characters in arguments:
   ```
  $ cat example2.sh
  parser=$(argparse argument-parser --name "$0" --description="Sample script with zero or more arguments")
  parser=$(argparse add-argument --parser "$parser" --argument=paths --metavar=path --nargs='*' --help-text="Zero or more paths")
  
  args=$(argparse parse-args --parser "$parser" -- "$@")
  if test -n "$args" && echo "$args" | base64 -d >/dev/null 2>&1
  then
    for path in $(argparse get --args "$args" paths)
    do
      echo "Path: $path"
    done
  else
    echo "$args" >&2
    exit 1
  fi
  $ bash example2.sh one two t\ h\ r\ e\ e
  Path: one
  Path: two
  Path: t
  Path: h
  Path: r
  Path: e
  Path: e
  $   
   ```
  
    I might want to fix this but I'm not sure what to do.  Ideally, a list of strings should be returned in a bash array but I'm honestly not strong in bash arrays!

    Plus, what psychopath is using blanks in paths?
- I am a big proponent of using the Python `argparse` module.  Before I started using it, I remember I thought it was kind of cumbersome but a colleague encouraged that I try it because of the benefits:
    - Powerful argument parsing: synonyms, typing
    - Built-in help for the caller

    It helps that I've incorporated a template in a kind of skeleton script that I use when I create any new Python script because I had coming up with it from scratch.
- The real magic of this tool comes from the honest-to-goodness Python `argparse` script.  The hard part was encapsulating argparse-like information so it could be stashed in a bash script and reused in multiple calls: not only the argument definitions but the results of parsing.
- I'm honestly not using this tool as much as I could.  Frankly I prefer Python for tools and I kind of did this just an exercise but I had a lot of fun proving that it can be done.

    I mentioned having a skeleton for a new Python script - I could likely do something similar for a bash script and that could facilitate my use of this tool but these days my bash scripts are pretty minimal - if I have to do something even slightly complicated, I'll slip into Python mode. 