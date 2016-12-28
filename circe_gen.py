#!/usr/bin/env python2

def camalize(name):
    if len(name) > 1:
        return name[0].lower() + name[1:]
    else:
        return name.lower()


def derive(name, what):
    n = camalize(name)
    return 'implicit val %s%s: %s[%s] = derive%s[%s]' % (
        n, what, what, name, what, name
    )

def main():
    import sys
    for name in sys.argv[1:]:
        print derive(name, 'Encoder')
        print derive(name, 'Decoder')

if __name__ == '__main__':
    main()
