# awesome-proxies.sh
Periodically build fresh proxy list from different online source and merge into big one.

 Update Frequency: ```Every 30 minutes```

------------------------------------------------------------

## Requirements
curl

------------------------------------------------------------

## Usage

```powershell
./awesome-proxies.sh [proxy type]
```
 Usable proxy types: http,https,socks4,socks5
------------------------------------------------------------
## Example

```powershell
./awesome-proxies.sh https | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}\:[0-9]{1,5}" | sort -u > proxies.lst
```
 When downloading proxy list from its source, sometimes occurs connection problems and output gets dirty. Below example filter ip:port and remove dublicateds then saves to proxies.lst file.

------------------------------------------------------------

## Proxy Sources

 awesome-proxies uses the [aschazesiger's list](https://github.com/saschazesiger/Free-Proxies), which is a comprehensive resource (32), in addition to the following sources:

Source | Description
--- | ---
https://github.com/saschazesiger/Free-Proxies | 32 sources:  [check for list](https://github.com/saschazesiger/Free-Proxies)
https://github.com/fate0/getproxy/ | 6 sources: cnproxy,coolproxy,freeproxylist,ip181,proxylist,xicidaili
https://github.com/proxy4parsing/proxy-list | 2 sources: hideme,spsys
https://github.com/UptimerBot/proxy-list | Unknown source(s)
https://github.com/ItzRazvyy/ProxyList | Unknown source(s)
https://github.com/saisuiu/uiu | Unknown source(s)
https://github.com/arunsakthivel96/proxyBEE | Unknown source(s)

------------------------------------------------------------

## Tools

You can check proxy list in Windows env. with [EliteProxySwitcher](https://www.eliteproxyswitcher.com/). EPS also has auto switch feature to change active proxy periodicaly.

