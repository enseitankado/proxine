"""
Proxine kaynak manifesti.

Her giriş: (URL, parser_adı). Parser adları proxine.py içindeki PARSERS sözlüğüne karşılık gelir:

    regex     : Metni IPv4:PORT regex'i ile tara. Düz metin + (kısmen) HTML için.
    ndjson    : Satır başına bir JSON (fate0 / arunsakthivel96/proxyBEE şeması).
                type == proto AND anonymity == "high_anonymous".
    stamparm  : Tek bir JSON dizisi. proto eşleşmesi AND type == "elite".
    geonode   : Satır başına {"data": {...}} zarflı JSON. (proxylist.geonode.com API'si)

Yeni kaynak eklemek = doğru protokole tek satır ilave etmek.
Kaynak kapatmak = satırı silmek veya yorum yapmak. Dört case bloğunu güncelleme derdi yok.
"""

from __future__ import annotations

Source = tuple[str, str]

SOURCES: dict[str, list[Source]] = {
    "http": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/saisuiu/uiu/main/cnfree.txt", "regex"),
        ("https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt", "regex"),
        ("https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/arunsakthivel96/proxyBEE/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt", "regex"),
        # NOT: eski URL /blob/ döndüğü için HTML alıyorduk; raw varyantına çevrildi.
        ("https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt", "regex"),
        ("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt", "regex"),
        ("https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt", "regex"),
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=http", "regex"),
        ("https://proxyspace.pro/http.txt", "regex"),
        ("https://www.ipaddress.com/proxy-list/", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=http&country=all&ssl=all&anonymity=all", "regex"),
        ("https://free-proxy-list.net/anonymous-proxy.html", "regex"),
        ("https://www.google-proxy.net/", "regex"),
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/http.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/stamparm/aux/master/fetch-some-list.txt", "stamparm"),
        ("https://raw.githubusercontent.com/rx443/proxy-list/main/online/http.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/vmheaven/VMHeaven.io-Free-Proxy-List/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/http_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/Mohammedcha/ProxRipper/main/full_proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/http/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/Proxy-List/main/HTTP.txt", "regex"),
        ("https://raw.githubusercontent.com/mzyui/proxy-list/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_http.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-http.txt", "regex"),
        ("https://raw.githubusercontent.com/b4mbo-o/Check-Free-Proxy/main/alive_http.txt", "regex"),
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/RioMMO/ProxyFree/main/HTTP.txt", "regex"),
        ("https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/http-proxy-list-by-EbraSha.txt", "regex"),
        # v2.3'te eklenen (protokol-spesifik dosya adları olanlar; agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/http.txt", "regex"),
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/http.txt", "regex"),
        # KALDIRILDI: proxyscan.io (servis kapatıldı), httptunnel.ge (ölü),
        # KALDIRILDI: proxylists.net (kararsız), saschazesiger + UptimerBot (GitHub TOS bloğu),
        # KALDIRILDI: officialputuid/KangProxy (repo silindi)
        # EKLENMEDİ: themiralay/data.txt, theriturajps/proxies.txt, openproxyhub/all_proxies.txt,
        #            notfaj/ester/proxies.txt, hendrikbgr/proxy_list.txt, Durgaa17/cf-sg-proxies,
        #            gitrecon1455/proxylist.txt — protokol-spesifik olmayan karışık içerikli dosyalar.
    ],
    "https": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/https.txt", "regex"),
        ("https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/arunsakthivel96/proxyBEE/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt", "regex"),
        ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt", "regex"),
        ("https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt", "regex"),
        ("https://raw.githubusercontent.com/RX4096/proxy-list/main/online/https.txt", "regex"),
        ("https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt", "regex"),
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=https", "regex"),
        ("https://proxyspace.pro/https.txt", "regex"),
        ("https://raw.githubusercontent.com/rx443/proxy-list/main/online/https.txt", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=https&country=all&ssl=all&anonymity=all", "regex"),
        ("https://www.google-proxy.net/", "regex"),
        ("https://www.sslproxies.org/", "regex"),
        ("https://www.ipaddress.com/proxy-list/", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt", "regex"),
        ("https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt", "regex"),
        ("https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/shiftytr/proxy-list/master/https.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/vmheaven/VMHeaven.io-Free-Proxy-List/main/https.txt", "regex"),
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt", "regex"),
        ("https://raw.githubusercontent.com/Mohammedcha/ProxRipper/main/full_proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/https/https.txt", "regex"),
        ("https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/https-proxy-list-by-EbraSha.txt", "regex"),
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt", "regex"),
        # KALDIRILDI: api.foxtools.ru/v2/Proxy.txt (ölü), proxyscan.io, httptunnel.ge,
        # KALDIRILDI: saschazesiger + UptimerBot (GitHub TOS bloğu), officialputuid/KangProxy (repo silindi)
    ],
    "socks4": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt", "regex"),
        ("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt", "regex"),
        # Eski betikte 'socsk4' yazılmıştı; düzeltildi.
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=socks4", "regex"),
        ("https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&country=all&ssl=all&anonymity=all", "regex"),
        ("https://spys.me/proxy.txt", "regex"),
        ("https://www.socks-proxy.net/", "regex"),
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/vmheaven/VMHeaven.io-Free-Proxy-List/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks4_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/Mohammedcha/ProxRipper/main/full_proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks4/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/Proxy-List/main/SOCKS4.txt", "regex"),
        ("https://raw.githubusercontent.com/mzyui/proxy-list/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/b4mbo-o/Check-Free-Proxy/main/alive_socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/RioMMO/ProxyFree/main/SOCKS4.txt", "regex"),
        ("https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/socks4-proxy-list-by-EbraSha.txt", "regex"),
        ("https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt", "regex"),
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/socks4.txt", "regex"),
        # KALDIRILDI: saschazesiger + UptimerBot (TOS bloğu), KangProxy (repo silindi)
    ],
    "socks5": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt", "regex"),
        ("https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt", "regex"),
        # Eski betikte 'socsk5' yazılmıştı; düzeltildi.
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=socks5", "regex"),
        ("https://proxyspace.pro/socks5.txt", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&country=all&ssl=all&anonymity=all", "regex"),
        ("https://spys.me/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/vmheaven/VMHeaven.io-Free-Proxy-List/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks5_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/Mohammedcha/ProxRipper/main/full_proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks5/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/Proxy-List/main/SOCKS5.txt", "regex"),
        ("https://raw.githubusercontent.com/mzyui/proxy-list/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/b4mbo-o/Check-Free-Proxy/main/alive_socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/RioMMO/ProxyFree/main/SOCKS5.txt", "regex"),
        ("https://raw.githubusercontent.com/openproxyhub/proxy-exports/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/socks5-proxy-list-by-EbraSha.txt", "regex"),
        ("https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt", "regex"),
        # v2.4'te eklenen (CN/RU araştırması — tek bulgu: Çinli geliştirici, "国内可用" focus):
        ("https://raw.githubusercontent.com/HankNovic/ProxyClean/main/SOCKS5_RAW.txt", "regex"),
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/socks5.txt", "regex"),
        # KALDIRILDI: saschazesiger + UptimerBot (TOS bloğu), KangProxy (repo silindi)
    ],
}
