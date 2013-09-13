#!/usr/bin/env bash

# -getsocksfirewallproxy networkservice
# -setsocksfirewallproxy networkservice domain portnumber authenticated username password
#
# -getproxybypassdomains networkservice
#     Displays Bypass Domain Names for <networkservice>.
# 
# -setproxybypassdomains networkservice domain1 [domain2] [...]
#     Set the Bypass Domain Name Servers for <networkservice> to <domain1> [domain2] [...]. Any number of Domain Name servers can be
#     specified. Specify "Empty" for <domain1> to clear all Domain Name entries.
#
# -setsocksfirewallproxystate networkservice on | off

# echo '127.0.0.1, *.local, 192.168.0.0/16, 169.254/16, localhost' > ~/.network_bypass.list
if [ ! -f $HOME/.network_bypass.list ]; then
    echo '>> please list bypass domains in ~/.network_bypass.list'
    exit -1
fi

BYPASS_LIST=''
# `cat $HOME/.network_bypass.list | head -n1 | sed 's/,//g'`

for domain in `cat $HOME/.network_bypass.list`; do
    if [ -n "$domain" ]; then
        if [ -z "$BYPASS_LIST" ]; then
            BYPASS_LIST="$domain"
        else
            BYPASS_LIST="${BYPASS_LIST}, $domain"
        fi
    fi
done

if [ "$1" = '-n' ]; then
    echo $BYPASS_LIST
else
    for DEV in `echo Ethernet Wi-Fi`; do
        networksetup -setproxybypassdomains $DEV $BYPASS_LIST
    done
fi

