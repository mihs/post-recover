# create-packages

Recreate java package directories.

## Usage

```
usage: create-packages.py [-h] [-v] -d DEST_DIR [file [file ...]]

Recreate directory structures for java packages. Typically used to reconstruct
java package directories from files recovered with photorec.

positional arguments:
  file                  A java file OR a directory that will be scanned for
                        java files

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode. Prints various operational messages
  -d DEST_DIR, --dest DEST_DIR
                        The directory where the program will recreate java
                        package directories
```
