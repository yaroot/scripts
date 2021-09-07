#!/usr/bin/env python3

import json
import sys


def format_args(args):
    if not args:
        return ''
    vals = []
    for x in args:
        name = x['name']
        typ = x['type']
        vals.append(f'{typ} {name}')
    return ', '.join(vals).strip()


def format(x):
    _type = x['type']
    if _type == 'function':
        name = x['name']
        inputs = x['inputs']
        outputs = x['outputs']
        state = x['stateMutability']
        if state == 'nonpayable':
            state = ''
        _ins = format_args(inputs)
        _outs = format_args(outputs)
        if _outs:
            _outs = f'returns ({_outs})'
        return f'λ {name}({_ins}) {state} {_outs}'.strip().replace('  ', '')
    elif _type == 'constructor':
        inputs = x['inputs']
        _ins = format_args(inputs)
        return f'⏻ ({_ins})'.strip().replace('  ', '')
    elif _type == 'event':
        name = x['name']
        inputs = x['inputs']
        _ins = format_args(inputs)
        return f'❄ {name}({_ins})'
    else:
        print('>>', _type)


def render(abis, out):
    for x in abis:
        y = format(x)
        if y:
            out.writelines([y, '\n'])
    pass


def main(path):
    with open(path, 'r') as f:
        _in = json.load(f)
    if 'abi' in _in:
        _abi = _in['abi']
    elif type(_in) == list:
        _abi = _in
    else:
        assert False, 'Unknown format'
    render(_abi, sys.stdout)


if __name__ == '__main__':
    main(sys.argv[1])
