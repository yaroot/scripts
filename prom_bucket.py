import sys
import re


def split(line: str):
    a, b = line.split(' ')
    if '"+Inf"' in a:
        a = -1
    else:
        m = re.search(r'le="(\d+\.?\d*)"', a)
        a = float(m.groups(0)[0])
    b = float(b)
    return a, b


def make_printable(buckets):
    # input: [(1.0, 5), (2.0, 10), (3.0, 10)]
    # output: [(1.0, 5), (2.0, 5), (3.0, 0)]
    output = []
    p = None
    for x in buckets:
        if p:
            output.append((x[0], x[1]-p[1]))
        else:
            output.append(x)
        p = x
    return output


def main():
    lines = [l for l in sys.stdin.readlines() if l.strip()]
    buckets = sorted([split(l) for l in lines], key=lambda x: x[0])
    buckets.append(buckets.pop(0))
    for x in make_printable(buckets):
        print(x)
    pass


if __name__ == '__main__':
    main()
