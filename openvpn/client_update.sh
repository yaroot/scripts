#!/usr/bin/env bash
#
# openvpn server setting:
#   script-security 2
#
#   client-connect     ./client_update.sh
#   client-disconnect  ./client_update.sh
#

logfile='client_update.log'
touch $logfile
echo "${script_type},${common_name},${trusted_ip},${trusted_port},${bytes_sent},${bytes_received},${time_unix},${time_ascii}" >> $logfile


