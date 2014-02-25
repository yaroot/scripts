#!/usr/bin/env bash

git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch $@" \
  --prune-empty --tag-name-filter cat -- --all
