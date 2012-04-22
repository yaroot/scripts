#!/bin/bash


create_repo() {
    reponame="${1}.git"
    mkdir $reponame
    cd $reponame
    git init --bare
    cd ..
    chown -R git.git $reponame
}

for name in "$@"; do
    create_repo $name
done

