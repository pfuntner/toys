# Bruno's Toys
This is a collection of Unix tools command line that make my life easier.  I think others might like them too so I'm making them available here but the repository is just a nice way for me to keep track of changes and deploy them easily to systems.

I will admit that the documentation is rather poor for some of the tools and many of them have little or **no** comments.  This is a work in progress - I'm constantly creating new tools and improving documentation.  In November 2017, I did a major overhaul of the documentation because I was disatisfed with having a huge table.  I'm liking the results so far.

If you have questions, problems, etc, you can reach me at <img src="doc/images/email.jpg" />.

### Unix platforms

Over the years, I've used many different _Unix_ platforms: Redhat, Suse, Solaris, HP/UX, AIX, Z/OS, Cygwin, Git bash, etc.  I owe no allegiance to any single platform and consider them all pretty much equal as long as they behave similarly.  I have seen some issues using my tools (and other commands!) from Git bash on Windoze and sometimes a tool was only designed to work on specific platforms - I'll try to put such stuff on the doc page for the tool.  In general if I find a platform where one of my tools doesn't work well, I will try to fix it!

## The much-heralded TOOLS

Select a tool below to learn more about it.  The _Bruno's Favorite_ column is used to indicate that a tool is:
- very useful and practical
- personally used by me a few times a week if not at least once a day!
- I thought about expressing an extreme affection for some tools but realized I might be expressing it for all of the favorites so I'll just leave it as _favorite_ or _not favorite_

| Tool                                                            | Bruno's Favorite? | Brief Description                                                                                    |
|-----------------------------------------------------------------|-------------------|------------------------------------------------------------------------------------------------------|
| [`ansible-distros`](doc/ansible-distros.md)                     |                   | Prints OS information about Ansible hosts                                                            |
| [`ansible-host-data`](doc/ansible-host-data.md)                 |                   | Extracts specific information about a host in an ansible inventory                                   |
| [`ansible-hosts`](doc/ansible-hosts.md)                         | Yes               | Lists host information from an Ansible inventory                                                     |
| [`ansible-role`](doc/ansible-role.md)                           | Yes               | Builds a minimial ephemeral Ansible playbook for a role and runs ansible-playbook with it            |
| [`aws-image`](doc/aws-image.md)                                 |                   | Displays details about an AWS EC2 AMI                                                                |
| [`aws-images`](doc/aws-images.md)                               |                   | Search for AWS EC2 AMIs                                                                              |
| [`banner`](doc/banner.md)                                       | Yes               | Prints text in a _banner_                                                                            |
| [`bashprofiles`](doc/bashprofiles.md)                           | Yes               | Prints profile script(s) `bash` will use                                                             |
| [`beeper`](doc/beeper.md)                                       |                   | Beeps over and over                                                                                  |
| [`bingrep`](doc/bingrep.md)                                     |                   | Searches for a regular expression in arbitrary data from stdin                                       |
| [`br`](doc/br.md)                                               | Yes               | Browse a file.  Sounds simple?  Maybe, but give it a try                                             |
| [`capture`](doc/capture.md)                                     |                   | Saves output and other information from a command                                                    |
| [`chars`](doc/chars.md)                                         |                   | Display a file character-by-character                                                                |
| [`color.py`](doc/color.py.md)                                   | Yes               | Print text in the specified foreground/background colors                                             |
| [`columns`](doc/columns.md)                                     | Yes               | Prints _columns_ of stdin where columns are separated by a character or regular expression           |
| [`comm2`](doc/comm2.md)                                         |                   | Alternate version of `comm` that does not expect the data to be sorted                               |
| [`cores`](doc/cores.md)                                         |                   | Prints CPU core information in a simple way                                                          |
| [`data-shell`](doc/data-shell.md)                               | Yes, maybe        | A shell-like interactive tool for navigating around JSON, YAML, and XML objects                      |
| [`datemath`](doc/datemath.md)                                   |                   | Perform arithmetic on date(s)                                                                        |
| [`dowhile`](doc/dowhile.md)                                     |                   | Perform a command repeatedly until output is seen in the output                                      |
| [`drop`](doc/drop.md)                                           | Yes               | Drop the first or last `n` lines, similar to `head`/`tail`                                           |
| [`extensions`](doc/extensions.md)                               |                   | Show extensions used by files                                                                        |
| [`fernet`](doc/fernet.md)                                       |                   | Perform fernet encryption/decryption                                                                 |
| [`fitwidth`](doc/fitwidth.md)                                   | Yes               | Restrict lines of data to a desired width                                                            |
| [`flow`](doc/flow.md)                                           | Yes               | Flow lines from stdin into columnar form                                                             |
| [`fulltime`](doc/fulltime.md)                                   |                   | Execute a command using standard `time` utility and all options available to it                      |
| [`git-cat`](doc/git-cat.md)                                     | Yes               | Display a file from another git branch                                                               |
| [`git-pulls`](doc/git-pulls.md)                                 | Yes               | Do `git pull` on one or more repositories                                                            |
| [`git-refresh-after-merge`](doc/git-refresh-after-merge.md)     | Yes               | Refresh local git master branch after merging a feature branch                                       |
| [`gitstatus`](doc/gitstatus.md)                                 | Yes               | Show files in a local git repo that have been changed, etc.                                          |
| [`grep-cat`](doc/grep-cat.md)                                   | Yes               | Show lines in a file based on line numbers and/or regular expressions, ranges.                       |
| [`headtail`](doc/headtail.md)                                   | Yes               | Print out the top and bottom of stdin or one or more files                                           |
| [`hex`](doc/hex.md)                                             |                   | Print out data or a file in hex and character form                                                   |
| [`indent`](doc/indent.md)                                       | Yes               | Indent stdin by a specified number of columns                                                        |
| [`json`](doc/json.md)                                           | Yes               | JSON magic - it's a disservice to try to summarize this tool in a single string.  Check out its page |
| [`jsoncompare`](doc/jsoncompare.md)                             |                   | Compares JSON and/or YAML files, element by element                                                  |
| [`lexec`](doc/lexec.md)                                         | Yes               | Locate executable files by pattern                                                                   |
| [`megadiff`](doc/megadiff.md)                                   |                   | Compare two directories trees                                                                        |
| [`megassh`](doc/megassh.md)                                     | Yes               | Execute a command on one or more remote targets                                                      |
| [`more-head`](doc/more-head.md)                                 |                   | Display the top of a file, filling up the the screen                                                 |
| [`nocrs`](doc/nocrs.md)                                         |                   | Remove carriage returns from files                                                                   |
| [`oldtable`](doc/oldtable.md)                                   |                   | Parse data into a tabular form using a few input and output forms - replaced by _table_              |
| [`peval`](doc/peval.md)                                         | Yes               | Evaluate Python expression strings                                                                   |
| [`pipeit`](doc/pipeit.md)                                       | Maybe? Still new  | Send data to a file on a remote system                                                               |
| [`push-ssh-key`](doc/push-ssh-key.md)                           | Maybe?            | Push your public ssh key to a remote system                                                          |
| [`pycomment`](doc/pycomment.md)                                 | Yes               | vi command to toggle Python-style comments, similar to PyCharm `ctrl-/` command                      |
| [`pythons`](doc/pythons.md)                                     |                   | Show versions of Python/Python2/Python3 interpreters                                                 |
| [`recentdownloads`](doc/recentdownloads.md)                     |                   | Find recently downloaded files                                                                       |
| [`remote-file`](doc/remote-file.md)                             |                   | Read or write a remote file in a filter                                                              |
| [`SecureKeyValues`](doc/SecureKeyValues.md)                     |                   | Manage secure key value stores                                                                       |
| [`side-diff`](doc/side-diff.md)                                 | Yes               | Perform side-by-side compare, utilizing all of the screen width                                      |
| [`ssh-exec`](doc/ssh-exec.md)                                   |                   | Execute a script on a remote host                                                                    |
| [`strip-trailing-whitespace`](doc/strip-trailing-whitespace.md) | Yes               | Strip trailing whitespace from one or more files                                                     |
| [`supercd.sh`](doc/supercd.sh.md)                               | Yes               | Change to a directory that matches a pattern                                                         |
| [`table`](doc/table.md)                                         | Yes               | Parse data into a tabular form using several input and output forms - more flexible than _oldtable_  |
| [`timer`](doc/timer.md)                                         |                   | Display a progress meter over a specified duration of time                                           |
| [`timestamp-my-file`](doc/timestamp-my-file.md)                 |                   | Add a timestamp to a filename                                                                        |
| [`timestamps`](doc/timestamps.md)                               |                   | Show times when files were last modified, most-recently updated first                                |
| [`uniqc`](doc/uniqc.md)                                         | Yes               | Counts unique instances of input                                                                     |
| [`undent`](doc/undent.md)                                       |                   | Removes indentation from stdin                                                                       |
| [`undupe`](doc/undupe.md)                                       |                   | Removes duplicate punctuation & whitespace                                                           |
| [`unixdate`](doc/unixdate.md)                                   |                   | Invokes `date` with Unix-style format on Windoze                                                     |
| [`versions`](doc/versions.md)                                   |                   | Show versions of arbitrary commands                                                                  |
| [`wholegrep`](doc/wholegrep.md)                                 |                   | Grep entire files that contain or do not contain regular expressions                                 |
