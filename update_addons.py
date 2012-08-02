#!/usr/bin/env python
"""

this script is written in python. `requests` is required (`pip install
requests`).

sample config file [WoW_install_directory]/Interface/addons.cfg]:

    git://github.com/haste/oUF.git
    github://p3lim/oUF_P3lim.git
    git://github.com/haste/Butsu.git
    git://github.com/tekkub/teksloot.git?teksLoot
    http://www.wowace.com/addons/mapster/
    http://www.wowinterface.com/downloads/info18855-TomTomLite.html
    http://www.curse.com/addons/wow/deadly-boss-mods
    #http://www.wowinterface.com/downloads/info7017-LightHeaded.html

put this script in the same directory, `cd path/to/Interface` 
then run `./update_addon.py`.

"""

from __future__ import absolute_import, print_function, unicode_literals, division

import requests
import re
import os
from HTMLParser import HTMLParser
import urlparse
from zipfile import ZipFile
import shutil
import subprocess

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0'
STATUS_FAIL = -1
headers = { 'user-agent': UA }

def append_path(a, b):
    return a.rstrip('/')+'/'+b

def unexcape_html(a):
    return HTMLParser().unescape(a)


def init_dir():
    if not os.path.exists('files'):
        os.mkdir('files')
    if not os.path.exists('AddOns'):
        os.mkdir('AddOns')


def is_file_downloaded(file_name):
    return os.path.exists(append_path('files', file_name))


def save_file(file_path, content):
    with open(file_path, 'wb') as f:
        f.write(content)


def install_addon(info):
    print(">>> Extracting " + info['file_name'])
    z = ZipFile('files/'+info['file_name'])
    dirs = dict()
    for zi in z.infolist():
        d = zi.filename.split('/')[0]
        if not dirs.has_key(d):
            dirs[d] = True
    for d in dirs.keys():
        if os.path.exists('AddOns/'+d):
            shutil.rmtree('AddOns/'+d)

    z.extractall('AddOns/')
    z.close()


def download_file(info):
    link = info['url']
    print(">>> Downloading " + link)
    r = requests.get(info['url'], headers=headers)
    if r.status_code == requests.codes.ok:
        save_file(append_path('files', info['file_name']), r.content)


def download_with_fileinfo(info):
    file_name = info['file_name']
    link = info['url']
    download_file(info)


wowace_download_link_re = re.compile(r'href="(.+)"')
def parse_dlpage_wowace(page):
    for line in page.splitlines():
        if line.find('<td class="col-file">') > 0:
            ma = wowace_download_link_re.search(line)
            if ma:
                group = ma.groups()
                if len(group) == 1:
                    return group[0]


wowi_dlpage_re = re.compile(r'<div id="icon"><a href="(.+)" onclick="')
wowi_md5_re = re.compile(r'value="(.+)" /></td>')
def parse_dlpage_wowi(page, info):
    for line in page.splitlines():
        ma = wowi_dlpage_re.search(line)
        if ma:
            info['dlink'] = unexcape_html(ma.groups()[0])
        elif line.find('titletext">MD5:</td>') > 0:
            ma = wowi_md5_re.search(line)
            info['hash'] = ma.groups()[0]
            info['hash_type'] = 'md5'
        if info.has_key('dlink') and info.has_key('hash'):
            return info


def parse_dlink_wowi(info):
    dlink = info['dlink']
    r = requests.head(dlink, allow_redirects=True, headers=headers)
    fh = r.headers['content-disposition']
    info['file_name'] = fh.split('filename=')[-1].strip('"').strip("'")
    info['url'] = r.url
    

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
                    info['url'], info['file_name'] = match.groups()
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
        if info.has_key('file_name') and info.has_key('url'
                ) and info.has_key('hash'):
            return info


def extract_download_info_wowace(link):
    files_page = append_path(link, 'files')

    r = requests.get(files_page, headers=headers)
    if(r.status_code != requests.codes.ok):
        return STATUS_FAIL
    download_page_link = parse_dlpage_wowace(r.text)
    if download_page_link is None:
        return STATUS_FAIL

    r = requests.get(urlparse.urljoin(link, download_page_link), headers=headers)
    if(r.status_code != requests.codes.ok):
        return STATUS_FAIL
    file_info = parse_file_info_wowace(r.text)
    return file_info


curse_download_link_re = re.compile(r'data\-href="(.+)" class="download\-link"')
def extract_download_info_curse(link):
    dl_page = append_path(link, 'download')
    r = requests.get(dl_page, headers=headers)
    if r.status_code != requests.codes.ok:
        return STATUS_FAIL
    info = dict()
    for line in r.text.splitlines():
        ma = curse_download_link_re.search(line)
        if ma:
            link = ma.groups()[0]
            info['file_name'] = link.split('/')[-1]
            info['url'] = link
        if info.has_key('url') and info.has_key('file_name'):
            return info
    return STATUS_FAIL


def extract_download_info_wowi(link):
    r = requests.get(link, headers=headers)
    if r.status_code != requests.codes.ok:
        return STATUS_FAIL
    info = dict()
    parse_dlpage_wowi(r.text, info)
    info['dlink'] = urlparse.urljoin(link, info['dlink'])
    parse_dlink_wowi(info)
    return info


def download_and_install(info):
    if is_file_downloaded(info['file_name']):
        return
    download_with_fileinfo(info)
    install_addon(info)


def download_wowace(link):
    info = extract_download_info_wowace(link)
    if info != STATUS_FAIL:
        download_and_install(info)


def download_curse(link):
    info = extract_download_info_curse(link)
    if info != STATUS_FAIL:
        download_and_install(info)


def download_wowi(link):
    info = extract_download_info_wowi(link)
    if info != STATUS_FAIL:
        download_and_install(info)


def git_do_checkout(info):
    url = info['url']
    directory = info['name']
    wd = os.getcwd()
    if os.path.exists('AddOns/'+directory):
        print('>>> git update ', url, os.getcwd())
        os.chdir('AddOns/' + directory)
        subprocess.call(['git', 'pull'])
    else:
        print('>>> git clone', url, directory, os.getcwd())
        os.chdir('AddOns')
        subprocess.call(['git', 'clone', url, directory])
    os.chdir(wd)


def checkout_git(link):
    sch, netloc, path, par, query, fra = urlparse.urlparse(link)
    info = dict()
    if sch == 'github':
        info['url'] = 'git://github.com/'+netloc
    elif sch == 'git':
        info['url'] = 'git://'+netloc

    i = path.find('?')
    if i > 0:
        info['url'] += path[0:i]
    else:
        info['url'] += path

    ls = link.split('?')
    if len(ls) > 1:
        info['name'] = ls[-1]
    else:
        info['name'] = link.split('/')[-1].rstrip('.git')

    git_do_checkout(info)


def download(link):
    print(">>> Parsing " + link)
    sch, netloc, path, par, query, fra = urlparse.urlparse(link)

    if 'git' in sch:
        checkout_git(link)
    elif sch == 'http':
        if 'curseforge' in netloc or 'wowace' in netloc:
            download_wowace(link)
        elif 'curse.com' in netloc:
            download_curse(link)
        elif 'wowinterface' in netloc:
            download_wowi(link)


def main(argv):
    init_dir()
    addon_list = list()
    with open('addons.cfg') as f:
        for l in f.readlines():
            addon_list.append(l.strip())
    for l in addon_list:
        download(l)

if __name__ == '__main__':
    import sys
    main(sys.argv)

