#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division

import requests
import re

STATUS_FAIL = -1
STATUS_OK = 0
log = dict()

def append_path(a, b):
    return a.rstrip('/')+'/'+b

def init_log():
    try:
        with open('addon_update.log', 'r') as f:
            for line in f.lines:
                log[line.strip()] = True
    except IOError as e:
        pass

def is_file_downloaded(file_name):
    return log.has_key(file_name)


def download_with_fileinfo(info):
    file_name = info['file_name']
    link = info['link']
    hash_ = info['hash']
    hash_type = info['hash_type']
    if is_file_downloaded(file_name):
        return STATUS_OK




wowace_download_link_re = re.compile(r'href="(.+)"')
def parse_dlpage_wowace(page):
    for line in page.splitlines():
        if line.find('<td class="col-file">') > 0:
            ma = wowace_download_link_re.search(line)
            if ma:
                group = ma.groups()
                if len(group) == 1:
                    return group[0]


wowace_filename_re = re.compile(r'<dd><a href="(.+)">(.+)</a></dd>')
wowace_md5_re = re.compile(r'<dd>(.+)</dd>')
def parse_file_info_wowace(page):
    info = dict()
    found = 'nothing'
    for line in page.splitlines():
        if found != 'nothing':
            if found == 'filename':
                match = wowace_filename_re.search(line)
                if match:
                    info['link'], info['file_name'] = match.groups()
            elif found == 'md5':
                match = wowace_md5_re.search(line)
                if match:
                    info['hash'] = match.groups()[0]
                    info['hash_type'] = 'md5'
            found = 'nothing'
        else:
            if line.find('<dt>Filename</dt>') > 0:
                found = 'filename'
            elif line.find('<dt>MD5</dt>') > 0:
                found = 'md5'
        if info.has_key('file_name') and info.has_key('link'
                ) and info.has_key('hash'):
            return info


def download_wowace(link):
    files_page = append_path(link, 'files')
    site = 'http://www.wowace.com'
    if link.find('curseforge.com') > 0:
        site = 'http://wow.curseforge.com'
    r = requests.get(files_page)
    if(r.status_code != requests.codes.ok):
        return STATUS_FAIL
    download_page_link = parse_dlpage_wowace(r.text)
    if download_page_link is None:
        return STATUS_FAIL

    r = requests.get(site+download_page_link)
    if(r.status_code != requests.codes.ok):
        return STATUS_FAIL
    file_info = parse_file_info_wowace(r.text)
    if file_info:
        download_with_fileinfo(file_info)


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
    init_log()
    # addon_list = parse_config('addon.cfg')
    download('http://wow.curseforge.com/addons/heal-bot-continued/')
    download('http://www.wowinterface.com/downloads/info20546-CurrencyMonitor.html')
    download('http://www.curse.com/addons/wow/clique')
    download('http://www.wowace.com/addons/ace3/')

if __name__ == '__main__':
    import sys
    main(sys.argv)

