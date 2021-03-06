# `unixdate`

## Purpose
Invoke `date` command using Unix format on Windoze

## Syntax
```
Syntax: unixdate [date options]
```

### Options and arguments
See options and arguments for `date` such this on this [man page](http://linuxcommand.org/lc3_man_pages/date1.html)

## Example

```
$ unixdate                       # simplest form of the command
Tue Apr  3 08:22:23 EDT 2018

$ unixdate -u                    # specify -u along and Unix format will still be added
Tue Apr  3 12:22:29 UTC 2018

$ unixdate +%Y%m%d%H%M%S         # specify a specific format, Unix format is avoided
20180403082255

$ /usr/bin/date                  # you can still get the "normal Windoze output" since you're not using the frontend at all
Tue, Apr  3, 2018  8:26:13 AM

$ alias date=unixdate            # override /usr/bin/date with an alias
$ date -R                        # alternate way of specifiying a format
Tue, 03 Apr 2018 08:54:08 -0400

$
```

## Notes

- This script was created specifically with Windoze shells in mind (Cygwin and Git bash) that print the date in a style inconsistent with a regular Unix shell.  There's nothing that stops you from using this script on a real Unix system but there's no purpose because the `date` command works as you might expect.
- If you don't specify your own format string, the script will supply a format string to print the date and time in the style you would see on a Unix system.
- You might want to set up an alias to this script so that any time you type `date` in a Windoze shell, you'll run this script instead.  I would encourage you add such an alias from your `~/.bashrc` but it's up to you.
## Known Bugs
- I take a fairly simple approach to seeing if a format is specified which can case the frontend.  For instance, you specify `-u` (UTC time) and `-R` (synonymous with `--rfc-2822`) without an intervening blank, the frontend isn't aware that you want an alternate format.  It tries to specify the Unix format which conflicts with `--rfc-2822` and an error is raised:

  ```
  $ date -uR
  date: multiple output formats specified
  $ date -u -R
  Mon, 16 Apr 2018 19:13:20 +0000
  $
  ```

  Obviously, an easy to solve this is to separate the options.
