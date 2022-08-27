# proxy-list.sh
Periodically build fresh proxy list from different online source and merge into big one.

## Requirements
curl

## Usage

./awesome-proxies.sh [proxy type]

Usable proxy types: http,https,socks4,socks5

./awesome-proxies.sh https | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u > proxies.lst

When downloading proxy list from its source, sometimes occurs connection problems and output gets dirty. Below example filter ip:port and remove dublicateds then saves to proxies.lst file.


## Proxy Sources

awesome-proxies uses the (aschazesiger's list)[https://github.com/saschazesiger/Free-Proxies], which is a comprehensive resource (32), in addition to the following sources:

1. https://github.com/saschazesiger/Free-Proxies : 32 source ((check for list)[https://github.com/saschazesiger/Free-Proxies])
1. https://github.com/fate0/getproxy/ : 6 source (cnproxy,coolproxy,freeproxylist,ip181,proxylist,xicidaili)
1. https://github.com/proxy4parsing/proxy-list : 2 source (hideme,spsys)
1. https://github.com/UptimerBot/proxy-list : Unknown source(s)
1. https://github.com/ItzRazvyy/ProxyList : Unknown source(s)
1. https://github.com/saisuiu/uiu : Unknown source(s)
1. https://github.com/arunsakthivel96/proxyBEE : Unknown source(s)


## Tools
You can check proxy list in Windows env. with (EliteProxySwitcher)[https://www.eliteproxyswitcher.com/]. EPS also has auto switch feature to change current proxy periodicaly.

