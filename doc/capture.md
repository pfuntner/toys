# `capture`

## Purpose
Capture output from a command.  Each line is preceded with:

  - The local wall clock time
  - The elapsed time since the command started
  - Whether the output is stdout or stderr

Lines printed to stdout or stderr are directed to their normal destination in the shell.

Along with the times shows for each line of output, the total elapsed time is shown when the command is complete.

## Syntax
```
capture [-h] [-v] cmd [arg [arg ...]]

```

### Options and arguments
| Option | Description | Default |
| ------ | ----------- | ------- |
|  `-v` or `--verbose`  | Enable verbose debugging | Debugging is not enabled |
|  `-h` or `--help`  | Display help | Help is not displayed |

### Arguments

- `cmd` is the name of the command and is required
- the list of `arg` tokens are the optional arguments to the command

## Example

```
$ capture bash -c 'echo Start; sleep 5; echo End'
2019-05-08 08:03:32.716248 +0:00:00.119175 stdout 'Start'
2019-05-08 08:03:37.803516 +0:00:05.206443 stdout 'End'
Elapsed time: 0:00:05.216319s

$ capture bash -c 'echo -e "\0"'
2019-05-08 08:04:18.496815 +0:00:00.099494 stdout '\x00'
Elapsed time: 0:00:00.110389s

$
$ capture python -c 'import getpass; print repr(getpass.getpass("Enter a string> "))'
Enter a string>
2019-05-08 08:13:48.956318 +0:00:04.634819 stdout "'foobar'"
Elapsed time: 0:00:04.635743s

$
```

## Notes

- The options for `capture` must appear before the command and arguments.  If you try to place them after the command, the option is assumed to pertain to the command, not `capture`.
- Note that some output is not trapped by the script.  For instance, I believe the Python `getpass.getpass()` option writes directly to `/dev/tty` rather than writing to stdout which might be redirected somewhere.
- The data of each line is enclosed by single or double quotes. Portions of the output might be protected by escape symbols, such as:
    - the tab character
    - the null character (see the example above)
    - If both double and single quotes appear in the output, the quotes that are chosen to enclose the string will be escaped when they appear in the output
