#!/usr/bin/python3

# Recreate directory structures for java packages. Works with files recovered
# with photorec.

# If no package declaration is detected in a file, then the file is skipped.
# Try to guess the file name from classes, interfaces and enums defined in the
# file. If no name can be detected, the original file name is used.
# The same name could be detected for several files. In this case, the original
# file name is used. One reason for this could be the recovery of multiple
# versions of the same file with the same item definitions (classes,
# interfaces, enums). You will have to examine the files in order to decide
# which version to keep.
import sys
import os
import re
import argparse

package_regex = r'^\s*package\s+([a-zA-Z0-9.]+)\s*;\s*$'
public_class_regex = r'^\s*(?:public\s+)(?:abstract\s+)?class\s+([a-zA-Z0-9.]+)'
class_regex = r'^\s*(?:abstract\s+)?class\s+([a-zA-Z0-9.]+)'
public_interface_regex = r'^\s*(?:public\s+)interface\s+([a-zA-Z0-9.]+)'
interface_regex = r'^\s*interface\s+([a-zA-Z0-9.]+)'
public_enum_regex = r'^\s*(?:public\s+)enum\s+([a-zA-Z0-9.]+)'
enum_regex = r'^\s*enum\s+([a-zA-Z0-9.]+)'

scanned = 0
config = argparse.Namespace()
config.verbose = False
encodings = ['utf-8', 'latin-1']

def log(message):
  if config.verbose:
    print(message)

def write(directory, base, ext, contents):
  base = base.replace('..', '_')
  if base.endswith(ext):
    base = os.path.splitext(base)[0]
  base_with_dir = os.path.join(directory, base)
  counter = 0
  while True:
    if counter == 0:
      name = base_with_dir + ext
    else:
      name = '{0} ({1}){2}'.format(base_with_dir, counter, ext)
    try:
      with open(name, 'xt') as fout:
        fout.write(contents)
      return
    except FileExistsError:
      counter += 1

def recover_file(file, dest):
  for encoding in encodings:
    with open(file, encoding = encoding) as fin:
      try:
        contents = fin.read()
        break
      except ValueError:
        # try the next encoding
        pass
  package_match = re.search(package_regex, contents, re.MULTILINE)
  name = None
  if not package_match:
    log("nothing interesting here, skipping")
    return
  package = package_match.group(1)
  log('found package {0}'.format(package))
  for regex in (public_class_regex, public_interface_regex, public_enum_regex):
    match = re.search(regex, contents, re.MULTILINE)
    if match:
      name = match.group(1)
      log('public item: {0}'.format(match.group(0)))
      break
  if not name:
    for regex in (class_regex, interface_regex, enum_regex):
      match = re.search(regex, contents, re.MULTILINE)
      if match:
        name = match.group(1)
        log('non-public item: {0}'.format(match.group(0)))
        break
  dest_dir = os.path.join(dest, package.replace('..', '_').replace('.', '/'))
  if not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)
  if name == None:
    name = os.path.basename(file)
    log('no name detected for {0}, using {1}'.format(file, name))
  write(dest_dir, name, '.java', contents)

def recover(sources, dest):
  global scanned

  def file_list():
    for path in sources:
      if os.path.isdir(path):
        for dirpath, dirs, dirfiles in os.walk(path, followlinks = True):
          for file in dirfiles:
            yield os.path.join(dirpath, file)
      else:
        yield path

  for file in file_list():
    log('scanning file {0}'.format(file))
    scanned += 1
    recover_file(file, dest)
    log('scanned {0} files'.format(scanned))
  log('scanned {0} files'.format(scanned))
  log('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Recreate directory structures for java packages. Typically used to reconstruct java package directories from files recovered with photorec.')
  parser.add_argument('-v', '--verbose', action = 'store_true', dest = 'verbose', default = False, help = 'verbose mode. Prints various operational messages')
  parser.add_argument('file', nargs = '*', help = 'A java file OR a directory that will be scanned for java files')
  parser.add_argument('-d', '--dest', dest = 'dest_dir', required = True, help = 'The directory where the program will recreate java package directories')
  config = parser.parse_args()
  recover(config.file, config.dest_dir)
