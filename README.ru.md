<p align="center">
<sub>
<a href="README.md">🇬🇧 English</a> ·
<a href="README.tr.md">🇹🇷 Türkçe</a> ·
<b>🇷🇺 Русский</b> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

Агрегатор списков прокси с открытым исходным кодом. Одной командой
параллельно собирает **свежие прокси HTTP / HTTPS / SOCKS4 / SOCKS5** из
сотен курируемых публичных конечных точек, автоматически отсеивает
устаревшие источники, удаляет дубликаты, проверяет формат и выдаёт чистый
отсортированный список `IP:PORT`.

<p align="center">
<b>86 уникальных источников</b> · <b>220 конечных точек</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine — агрегатор, а не проверщик качества. Чтобы получить рабочие
> и действительно elite-прокси, передайте вывод в тестер, например
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## Возможности

- **86 различных источников**, 220 конечных точек — GitHub raw + 8
  динамических API/HTML-каналов.
- **Параллельная загрузка HTTP** — по умолчанию вежливо (`-c 1`); поднимите
  до `-c 20`+ для ~10× ускорения.
- **Таймаут + повтор для каждого источника** — медленный хост не остановит
  весь процесс.
- **Отслеживание актуальности.** Время последнего обновления каждого
  источника указывается; для GitHub оно вычисляется через API. `-F SECONDS`
  отсеивает устаревшие (по умолчанию 24 ч).
- **Строгая проверка.** Октеты IPv4 (0–255) и порты (1–65535) проверяются
  жёстким регулярным выражением.
- **Умный вывод.** Индикатор прогресса в TTY; молча в пайпах; ASCII-таблицы;
  `-s` для полной тишины; `-o` для записи в файл.
- **Без зависимостей.** Только стандартная библиотека Python ≥ 3.10.

------------------------------------------------------------

## Установка

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

Требование: **Python ≥ 3.10**. Опционально: `gh` CLI или GitHub personal
access token (для определения возраста источников — см. ниже).

------------------------------------------------------------

## Использование

```bash
./proxine.py -p <http|https|socks4|socks5> [параметры]
```

### Параметры

| Длинный | Краткий | По умолчанию | Описание |
|---|---|---|---|
| `--protocol` | `-p` | — | **Обязательно.** Протокол для сбора: `http`, `https`, `socks4`, `socks5`. |
| `--format` | `-f` | `ip-port` | Формат вывода. `url` даёт `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | HTTP-таймаут на источник (секунды). |
| `--concurrency` | `-c` | `1` | Параллельные запросы. Больше = быстрее + больше сокетов. |
| `--retries` | `-r` | `2` | Число повторов при ошибке источника. |
| `--max-ports` | `-m` | `5` | Полностью отбросить IP, если он встречается на более чем N разных портах (фильтр сканеров портов/honeypot). `0` отключает. |
| `--fresh` | `-F` | `86400` | Источники старше N секунд отбрасываются. `0` отключает фильтр. |
| `--github-token` | `-g` | — | GitHub PAT. Иначе `$GITHUB_TOKEN`, затем `gh auth token`. |
| `--output` | `-o` | — | Записать список прокси в FILE; stdout остаётся пустым. |
| `--lang` | `-L` | авто | Язык интерфейса: `tr`, `en`, `de`, `es`, `ru`, `zh`. Иначе автоопределение из `$PROXINE_LANG`/`$LANG`/локали. |
| `--strict-ports` / `--no-strict-ports` | — | вкл | Отбрасывать прокси, чей порт не соответствует объявленному семейству протоколов (напр. SOCKS на порту 80). |
| `--silent` | `-s` | — | Подавить весь вывод в stderr. |

### Примеры

```bash
# Прокси HTTPS в stdout (фильтр актуальности по умолчанию: 24 ч)
./proxine.py -p https

# Список SOCKS5 в файл, быстрее
./proxine.py -p socks5 -c 32 -o socks5.lst

# Только источники, обновлённые за последний час
./proxine.py -p http -F 3600

# Вывод в формате URL: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# Тихий режим — идеально для пайплайнов
./proxine.py -p http -s | grep '^192\.'

# Цепочка с Proxy Profiler — 3 примера
# 1) Извлечь Elite (L1) анонимные HTTP-прокси
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — пропустить judge (быстро), оставить только проходящих Cloudflare WAF
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + фильтр по странам (US/DE/JP) + тест доступа к Google
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
```

### GitHub-токен (необязательный, но рекомендуется)

GitHub raw URLs не возвращают `Last-Modified`, поэтому возраст источников
определяется через GitHub API. **Анонимный лимит — 60 запросов/час**; один
запуск обращается к 50+ GitHub-источникам, так что без токена большинство
возрастов будет показано как «LIVE». С токеном лимит — **5 000 запросов/час**;
права `repo` не нужны, достаточно public read.

Три способа — Proxine выбирает первый доступный:

```bash
# 1) Явный параметр
./proxine.py -p socks5 -g ghp_xxx

# 2) Переменная окружения
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) Ничего — если установлен и авторизован `gh` CLI
./proxine.py -p socks5
```

При срабатывании лимита или недействительном токене в конце отчёта
выводится явное предупреждение.

------------------------------------------------------------

## Вывод

### 1. Индикатор прогресса

Во время работы — две фазы на stderr:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20-символьная полоса `█/░`, процент, выполнено/всего
- Метка фазы: `fetching` (HTTP) или `enriching` (GitHub commit API)
- `✓` успех, `x` ошибка
- `+N` новые прокси из этого источника
- `total N` накопленный уникальный итог

Автоматически тихий вне TTY (не загрязняет перенаправленный вывод).

### 2. Таблица состояния источников

В конце, на stderr:

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
  OK     актуально в пределах `--fresh`; прокси использованы
  LIVE   нет данных о возрасте (динамический API); прокси использованы
  STALE  старше `--fresh`; прокси не попадают в вывод
  FAIL   ошибка загрузки; нет вклада
```

Порядок: OK (свежее сверху) → LIVE → STALE → FAIL.

### 3. Сводный блок

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### Режимы вывода

| Команда | stdout | stderr |
|---|---|---|
| `proxine -p http` | список прокси | построчный лог + прогресс → таблица → сводка |
| `proxine -p http -o f.lst` | (пусто) | построчный лог + прогресс → таблицы |
| `proxine -p http -s` | список прокси | (пусто) |
| `proxine -p http -o f.lst -s` | (пусто) | (пусто) |

------------------------------------------------------------

## Источники

Всего **86 уникальных источников**, **220 протокольных конечных точек**.
Все определены в `sources.py`; добавление нового источника — одна строка.

### GitHub raw списки (77 репо)

| Репозиторий | Протоколы |
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

### GitLab списки (1 репо)

| Репозиторий | Протоколы |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### Динамические API и HTML-источники (8 эндпоинтов)

| Эндпоинт | Тип | Протоколы |
|---|---|---|
| `api.proxyscrape.com` | Публичный API | http, https, socks4, socks5 |
| `free-proxy-list.net` | HTML-скрапер | http |
| `proxyspace.pro` | Текстовый список | https, socks5 |
| `pubproxy.com` | Публичный API | http, https, socks4, socks5 |
| `www.google-proxy.net` | HTML-скрапер | http, https |
| `www.ipaddress.com` | HTML-скрапер | http, https |
| `www.socks-proxy.net` | HTML-скрапер | socks4 |
| `www.sslproxies.org` | HTML-скрапер | https |

------------------------------------------------------------

## Автоматизация

Proxine спроектирован под разовый запуск; для регулярного обновления
оберните его cron / systemd-timer / GitHub Actions. Для пайплайнов
рекомендуются `-s` и `-o`:

```bash
# Cron: обновлять список SOCKS5 каждый час
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# Ночная сборка elite-HTTP (proxine + profiler)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst

```

------------------------------------------------------------

## Связанные инструменты

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  многопоточный тестер живучести, анонимности (Elite/Anonymous/Transparent),
  обхода CloudFlare и Google.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — GUI-ротатор
  прокси для Windows.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  проверка списков под Windows.

------------------------------------------------------------

## Лицензия

Открытый исходный код. Можно распространять, модифицировать, использовать
в коммерческих и личных целях. В производных работах сохраняйте
оригинальное авторство (Özgür Koca). ПО предоставляется «как есть»; весь
риск использования — на пользователе.

## Автор

**Özgür Koca** — учитель профессионального
[лицея](https://samsuneml.meb.k12.tr/).
GitHub: [enseitankado](https://github.com/enseitankado) · Блог:
[tankado.com](https://www.tankado.com)

## Поддержка

Если проект пригодился — поставьте ⭐. Хотите угостить кофе?
[Сюда](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
