<p align="center">
<sub>
<a href="README.md">🇬🇧 English</a> ·
<a href="README.tr.md">🇹🇷 Türkçe</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<b>🇩🇪 Deutsch</b> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

Open-Source-Aggregator für Proxy-Listen. Ein einziger Befehl ruft parallel
**HTTP / HTTPS / SOCKS4 / SOCKS5**-Proxys aus Dutzenden öffentlichen Quellen
ab, verwirft veraltete Quellen automatisch, entfernt Duplikate, validiert
und liefert eine saubere, sortierte `IP:PORT`-Liste.

<p align="center">
<b>86 unterschiedliche Quellen</b> · <b>220 Endpunkte</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine ist ein Aggregator, kein Qualitätsprüfer. Für funktionierende und
> wirklich Elite-Proxys leiten Sie die Ausgabe an einen Tester wie
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler) weiter.

------------------------------------------------------------

## Funktionen

- **86 verschiedene Quellen**, 220 Endpunkte — GitHub-Raw-Listen + 8
  dynamische API/HTML-Feeds.
- **Paralleler HTTP-Abruf** — Standard ist höflich (`-c 1`); mit `-c 20`+
  rund 10× schneller.
- **Timeout + Retry je Quelle** — ein langsamer Host blockiert nicht den
  ganzen Lauf.
- **Aktualitätsverfolgung.** Letztes Update jeder Quelle wird gemeldet; bei
  GitHub-Quellen über die API per Commit-Zeit. `-F SECONDS` filtert
  veraltete Quellen (Standard 24 h).
- **Strenge Validierung.** IPv4-Oktette (0–255) und Ports (1–65535) werden
  per gehärtetem Regex geprüft.
- **Intelligente Ausgabe.** TTY-Fortschrittsbalken; stumm in Pipes;
  ASCII-Statustabellen; `-s` für vollständige Stille; `-o` zum Schreiben in
  eine Datei.
- **Keine Abhängigkeiten.** Nur Python ≥ 3.10 Standardbibliothek.

------------------------------------------------------------

## Installation

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

Voraussetzung: **Python ≥ 3.10**. Optional: `gh` CLI oder ein GitHub
Personal Access Token (zur Auflösung von Quellaltern — siehe unten).

------------------------------------------------------------

## Verwendung

```bash
./proxine.py -p <http|https|socks4|socks5> [Optionen]
```

### Optionen

| Lang | Kurz | Standard | Beschreibung |
|---|---|---|---|
| `--protocol` | `-p` | — | **Erforderlich.** Zu sammelndes Protokoll: `http`, `https`, `socks4`, `socks5`. |
| `--format` | `-f` | `ip-port` | Ausgabeformat. `url` erzeugt `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | HTTP-Timeout je Quelle (Sekunden). |
| `--concurrency` | `-c` | `1` | Parallele Anfragen. Höher = schneller + mehr Sockets. |
| `--retries` | `-r` | `2` | Wiederholungen pro fehlgeschlagener Quelle. |
| `--max-ports` | `-m` | `5` | Eine IP komplett verwerfen, wenn sie auf mehr als N verschiedenen Ports erscheint (Port-Scanner/Honeypot-Filter). `0` deaktiviert. |
| `--fresh` | `-F` | `86400` | Quellen älter als N Sekunden werden verworfen. `0` deaktiviert. |
| `--github-token` | `-g` | — | GitHub-PAT. Fallback: `$GITHUB_TOKEN`, dann `gh auth token`. |
| `--output` | `-o` | — | Proxy-Liste in DATEI schreiben; stdout bleibt leer. |
| `--lang` | `-L` | auto | UI-Sprache: `tr`, `en`, `de`, `es`, `ru`, `zh`. Sonst aus `$PROXINE_LANG`/`$LANG`/Locale ermittelt. |
| `--strict-ports` / `--no-strict-ports` | — | an | Proxys verwerfen, deren Port nicht zur deklarierten Protokoll-Familie passt (z.B. SOCKS-deklariert auf Port 80). |
| `--silent` | `-s` | — | Sämtliche stderr-Ausgabe unterdrücken. |

### Beispiele

```bash
# HTTPS-Proxys nach stdout (Standardfilter: 24h)
./proxine.py -p https

# SOCKS5-Liste in Datei, schneller
./proxine.py -p socks5 -c 32 -o socks5.lst

# Nur Quellen, die in der letzten Stunde aktualisiert wurden
./proxine.py -p http -F 3600

# URL-Format-Ausgabe: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# Stiller Modus — ideal für Pipelines
./proxine.py -p http -s | grep '^192\.'

# Kette mit Proxy Profiler — 3 Beispiele
# 1) Elite (L1) anonyme HTTP-Proxys extrahieren
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — Judge überspringen (schnell), nur Cloudflare-WAF-passierende Proxys behalten
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + Länderfilter (US/DE/JP) + Google-Erreichbarkeitstest
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
```

### GitHub-Token (optional, empfohlen)

GitHub-Raw-URLs liefern kein `Last-Modified`, daher werden Quellalter über
die GitHub-API ermittelt. Das **anonyme Limit beträgt 60 Anfragen/Stunde**;
ein Lauf erreicht 50+ GitHub-URLs, daher zeigen ohne Token die meisten
Alter als „LIVE". Mit Token sind es **5.000 Anfragen/Stunde** — kein
`repo`-Scope nötig, öffentlicher Lesezugriff reicht.

Drei Wege — Proxine wählt den ersten verfügbaren:

```bash
# 1) Expliziter Parameter
./proxine.py -p socks5 -g ghp_xxx

# 2) Umgebungsvariable
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) Nichts — wenn `gh` CLI installiert und angemeldet
./proxine.py -p socks5
```

Bei Rate-Limit oder ungültigem Token erscheint am Ende eine klare Warnung.

------------------------------------------------------------

## Ausgabe

### 1. Fortschrittsbalken

Während des Laufs, zweiphasig auf stderr:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20-Zeichen-Balken `█/░`, Prozent, fertig/gesamt
- Phasen-Label: `fetching` (HTTP) oder `enriching` (GitHub Commit-API)
- `✓` Erfolg, `x` Fehler
- `+N` neue Proxys aus dieser Quelle
- `total N` akkumulierter eindeutiger Gesamtbestand

Außerhalb von TTY automatisch stumm (verschmutzt keine Umleitungen).

### 2. Quellen-Statustabelle

Am Ende, auf stderr:

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
  OK     aktuell im `--fresh`-Fenster; Proxys übernommen
  LIVE   keine Altersangabe (dynamische API); Proxys übernommen
  STALE  älter als `--fresh`; Proxys werden aus der Ausgabe entfernt
  FAIL   Abruffehler; kein Beitrag
```

Sortierung: OK (am frischesten oben) → LIVE → STALE → FAIL.

### 3. Zusammenfassungsbox

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### Ausgabemodi

| Befehl | stdout | stderr |
|---|---|---|
| `proxine -p http` | Proxy-Liste | Quellen-Log + Fortschritt → Tabelle → Zusammenfassung |
| `proxine -p http -o f.lst` | (leer) | Quellen-Log + Fortschritt → Tabellen |
| `proxine -p http -s` | Proxy-Liste | (leer) |
| `proxine -p http -o f.lst -s` | (leer) | (leer) |

------------------------------------------------------------

## Quellen

Insgesamt **86 eindeutige Quellen**, **220 Protokoll-Endpunkte**. Alle in
`sources.py` definiert; eine neue Quelle hinzufügen ist eine einzeilige Änderung.

### GitHub-Raw-Listen (77 Repos)

| Repo | Protokolle |
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

### GitLab-Listen (1 Repo)

| Repo | Protokolle |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### Dynamische API- und HTML-Quellen (8 Endpunkte)

| Endpunkt | Art | Protokolle |
|---|---|---|
| `api.proxyscrape.com` | Öffentliche API | http, https, socks4, socks5 |
| `free-proxy-list.net` | HTML-Scraper | http |
| `proxyspace.pro` | Klartext-Liste | https, socks5 |
| `pubproxy.com` | Öffentliche API | http, https, socks4, socks5 |
| `www.google-proxy.net` | HTML-Scraper | http, https |
| `www.ipaddress.com` | HTML-Scraper | http, https |
| `www.socks-proxy.net` | HTML-Scraper | socks4 |
| `www.sslproxies.org` | HTML-Scraper | https |

------------------------------------------------------------

## Automatisierung

Proxine ist für Einzelläufe konzipiert; für geplante Updates mit cron /
systemd-timer / GitHub Actions umhüllen. Für Pipelines werden `-s` und `-o`
empfohlen:

```bash
# Cron: SOCKS5-Liste stündlich aktualisieren
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# Nächtlich Elite-HTTP-Build (proxine + Profiler-Kette)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst
```

------------------------------------------------------------

## Verwandte Tools

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  Multithread-Tester für Lebendigkeit, Anonymität (Elite/Anonymous/
  Transparent), CloudFlare- und Google-Durchlässigkeit.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — GUI-
  Proxy-Rotator für Windows.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  Listen-Verifizierer für Windows.

------------------------------------------------------------

## Lizenz

Open Source. Sie dürfen weitergeben, modifizieren, kommerziell oder privat
nutzen. Behalten Sie die Original-Autorschaft (Özgür Koca) in abgeleiteten
Werken bei. Software wird „wie besehen" bereitgestellt; jegliches
Nutzungsrisiko trägt der Nutzer.

## Autor

**Özgür Koca** — Lehrer an einer
[Berufsschule](https://samsuneml.meb.k12.tr/).
GitHub: [enseitankado](https://github.com/enseitankado) · Blog:
[tankado.com](https://www.tankado.com)

## Unterstützung

Wenn nützlich, gerne ein ⭐. Lust auf einen Kaffee?
[Bitte schön](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
