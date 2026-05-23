# 🚀 Proxine — Açık kaynak proxy toplayıcı (v2.3, Python)

**Proxine**, **165+ açık kaynaktan** HTTP / HTTPS / SOCKS4 / SOCKS5 proxy
listelerini **paralel** olarak çeker, kaynak başına tazelik bilgisi toplar,
eskimiş kaynakları otomatik düşürür, sıkı IPv4+port doğrulamasıyla filtreler
ve **benzersiz**, sıralı `IP:PORT` listesi olarak yazar.

Tek başına bir **kalite süzgeci** değildir — çıktıyı
[Proxy Profiler](https://github.com/enseitankado/proxy-profiler) gibi bir test
aracına borulayarak yalnızca **Elite (Level-1)** ve çalışan proxy'leri elde
edebilirsiniz.

------------------------------------------------------------

## Yenilikler

- **Kaynaklar veri oldu** (`sources.py`): yeni kaynak = 1 satır.
- **Paralel HTTP fetch** (`ThreadPoolExecutor`). Default'ta `-c 1` (kaynaklara
  nazik); `-c 20` veya üstüyle ~10× hız.
- **Timeout + retry** her kaynak için (`-t` / `-r`).
- **Tazelik raporu + filtre.** `raw.githubusercontent.com` için son commit
  zamanı GitHub API'den çekilir (`-g` / `$GITHUB_TOKEN` / `gh auth token`).
  `-F/--fresh` ile eskimiş kaynaklar otomatik elenir (default 24h).
- **Çok fazlı progress bar.** TTY'de yatay yüzde çubuğu (`fetching` +
  `enriching`); pipe/dosyada sessiz.
- **Dikdörtgen tablo raporları.** Kaynak durum tablosu + summary kutusu.
- **Rate-limit ve geçersiz token uyarıları.** Çalışma sonunda açıkça raporlanır.
- **Tek parser modülü** (`regex`, `ndjson`, `stamparm`, `geonode`).
- **Sıkı IPv4+port doğrulaması** (0–255 oktet, 1–65535 port).
- **165+ aktif kaynak**: http 51, https 29, socks4 42, socks5 43.

Çıktı sözleşmesi: stdout veya `-o FILE`'a tek tek `IP:PORT` satırları.

------------------------------------------------------------

## Gereksinimler

- Python ≥ 3.10 (stdlib-only, ek bağımlılık yok)
- (Opsiyonel) `gh` CLI veya GitHub PAT — GitHub kaynakların yaşını çözmek için

------------------------------------------------------------

## Kullanım

```bash
./proxine.py <http|https|socks4|socks5> [options]
# veya
python3 proxine.py <http|https|socks4|socks5> [options]
```

Tüm seçenekler ve örnek komutlar için:

```bash
./proxine.py --help
```

### Bayraklar

| Uzun | Kısa | Default | İşlev |
|---|---|---|---|
| `--format` | `-f` | `ip-port` | Çıktı biçimi: `ip-port` veya `url` (`<proto>://IP:PORT`) |
| `--timeout` | `-t` | `15` | Kaynak başına HTTP timeout (s) |
| `--concurrency` | `-c` | `1` | Eşzamanlı istek sayısı (kaynaklara nazik olmak için sıralı; `-c 20` ile hızlandırılabilir) |
| `--retries` | `-r` | `2` | Hatada tekrar deneme |
| `--fresh` | `-F` | `86400` | Bundan eski kaynaklar STALE damgalanıp çıktıdan düşürülür (s). `0` = filtre kapalı |
| `--github-token` | `-g` | — | GitHub PAT — kaynakların yaşını çözmek için. Yoksa `$GITHUB_TOKEN` → `gh auth token` |
| `--output` | `-o` | — | Proxy listesini dosyaya yaz; stdout boş kalır |
| `--verbose` | `-v` | — | Kaynak başına satır satır log (progress bar yerine) |
| `--silent` | `-s` | — | Tüm stderr çıktısını sustur; sadece liste |

### Hızlı örnekler

```bash
./proxine.py https > https_proxies.lst
./proxine.py socks5 -f url -c 32 -v                   # url biçim, 32 paralel, verbose
./proxine.py http -t 5 -r 0 > proxies.txt             # 5s timeout, retry yok
./proxine.py socks4 -F 3600                           # son 1 saatte güncellenen kaynaklar
./proxine.py socks5 -F 0                              # tazelik filtresi kapalı
./proxine.py http -o http.lst                         # dosyaya yaz; stderr'de rapor
./proxine.py http -s > proxies.txt                    # sadece liste, stderr boş
./proxine.py socks5 --github-token ghp_xxx            # explicit token
```

### GitHub commit zamanını çözmek

`raw.githubusercontent.com` `Last-Modified` göndermediği için kaynak yaşı GitHub
API'ye sorulur. Unauth limit 60 req/h olduğundan, sık çalıştırıyorsanız token
verin:

```bash
# 1. Açık parametre:
./proxine.py socks5 --github-token ghp_xxx

# 2. Veya env var:
export GITHUB_TOKEN="$(gh auth token)"
./proxine.py socks5

# 3. Veya hiç ayarlama yapmadan — gh CLI yüklü ve auth'lu ise otomatik bulur
./proxine.py socks5
```

Token rate-limit'e takılır veya geçersizse rapor sonunda açık uyarı belirir.

------------------------------------------------------------

## Ekran düzeni

### 1. Progress bar (çalışma sırasında, TTY'de)

İki fazlı:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20 karakter `█/░` çubuğu, yüzde, done/total
- Faz etiketi: `fetching` (HTTP fetch) → `enriching` (GitHub commit zamanı API)
- ✓ = başarılı, x = hata
- `+N` = o kaynaktan gelen proxy sayısı (yalnızca fetch fazında)
- `total N` = birikmiş benzersiz toplam

Pipe/dosyaya yönlendirildiğinde progress otomatik sessizdir.

### 2. Kaynak durum tablosu

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
  OK     fresh enough (within --fresh window); proxies kept
  LIVE   no Last-Modified / commit info (dynamic API); proxies kept
  STALE  older than --fresh; proxies dropped from output
  FAIL   fetch error; no proxies contributed
```

Sıralama: OK (en taze üstte) → LIVE → STALE → FAIL.

### 3. Summary kutusu

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

------------------------------------------------------------

## Mod matrisi (hangi durumda nereye ne gider)

| Komut | stdout | stderr |
|---|---|---|
| `proxine http` | proxy listesi | progress → status tablosu → summary |
| `proxine http -v` | proxy listesi | per-source log → tablolar (progress yok) |
| `proxine http -o f.lst` | (boş) | progress → tablolar |
| `proxine http -o f.lst -s` | (boş) | (boş) |
| `proxine http -s` | proxy listesi | (boş) |

------------------------------------------------------------

## Proxy Kaynakları

Tüm aktif kaynaklar `sources.py` içinde, protokol bazlı listelenir. Toplam
**165+ URL** (http 51, https 29, socks4 42, socks5 43).

Başlıca beslenir:

- **GitHub raw (v2.0):** TheSpeedX, monosans, jetkai, zevtyardt, roosterkid,
  hookzof, MuRongPIG, ItzRazvyy, RX4096, mertguvencli, rdavydov, rx443,
  saisuiu, fate0, arunsakthivel96/proxyBEE, stamparm/aux, proxy4parsing,
  sunny9577.
- **GitHub raw (v2.1):** proxifly, ALIILAPRO, prxchk, vakhov, mmpx12,
  ErcinDedeoglu, Zaeem20, Anonym0usWork1221, elliottophellia/yakumo, shiftytr.
- **GitHub raw (v2.2):** databay-labs, vmheaven, zloi-user, dpangestuw,
  Mohammedcha/ProxRipper, officialputuid/ProxyForEveryone, Argh94, mzyui,
  MohammadKobirShah, Skillter, b4mbo-o, Seeh-Saah, RioMMO, openproxyhub,
  ebrasha/abdal-proxy-hub, Vann-Dev.
- **GitHub raw (v2.3):** ahahaabas, r00tee, Thordata, komutan234, anutmagang,
  yemixzy.
- **GitHub raw (v2.4 — CN/RU odaklı):** HankNovic/ProxyClean (Çinli
  geliştirici, "国内可用" — Çin'den erişilebilen socks5'ler).
- **Dinamik API / HTML:** pubproxy.com, proxyspace.pro, proxyscrape.com,
  ipaddress.com, free-proxy-list.net, google-proxy.net, socks-proxy.net,
  sslproxies.org, spys.me.

**Non-GitHub git host araştırması:** Gitee (CN), Codeberg, GitLab.com,
GitVerse (RU), GitFlic (RU), AtomGit (CN), SourceHut, Bitbucket detaylı
tarandı (iki ayrı tur). 30 gün içinde aktif **IP:PORT formatında** proxy
listesi tutan repo bulunamadı:

- **Gitee/AtomGit (CN):** Discovery arayüzleri JS-rendered, programatik
  taramaya kapalı. API timeout veriyor. Tek tek bilinen repolar çekilebiliyor
  ama search yapılamıyor.
- **GitVerse/GitFlic (RU):** GitVerse explore'da yalnızca Sber tech /
  `russian_ban_words` / `ru-services` var. GitFlic bağlantı reddediyor.
- **CN/RU temalı GitHub repoları:** Çoğu V2Ray/Clash subscription (`vmess://`
  / `vless://` formatı, IP:PORT değil). RU repoları ise domain blok
  listeleri ya da Telegram proxy URL'leri (`tg://`). Tek istisna:
  HankNovic/ProxyClean — eklendi.

Manifest host-agnostik olduğundan ilerde böyle bir kaynak çıkarsa 1 satırla
eklenebilir.

------------------------------------------------------------

## Otomatikleştirme

Proxine tek seferlik bir aggregator olarak tasarlandı; tekrarlı çalıştırma
gerekiyorsa cron / systemd-timer / GitHub Actions ile sarmalanır. Boru hattına
girecekse `-s` ve `-o` öneririz — progress/tablolar stderr'de kalır, boru/dosya
yalnızca proxy listesi alır:

```bash
# her saat başı socks5 listesini güncelle
0 * * * * cd ~/proxine && python3 proxine.py socks5 -s -o /var/lib/proxies/socks5.lst

# proxy-profiler ile zincirle (canlılık + elite testi)
python3 proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

------------------------------------------------------------

## Araçlar

Çıktıyı Windows'ta [EliteProxySwitcher](https://www.eliteproxyswitcher.com/)
veya [Open Proxy Checker](https://openproxy.space/software/proxy-checker) ile
test edebilirsiniz. Toplu test/profilleme için
[Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## Disclaimer

This is an open source for everyone. You may redistribute, modify, use patents
and use privately without any obligation to redistribute. The original
copyright must remain with the author (Özgür Koca). Users assume all risk; the
author is not liable for any damage caused by use of this tool.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)

## Author

I'm Özgür. I teach at a vocational [school](https://samsuneml.meb.k12.tr/).
GitHub: https://github.com/enseitankado · Blog: www.tankado.com

## Donation

Would you like to buy me a coffee? [Click](https://www.buymeacoffee.com/ozgurkoca).
