#!/usr/bin/env python3

import json
import sys


def main(path):
    with open(path, 'r') as f:
        sol_out = json.load(f)
    print('bytecode size:', len(bytes.fromhex(sol_out['bytecode'][2:])))
    print('bytecode (deployed) size:', len(bytes.fromhex(sol_out['deployedBytecode'][2:])))
    pass


if __name__ == '__main__':
    main(sys.argv[1])
