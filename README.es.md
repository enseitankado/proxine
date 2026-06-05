<p align="right">
<sub>
<a href="README.md">🇹🇷 Türkçe</a> ·
<a href="README.en.md">🇬🇧 English</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<b>🇪🇸 Español</b> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

Agregador de listas de proxies de código abierto. Con un solo comando obtiene
proxies **HTTP / HTTPS / SOCKS4 / SOCKS5** de docenas de fuentes públicas en
paralelo, descarta automáticamente fuentes obsoletas, elimina duplicados,
valida y entrega una lista `IP:PORT` ordenada y limpia.

<p align="center">
<b>86 fuentes únicas</b> · <b>220 endpoints</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine es un agregador, no un verificador de calidad. Para obtener proxies
> funcionales y verdaderamente elite, canalice la salida hacia un comprobador
> como [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## Características

- **86 fuentes distintas**, 220 endpoints — listas raw de GitHub + 8 feeds
  dinámicos API/HTML.
- **Descarga HTTP paralela** — por defecto cortés (`-c 1`); con `-c 20`+
  alrededor de 10× más rápido.
- **Timeout + reintento por fuente** — un host lento no detiene toda la
  ejecución.
- **Seguimiento de frescura.** Se informa la última actualización de cada
  fuente; para GitHub se resuelve mediante la API. `-F SEGUNDOS` filtra
  fuentes obsoletas (predeterminado 24 h).
- **Validación estricta.** Octetos IPv4 (0–255) y puertos (1–65535)
  comprobados con un regex reforzado.
- **Salida inteligente.** Barra de progreso en TTY; silenciosa en pipes;
  tablas ASCII de estado; `-s` para silencio total; `-o` para escribir a
  archivo.
- **Sin dependencias.** Solo Python ≥ 3.10 stdlib.

------------------------------------------------------------

## Instalación

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

Requisito: **Python ≥ 3.10**. Opcional: `gh` CLI o un personal access token
de GitHub (para resolver edades de fuentes — ver abajo).

------------------------------------------------------------

## Uso

```bash
./proxine.py -p <http|https|socks4|socks5> [opciones]
```

### Banderas

| Larga | Corta | Predet. | Descripción |
|---|---|---|---|
| `--protocol` | `-p` | — | **Obligatorio.** Protocolo a recopilar: `http`, `https`, `socks4`, `socks5`. |
| `--format` | `-f` | `ip-port` | Formato de salida. `url` produce `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | Timeout HTTP por fuente (segundos). |
| `--concurrency` | `-c` | `1` | Solicitudes paralelas. Más alto = más rápido + más sockets. |
| `--retries` | `-r` | `2` | Reintentos por fuente fallida. |
| `--max-ports` | `-m` | `5` | Descartar una IP por completo si aparece en más de N puertos distintos (filtro escáner/honeypot). `0` desactiva. |
| `--fresh` | `-F` | `86400` | Descartar fuentes con más de N segundos. `0` desactiva. |
| `--github-token` | `-g` | — | PAT de GitHub. Si no, `$GITHUB_TOKEN`, luego `gh auth token`. |
| `--output` | `-o` | — | Escribir la lista en ARCHIVO; stdout queda vacío. |
| `--lang` | `-L` | auto | Idioma de la interfaz: `tr`, `en`, `de`, `es`, `ru`, `zh`. Si no, se autodetecta desde `$PROXINE_LANG`/`$LANG`/locale. |
| `--strict-ports` / `--no-strict-ports` | — | on | Descartar proxies cuyo puerto no coincide con la familia del protocolo declarado (p.ej. SOCKS en puerto 80). |
| `--silent` | `-s` | — | Suprimir toda la salida stderr. |

### Ejemplos

```bash
# Proxies HTTPS a stdout (filtro de frescura por defecto: 24h)
./proxine.py -p https

# Lista SOCKS5 a archivo, más rápido
./proxine.py -p socks5 -c 32 -o socks5.lst

# Solo fuentes actualizadas en la última hora
./proxine.py -p http -F 3600

# Salida tipo URL: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# Modo silencioso — ideal para pipelines
./proxine.py -p http -s | grep '^192\.'

# Encadenar con Proxy Profiler — 3 ejemplos
# 1) Extraer proxies HTTP elite (L1) anónimos
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — saltar el judge (rápido), conservar solo los que pasan Cloudflare WAF
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + filtro por país (US/DE/JP) + test de acceso a Google
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
```

### Token de GitHub (opcional pero recomendado)

Las URL raw de GitHub no exponen `Last-Modified`, por lo que las edades se
resuelven mediante la API de GitHub. El **límite anónimo es 60 peticiones/
hora**; una sola ejecución alcanza 50+ URLs de GitHub, así que sin token la
mayoría de las edades aparece como «LIVE». Con un token el límite sube a
**5 000 peticiones/hora** — no se requiere scope `repo`, basta con lectura
pública.

Tres formas — Proxine elige la primera disponible:

```bash
# 1) Bandera explícita
./proxine.py -p socks5 -g ghp_xxx

# 2) Variable de entorno
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) Nada — si `gh` CLI está instalado y autenticado
./proxine.py -p socks5
```

Si el token llega al límite o es inválido, se muestra una advertencia clara
al final.

------------------------------------------------------------

## Salida

### 1. Barra de progreso

Durante la ejecución, dos fases en stderr:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- Barra `█/░` de 20 caracteres, porcentaje, hecho/total
- Etiqueta de fase: `fetching` (HTTP) o `enriching` (API de commits de GitHub)
- `✓` éxito, `x` fallo
- `+N` nuevos proxies de esta fuente
- `total N` total único acumulado

Silenciosa automáticamente fuera de TTY (no contamina redirecciones).

### 2. Tabla de estado de fuentes

Al final, en stderr:

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
  OK     fresco dentro de la ventana `--fresh`; proxies conservados
  LIVE   sin info de edad (API dinámica); proxies conservados
  STALE  más antiguo que `--fresh`; proxies descartados de la salida
  FAIL   error de descarga; sin contribución
```

Orden: OK (más frescos arriba) → LIVE → STALE → FAIL.

### 3. Caja resumen

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### Modos de salida

| Comando | stdout | stderr |
|---|---|---|
| `proxine -p http` | lista de proxies | log por fuente + progreso → tabla → resumen |
| `proxine -p http -o f.lst` | (vacío) | log por fuente + progreso → tablas |
| `proxine -p http -s` | lista de proxies | (vacío) |
| `proxine -p http -o f.lst -s` | (vacío) | (vacío) |

------------------------------------------------------------

## Fuentes

Un total de **86 fuentes únicas**, **220 endpoints de protocolo**. Todas
definidas en `sources.py`; añadir una nueva fuente es un cambio de una línea.

### Listas raw de GitHub (77 repos)

| Repo | Protocolos |
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

### Listas de GitLab (1 repo)

| Repo | Protocolos |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### API dinámicas y fuentes HTML (8 endpoints)

| Endpoint | Tipo | Protocolos |
|---|---|---|
| `api.proxyscrape.com` | API pública | http, https, socks4, socks5 |
| `free-proxy-list.net` | Scraper HTML | http |
| `proxyspace.pro` | Lista de texto plano | https, socks5 |
| `pubproxy.com` | API pública | http, https, socks4, socks5 |
| `www.google-proxy.net` | Scraper HTML | http, https |
| `www.ipaddress.com` | Scraper HTML | http, https |
| `www.socks-proxy.net` | Scraper HTML | socks4 |
| `www.sslproxies.org` | Scraper HTML | https |

------------------------------------------------------------

## Automatización

Proxine está diseñado para ejecuciones puntuales; para actualizaciones
programadas envuélvalo con cron / systemd-timer / GitHub Actions. Para
pipelines se recomiendan `-s` y `-o`:

```bash
# Cron: actualiza la lista SOCKS5 cada hora
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# Build nocturno de HTTP elite (proxine + profiler)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst
```

------------------------------------------------------------

## Herramientas relacionadas

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  comprobador multihilo de vida, anonimato (Elite/Anonymous/Transparent),
  paso de CloudFlare y Google.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — rotador
  de proxies con GUI para Windows.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  verificador de listas para Windows.

------------------------------------------------------------

## Licencia

Código abierto. Puede redistribuir, modificar, usar comercial o
privadamente. Conserve la autoría original (Özgür Koca) en trabajos
derivados. El software se proporciona «tal cual»; todo riesgo de uso recae
en el usuario.

## Autor

**Özgür Koca** — profesor en un
[instituto técnico](https://samsuneml.meb.k12.tr/).
GitHub: [enseitankado](https://github.com/enseitankado) · Blog:
[tankado.com](https://www.tankado.com)

## Apoyo

Si te resulta útil, deja una ⭐. ¿Quieres invitarme a un café?
[Por aquí](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
