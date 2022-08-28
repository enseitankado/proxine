#!/bin/bash
./utils/ap-main.sh "$@" | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u
