#!/usr/bin/python2

import urllib2, re, sys

LINKBASE = r'http://tvunderground.org.ru/'

def geted2k(link):
    page = urllib2.urlopen(link).read()
    match = re.findall(r'href="(ed2k://\|file\|[^\"]+)"', page, re.S)
    for l in match:
        print(l)
    pass

def get(link):
    page = urllib2.urlopen(link).read()
    # index.php?show=ed2k&amp;season=12337&amp;sid[204769]=1
    #ma = re.findall(r'"(index.php\?show=ed2k\&amp\;season=\d+\&amp;sid\[\d+\]=1)"', page.read(), re.S)
    ma = re.findall(r'"(index.php\?show=ed2k.+?)"', page, re.S)
    if(ma):
        #print(len(ma))
        #print(ma)
        for l in ma:
            geted2k(LINKBASE+l)
        print('\n\n\n')
    pass


if __name__ == '__main__':
    try:
        get(sys.argv[1])
    except:
        sys.stderr.writelines('You must give a link')

