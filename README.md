<p align="right">
<sub>
<b>🇹🇷 Türkçe</b> ·
<a href="README.en.md">🇬🇧 English</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

Açık kaynak proxy listesi toplayıcı. Tek bir komutla onlarca farklı kaynaktan
**HTTP / HTTPS / SOCKS4 / SOCKS5** proxy adresini paralel olarak çeker, eskimiş
kaynakları otomatik eler, yinelenenleri ayıklar ve sıralı, doğrulanmış
`IP:PORT` listesi üretir.

<p align="center">
<b>86 benzersiz kaynak</b> · <b>220 uç nokta</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine bir aggregator'dır, kalite testçisi değil. Çalışan ve gerçekten elite
> seviyeli proxy'ler için çıktıyı
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler) gibi bir
> test aracına borulayın.

------------------------------------------------------------

## Özellikler

- **86 farklı kaynak**, 220 uç nokta — GitHub raw listeler + 8 dinamik
  API/HTML kaynağı.
- **Paralel HTTP** ile çekim; varsayılan kaynaklara nazik (`-c 1`), istenirse
  `-c 20`+ ile 10× hız.
- **Kaynak başına timeout + retry** — yavaş bir host tüm işi tıkamaz.
- **Tazelik takibi.** Her kaynağın son güncellenme zamanı raporlanır; GitHub
  kaynakları için commit zamanı API'den çözülür. `-F SECONDS` ile yaşlı
  kaynaklar otomatik elenir (varsayılan 24 saat).
- **Sıkı doğrulama.** IPv4 oktet (0–255) ve port (1–65535) regex'le süzülür.
- **Akıllı çıktı.** Progress bar TTY'de, dosya/pipe'da sessiz; ASCII tablo
  raporları; `-s` ile tamamen sessiz mod; `-o` ile dosyaya yazma.
- **Sıfır bağımlılık.** Yalnızca Python ≥ 3.10 stdlib.

------------------------------------------------------------

## Kurulum

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

Gereksinim: **Python ≥ 3.10**. İsteğe bağlı: `gh` CLI veya GitHub personal
access token (kaynak yaşlarını çözmek için — aşağıya bkz.).

------------------------------------------------------------

## Kullanım

```bash
./proxine.py -p <http|https|socks4|socks5> [seçenekler]
```

### Bayraklar

| Uzun | Kısa | Varsayılan | Açıklama |
|---|---|---|---|
| `--protocol` | `-p` | — | **Zorunlu.** Toplanacak protokol: `http`, `https`, `socks4`, `socks5`. |
| `--format` | `-f` | `ip-port` | Çıktı biçimi. `url` seçilirse `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | Kaynak başına HTTP timeout (saniye). |
| `--concurrency` | `-c` | `1` | Eşzamanlı istek sayısı. Yüksek değer = daha hızlı, daha çok soket. |
| `--retries` | `-r` | `2` | Başarısız kaynak başına tekrar deneme sayısı. |
| `--max-ports` | `-m` | `5` | Bir IP bu kadardan fazla farklı portla görünürse tamamen at (port-scanner/honeypot eleme). `0` = devre dışı. |
| `--fresh` | `-F` | `86400` | Bundan eski kaynaklar çıktıya katılmaz (saniye). `0` = filtre kapalı. |
| `--github-token` | `-g` | — | GitHub PAT. Yoksa `$GITHUB_TOKEN`, o da yoksa `gh auth token` denenir. |
| `--output` | `-o` | — | Proxy listesini bu dosyaya yaz; stdout boş kalır. |
| `--lang` | `-L` | otomatik | Arayüz dili: `tr`, `en`, `de`, `es`, `ru`, `zh`. Yoksa `$PROXINE_LANG`/`$LANG`/locale'den algılanır. |
| `--strict-ports` / `--no-strict-ports` | — | açık | Beyan edilen protokol ailesine uymayan portlardaki proxy'leri at (örn. SOCKS olarak listelenmiş port 80 atılır). |
| `--silent` | `-s` | — | Tüm stderr çıktısını sustur. |

### Örnekler

```bash
# Stdout'a HTTPS proxy listesi (varsayılan tazelik filtresi 24h)
./proxine.py -p https

# SOCKS5 listesini dosyaya yaz, hızı artır
./proxine.py -p socks5 -c 32 -o socks5.lst

# Sadece son 1 saatte güncellenen kaynakları kullan
./proxine.py -p http -F 3600

# URL biçiminde çıktı: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# Sessiz mod — boru hattı için ideal
./proxine.py -p http -s | grep '^192\.'

# Proxy Profiler ile zincirleme — 3 örnek
# 1) Elite (L1) anonim HTTP'leri çıkar
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — judge'ı atla (hızlı), sadece Cloudflare WAF bypass eden canlı proxy'leri al
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + ülke filtresi (US/DE/JP) + Google erişim testi
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
```

### GitHub token (opsiyonel ama önerilir)

GitHub raw URL'leri `Last-Modified` döndürmediği için kaynak yaşları GitHub
API'sinden çözülür. API'nin **anonim limiti 60 istek/saat**, tek bir çalışmada
50+ GitHub kaynağına bakıldığından token vermeden çoğu yaş "live" görünür.
Token verirseniz limit **5.000 istek/saat**'e çıkar — `repo` izni gerekmez,
public read yeterlidir.

Üç yol — biri varsa Proxine otomatik bulur:

```bash
# 1) Açık parametre
./proxine.py -p socks5 -g ghp_xxx

# 2) Env değişkeni
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) Hiçbir şey yapmayın — `gh` CLI yüklü ve giriş yapılmışsa
./proxine.py -p socks5
```

Token rate-limit'e takılır veya geçersizse rapor sonunda açık uyarı görürsünüz.

------------------------------------------------------------

## Çıktı

### 1. İlerleme çubuğu

Çalışma sırasında stderr'e iki fazlı bir yüzde çubuğu yazılır:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20 karakter `█/░` çubuğu, yüzde, tamamlanan/toplam sayım
- Faz etiketi: `fetching` (HTTP fetch) ya da `enriching` (GitHub commit API)
- `✓` başarı, `x` hata
- `+N` o kaynaktan gelen yeni proxy sayısı
- `total N` birikmiş benzersiz toplam

TTY dışında otomatik sessiz olur (dosya/pipe yönlendirmesini bozmaz).

### 2. Kaynak durum tablosu

Çalışma sonunda stderr'e:

```
┌────────┬──────┬─────────┬─────────────────────────────────────────────────┐
│ STATUS │  AGE │ PROXIES │ SOURCE                                          │
├────────┼──────┼─────────┼─────────────────────────────────────────────────┤
│ OK     │  26s │  24,769 │ github.com/ebrasha/abdal-proxy-hub              │
│ OK     │  88s │   9,322 │ api.proxyscrape.com                             │
│ ...                                                                       │
│ LIVE   │    — │       2 │ pubproxy.com                                    │
│ STALE  │  47w │  89,708 │ github.com/MuRongPIG/Proxy-Master               │
│ FAIL   │    — │       — │ www.socks-proxy.net                             │
└────────┴──────┴─────────┴─────────────────────────────────────────────────┘
  OK     `--fresh` penceresi içinde güncellenmiş; proxy'leri kullanıldı
  LIVE   yaş bilgisi yok (dinamik API); proxy'leri kullanıldı
  STALE  `--fresh` eşiğinden eski; proxy'leri çıktıdan düşürüldü
  FAIL   çekme hatası; katkı yok
```

Sıralama: OK (en taze üstte) → LIVE → STALE → FAIL.

### 3. Özet kutusu

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### Çıktı modu tablosu

| Komut | stdout | stderr |
|---|---|---|
| `proxine -p http` | proxy listesi | satır satır log + progress → durum tablosu → özet |
| `proxine -p http -o f.lst` | (boş) | satır satır log + progress → tablolar |
| `proxine -p http -s` | proxy listesi | (boş) |
| `proxine -p http -o f.lst -s` | (boş) | (boş) |

------------------------------------------------------------

## Kaynaklar

Toplam **86 benzersiz kaynak**, **220 protokol uç noktası**. Hepsi
`sources.py` içinde tanımlıdır; yeni bir kaynak eklemek tek satır
değişiklik gerektirir.

### GitHub raw listeleri (77 repo)

| Repo | Protokoller |
|---|---|
| `abusaeeidx/TazaProxy-Troxy` | https |
| `adasd223/global-proxy-list` | socks5 |
| `ahahaabas/anonymous-proxy-list-free` | http, socks4, socks5 |
| `ahahaabas/global-proxy-list` | socks5 |
| `ALIILAPRO/Proxy` | http, socks4, socks5 |
| `alphaa1111/proxyscraper` | http, socks4, socks5 |
| `Anonym0usWork1221/Free-Proxies` | http, https, socks5 |
| `anutmagang/Free-HighQuality-Proxy-Socks` | http |
| `Argh94/Proxy-List` | http, socks4 |
| `Argh94/ProxyProwler` | socks4, socks5 |
| `arunsakthivel96/proxyBEE` | http, https |
| `b4mbo-o/Check-Free-Proxy` | socks4 |
| `berkay-digital/Proxy-Scraper` | http |
| `CB-X2-Jun/proxy-lists` | http, https, socks4, socks5 |
| `Cheagjihvg/simple-proxylist` | http, https, socks4, socks5 |
| `claude89757/free_https_proxies` | https |
| `databay-labs/free-proxy-list` | http, socks4, socks5 |
| `dpangestuw/Free-Proxy` | http |
| `elliottophellia/yakumo` | socks4, socks5 |
| `ErcinDedeoglu/proxies` | https |
| `fate0/proxylist` | http, https |
| `Firmfox/Proxify` | socks5 |
| `gitrecon1455/fresh-proxy-list` | https, socks4, socks5 |
| `HankNovic/ProxyClean` | socks5 |
| `hookzof/socks5_list` | socks5 |
| `i-am-unbekannt/BLITZPROXY` | http, socks4, socks5 |
| `iplocate/free-proxy-list` | http, https, socks4 |
| `IPParrot/proxy_ips` | http, https, socks4, socks5 |
| `ItzRazvyy/ProxyList` | http, https, socks4, socks5 |
| `jetkai/proxy-list` | http, https, socks4, socks5 |
| `LoneKingCode/free-proxy-db` | http, https, socks4 |
| `mauricegift/free-proxies` | http, https, socks5 |
| `mertguvencli/http-proxy-list` | http, https |
| `MohammadKobirShah/ProxyScraper-Pro` | http, socks4, socks5 |
| `monosans/proxy-list` | http, https, socks4, socks5 |
| `MrMarble/proxy-list` | https |
| `Munachukwuw/Best-Free-Proxys` | http, socks4, socks5 |
| `mzyui/proxy-list` | http |
| `naravid19/checked-proxies` | http, socks4, socks5 |
| `NikolaiT/free-proxy-list` | http, https, socks4, socks5 |
| `noctiro/getproxy` | socks4 |
| `officialputuid/ProxyForEveryone` | http, socks4, socks5 |
| `openproxyhub/proxy-exports` | socks5 |
| `parserpp/ip_ports` | http, https |
| `proxifly/free-proxy-list` | http, https, socks4, socks5 |
| `proxygenerator1/ProxyGenerator` | http, https, socks4, socks5 |
| `prxchk/proxy-list` | http, socks4, socks5 |
| `r00tee/Proxy-List` | https, socks4 |
| `rdavydov/proxy-list` | http, socks4, socks5 |
| `RioMMO/ProxyFree` | http |
| `roosterkid/openproxylist` | https, socks4, socks5 |
| `RX4096/proxy-list` | http, https |
| `rx443/proxy-list` | http, https |
| `saisuiu/uiu` | http |
| `Seeh-Saah/awesome-free-proxy-list` | http, socks4, socks5 |
| `SevenworksDev/proxy-list` | https, socks4 |
| `shiftytr/proxy-list` | https |
| `shubhamshendre/Free-Proxies` | http |
| `shulganovo/Proxylists` | socks5 |
| `Skillter/ProxyGather` | http, socks4, socks5 |
| `SoliSpirit/proxy-list` | socks4 |
| `stamparm/aux` | http |
| `sunny9577/proxy-scraper` | http, https |
| `themiralay/Proxy-List-World` | http |
| `theriturajps/proxy-list` | https, socks4, socks5 |
| `TheSpeedX/PROXY-List` | http, socks4, socks5 |
| `Thordata/awesome-free-proxy-list` | http, socks4, socks5 |
| `Tsprnay/Proxy-lists` | http, https, socks4, socks5 |
| `TuanMinPay/live-proxy` | https |
| `vakhov/fresh-proxy-list` | https, socks4, socks5 |
| `Vann-Dev/proxy-list` | socks4, socks5 |
| `VPSLabCloud/VPSLab-Free-Proxy-List` | http, https, socks4, socks5 |
| `watchttvv/free-proxy-list` | http, https |
| `yemixzy/free-proxy-list` | http, socks4, socks5 |
| `Zaeem20/FREE_PROXIES_LIST` | http, https, socks4, socks5 |
| `zevtyardt/proxy-list` | socks4, socks5 |
| `zloi-user/hideip.me` | http, https, socks4, socks5 |

### GitLab listeleri (1 repo)

| Repo | Protokoller |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### Dinamik API ve HTML kaynakları (8 endpoint)

| Endpoint | Tür | Protokoller |
|---|---|---|
| `api.proxyscrape.com` | Açık API | http, https, socks4, socks5 |
| `free-proxy-list.net` | HTML scraper | http |
| `proxyspace.pro` | Düz metin liste | https, socks5 |
| `pubproxy.com` | Açık API | http, https, socks4, socks5 |
| `www.google-proxy.net` | HTML scraper | http, https |
| `www.ipaddress.com` | HTML scraper | http, https |
| `www.socks-proxy.net` | HTML scraper | socks4 |
| `www.sslproxies.org` | HTML scraper | https |

------------------------------------------------------------

## Otomatikleştirme

Proxine tek seferlik çalıştırma için tasarlanmıştır; düzenli güncelleme için
cron / systemd-timer / GitHub Actions ile sarmalayın. Boru hattına girecekse
`-s` ve `-o` önerilir:

```bash
# Cron: her saat başı socks5 listesini güncelle
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# Her gece elite HTTP listesi (proxine + profiler zinciri)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst
```

------------------------------------------------------------

## İlgili araçlar

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** — proxy
  listesini canlılık, anonimlik (Elite/Anonymous/Transparent), CloudFlare ve
  Google geçişi açısından çoklu iş parçacığıyla test eder.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — Windows için
  GUI tabanlı periyodik proxy değiştirici.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  Windows için liste doğrulayıcı.

------------------------------------------------------------

## Lisans

Açık kaynaktır. Yeniden dağıtabilir, değiştirebilir, ticari ya da özel olarak
kullanabilirsiniz. Türev çalışmalarda orijinal yazar (Özgür Koca) atıfını
koruyun. Yazılım "olduğu gibi" sunulur; kullanım riski tamamen kullanıcıya
aittir.

## Yazar

**Özgür Koca** — meslek lisesinde
[öğretmenlik](https://samsuneml.meb.k12.tr/) yapıyor.
GitHub: [enseitankado](https://github.com/enseitankado) · Blog:
[tankado.com](https://www.tankado.com)

## Destek

Beğendiyseniz ⭐ verin; bir kahve ısmarlamak isterseniz
[buyrun](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
