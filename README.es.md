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
<b>60 fuentes únicas</b> · <b>166 endpoints</b><br>
HTTP: 51 &nbsp;·&nbsp; HTTPS: 29 &nbsp;·&nbsp; SOCKS4: 42 &nbsp;·&nbsp; SOCKS5: 44
</p>

> Proxine es un agregador, no un verificador de calidad. Para obtener proxies
> funcionales y verdaderamente elite, canalice la salida hacia un comprobador
> como [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## Características

- **60 fuentes distintas**, 166 endpoints — listas raw de GitHub + 9 feeds
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
./proxine.py <http|https|socks4|socks5> [opciones]
```

### Banderas

| Larga | Corta | Predet. | Descripción |
|---|---|---|---|
| `--format` | `-f` | `ip-port` | Formato de salida. `url` produce `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | Timeout HTTP por fuente (segundos). |
| `--concurrency` | `-c` | `1` | Solicitudes paralelas. Más alto = más rápido + más sockets. |
| `--retries` | `-r` | `2` | Reintentos por fuente fallida. |
| `--fresh` | `-F` | `86400` | Descartar fuentes con más de N segundos. `0` desactiva. |
| `--github-token` | `-g` | — | PAT de GitHub. Si no, `$GITHUB_TOKEN`, luego `gh auth token`. |
| `--output` | `-o` | — | Escribir la lista en ARCHIVO; stdout queda vacío. |
| `--verbose` | `-v` | — | Registrar el resultado de cada fuente línea por línea. |
| `--silent` | `-s` | — | Suprimir toda la salida stderr. |

### Ejemplos

```bash
# Proxies HTTPS a stdout (filtro de frescura por defecto: 24h)
./proxine.py https

# Lista SOCKS5 a archivo, más rápido
./proxine.py socks5 -c 32 -o socks5.lst

# Solo fuentes actualizadas en la última hora
./proxine.py http -F 3600

# Salida tipo URL: socks5://1.2.3.4:1080
./proxine.py socks5 -f url

# Modo silencioso — ideal para pipelines
./proxine.py http -s | grep '^192\.'

# Encadenar con Proxy Profiler
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
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
./proxine.py socks5 -g ghp_xxx

# 2) Variable de entorno
export GITHUB_TOKEN=ghp_xxx
./proxine.py socks5

# 3) Nada — si `gh` CLI está instalado y autenticado
./proxine.py socks5
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
| `proxine http` | lista de proxies | progreso → tabla → resumen |
| `proxine http -v` | lista de proxies | log línea a línea → tablas |
| `proxine http -o f.lst` | (vacío) | progreso → tablas |
| `proxine http -s` | lista de proxies | (vacío) |
| `proxine http -o f.lst -s` | (vacío) | (vacío) |

------------------------------------------------------------

## Fuentes

Un total de **60 fuentes únicas**, **166 endpoints de protocolo**. Todas
están definidas en `sources.py`; añadir una nueva es un cambio de una línea.

### Listas raw de GitHub (51 repositorios)

| Repo | Protocolos |
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

### Fuentes dinámicas API y HTML (9 endpoints)

| Endpoint | Tipo | Protocolos |
|---|---|---|
| `api.proxyscrape.com` | API pública | http, https, socks4, socks5 |
| `pubproxy.com` | API pública | http, https, socks4, socks5 |
| `proxyspace.pro` | Lista texto plano | http, https, socks5 |
| `spys.me` | Lista texto plano | socks4, socks5 |
| `free-proxy-list.net` | Scraper HTML | http |
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
0 * * * * cd ~/proxine && ./proxine.py socks5 -s -o /var/lib/proxies/socks5.lst

# Encadenar con Proxy Profiler (vida + test elite)
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
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
