# Proxine: Fast and Elite Proxy List
Periodically build fresh proxy list from more than 110 online sources, checks and merges into one list. This repo has only elite proxies.
Raw lists profiled with [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

 Update Frequency: ```Every 30 minutes```

## Contains Proxies of over 100 Providers and is updated regularely

[![Commits](https://img.shields.io/github/last-commit/enseitankado/awesome-proxies?style=flat&logo=github)](https://github.com/enseitankado/awesome-proxies/commits/master)
[![Commits](https://img.shields.io/github/commit-activity/w/enseitankado/awesome-proxies?style=flat&logo=github)](https://github.com/enseitankado/awesome-proxies/commits/master)
[![Issues](https://img.shields.io/github/issues/enseitankado/awesome-proxies?style=flat&logo=github)](https://github.com/enseitankado/awesome-proxies/issues)
[![Stargazers](https://img.shields.io/github/stars/enseitankado/awesome-proxies?style=flat&logo=github)](https://github.com/enseitankado/awesome-proxies/stargazers)

------------------------------------------------------------

## Requirements
curl, python3

------------------------------------------------------------

## Usage

```powershell
./awesome-proxies.sh [proxy type]
```
 Usable proxy types: ```http, https, socks4, socks5```

------------------------------------------------------------

## Example

```powershell
./awesome-proxies.sh https > proxies.lst
```

------------------------------------------------------------

## Proxy Sources

 Proxine uses a lot of provider:

Source | Description
--- | ---
saschazesiger@github | 32 provider
nanosans@github | 31 provider
MuRongPIG | 22 provider
fate0@github | 6 provider
proxy4parsing@github | 2 provider
UptimerBot@github | *1 provider
ItzRazvyy@github | *1 provider
saisuiu@github | *1 provider
arunsakthivel96@github | *1 provider
jetkai@github | *1 provider
roosterkid@github | *1 provider
hookzof@github | *1 provider
mertguvencli@github | *1 provider
RX4095@github | *1 provider
officialputuid@github | *1 provider
sunny9577@github | *1 provider
pubproxy.com | *1 provider
arunsakthivel96 | *1 provider
proxyspace.pro | *1 provider
ipaddress.com | *1 provider
httptunnel.ge | *1 provider
proxyscan.io | *1 provider

* Highly possible multiple provider which undisclosed by project owner.

------------------------------------------------------------

## Tools

You can check proxy list in Windows env. with [EliteProxySwitcher](https://www.eliteproxyswitcher.com/). EPS also has auto switch feature to change active proxy periodicaly.
[Open Proxy Checker](https://openproxy.space/software/proxy-checker) is good alternative for Windows to check proxies.
