#!/bin/bash

#   this script make use of ssh tunnel to break the GREAT FIREWALL
#   each time this script excuted will respawn all the tunnel
#   remember to use a key for authorize (and keychain if using passphase)
#
#   install [autossh] and create a config file: $HOME/.fuckgfw.rc
#   example:
#       SSH_SRV="john@192.168.0.254"
#       FORWARD_PORTS=(7070 7071 7072)
#

killall -9 autossh 2>/dev/null

source $HOME/.fuckgfw.rc

for port in ${FORWARD_PORTS[@]}; do
    # -M 0      no listening
    # -f        run background
    # -NC       no shell, compress data transfer
    eval "autossh -M 0 -f -NCD ${port} ${SSH_SRV}"
done


