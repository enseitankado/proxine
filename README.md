# 🚀 Proxine: Only FAST + ELITE (LEVEL-1) PROXIES

Periodically build fresh proxy list from more than 110 online sources, checks and merges into one list. This repo HAS ONLY ELITE (LEVEL 1) proxies. Filtering is performed by [Proxy Profiler](https://github.com/enseitankado/proxy-profiler). 

 Update Frequency: ```Every 2 hours```

## Contains Proxies of over 110 Providers and is updated regularely

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
./proxine.sh [proxy type]
```
 Usable proxy types: ```http, https, socks4, socks5```

------------------------------------------------------------

## Example

```powershell
./proxine.sh https > proxies.lst
```

------------------------------------------------------------

## 🔎 Proxy Sources

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
arunsakthivel96@github | *1 provider
rx443@github | *1 provider
pubproxy.com | *1 provider
proxyspace.pro | *1 provider
ipaddress.com | *1 provider
httptunnel.ge | *1 provider
proxyscan.io | *1 provider
proxylists.net | *1 provider
proxyscrape.com | *1 provider
rdavydov | *1 provider 
spys.me | *1 provider
free-proxy-list.net | *1 provider
google-proxy.net | *1 provider
socks-proxy.net | *1 provider
sslproxies.org | *1 provider
zevtyardt | *1 provider
TheSpeedX | *1 provider

* Highly possible multiple provider which undisclosed by project owner.

------------------------------------------------------------

## Tools

You can check proxy list in Windows env. with [EliteProxySwitcher](https://www.eliteproxyswitcher.com/). EPS also has auto switch feature to change active proxy periodicaly.
[Open Proxy Checker](https://openproxy.space/software/proxy-checker) is good alternative for Windows to check proxies. [Proxy profiler](https://github.com/enseitankado/proxy-profiler) to test and profile large proxy lists.

# Scheduled Script (Proxine + Proxy Profiler)

```powershell
#!/bin/bash
cd /home/pi/proxine

# Only Level-1 good proxies
./proxine.sh socks5 | php /home/pi/proxy-profiler/proxyprof.php -t socks5 -l 1 -g -o proxy/socks5.txt -s -e -n 500
git add .; git commit -m "`cat proxy/socks5.txt | wc -l` working elite socks5 proxies added."; git push -f

./proxine.sh socks4 | php /home/pi/proxy-profiler/proxyprof.php -t socks4 -l 1 -g -o proxy/socks4.txt -s -e -n 500
git add .; git commit -m "`cat proxy/socks4.txt | wc -l` working elite socks4 proxies added."; git push -f

./proxine.sh https | php /home/pi/proxy-profiler/proxyprof.php -t https -l 1 -g -o proxy/https.txt -n 1000 -s -e
git add .; git commit -m "`cat proxy/https.txt | wc -l` working elite https proxies added."; git push -f

./proxine.sh http | php /home/pi/proxy-profiler/proxyprof.php -t http -l 1 -g -o proxy/http.txt -n 1000 -s -e
git add .; git commit -m "`cat proxy/http.txt | wc -l` working elite http proxies added."; git push -f


# CloudFlare approved Level-1 proxies
php /home/pi/proxy-profiler/proxyprof.php -f proxy/socks5.txt -t socks5 -o proxy-cloudflare-pass/socks5.txt -s -a https://www.tankado.com/ -y 3 -c 5 -e -g
git add .; git commit -m "`cat proxy-cloudflare-pass/socks5.txt | wc -l` CloudFlare approved elite socks5 proxies added."; git push -f

php /home/pi/proxy-profiler/proxyprof.php -f proxy/socks4.txt -t socks4 -o proxy-cloudflare-pass/socks4.txt -s -a https://www.tankado.com/ -y 3 -c 5 -e -g
git add .; git commit -m "`cat proxy-cloudflare-pass/socks4.txt | wc -l` CloudFlare approved elite socks4 proxies added."; git push -f

php /home/pi/proxy-profiler/proxyprof.php -f proxy/https.txt -t https -o proxy-cloudflare-pass/https.txt -n 1000 -s -a https://www.tankado.com/ -y 3 -c 5 -e -g
git add .; git commit -m "`cat proxy-cloudflare-pass/https.txt | wc -l` CloudFlare approved elite https proxies added."; git push -f

php /home/pi/proxy-profiler/proxyprof.php -f proxy/http.txt -t http -o proxy-cloudflare-pass/http.txt -n 1000 -s -a https://www.tankado.com/ -y 3 -c 5 -e -g
git add .; git commit -m "`cat proxy-cloudflare-pass/http.txt | wc -l` CloudFlare approved elite http proxies added."; git push -f
```

# Disclaimer

This is an open source for everyone, you may redistribute, modify, use patents and use privately without any obligation to redistribute. but it should be noted to include the source code of the library that was modified (not the source code of the entire program), include the license, include the original copyright of the author (Özgür Koca), and include any changes made (if modified). Users do not have the right to sue the creator when there is damage to the software or even demand if there is a problem caused by the makers of this tool. because every risk is caused by the user risk itself.


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)

# Author

I'm Özgür. I'm a teacher at a vocational [school](https://samsuneml.meb.k12.tr/)
Repos: https://github.com/enseitankado
Blog: www.tankado.com

# Donation

Would you like to buy me a coffee? [Click](https://www.buymeacoffee.com/ozgurkoca).

