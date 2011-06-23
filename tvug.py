#!/usr/bin/python2

import xml, urllib2, re, sys
import ed2k
import xml.sax.saxutils

LINKBASE = r'http://tvunderground.org.ru/'

def get(link):
    page = urllib2.urlopen(link).read()
    # index.php?show=ed2k&amp;season=12337&amp;sid[204769]=1
    #ma = re.findall(r'"(index.php\?show=ed2k\&amp\;season=\d+\&amp;sid\[\d+\]=1)"', page.read(), re.S)
    ma = re.findall(r'"(index.php\?show=ed2k.+?)"', page, re.S)
    if(ma):
        for l in ma:
	    ed2k.get(xml.sax.saxutils.unescape(LINKBASE+l))
	    #print xml.sax.saxutils.unescape(LINKBASE+l)

if __name__ == '__main__':
    get(sys.argv[1])

