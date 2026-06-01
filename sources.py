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
        # Audit 2026-05: proxy4parsing http → STALE (push 2024-04), %100 MuRongPIG/ErcinDedeoglu içinde. Çıkarıldı.
        ("https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/arunsakthivel96/proxyBEE/master/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt", "regex"),
        # NOT: eski URL /blob/ döndüğü için HTML alıyorduk; raw varyantına çevrildi.
        ("https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt", "regex"),
        # Audit 2026-05: MuRongPIG http → aggregator (proxy4parsing/jetkai %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt", "regex"),
        ("https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt", "regex"),
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=http", "regex"),
        # Audit 2026-05: proxyspace.pro http → aggregator (TheSpeedX/monosans/mmpx12 %100 dahil). Çıkarıldı.
        ("https://www.ipaddress.com/proxy-list/", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=http&country=all&ssl=all&anonymity=all", "regex"),
        ("https://free-proxy-list.net/anonymous-proxy.html", "regex"),
        ("https://www.google-proxy.net/", "regex"),
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/http.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "regex"),
        # Audit 2026-05: zevtyardt http → aggregator (jetkai/b4mbo-o/vakhov %95-100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/stamparm/aux/master/fetch-some-list.txt", "stamparm"),
        ("https://raw.githubusercontent.com/rx443/proxy-list/main/online/http.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt", "regex"),
        # Audit 2026-05: vakhov http → %99 proxifly içinde. Çıkarıldı.
        # Audit 2026-05: mmpx12 http → %100 proxifly içinde. Çıkarıldı.
        # Audit 2026-05: ErcinDedeoglu http → aggregator (TheSpeedX/zevtyardt/monosans %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt", "regex"),
        # Audit 2026-05: elliottophellia http → %100 monosans ile aynı (cluster sim=100%). Çıkarıldı.
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt", "regex"),
        # Audit 2026-05: vmheaven http → aggregator (arunsakthivel96/monosans/zloi-user %86-94 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/http_proxies.txt", "regex"),
        # Audit 2026-05: Mohammedcha http → mega-aggregator (29 source %85-100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/http/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/Proxy-List/main/HTTP.txt", "regex"),
        ("https://raw.githubusercontent.com/mzyui/proxy-list/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_http.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-http.txt", "regex"),
        # Audit 2026-05: b4mbo-o http → %95 TheSpeedX içinde (20 entry'lik küçük subset). Çıkarıldı.
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/RioMMO/ProxyFree/main/HTTP.txt", "regex"),
        # Audit 2026-05: ebrasha http → aggregator (monosans/jetkai/mmpx12/vakhov/elliotto %100 dahil). Çıkarıldı.
        # v2.3'te eklenen (protokol-spesifik dosya adları olanlar; agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt", "regex"),
        # Audit 2026-05: komutan234 http → aggregator (TheSpeedX %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/http.txt", "regex"),
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/http.txt", "regex"),
        # v2.5'te eklenen (2026-05-31 araştırması, Jaccard sim < %50, n >= 20):
        ("https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/Munachukwuw/Best-Free-Proxys/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_all.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_nossl.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_transparent.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_anonymous.txt", "regex"),
        ("https://raw.githubusercontent.com/naravid19/checked-proxies/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/berkay-digital/Proxy-Scraper/main/proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/alphaa1111/proxyscraper/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/http.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/http.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/http.txt", "regex"),
        ("https://raw.githubusercontent.com/shubhamshendre/Free-Proxies/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/i-am-unbekannt/BLITZPROXY/main/out-files/http.txt", "regex"),
        ("https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt", "regex"),
        ("https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt", "regex"),
        ("https://raw.githubusercontent.com/IPParrot/proxy_ips/main/proxies/http.txt", "regex"),
        # v2.6'da eklenen (2026-06-01 CN/non-Western araştırması, Jaccard sim < %50):
        ("https://raw.githubusercontent.com/Cheagjihvg/simple-proxylist/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/http.txt", "regex"),
        ("https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/all.txt", "regex"),
        ("https://raw.githubusercontent.com/mauricegift/free-proxies/main/files/http.json", "regex"),
        ("https://raw.githubusercontent.com/CB-X2-Jun/proxy-lists/main/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/NikolaiT/free-proxy-list/main/proxies/http_working.txt", "regex"),
        ("https://raw.githubusercontent.com/parserpp/ip_ports/main/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/parserpp/ip_ports/main/proxy.list.out", "ndjson"),
        ("https://raw.githubusercontent.com/watchttvv/free-proxy-list/main/proxy.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/google.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/twitter.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/discord.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/facebook.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/instagram.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/tiktok.txt", "regex"),
        ("https://gitlab.com/syedusama5556/auto-proxy-list-generator/-/raw/main/proxies/http-tested/microsoft.txt", "regex"),
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
        # Audit 2026-05: mmpx12 https → küçük (192 entry), aggregator'larda %100. Çıkarıldı.
        ("https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/shiftytr/proxy-list/master/https.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        # Audit 2026-05: vmheaven https → aggregator (monosans %92 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt", "regex"),
        # Audit 2026-05: Mohammedcha https → mega-aggregator (10 source %91-100 dahil). Çıkarıldı.
        # Audit 2026-05: officialputuid https → %98 r00tee ile aynı (cluster). Çıkarıldı.
        # Audit 2026-05: ebrasha https → aggregator (vakhov/shiftytr/mmpx12/r00tee %100 dahil). Çıkarıldı.
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt", "regex"),
        # v2.5'te eklenen (2026-05-31 araştırması, Jaccard sim < %50, n >= 20):
        ("https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_ssl.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_ssl_elite.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl_elite.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl_anonymous.txt", "regex"),
        ("https://raw.githubusercontent.com/MrMarble/proxy-list/main/all.txt", "regex"),
        ("https://raw.githubusercontent.com/abusaeeidx/TazaProxy-Troxy/main/working_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/IPParrot/proxy_ips/main/proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/https.txt", "regex"),
        ("https://raw.githubusercontent.com/claude89757/free_https_proxies/main/isz_https_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/claude89757/free_https_proxies/main/https_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/https.txt", "regex"),
        # v2.6'da eklenen (2026-06-01 CN/non-Western araştırması, Jaccard sim < %50):
        ("https://raw.githubusercontent.com/gitrecon1455/fresh-proxy-list/main/proxylist.txt", "regex"),
        ("https://raw.githubusercontent.com/Cheagjihvg/simple-proxylist/main/http.txt", "regex"),
        ("https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/all.txt", "regex"),
        ("https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/https.txt", "regex"),
        ("https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/all.txt", "regex"),
        ("https://raw.githubusercontent.com/mauricegift/free-proxies/main/files/http.json", "regex"),
        ("https://raw.githubusercontent.com/CB-X2-Jun/proxy-lists/main/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/NikolaiT/free-proxy-list/main/proxies/https_working.txt", "regex"),
        ("https://raw.githubusercontent.com/parserpp/ip_ports/main/proxy.list", "ndjson"),
        ("https://raw.githubusercontent.com/watchttvv/free-proxy-list/main/proxy.txt", "regex"),
        # KALDIRILDI: api.foxtools.ru/v2/Proxy.txt (ölü), proxyscan.io, httptunnel.ge,
        # KALDIRILDI: saschazesiger + UptimerBot (GitHub TOS bloğu), officialputuid/KangProxy (repo silindi)
    ],
    "socks4": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt", "regex"),
        # Audit 2026-05: MuRongPIG socks4 → match %6 (HTTP listesi olarak çıktı). Çıkarıldı.
        # Eski betikte 'socsk4' yazılmıştı; düzeltildi.
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=socks4", "regex"),
        # Audit 2026-05: saisuiu/free.txt socks4 → match %2 (HTTP listesi). Çıkarıldı.
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&country=all&ssl=all&anonymity=all", "regex"),
        # Audit 2026-05: spys.me/proxy.txt → karışık liste, match %0 SOCKS4. Çıkarıldı.
        ("https://www.socks-proxy.net/", "regex"),
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt", "regex"),
        # Audit 2026-05: mmpx12 socks4 → %100 birçok aggregator'da. Çıkarıldı.
        # Audit 2026-05: ErcinDedeoglu socks4 → mega-aggregator (13 kaynak %85-100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt", "regex"),
        # Audit 2026-05: Anonym0usWork1221 socks4 → aggregator (10 kaynak %85-100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt", "regex"),
        # Audit 2026-05: vmheaven socks4 → aggregator (Skillter/Vann-Dev/proxyscrape %87-97 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt", "regex"),
        # Audit 2026-05: dpangestuw socks4 → aggregator (mmpx12/TheSpeedX/roosterkid %100 dahil). Çıkarıldı.
        # Audit 2026-05: Mohammedcha socks4 → match %6 (HTTP listesi olarak çıktı). Çıkarıldı.
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks4/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/Proxy-List/main/SOCKS4.txt", "regex"),
        # Audit 2026-05: mzyui socks4 → zevtyardt ile birebir aynı (5593 entry, identical SUBSET map). Çıkarıldı.
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/b4mbo-o/Check-Free-Proxy/main/alive_socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks4.txt", "regex"),
        # Audit 2026-05: RioMMO SOCKS4 → match %5 (HTTP listesi). Çıkarıldı.
        # Audit 2026-05: ebrasha socks4 → aggregator (mmpx12/roosterkid/r00tee/proxifly %96-100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt", "regex"),
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks4.txt", "regex"),
        # Audit 2026-05: komutan234 socks4 → aggregator (mmpx12/TheSpeedX %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/socks4.txt", "regex"),
        # v2.5'te eklenen (2026-05-31 araştırması, Jaccard sim < %50, n >= 20):
        ("https://raw.githubusercontent.com/noctiro/getproxy/master/file/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks4_all.txt", "regex"),
        ("https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/naravid19/checked-proxies/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Munachukwuw/Best-Free-Proxys/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/i-am-unbekannt/BLITZPROXY/main/out-files/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/IPParrot/proxy_ips/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/alphaa1111/proxyscraper/main/proxies/socks.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/ProxyProwler/main/proxy_output/SOCKS4.txt", "regex"),
        # v2.6'da eklenen (2026-06-01 CN/non-Western araştırması, Jaccard sim < %50):
        ("https://raw.githubusercontent.com/gitrecon1455/fresh-proxy-list/main/proxylist.txt", "regex"),
        ("https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/Cheagjihvg/simple-proxylist/main/socks4.txt", "regex"),
        ("https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/CB-X2-Jun/proxy-lists/main/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/NikolaiT/free-proxy-list/main/proxies/socks4_working.txt", "regex"),
        ("https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/socks4.txt", "regex"),
        # KALDIRILDI: saschazesiger + UptimerBot (TOS bloğu), KangProxy (repo silindi)
    ],
    "socks5": [
        ("https://raw.githubusercontent.com/ItzRazvyy/ProxyList/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt", "regex"),
        ("https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt", "regex"),
        # Audit 2026-05: MuRongPIG socks5 → match %5 (HTTP listesi olarak çıktı). Çıkarıldı.
        # Eski betikte 'socsk5' yazılmıştı; düzeltildi.
        ("http://pubproxy.com/api/proxy?limit=100&format=txt&type=socks5", "regex"),
        ("https://proxyspace.pro/socks5.txt", "regex"),
        ("https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&country=all&ssl=all&anonymity=all", "regex"),
        # Audit 2026-05: spys.me/proxy.txt → karışık liste, match %0 SOCKS5. Çıkarıldı.
        ("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies_anonymous/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt", "regex"),
        # v2.1'de eklenen aktif GitHub kaynakları:
        ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt", "regex"),
        ("https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt", "regex"),
        # Audit 2026-05: mmpx12 socks5 → %100 TheSpeedX'in altkümesi (kopya). Çıkarıldı.
        # Audit 2026-05: ErcinDedeoglu socks5 → aggregator (mmpx12/TheSpeedX/mzyui %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt", "regex"),
        # v2.2'de eklenen (GitHub araştırması; hepsi 2026-05-22 commit'i):
        ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt", "regex"),
        # Audit 2026-05: vmheaven socks5 → aggregator (elliottophellia/Skillter/zloi-user vs. %87-100). Çıkarıldı.
        ("https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt", "regex"),
        # Audit 2026-05: dpangestuw socks5 → aggregator (TheSpeedX/mmpx12 vs. %85-100). Çıkarıldı.
        # Audit 2026-05: Mohammedcha socks5 → match %5 (HTTP listesi olarak çıktı). Çıkarıldı.
        ("https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks5/socks5.txt", "regex"),
        # Audit 2026-05: Argh94 socks5 → %92 TheSpeedX'in altkümesi. Çıkarıldı.
        # Audit 2026-05: mzyui socks5 → %100 aggregator'larda var, TheSpeedX türevi. Çıkarıldı.
        ("https://raw.githubusercontent.com/MohammadKobirShah/ProxyScraper-Pro/main/output/proxies_socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks5.txt", "regex"),
        # Audit 2026-05: b4mbo-o socks5 → %92 TheSpeedX'in altkümesi. Çıkarıldı.
        ("https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks5.txt", "regex"),
        # Audit 2026-05: RioMMO SOCKS5 → match %5 (HTTP listesi). Çıkarıldı.
        ("https://raw.githubusercontent.com/openproxyhub/proxy-exports/main/socks5.txt", "regex"),
        # Audit 2026-05: ebrasha socks5 → match %6 (büyük çoğunluk HTTP portu). Çıkarıldı.
        ("https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt", "regex"),
        # v2.4'te eklenen (CN/RU araştırması — tek bulgu: Çinli geliştirici, "国内可用" focus):
        ("https://raw.githubusercontent.com/HankNovic/ProxyClean/main/SOCKS5_RAW.txt", "regex"),
        # v2.3'te eklenen (agent araştırması):
        ("https://raw.githubusercontent.com/ahahaabas/anonymous-proxy-list-free/main/socks5.txt", "regex"),
        # Audit 2026-05: r00tee Socks5 → match %6 (HTTP listesi). Çıkarıldı.
        ("https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks5.txt", "regex"),
        # Audit 2026-05: komutan234 socks5 → aggregator (mmpx12/TheSpeedX %100 dahil). Çıkarıldı.
        ("https://raw.githubusercontent.com/yemixzy/free-proxy-list/main/proxies/socks5.txt", "regex"),
        # v2.5'te eklenen (2026-05-31 araştırması, Jaccard sim < %50, n >= 20):
        ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks5_all.txt", "regex"),
        ("https://raw.githubusercontent.com/naravid19/checked-proxies/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/alphaa1111/proxyscraper/main/proxies/socks.txt", "regex"),
        ("https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/i-am-unbekannt/BLITZPROXY/main/out-files/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Munachukwuw/Best-Free-Proxys/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/IPParrot/proxy_ips/main/proxies/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/adasd223/global-proxy-list/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/ahahaabas/global-proxy-list/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/Argh94/ProxyProwler/main/proxy_output/SOCKS5.txt", "regex"),
        # v2.6'da eklenen (2026-06-01 CN/non-Western araştırması, Jaccard sim < %50):
        ("https://raw.githubusercontent.com/gitrecon1455/fresh-proxy-list/main/proxylist.txt", "regex"),
        ("https://raw.githubusercontent.com/Cheagjihvg/simple-proxylist/main/socks5.txt", "regex"),
        ("https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/NikolaiT/free-proxy-list/main/proxies/socks5_working.txt", "regex"),
        ("https://raw.githubusercontent.com/CB-X2-Jun/proxy-lists/main/proxy.txt", "regex"),
        ("https://raw.githubusercontent.com/shulganovo/Proxylists/main/proxies.txt", "regex"),
        ("https://raw.githubusercontent.com/mauricegift/free-proxies/main/files/socks5.json", "regex"),
        # KALDIRILDI: saschazesiger + UptimerBot (TOS bloğu), KangProxy (repo silindi)
    ],
}
