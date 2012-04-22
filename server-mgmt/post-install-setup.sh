#!/bin/bash


which apt-get 2>&1 > /dev/null

PKGS="git openssh-server sudo"

if [ -x /usr/bin/apt-get ] ; then
    #apt-get update -y && apt-get upgrade -y && apt-get dest-update -y
    apt-get install -y $PKGS
elif [ -x /usr/bin/yum ] ; then
    yum install -y $PKGS
fi



addstuff() {
    if getent passwd ${1} > /dev/null ; then
        echo "User already exists: ${1}"
    else
        echo "Adding user: ${1}"
        useradd -m ${1}
    fi

    mkdir -p /home/${1}/.ssh
    chown ${1}:${1} /home/${1}/.ssh
    chmod 700 /home/${1}/.ssh

    touch /home/${1}/.ssh/authorized_keys
    chown ${1}:${1} /home/${1}/.ssh/authorized_keys
    chmod 600 /home/${1}/.ssh/authorized_keys

    if [ -f "./${1}.pub" ] && [ -r "./${1}.pub" ] ; then
        cat ./${1}.pub >> /home/${1}/.ssh/authorized_keys
    fi

    if ! grep ${1} /etc/sudoers 2>&1 > /dev/null ; then
        echo "${1}    ALL = NOPASSWD: ALL" >> /etc/sudoers
    fi

}

for username in $@; do
    addstuff $username
done


