# `table.py`

## Purpose
A script to manipulate tables, reading from various formats (fixed column, CSV, etc), and writing to other formats (JSON, HTML, etc).

## Syntax
```
table.py [-h] [-H] -i {csv,yaml,fixed,json,separator,xml} -o
         {csv,yaml,fixed,bbcode,html,json,markdown,separator,xml}
         [--order COL,...] [--sort COL,...] [-r REGEXP] [-s SEPARATOR] [-v]
```

### Options and arguments
| Option | Description                                                                                                                                                                                                                                                          | Default |
| ------ |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| ------- |
|  `-i FORMAT` or `--input FORMAT`  | Required option that identifies the input format: `csv`, `yaml`, `fixed`, `json`, `separator`, or `xml`                                                                                                                                                              | There is no default.  You must identify the input format. |
|  `-o FORMAT` or `--output FORMAT`  | Required option that identifies the output format: `csv`, `yaml`, `fixed`, `banner`, `json`, `separator`, `html`, `markdown`, `bbcode`, or `xml`                                                                                                                     | There is no default.  You must identify the output format. |
|  `-H` or `--headings`  | Treat first row of input as headings.  Significant for formats `csv`, `fixed`, and `separator` where the first row could be interpreted either way.  The option is ignored for other formats `json` and `yaml` where the interpretation is not possible.             | The default is to not treat the first row as headings |
| `-r REGEXP` or `--regexp REGEXP` | Regular expression to be used when reading with the `separator` format, ignored in all other cases                                                                                                                                                                   | The default regular expression is to treat whitespace (`\w+`) as column separators |
| `-s SEPARATOR` or `--separator SEPARATOR` | One or more characters to use to seperate columns when writing with the `separator` or `fixed` formats                                                                                                                                                               | The default is to use a single blank to separate columns in `fixed` format and a single vertical bar when writing in `separator` format. |
|  `--order COL,...`  | List of named headings to appear first in a list of columns. The option is important for situations when the heading order is not implied by the input format (`yaml` or `json` dictionaries) but is important in the output format (`separator`, `fixed` or `csv`). | For those headings that are not expressed in `--order` (even when none are specified), the headings are simply supplied in alphabetized order  |
| `--sort COL,...` | Specify one or more comma-seperated columns by which to sort the rows                                                                                                                                                                                                | The default is to not sort the table |
| `--no-sort` | Do not sort column headings                                                                                                                                                                                                                                          |
|  `-v`  | Enable verbose debugging                                                                                                                                                                                                                                             | Debugging is not enabled |

#### Formats

| Format      | Input                               | Output | Description                                                                                                                                                                                                                                                                        |
|-------------|-------------------------------------| --- |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `csv`       | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | Comma-separator file format                                                                                                                                                                                                                                                        |
| `separator` | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | A free format where columns are separated by the `--regexp` regular expression.  Suseptible to mistakes when the separator is used within data.  Whitespace is a common separator but whitespace can also appear within data and headings                                          |
| `fixed`     | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | Common to many Unix utilities such as `df` or `ls -l`.  The script identifies the beginning and ending of columns by looking for whitespace on every row                                                                                                                           |
| `banner`    | ![Not Supported](images/red_x.png)  | ![Supported](images/Green_tick.png) | Similar to `fixed` output but a pretty boxes are rendered between columns and after the headings                                                                                                                                                                                   |
| `json`      | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | Popular structured format, less ambiguities than less structured formats, more flexability                                                                                                                                                                                         |
| `yaml`      | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | Another popular structured format with the same strengths as `json`                                                                                                                                                                                                                |
| `xml`       | ![Supported](images/Green_tick.png) | ![Supported](images/Green_tick.png) | Another popular structured format.                                                                                                                                                                                                                                                 |
| `html`      | ![Not Supported](images/red_x.png)  | ![Supported](images/Green_tick.png) | A format that can only be used for output to produce a table in [HTML](https://www.wikiwand.com/en/HTML)                                                                                                                                                                           |
| `markdown`  | ![Not Supported](images/red_x.png)  | ![Supported](images/Green_tick.png) | A format that can only be used for output to produce a table in [Markdown](https://www.wikiwand.com/en/Markdown).  Used extensively in [Slack](https://slack.com/) and [Github](https://www.wikiwand.com/en/GitHub): Issues (including pull requests), documentation, reviews, etc. |
| `bbcode`    | ![Not Supported](images/red_x.png)  | ![Supported](images/Green_tick.png) | A format that can only be used for output to produce a table in [BBCode](https://www.wikiwand.com/en/BBCode).  Used in some bulletin board systems such as [Ubuntu Forums](https://ubuntuforums.org)                                                                               |

## Examples


### `df`

Output from `df` is best handled by a `fixed` input format because the columns are both right and left justified and the `Mounted on` heading can't be parsed with a single blank as a separator.

#### Original output
```
$ df -k
Filesystem      1K-blocks     Used  Available Use% Mounted on
udev              8133732        0    8133732   0% /dev
tmpfs             1631580     2092    1629488   1% /run
/dev/sdb2       236102400 79059060  145026908  36% /
tmpfs             8157880   108672    8049208   2% /dev/shm
tmpfs                5120        4       5116   1% /run/lock
tmpfs             8157880        0    8157880   0% /sys/fs/cgroup
/dev/loop1           8704     8704          0 100% /snap/canonical-livepatch/77
/dev/loop0         304256   304256          0 100% /snap/pycharm-community/132
/dev/loop2         304256   304256          0 100% /snap/pycharm-community/128
/dev/loop3          90624    90624          0 100% /snap/core/7169
/dev/loop5         147840   147840          0 100% /snap/skype/63
/dev/loop4         150912   150912          0 100% /snap/skype/66
/dev/loop6          90624    90624          0 100% /snap/core/7270
/dev/loop7         145280   145280          0 100% /snap/skype/60
/dev/loop8           8704     8704          0 100% /snap/canonical-livepatch/81
/dev/sda1      1922727728 89149004 1833562340   5% /media/mrbruno/ExtraDrive1
tmpfs             1631576       16    1631560   1% /run/user/125
tmpfs             1631576       36    1631540   1% /run/user/1000
```

#### Banner output
```commandline
$ df -k | table --loose -i fixed -o banner
+------------+------------+----------+------------+------+------------------------------+
| Filesystem | 1K-blocks  | Used     | Available  | Use% | Mounted on                   |
+------------+------------+----------+------------+------+------------------------------+
| udev       | 8133732    | 0        | 8133732    | 0%   | /dev                         |
| tmpfs      | 1631580    | 2092     | 1629488    | 1%   | /run                         |
| /dev/sdb2  | 236102400  | 79059060 | 145026908  | 36%  | /                            |
| tmpfs      | 8157880    | 108672   | 8049208    | 2%   | /dev/shm                     |
| tmpfs      | 5120       | 4        | 5116       | 1%   | /run/lock                    |
| tmpfs      | 8157880    | 0        | 8157880    | 0%   | /sys/fs/cgroup               |
| /dev/loop1 | 8704       | 8704     | 0          | 100% | /snap/canonical-livepatch/77 |
| /dev/loop0 | 304256     | 304256   | 0          | 100% | /snap/pycharm-community/132  |
| /dev/loop2 | 304256     | 304256   | 0          | 100% | /snap/pycharm-community/128  |
| /dev/loop3 | 90624      | 90624    | 0          | 100% | /snap/core/7169              |
| /dev/loop5 | 147840     | 147840   | 0          | 100% | /snap/skype/63               |
| /dev/loop4 | 150912     | 150912   | 0          | 100% | /snap/skype/66               |
| /dev/loop6 | 90624      | 90624    | 0          | 100% | /snap/core/7270              |
| /dev/loop7 | 145280     | 145280   | 0          | 100% | /snap/skype/60               |
| /dev/loop8 | 8704       | 8704     | 0          | 100% | /snap/canonical-livepatch/81 |
| /dev/sda1  | 1922727728 | 89149004 | 1833562340 | 5%   | /media/mrbruno/ExtraDrive1   |
| tmpfs      | 1631576    | 16       | 1631560    | 1%   | /run/user/125                |
| tmpfs      | 1631576    | 36       | 1631540    | 1%   | /run/user/1000               |
+------------+------------+----------+------------+------+------------------------------+
$ 
```

#### CSV output
```
$ df -k | table -i fixed -o csv
Filesystem,1K-blocks,Used,Available,Use%,Mounted on
udev,8133732,0,8133732,0%,/dev
tmpfs,1631580,2092,1629488,1%,/run
/dev/sdb2,236102400,79059060,145026908,36%,/
tmpfs,8157880,108672,8049208,2%,/dev/shm
tmpfs,5120,4,5116,1%,/run/lock
tmpfs,8157880,0,8157880,0%,/sys/fs/cgroup
/dev/loop1,8704,8704,0,100%,/snap/canonical-livepatch/77
/dev/loop0,304256,304256,0,100%,/snap/pycharm-community/132
/dev/loop2,304256,304256,0,100%,/snap/pycharm-community/128
/dev/loop3,90624,90624,0,100%,/snap/core/7169
/dev/loop5,147840,147840,0,100%,/snap/skype/63
/dev/loop4,150912,150912,0,100%,/snap/skype/66
/dev/loop6,90624,90624,0,100%,/snap/core/7270
/dev/loop7,145280,145280,0,100%,/snap/skype/60
/dev/loop8,8704,8704,0,100%,/snap/canonical-livepatch/81
/dev/sda1,1922727728,89149004,1833562340,5%,/media/mrbruno/ExtraDrive1
tmpfs,1631576,16,1631560,1%,/run/user/125
tmpfs,1631576,36,1631540,1%,/run/user/1000
```

#### JSON output, without headings

This generates a list of lists but we could do better.
```
$ df -k | table -i fixed -o json
[
  [
    "Filesystem",
    "1K-blocks",
    "Used",
    "Available",
    "Use%",
    "Mounted on"
  ],
  [
    "udev",
    "8133732",
    "0",
    "8133732",
    "0%",
    "/dev"
  ],
  .
  .
  .
  [
    "tmpfs",
    "1631576",
    "16",
    "1631560",
    "1%",
    "/run/user/125"
  ],
  [
    "tmpfs",
    "1631576",
    "36",
    "1631540",
    "1%",
    "/run/user/1000"
  ]
]
```

#### JSON output, with headings
Headings can rock!
```
$ df -k | table -i fixed -o json --headings
[
  {
    "1K-blocks": "8133732",
    "Available": "8133732",
    "Filesystem": "udev",
    "Mounted on": "/dev",
    "Use%": "0%",
    "Used": "0"
  },
  {
    "1K-blocks": "1631580",
    "Available": "1629488",
    "Filesystem": "tmpfs",
    "Mounted on": "/run",
    "Use%": "1%",
    "Used": "2092"
  },
  .
  .
  .
  {
    "1K-blocks": "1631576",
    "Available": "1631560",
    "Filesystem": "tmpfs",
    "Mounted on": "/run/user/125",
    "Use%": "1%",
    "Used": "16"
  },
  {
    "1K-blocks": "1631576",
    "Available": "1631540",
    "Filesystem": "tmpfs",
    "Mounted on": "/run/user/1000",
    "Use%": "1%",
    "Used": "36"
  }
]
```

### YAML output, with headings
```
$ df -k | table -i fixed -o yaml --headings
- {1K-blocks: '8133732', Available: '8133732', Filesystem: udev, Mounted on: /dev,
  Use%: 0%, Used: '0'}
- {1K-blocks: '1631580', Available: '1629488', Filesystem: tmpfs, Mounted on: /run,
  Use%: 1%, Used: '2092'}
.
.
.
- {1K-blocks: '1631576', Available: '1631560', Filesystem: tmpfs, Mounted on: /run/user/125,
  Use%: 1%, Used: '16'}
- {1K-blocks: '1631576', Available: '1631540', Filesystem: tmpfs, Mounted on: /run/user/1000,
  Use%: 1%, Used: '36'}
```

#### HTML output, with headings
```
$ df -k | table -i fixed -o html --headings
<table>
<tbody>
<tr><th>Filesystem</th><th>1K-blocks</th><th>Used</th><th>Available</th><th>Use%</th><th>Mounted on</th></tr>
<tr><td>udev</td><td>8133732</td><td>0</td><td>8133732</td><td>0%</td><td>/dev</td></tr>
<tr><td>tmpfs</td><td>1631580</td><td>2092</td><td>1629488</td><td>1%</td><td>/run</td></tr>
<tr><td>/dev/sdb2</td><td>236102400</td><td>79059112</td><td>145026856</td><td>36%</td><td>/</td></tr>
<tr><td>tmpfs</td><td>8157880</td><td>108672</td><td>8049208</td><td>2%</td><td>/dev/shm</td></tr>
<tr><td>tmpfs</td><td>5120</td><td>4</td><td>5116</td><td>1%</td><td>/run/lock</td></tr>
<tr><td>tmpfs</td><td>8157880</td><td>0</td><td>8157880</td><td>0%</td><td>/sys/fs/cgroup</td></tr>
<tr><td>/dev/loop1</td><td>8704</td><td>8704</td><td>0</td><td>100%</td><td>/snap/canonical-livepatch/77</td></tr>
<tr><td>/dev/loop0</td><td>304256</td><td>304256</td><td>0</td><td>100%</td><td>/snap/pycharm-community/132</td></tr>
<tr><td>/dev/loop2</td><td>304256</td><td>304256</td><td>0</td><td>100%</td><td>/snap/pycharm-community/128</td></tr>
<tr><td>/dev/loop3</td><td>90624</td><td>90624</td><td>0</td><td>100%</td><td>/snap/core/7169</td></tr>
<tr><td>/dev/loop5</td><td>147840</td><td>147840</td><td>0</td><td>100%</td><td>/snap/skype/63</td></tr>
<tr><td>/dev/loop4</td><td>150912</td><td>150912</td><td>0</td><td>100%</td><td>/snap/skype/66</td></tr>
<tr><td>/dev/loop6</td><td>90624</td><td>90624</td><td>0</td><td>100%</td><td>/snap/core/7270</td></tr>
<tr><td>/dev/loop7</td><td>145280</td><td>145280</td><td>0</td><td>100%</td><td>/snap/skype/60</td></tr>
<tr><td>/dev/loop8</td><td>8704</td><td>8704</td><td>0</td><td>100%</td><td>/snap/canonical-livepatch/81</td></tr>
<tr><td>/dev/sda1</td><td>1922727728</td><td>89149004</td><td>1833562340</td><td>5%</td><td>/media/mrbruno/ExtraDrive1</td></tr>
<tr><td>tmpfs</td><td>1631576</td><td>16</td><td>1631560</td><td>1%</td><td>/run/user/125</td></tr>
<tr><td>tmpfs</td><td>1631576</td><td>36</td><td>1631540</td><td>1%</td><td>/run/user/1000</td></tr>
</tbody>
</table>
```

#### Markdown output, with headings
Note that I only used `mark` for the name of the output format.  You can provide unique abbreviations format names.

```
$ df -k | table -i fixed -o mark --headings
| Filesystem | 1K-blocks | Used | Available | Use% | Mounted on |
| - | - | - | - | - | - |
| udev | 8133732 | 0 | 8133732 | 0% | /dev |
| tmpfs | 1631580 | 2092 | 1629488 | 1% | /run |
| /dev/sdb2 | 236102400 | 79059112 | 145026856 | 36% | / |
| tmpfs | 8157880 | 108672 | 8049208 | 2% | /dev/shm |
| tmpfs | 5120 | 4 | 5116 | 1% | /run/lock |
| tmpfs | 8157880 | 0 | 8157880 | 0% | /sys/fs/cgroup |
| /dev/loop1 | 8704 | 8704 | 0 | 100% | /snap/canonical-livepatch/77 |
| /dev/loop0 | 304256 | 304256 | 0 | 100% | /snap/pycharm-community/132 |
| /dev/loop2 | 304256 | 304256 | 0 | 100% | /snap/pycharm-community/128 |
| /dev/loop3 | 90624 | 90624 | 0 | 100% | /snap/core/7169 |
| /dev/loop5 | 147840 | 147840 | 0 | 100% | /snap/skype/63 |
| /dev/loop4 | 150912 | 150912 | 0 | 100% | /snap/skype/66 |
| /dev/loop6 | 90624 | 90624 | 0 | 100% | /snap/core/7270 |
| /dev/loop7 | 145280 | 145280 | 0 | 100% | /snap/skype/60 |
| /dev/loop8 | 8704 | 8704 | 0 | 100% | /snap/canonical-livepatch/81 |
| /dev/sda1 | 1922727728 | 89149004 | 1833562340 | 5% | /media/mrbruno/ExtraDrive1 |
| tmpfs | 1631576 | 16 | 1631560 | 1% | /run/user/125 |
| tmpfs | 1631576 | 36 | 1631540 | 1% | /run/user/1000 |
$
```

### Why is `--order` important?
The `--order` option may not be clear without examples.  Consider converting from JSON dictionaries to fixed.  You start with a form that has no implied order for the headings and change it to a form where the order is very important.  If we don't use `--order`, the headings are just alphabetized.

For this example, I'm going to cheat a little bit, starting with fixed format, converting to JSON, and then converting back to fixed.  It's just easier that way.

#### Without `--order`

```
$ df -k | table -i fixed -o json --headings | table -i json -o fixed
1K-blocks  Available  Filesystem Mounted on                   Use% Used
8133732    8133732    udev       /dev                         0%   0
1631580    1629480    tmpfs      /run                         1%   2100
236102400  145011804  /dev/sdb2  /                            36%  79074164
8157880    8049200    tmpfs      /dev/shm                     2%   108680
5120       5116       tmpfs      /run/lock                    1%   4
8157880    8157880    tmpfs      /sys/fs/cgroup               0%   0
8704       0          /dev/loop1 /snap/canonical-livepatch/77 100% 8704
304256     0          /dev/loop0 /snap/pycharm-community/132  100% 304256
304256     0          /dev/loop2 /snap/pycharm-community/128  100% 304256
90624      0          /dev/loop3 /snap/core/7169              100% 90624
147840     0          /dev/loop5 /snap/skype/63               100% 147840
150912     0          /dev/loop4 /snap/skype/66               100% 150912
90624      0          /dev/loop6 /snap/core/7270              100% 90624
145280     0          /dev/loop7 /snap/skype/60               100% 145280
8704       0          /dev/loop8 /snap/canonical-livepatch/81 100% 8704
1922727728 1833562324 /dev/sda1  /media/mrbruno/ExtraDrive1   5%   89149020
1631576    1631560    tmpfs      /run/user/125                1%   16
1631576    1631536    tmpfs      /run/user/1000               1%   40
```
This ordering may not be what you want.

#### With `--order`
Let's supply an order for some of the columns.  Note that when you specify order, case is ignored and you can use abbreviations.

```
$ df -k | table -i fixed -o json --headings | table -i json -o fixed --order filesystem,mounted\ on
Filesystem Mounted on                   1K-blocks  Available  Use% Used
udev       /dev                         8133732    8133732    0%   0
tmpfs      /run                         1631580    1629480    1%   2100
/dev/sdb2  /                            236102400  145011904  36%  79074064
tmpfs      /dev/shm                     8157880    8049200    2%   108680
tmpfs      /run/lock                    5120       5116       1%   4
tmpfs      /sys/fs/cgroup               8157880    8157880    0%   0
/dev/loop1 /snap/canonical-livepatch/77 8704       0          100% 8704
/dev/loop0 /snap/pycharm-community/132  304256     0          100% 304256
/dev/loop2 /snap/pycharm-community/128  304256     0          100% 304256
/dev/loop3 /snap/core/7169              90624      0          100% 90624
/dev/loop5 /snap/skype/63               147840     0          100% 147840
/dev/loop4 /snap/skype/66               150912     0          100% 150912
/dev/loop6 /snap/core/7270              90624      0          100% 90624
/dev/loop7 /snap/skype/60               145280     0          100% 145280
/dev/loop8 /snap/canonical-livepatch/81 8704       0          100% 8704
/dev/sda1  /media/mrbruno/ExtraDrive1   1922727728 1833562312 5%   89149032
tmpfs      /run/user/125                1631576    1631560    1%   16
tmpfs      /run/user/1000               1631576    1631536    1%   40
```

I forced two columns to the start of the output but I just accepted the default for the remaining columns.

### Sorting
The numbers might be a little different because I added the `--sort` option after I prepared the other examples so the `df` output is a little different.
```
$ df -k | table --headings -i fixed -o sep --sort avail
Filesystem|1K-blocks|Used|Available|Use%|Mounted on
/dev/loop1|8704|8704|0|100%|/snap/canonical-livepatch/77
/dev/loop0|304256|304256|0|100%|/snap/pycharm-community/132
/dev/loop2|304256|304256|0|100%|/snap/pycharm-community/128
/dev/loop3|90624|90624|0|100%|/snap/core/7169
/dev/loop5|147840|147840|0|100%|/snap/skype/63
/dev/loop4|150912|150912|0|100%|/snap/skype/66
/dev/loop6|90624|90624|0|100%|/snap/core/7270
/dev/loop7|145280|145280|0|100%|/snap/skype/60
/dev/loop8|8704|8704|0|100%|/snap/canonical-livepatch/81
tmpfs|5120|4|5116|1%|/run/lock
tmpfs|1631580|2112|1629468|1%|/run
tmpfs|1631576|56|1631520|1%|/run/user/1000
tmpfs|1631576|16|1631560|1%|/run/user/125
tmpfs|8157880|184032|7973848|3%|/dev/shm
udev|8133732|0|8133732|0%|/dev
tmpfs|8157880|0|8157880|0%|/sys/fs/cgroup
/dev/sdb2|236102400|79077792|145008176|36%|/
/dev/sda1|1922727728|89154004|1833557340|5%|/media/mrbruno/ExtraDrive1
```


### `ls`
Output from `ls -l` is also read fairly well by the fixed input format:
```
$ ls -l ~ | drop 1 | table -i fixed -o csv
lrwxrwxrwx,1,mrbruno,mrbruno,8,Jun,29,08:43,bin -> toys/bin
lrwxrwxrwx,1,mrbruno,mrbruno,25,Aug,11,2017,bruno -> /home/mrbruno/extra/bruno
drwxr-xr-x,2,mrbruno,mrbruno,4096,Jan,27,2018,Desktop
lrwxrwxrwx,1,mrbruno,mrbruno,29,Aug,4,2017,Documents -> /home/mrbruno/extra/Documents
lrwxrwxrwx,1,mrbruno,mrbruno,9,Aug,4,2017,downloads -> Downloads
lrwxrwxrwx,1,mrbruno,mrbruno,29,Aug,4,2017,Downloads -> /home/mrbruno/extra/Downloads
drwxr-xr-x,2,mrbruno,mrbruno,4096,Jun,14,16:56,drive-download-20190614T205316Z-001
-rw-r--r--,1,mrbruno,mrbruno,8980,Aug,4,2017,examples.desktop
lrwxrwxrwx,1,mrbruno,mrbruno,26,Aug,4,2017,extra -> /media/mrbruno/ExtraDrive1
-rw-r--r--,1,mrbruno,mrbruno,27,Nov,5,2017,extraDrivePath.txt
lrwxrwxrwx,1,mrbruno,mrbruno,9,Jun,29,08:45,fun -> repos/fun
-r--------,1,mrbruno,mrbruno,41,Aug,5,2017,git-personal_access_token.txt
drwxr-xr-x,2,mrbruno,mrbruno,4096,Mar,2,16:01,hexchat-scripts
drwxr-xr-x,2,mrbruno,mrbruno,4096,Feb,17,07:21,misc
lrwxrwxrwx,1,mrbruno,mrbruno,25,Aug,4,2017,Music -> /home/mrbruno/extra/Music
-rw-------,1,mrbruno,mrbruno,45,Feb,24,2018,nohup.out
lrwxrwxrwx,1,mrbruno,mrbruno,28,Aug,4,2017,Pictures -> /home/mrbruno/extra/Pictures
drwxr-xr-x,2,mrbruno,mrbruno,24576,Apr,21,00:00,pinger
drwxr-xr-x,2,mrbruno,mrbruno,4096,Aug,4,2017,Public
lrwxrwxrwx,1,mrbruno,mrbruno,23,Jun,29,08:44,python -> /home/mrbruno/repos/fun
lrwxrwxrwx,1,mrbruno,mrbruno,25,Jun,29,08:40,repos -> /home/mrbruno/extra/repos
-rw-rw-r--,1,mrbruno,mrbruno,269322,Jul,17,2018,Screenshot from 2018-07-17 05-46-03.png
-rw-rw-r--,1,mrbruno,mrbruno,49616,Sep,14,2018,Screenshot from 2018-09-14 15-06-56.png
drwxr-xr-x,6,mrbruno,mrbruno,4096,Jun,15,07:47,snap
lrwxrwxrwx,1,mrbruno,mrbruno,28,Aug,5,2017,tarballs -> /home/mrbruno/extra/tarballs
drwxr-xr-x,2,mrbruno,mrbruno,4096,Aug,4,2017,Templates
lrwxrwxrwx,1,mrbruno,mrbruno,23,Aug,4,2017,tmp -> /home/mrbruno/extra/tmp
lrwxrwxrwx,1,mrbruno,mrbruno,10,Jun,29,08:42,toys -> repos/toys
lrwxrwxrwx,1,mrbruno,mrbruno,26,Aug,4,2017,Videos -> /home/mrbruno/extra/Videos
drwxrwxr-x,3,mrbruno,mrbruno,4096,Jun,8,08:19,VirtualBox VMs
drwxrwxr-x,2,mrbruno,mrbruno,4096,Nov,19,2017,Webcam
$
```

I used my [`drop` script](../doc/drop.md) to strip off the first line of output which doesn't lend itself to the columns of all the other lines and I didn't care about the line anyway.

I'm not super stoked about how it handles the modification date.  You'll notice that it split it up into columns (fields): month only, day of month only, and year or time.  It's consistent so I'm not too worried about it and I don't know how to handle this better but kept the fixed input format as generic as possible.

### Python class
The script can be used as a Python class, rendering the output using the fixed format.  The calling code bypasses input formats and supplies the data directly.
```
$ cat tabular
#! /usr/bin/env python

from table import Table

table = Table(['col 1', 'col 2', 'col 3'])
table.add(['cell11', 'cell12', 'cell13'])
table.add(['cell21', 'cell22', 'cell23'])
table.add(['...cell21...', 'cell22', '23'])

print str(table)
$ ./tabular
col 1        col 2  col 3
cell11       cell12 cell13
cell21       cell22 cell23
...cell21... cell22 23
$
```

## Notes

- I have other versions of this script that may do something similiar but none of them approach the flexibility of this script.
- The script only reads input from stdin
- I am not crazy about calling the script `table.py` but it's necessary for using it as a Python class.  You can abbreviate it as `table` by simply using a Unix alias:
  ```
  alias table=table.py
  ```
  This could be placed in your `$HOME/.bashrc` profile to get set automatically.
- Speaking of aliases, I have a couple that I use regularly as filters because I'm too lazy to type the options:
    ```
    alias fixed2sep='table.py -i fixed --headings -o sep --sep \|'
    alias fixed2json='table.py -i fixed --headings -o json'
    ```
  I tend to use `fixed2sep` more often to create a table in a Word document.  I'll copy the table with the separators, paste them into Word, and then use _Insert -> Table -> Convert Text to Table_ and make sure I specify _Separate text at |_.  I'll even do this for a document I don't plan on saving because it's a good way to visualize the data.
  Check out [this fragment I typically append to my `.bashrc` on my users](https://github.com/pfuntner/toys/blob/6422926d5c5c7201d2dc7a629a739082da236f88/misc/.bashrc#L91-L92).
- There is minimal XML support:
  - When reading XML:
    - The second level node tags must all be the same
    - Node attributes are ignored
    - Fourth level elements and beyond are ignored
    - I haven't found _naturally occurring_ XMLs that get processed very well.  Many are processed without error but render very little table content.  A sample XML I was using for testing was:
      ```
        <root>
          <node>
            <firstname>First 1</firstname>
            <lastname>Last 1</lastname>
          </node>
          <node>
            <firstname>First 2</firstname>
            <lastname>Last 2</lastname>
          </node>
        </root>
      ```
  - When writing XML:
    - The 1st level node tag is `<table>`
    - The 2nd level node tags are `<row>`
    - When processing a list of lists (no headings) 3rd level tags are follow the style `col00000000`, `col00000001`, etc.
