#!/bin/bash

SERVICE=$1
TEST_IP='1.1.1.1'
#TEST_IP='10.0.0.1'

test_link() {
    ping -w10 -c4 $TEST_IP  > /dev/null
}

reconnect() {
    connmanctl disable wifi && sleep 5s && \
    connmanctl enable wifi && sleep 5s && \
    connmanctl connect $SERVICE
}

test_link || reconnect
