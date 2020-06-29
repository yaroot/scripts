#!/usr/bin/env python3

'''
https://gist.github.com/jbeda/5c79d2b1434f0018d693
http://nixos.org/~eelco/pubs/phd-thesis.pdf

serialise(fso) = str("nix-archive-1") + serialise1(fso)

serialise1(fso) = str("(") + seralise2(fso) + str(")")

serialise2(type=Regular, exec, contents) =
  str("type") + str("regular")
  + (
    str("executable") + str(""), if exec = Executable
    "", if exec = NonExecutable
  ) + str("contents") + str(contents)

serialise2(type=SymLink, target) =
  str("type") + str("symlink")
  + str("target") + str(target)

serialise2(type=Directory, entries) =
  str("type") + str("directory")
  + concatMap(serialiseEntry, sortEntries(entries))

serialiseEntry((name, fso)) =
  str("entry") + str("(")
  + str("name") + str(name)
  + str("node") + serialise1(fso)
  + str(")")

str(s) = int(|s|) + pad(s)

int(n) = the 64-bit little endian representation of the number n

pad(s) = the byte sequence s, padded with 0s to a multiple of 8 bytes
'''

import sys
from pathlib import Path
import struct


def _read(size: int):
    return sys.stdin.buffer.read(size)


def read_length():
    return struct.unpack('Q', _read(8))[0]


def read_bytes() -> bytes:
    n = read_length()
    try:
        return _read(n)
    finally:
        if n % 8 != 0:
            _read(8 - n % 8)
        pass


def read_ascii():
    return read_bytes().decode('ascii')


def read_ascii_const(value: str):
    assert read_bytes().decode('ascii') == value


def read_attr(name: str):
    read_ascii_const(name)
    return read_ascii()


def read_directory():
    read_ascii_const('entry')
    read_ascii_const('(')
    name = read_attr('name')
    print(name)
    read_ascii_const(')')
    pass


def read_next():
    read_ascii_const('(')   # open
    _ftype = read_attr('type')
    if _ftype == 'directory':
        read_directory()
    else:
        assert False, f'Unknown `{_ftype}`'
    read_ascii_const(')')   # close


def unpack_to(path: Path):
    read_ascii_const('nix-archive-1')
    read_next()
    pass


def main(args):
    assert len(args) in (0, 1)
    write_path = Path('.')
    if args:
        write_path = Path(args[0])
    write_path = write_path.absolute()
    if not write_path.exists():
        write_path.mkdir(parents=True)
    unpack_to(write_path)


if __name__ == '__main__':
    main(sys.argv[1:])
