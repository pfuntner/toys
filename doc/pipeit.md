# `pipeit`

## Purpose
Sends piped/redirected output to/from a file on a remote system

## Syntax
```
Syntax: pipeit [--verbose] system:path
```

### Positional arguments
| Argument | Description | Default |
| ------ | ----------- | ------- |
| `dest` | Source/destination in form `system:path` | This is a required argument and there is no default |


### Options
| Option | Description | Default |
| ------ | ----------- | ------- |
|  `-v`  | Enable verbose debugging | Debugging is not enabled |

## Examples
### Writing example

```
$ head -c10000 /dev/random > random
$ md5sum random
0bed19ac814a70a23065ac4842badc75 *random
$ ls -lh random
-rw-r--r-- 1 mrbruno mrbruno 9.8K Sep 15 15:44 random
$ pipeit ubuntu:/tmp/random < random
$ ssh -q ubuntu md5sum /tmp/random
0bed19ac814a70a23065ac4842badc75  /tmp/random
$
```
Note: Since `/dev/random` produces random data, your mileage will vary - the checksum will be different but the amount of data is the same.

### Reading example

```
$ cat /dev/random | head -c10000 | pipeit vm1:/tmp/random
$ ssh vm1 md5sum /tmp/random
57adc4d45553de79f2ce5c6925b2ccdc  /tmp/random
$ pipeit vm1:/tmp/random | md5sum

57adc4d45553de79f2ce5c6925b2ccdc  -
$ 
```

## Notes

- `ssh` is used under the covers and it works best if you have passwordless ssh working with an ssh key
- I took pains to allow for arbitrary data so you could transmit things like compressed tarballs, images, whatever.  `base64` is used on both sides for transport.
- The command seem kind of ridiculously simple and, like you, I find it hard to believe that there aren't other ways to do the same thing easily but I don't know of any.  After I wrote it, I
 thought _Hey, can `scp` be used??_ but, alas, no:
    ```
    $ date | scp -q -- - ubuntu:/dev/null # it won't read directly from stdin
    scp: stat local "-": No such file or directory
    $ scp -q <(date) ubuntu:/dev/null # you can't fake it out either - other tools are like this and don't plan for pipes even though they would work fine
    scp: local "/dev/fd/63" is not a regular file
    scp: failed to upload file /dev/fd/63 to /dev/null
    $
    ```
    I am often disappointed in Linux commands that don't allow `<(command)` for a file.  Some of my older tools might be the same way but lately instead of making sure a file is a regular file, I just make sure it **isn't** a directory - that way, I can support pipes.  Ansible is a good example of this - I think I learned that `ansible-playbook` doesn't like a temporary playbook that I build on the fly in a pipe.
- I had started to work in a `--become` option but abandoned it when I was facing strange errors I couldn't correct.  If someone has a good use case, I might return to it and get it to work.  It should be possible!
- I originally came up with the idea for this script when I was getting a new work laptop and wanted to backup (store) some files on a remote Ubuntu machine I also use at work.  Writing the tarball to the remote system worked great but I wanted to do something similar to read the file too.  It took a little doing to do things quite right to preserve arbitrary data but I think both directions are working well. 
