#!/bin/bash

if [ $# -eq 0 ]; then
   echo ""
   echo "  What is it: Collect fresh proxy list from tens of unique sources,"
   echo "  and sorts as unique records. github.com/enseitankado/"
   echo ""
   echo "      Usage: ./proxine.sh <http/https/socks4/socks5>"
   echo ""
   echo "    Example: ./proxine.sh http"
   echo ""
   exit 1
fi

if ! [[ "$1" =~ ^(http|https|socks4|socks5)$ ]]; then
	printf "\n Unsupported proxy type! \n\n Please use one of these: http/https/socks4/socks5\n"
	exit 2
fi

coresh=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")"/utils/core.sh"
$coresh $@ | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u 
