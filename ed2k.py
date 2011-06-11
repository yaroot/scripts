import re, urllib2, sys


def get(link):
    content = urllib2.urlopen(link).read()
    match = re.findall(r'"(ed2k://\|file\|[^\"]+)"', content, re.S)

    all_links = list()
    for link in match:
        if link in all_links:
            continue
        else:
            all_links.append(link)

    for link in all_links:
        print link


if __name__ == '__main__':
    try:
        get(sys.argv[1])
    except:
        sys.stderr.writelines('You must give a link\n')

