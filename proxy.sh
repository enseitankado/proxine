#!/bin/bash
if [ $# -eq 0 ]; then
   echo ""
   echo "  Usage: ./proxine.sh http/https/socks4/socks5"
   echo ""
   echo "  Example: ./proxine.sh http"
   echo ""
   exit 1
fi

if ! [[ "$1" =~ ^(http|https|socks4|socks5)$ ]]; then
	printf "\n Unsupported proxy type! \n\n Please use one of these: http/https/socks4/socks5\n"
fi

./utils/core.sh $@ | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u