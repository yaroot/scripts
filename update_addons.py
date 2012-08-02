#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division

import requests

def append_path(a, b):
    return a.rstrip('/')+'/'+b

def get_wowace_file_link_from_download_page(page):
    for line in page.splitlines():
        if line.find('<td class="col-file">') > 0:
            print(line)
            return


def download_wowace(link):
    files_page = append_path(link, 'files')
    r = requests.get(files_page)
    if(r.status_code == requests.codes.ok):
        download_page_link = get_wowace_file_link_from_download_page(r.text)

def download_curse(link):
    pass

def download_wowi(link):
    pass

def download(link):
    if(link.find('curseforge.com') > 0 or link.find('wowace.com') > 0):
        download_wowace(link)
    elif(link.find('curse.com') > 0):
        download_curse(link)
    elif(link.find('wowinterface.com') > 0):
        download_wowi(link)


def parse_cfg_line(line):
    pass

def read_cfg_by_line(fd):
    alist = list()
    for line in fd.lines():
        a = parse_cfg_line(line)
        if a:
            alist.append(a)
    return alist


def parse_config(cfg_file):
    try:
        with open(cfg_file) as f:
            cfg = read_cfg_by_line(f)
            return cfg
    except IOError:
        raise Exception("Open [{}] error".format(cfg_file))


def main(argv):
    # addon_list = parse_config('addon.cfg')
    download('http://wow.curseforge.com/addons/heal-bot-continued/')
    download('http://www.wowinterface.com/downloads/info20546-CurrencyMonitor.html')
    download('http://www.curse.com/addons/wow/clique')
    download('http://www.wowace.com/addons/ace3/')

if __name__ == '__main__':
    import sys
    main(sys.argv)

