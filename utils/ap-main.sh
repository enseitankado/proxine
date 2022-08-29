for arg
do
case $arg in
   "http")
	curl -s "https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/http.txt"
	echo "\n"
	curl -s "https://github.com/saisuiu/uiu"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/premium.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list" | python utils/parsefate0.py http
	echo "\n"
	curl -s "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt"
       ;;
   "https")
	echo "\n"
	curl -s "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/https.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/premium.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list" | python utils/parsefate0.py https
	echo "\n"
	curl -s "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt"
	;;
   "socks4")
	echo "\n"
	curl -s "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks4.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks4.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt"
       ;;
   "socks5")
	echo "\n"
	curl -s "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks5.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt"
	echo "\n"
	curl -s "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt"
       ;;
   *)
esac
done
