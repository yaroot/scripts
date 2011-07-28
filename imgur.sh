#!/bin/bash

# API Key provided by Alan@imgur.com
API_KEY="b3625162d3418ac51a9ee805b1840452"
API_URL="http://imgur.com/api/upload.xml"

FILE_NAME=$1

RESPONSE=$(curl -F "key=$API_KEY" -F "image=@$FILE_NAME" $API_URL)

echo "$RESPONSE" | grep -E -o '<original_image>(.+)</original_image>' | grep -E -o 'http://i.imgur.com/[^<]*'
#echo "$RESPONSE" | grep -E -o '<delete_page>(.+)</delete_page>' | grep -E -o 'http://imgur.com/[^<]*'

