# `push-ssh-key`

## Purpose
Push a public ssh key to a remote system's `authorized_keys` file to enable passwordless-ssh.

## Syntax
```
Syntax: push-ssh-key [-h] [--dry-run] [-v] remote [public-key]
```
### Positional arguments

| Argument | Description                                                                                                                                                              | Default                                                                                                         |
| ------ |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `remote` | ssh target<br/><br/>Examples:<li>`hostname`<li>`ip`<li>`user@hostname`<li>`user@ip`                                                                                      | No default, this is a required argument                                                                         |
| `public-key-path` | Optional path to public key to push | <li>First choice: `~/.ssh/id_rsa.pub`<li>Second choice: `~/.ssh/id_dsa.pub` if `~/.ssh/id_rsa.pub` is not found |

### Options
| Option      | Description                                                                                                                                | Default                  |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| `--dry-run` | Do not push the public key, only display command that would have been used                                                                 | Public key is pushed     |
| `-v`        | Enable verbose debugging<br><br>`-v`: public key and its path are printed<br>`-vv`: Same as `-v` but command to add the key is printed too | Debugging is not enabled |

## Examples

### Simple push
```
$ push-ssh-key mrbruno@192.168.1.14
mrbruno@192.168.1.14's password:
$ ssh mrbruno@192.168.1.14 hostname
bruno-meerkat
$
```

### Dry-run
```
$ push-ssh-key --dry mrbruno@192.168.1.14
['ssh', 'mrbruno@192.168.1.14', 'echo', "'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDOkpspv29OTK9omB7sgqwLsUWBtDX/R8DjAYWJy8a/MzeduNWRSUDnnUaAyu1Qf9CYGu1oaahvINzUh7xnGUo1O2uHSWRN8P+6avqUqC9TyD7/+Ao2UvE6pUp/A048TuvpQ37o78U6oJDIiGeTIafZFf6RuBBuJTizAGLnW+hj4xU3DE0g3camDOv4j/kWECKHFM5CmH08roMhfgpQCs67MtZtX6IVBPvzLawP5sX8QnRoft9AxybCDEqbsYjDw8Z/MMQdOWCWf9i5cjCV6nsi/NtU1zzG8O0x0TdlWUODHvVpn+SpHfH/0PP0WLWQuEEIOcQOaPYXVHEjnX5nIcD6S+H1XvllJDsHs5n4HlIn3GTeVKNwTCIN1h9kIiQDMBRhLXiX7Dhz0Gy/t842yMiCfq3EMpFJSq4SnYsJHDXi1zdhP/cgzuAvcylQyuL/L8nxwic584m4bWLOqvco0ejiFQMIE4nSj6zmN/+dxjBpi68XT5l5AnAA2v/H9wIYNKs= mrbruno@DESKTOP-02TEPNS\\n'", '>>', '.ssh/authorized_keys', ';', 'chmod', '600', '.ssh/authorized_keys']
$
```

### Level-one push
```
$ push-ssh-key -v mrbruno@192.168.1.14
2023-09-16 09:11:10,471 INFO /home/mrbruno/repos/toys/bin/push-ssh-key:44 Pushing '/home/mrbruno/.ssh/id_rsa.pub': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDOkpspv29OTK9omB7sgqwLsUWBtDX/R8DjAYWJy8a/MzeduNWRSUDnnUaAyu1Qf9CYGu1oaahvINzUh7xnGUo1O2uHSWRN8P+6avqUqC9TyD7/+Ao2UvE6pUp/A048TuvpQ37o78U6oJDIiGeTIafZFf6RuBBuJTizAGLnW+hj4xU3DE0g3camDOv4j/kWECKHFM5CmH08roMhfgpQCs67MtZtX6IVBPvzLawP5sX8QnRoft9AxybCDEqbsYjDw8Z/MMQdOWCWf9i5cjCV6nsi/NtU1zzG8O0x0TdlWUODHvVpn+SpHfH/0PP0WLWQuEEIOcQOaPYXVHEjnX5nIcD6S+H1XvllJDsHs5n4HlIn3GTeVKNwTCIN1h9kIiQDMBRhLXiX7Dhz0Gy/t842yMiCfq3EMpFJSq4SnYsJHDXi1zdhP/cgzuAvcylQyuL/L8nxwic584m4bWLOqvco0ejiFQMIE4nSj6zmN/+dxjBpi68XT5l5AnAA2v/H9wIYNKs= mrbruno@DESKTOP-02TEPNS\n' to mrbruno@192.168.1.14
mrbruno@192.168.1.14's password:
$
```
#### Note
Some debugging messages are not present in the above output.  The present script prints more debugging.

### Level-two verbosity
```
$ push-ssh-key -vv mrbruno@192.168.1.14
2023-09-16 09:11:35,390 INFO /home/mrbruno/repos/toys/bin/push-ssh-key:44 Pushing '/home/mrbruno/.ssh/id_rsa.pub': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDOkpspv29OTK9omB7sgqwLsUWBtDX/R8DjAYWJy8a/MzeduNWRSUDnnUaAyu1Qf9CYGu1oaahvINzUh7xnGUo1O2uHSWRN8P+6avqUqC9TyD7/+Ao2UvE6pUp/A048TuvpQ37o78U6oJDIiGeTIafZFf6RuBBuJTizAGLnW+hj4xU3DE0g3camDOv4j/kWECKHFM5CmH08roMhfgpQCs67MtZtX6IVBPvzLawP5sX8QnRoft9AxybCDEqbsYjDw8Z/MMQdOWCWf9i5cjCV6nsi/NtU1zzG8O0x0TdlWUODHvVpn+SpHfH/0PP0WLWQuEEIOcQOaPYXVHEjnX5nIcD6S+H1XvllJDsHs5n4HlIn3GTeVKNwTCIN1h9kIiQDMBRhLXiX7Dhz0Gy/t842yMiCfq3EMpFJSq4SnYsJHDXi1zdhP/cgzuAvcylQyuL/L8nxwic584m4bWLOqvco0ejiFQMIE4nSj6zmN/+dxjBpi68XT5l5AnAA2v/H9wIYNKs= mrbruno@DESKTOP-02TEPNS\n' to mrbruno@192.168.1.14
2023-09-16 09:11:35,390 DEBUG /home/mrbruno/repos/toys/bin/push-ssh-key:45 cmd=['ssh', 'mrbruno@192.168.1.14', 'echo', "'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDOkpspv29OTK9omB7sgqwLsUWBtDX/R8DjAYWJy8a/MzeduNWRSUDnnUaAyu1Qf9CYGu1oaahvINzUh7xnGUo1O2uHSWRN8P+6avqUqC9TyD7/+Ao2UvE6pUp/A048TuvpQ37o78U6oJDIiGeTIafZFf6RuBBuJTizAGLnW+hj4xU3DE0g3camDOv4j/kWECKHFM5CmH08roMhfgpQCs67MtZtX6IVBPvzLawP5sX8QnRoft9AxybCDEqbsYjDw8Z/MMQdOWCWf9i5cjCV6nsi/NtU1zzG8O0x0TdlWUODHvVpn+SpHfH/0PP0WLWQuEEIOcQOaPYXVHEjnX5nIcD6S+H1XvllJDsHs5n4HlIn3GTeVKNwTCIN1h9kIiQDMBRhLXiX7Dhz0Gy/t842yMiCfq3EMpFJSq4SnYsJHDXi1zdhP/cgzuAvcylQyuL/L8nxwic584m4bWLOqvco0ejiFQMIE4nSj6zmN/+dxjBpi68XT5l5AnAA2v/H9wIYNKs= mrbruno@DESKTOP-02TEPNS\\n'", '>>', '.ssh/authorized_keys', ';', 'chmod', '600', '.ssh/authorized_keys']
mrbruno@192.168.1.14's password:
$
```
#### Note
Some debugging messages are not present in the above output.  The present script prints more debugging.

## Notes

- `ssh` is used under the covers but since password-less ssh is likely not enabled, your password will be prompted for
- Not only is the public key appended to `~/.ssh/authorized_keys` but the script also ensures the permissions of `~/.ssh/authorized_keys` are `0600` - `ssh` can be super-picky about that so I think it's a good precaution, especially if the script _creates_ `~/.ssh/authorized_keys`!
- If you don't have a public ssh key to push, remember that you can use [`ssh-keygen`](https://man7.org/linux/man-pages/man1/ssh-keygen.1.html) to create one.  I know the prompts can seem a little confusing - I always just accept all of the defaults!
- The public key is not copied to the remote target if passwordless ssh appears to already be enabled.
- A good use-case: At work, I deal a lot with cloud instances - often they are imphemeral but that's just the nature of my work.  I'm usually the only person using the instance and ssh with my own private key that was used when I created the instance - there are typically no passwords whatsoever.  If I want want to give a co-worker access, I can ask them for the public ssh key, push it to the instance and I just have to tell them the remote user and IP of the instance.
