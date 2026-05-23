<p align="right">
<sub>
<a href="README.md">🇹🇷 Türkçe</a> ·
<b>🇬🇧 English</b> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

Open-source proxy list aggregator. A single command fetches **HTTP / HTTPS /
SOCKS4 / SOCKS5** proxies from dozens of public sources in parallel,
automatically drops stale sources, deduplicates, validates, and emits a clean
sorted `IP:PORT` list.

<p align="center">
<b>60 unique sources</b> · <b>166 endpoints</b><br>
HTTP: 51 &nbsp;·&nbsp; HTTPS: 29 &nbsp;·&nbsp; SOCKS4: 42 &nbsp;·&nbsp; SOCKS5: 44
</p>

> Proxine is an aggregator, not a quality checker. For working, truly elite
> proxies, pipe its output into a tester like
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## Features

- **60 distinct sources**, 166 endpoints — GitHub raw lists + 9 dynamic
  API/HTML feeds.
- **Parallel HTTP fetch** — default is polite (`-c 1`); raise to `-c 20`+ for
  ~10× speedup.
- **Per-source timeout + retry** — a slow host can't stall the whole run.
- **Freshness tracking.** Each source's last update is reported; GitHub
  commit times are resolved via the API. `-F SECONDS` filters out stale
  sources (default 24 h).
- **Strict validation.** IPv4 octets (0–255) and ports (1–65535) checked
  with a hardened regex.
- **Smart output.** TTY progress bar; silent in pipes; ASCII status tables;
  `-s` for full quiet; `-o` to write a file.
- **Zero dependencies.** Python ≥ 3.10 stdlib only.

------------------------------------------------------------

## Installation

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

Requirement: **Python ≥ 3.10**. Optional: `gh` CLI or a GitHub personal
access token (to resolve source ages — see below).

------------------------------------------------------------

## Usage

```bash
./proxine.py <http|https|socks4|socks5> [options]
```

### Flags

| Long | Short | Default | Description |
|---|---|---|---|
| `--format` | `-f` | `ip-port` | Output format. `url` produces `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | Per-source HTTP timeout (seconds). |
| `--concurrency` | `-c` | `1` | Number of parallel requests. Higher = faster + more sockets. |
| `--retries` | `-r` | `2` | Retry attempts per failed source. |
| `--fresh` | `-F` | `86400` | Drop sources older than this many seconds. `0` disables the filter. |
| `--github-token` | `-g` | — | GitHub PAT. Falls back to `$GITHUB_TOKEN`, then `gh auth token`. |
| `--output` | `-o` | — | Write the proxy list to FILE; stdout stays empty. |
| `--verbose` | `-v` | — | Log each source's result line by line. |
| `--silent` | `-s` | — | Suppress all stderr output. |

### Examples

```bash
# HTTPS proxies to stdout (default freshness filter: 24h)
./proxine.py https

# SOCKS5 list to a file, faster
./proxine.py socks5 -c 32 -o socks5.lst

# Only sources updated in the last hour
./proxine.py http -F 3600

# URL-style output: socks5://1.2.3.4:1080
./proxine.py socks5 -f url

# Silent mode — ideal for pipelines
./proxine.py http -s | grep '^192\.'

# Chain with Proxy Profiler
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

### GitHub token (optional but recommended)

GitHub raw URLs don't expose `Last-Modified`, so source ages are resolved via
the GitHub API. The **anonymous limit is 60 requests/hour**; one run hits 50+
GitHub URLs, so without a token most ages show as "LIVE". With a token the
limit is **5,000 requests/hour** — no `repo` scope needed, public read is
enough.

Three ways — Proxine picks the first available:

```bash
# 1) Explicit flag
./proxine.py socks5 -g ghp_xxx

# 2) Environment variable
export GITHUB_TOKEN=ghp_xxx
./proxine.py socks5

# 3) Nothing — if `gh` CLI is installed and authenticated
./proxine.py socks5
```

If the token is rate-limited or invalid, a clear warning is shown at the end.

------------------------------------------------------------

## Output

### 1. Progress bar

During the run, two phases on stderr:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20-character `█/░` bar, percentage, done/total
- Phase label: `fetching` (HTTP) or `enriching` (GitHub commit API)
- `✓` success, `x` failure
- `+N` new proxies from this source
- `total N` accumulated unique total

Automatically silent off-TTY (won't pollute redirected output).

### 2. Source status table

At the end, on stderr:

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
  OK     fresh within `--fresh` window; proxies kept
  LIVE   no age info (dynamic API); proxies kept
  STALE  older than `--fresh`; proxies dropped from output
  FAIL   fetch error; no contribution
```

Sort order: OK (freshest first) → LIVE → STALE → FAIL.

### 3. Summary box

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### Output mode matrix

| Command | stdout | stderr |
|---|---|---|
| `proxine http` | proxy list | progress → status table → summary |
| `proxine http -v` | proxy list | per-source log → tables |
| `proxine http -o f.lst` | (empty) | progress → tables |
| `proxine http -s` | proxy list | (empty) |
| `proxine http -o f.lst -s` | (empty) | (empty) |

------------------------------------------------------------

## Sources

A total of **60 unique sources**, **166 protocol endpoints**. All defined in
`sources.py`; adding a new one is a one-line change.

### GitHub raw lists (51 repos)

| Repo | Protocols |
|---|---|
| `ALIILAPRO/Proxy` | http, socks4, socks5 |
| `Anonym0usWork1221/Free-Proxies` | http, https, socks4, socks5 |
| `Argh94/Proxy-List` | http, socks4, socks5 |
| `HankNovic/ProxyClean` | socks5 |
| `ItzRazvyy/ProxyList` | http, https, socks4, socks5 |
| `MohammadKobirShah/ProxyScraper-Pro` | http, socks4, socks5 |
| `Mohammedcha/ProxRipper` | http, https, socks4, socks5 |
| `MuRongPIG/Proxy-Master` | http, socks4, socks5 |
| `RX4096/proxy-list` | http, https |
| `RioMMO/ProxyFree` | http, socks4, socks5 |
| `Seeh-Saah/awesome-free-proxy-list` | http, socks4, socks5 |
| `Skillter/ProxyGather` | http, socks4, socks5 |
| `TheSpeedX/PROXY-List` | http, socks4, socks5 |
| `Thordata/awesome-free-proxy-list` | http, socks4, socks5 |
| `Vann-Dev/proxy-list` | socks4, socks5 |
| `Zaeem20/FREE_PROXIES_LIST` | http, https, socks4, socks5 |
| `ahahaabas/anonymous-proxy-list-free` | http, socks4, socks5 |
| `anutmagang/Free-HighQuality-Proxy-Socks` | http |
| `arunsakthivel96/proxyBEE` | http, https |
| `b4mbo-o/Check-Free-Proxy` | http, socks4, socks5 |
| `databay-labs/free-proxy-list` | http, socks4, socks5 |
| `dpangestuw/Free-Proxy` | http, socks4, socks5 |
| `ebrasha/abdal-proxy-hub` | http, https, socks4, socks5 |
| `elliottophellia/yakumo` | http, socks4, socks5 |
| `ErcinDedeoglu/proxies` | http, https, socks4, socks5 |
| `fate0/proxylist` | http, https |
| `hookzof/socks5_list` | socks5 |
| `jetkai/proxy-list` | http, https, socks4, socks5 |
| `komutan234/Proxy-List-Free` | http, socks4, socks5 |
| `mertguvencli/http-proxy-list` | http, https |
| `mmpx12/proxy-list` | http, https, socks4, socks5 |
| `monosans/proxy-list` | http, https, socks4, socks5 |
| `mzyui/proxy-list` | http, socks4, socks5 |
| `officialputuid/ProxyForEveryone` | http, https, socks4, socks5 |
| `openproxyhub/proxy-exports` | socks5 |
| `proxifly/free-proxy-list` | http, https, socks4, socks5 |
| `proxy4parsing/proxy-list` | http |
| `prxchk/proxy-list` | http, socks4, socks5 |
| `r00tee/Proxy-List` | https, socks4, socks5 |
| `rdavydov/proxy-list` | http, socks4, socks5 |
| `roosterkid/openproxylist` | https, socks4, socks5 |
| `rx443/proxy-list` | http, https |
| `saisuiu/uiu` | http, socks4 |
| `shiftytr/proxy-list` | https |
| `stamparm/aux` | http |
| `sunny9577/proxy-scraper` | http, https |
| `vakhov/fresh-proxy-list` | http, https, socks4, socks5 |
| `vmheaven/VMHeaven.io-Free-Proxy-List` | http, https, socks4, socks5 |
| `yemixzy/free-proxy-list` | http, socks4, socks5 |
| `zevtyardt/proxy-list` | http, socks4, socks5 |
| `zloi-user/hideip.me` | http, https, socks4, socks5 |

### Dynamic API and HTML sources (9 endpoints)

| Endpoint | Type | Protocols |
|---|---|---|
| `api.proxyscrape.com` | Public API | http, https, socks4, socks5 |
| `pubproxy.com` | Public API | http, https, socks4, socks5 |
| `proxyspace.pro` | Plain-text list | http, https, socks5 |
| `spys.me` | Plain-text list | socks4, socks5 |
| `free-proxy-list.net` | HTML scraper | http |
| `www.google-proxy.net` | HTML scraper | http, https |
| `www.ipaddress.com` | HTML scraper | http, https |
| `www.socks-proxy.net` | HTML scraper | socks4 |
| `www.sslproxies.org` | HTML scraper | https |

------------------------------------------------------------

## Automation

Proxine is designed for one-shot runs; wrap it with cron / systemd-timer /
GitHub Actions for scheduled updates. For pipelines, `-s` and `-o` are
recommended:

```bash
# Cron: update the SOCKS5 list every hour
0 * * * * cd ~/proxine && ./proxine.py socks5 -s -o /var/lib/proxies/socks5.lst

# Chain with Proxy Profiler (liveness + elite test)
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

------------------------------------------------------------

## Related tools

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  multi-threaded tester for liveness, anonymity (Elite/Anonymous/Transparent),
  CloudFlare and Google pass-through.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — GUI proxy
  rotator for Windows.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  Windows list verifier.

------------------------------------------------------------

## License

Open source. You may redistribute, modify, and use it commercially or
privately. Keep the original author attribution (Özgür Koca) in derivative
work. Software is provided "as is"; all usage risk is on the user.

## Author

**Özgür Koca** — teacher at a vocational
[school](https://samsuneml.meb.k12.tr/).
GitHub: [enseitankado](https://github.com/enseitankado) · Blog:
[tankado.com](https://www.tankado.com)

## Support

If you find this useful, leave a ⭐. Want to buy me a coffee?
[Here you go](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
