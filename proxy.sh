#!/bin/bash
if [ $# -eq 0 ]; then
   echo ""
   echo "  Usage: ./proxine.sh http/https/socks4/socks5";
   echo ""
   echo "  Example: ./proxine.sh http"
   echo ""
   exit 1
fi
./utils/ap-main.sh "$@" | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u
