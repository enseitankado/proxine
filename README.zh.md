<p align="center">
<sub>
<a href="README.md">🇬🇧 English</a> ·
<a href="README.tr.md">🇹🇷 Türkçe</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<b>🇨🇳 中文</b>
</sub>
</p>

# 🚀 Proxine

开源代理列表聚合器。一条命令即可从数十个公共源并行抓取
**HTTP / HTTPS / SOCKS4 / SOCKS5** 代理,自动剔除陈旧源、去重、校验,
输出干净有序的 `IP:PORT` 列表。

<p align="center">
<b>86 个独立源</b> · <b>220 个端点</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine 是聚合器,不是质量检测器。如需可用且真正 elite 级的代理,请将
> 输出管道传入诸如
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler) 的检测
> 工具。

------------------------------------------------------------

## 特性

- **86 个不同源**,220 个端点 —— GitHub raw 列表 + 8 个动态 API/HTML 源。
- **并行 HTTP 抓取** —— 默认温和(`-c 1`);使用 `-c 20`+ 可提速约 10×。
- **每源超时 + 重试** —— 慢主机不会拖累整体。
- **新鲜度追踪。** 报告每个源的最后更新时间;GitHub 源通过 API 解析
  commit 时间。`-F SECONDS` 自动过滤陈旧源(默认 24 小时)。
- **严格校验。** IPv4 八位组(0–255)和端口(1–65535)使用稳健的正则
  校验。
- **智能输出。** TTY 下进度条;管道下静默;ASCII 状态表;`-s` 完全静默;
  `-o` 写入文件。
- **零依赖。** 仅 Python ≥ 3.10 标准库。

------------------------------------------------------------

## 安装

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

要求:**Python ≥ 3.10**。可选:`gh` CLI 或 GitHub 个人访问令牌(用于
解析源年龄 —— 见下文)。

------------------------------------------------------------

## 用法

```bash
./proxine.py -p <http|https|socks4|socks5> [选项]
```

### 参数

| 长 | 短 | 默认 | 说明 |
|---|---|---|---|
| `--protocol` | `-p` | — | **必填。** 要采集的协议:`http`、`https`、`socks4`、`socks5`。 |
| `--format` | `-f` | `ip-port` | 输出格式。`url` 产生 `<proto>://IP:PORT`。 |
| `--timeout` | `-t` | `15` | 每源 HTTP 超时(秒)。 |
| `--concurrency` | `-c` | `1` | 并行请求数。越高越快,占用更多套接字。 |
| `--retries` | `-r` | `2` | 单源失败重试次数。 |
| `--max-ports` | `-m` | `5` | 若一个 IP 出现在超过 N 个不同端口,则整体丢弃(端口扫描器/蜜罐过滤)。`0` 禁用。 |
| `--fresh` | `-F` | `86400` | 丢弃超过 N 秒的源。`0` 关闭过滤。 |
| `--github-token` | `-g` | — | GitHub PAT。否则使用 `$GITHUB_TOKEN`,再尝试 `gh auth token`。 |
| `--output` | `-o` | — | 将代理列表写入 FILE;stdout 保持空。 |
| `--lang` | `-L` | 自动 | 界面语言:`tr`、`en`、`de`、`es`、`ru`、`zh`。否则从 `$PROXINE_LANG`/`$LANG`/区域自动检测。 |
| `--strict-ports` / `--no-strict-ports` | — | 启用 | 丢弃端口不符合声明协议族的代理(例如声明为 SOCKS 但在 80 端口)。 |
| `--silent` | `-s` | — | 抑制所有 stderr 输出。 |

### 示例

```bash
# HTTPS 代理输出到 stdout(默认新鲜度过滤:24 小时)
./proxine.py -p https

# SOCKS5 列表写入文件,更快
./proxine.py -p socks5 -c 32 -o socks5.lst

# 仅最近一小时内更新的源
./proxine.py -p http -F 3600

# URL 形式输出:socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# 静默模式 —— 适合管道
./proxine.py -p http -s | grep '^192\.'

# 与 Proxy Profiler 串联 — 3 个示例
# 1) 提取 Elite (L1) 匿名 HTTP 代理
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — 跳过 judge(更快),只保留能绕过 Cloudflare WAF 的活代理
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + 国家筛选 (US/DE/JP) + Google 可达性测试
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
```

### GitHub 令牌(可选但推荐)

GitHub raw URL 不返回 `Last-Modified`,因此源年龄通过 GitHub API 解析。
**匿名限额为 60 请求/小时**;单次运行会访问 50+ 个 GitHub URL,所以不
使用令牌时大多数年龄会显示为 "LIVE"。使用令牌后限额升至 **5,000 请求/
小时** —— 无需 `repo` 权限,公共读取即可。

三种方式 —— Proxine 选择第一个可用的:

```bash
# 1) 显式参数
./proxine.py -p socks5 -g ghp_xxx

# 2) 环境变量
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) 什么都不做 —— 若已安装并登录 `gh` CLI
./proxine.py -p socks5
```

若令牌超限或无效,报告末尾会有明确警告。

------------------------------------------------------------

## 输出

### 1. 进度条

运行时,stderr 上两个阶段:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20 字符 `█/░` 条、百分比、完成/总数
- 阶段标签:`fetching`(HTTP)或 `enriching`(GitHub commit API)
- `✓` 成功、`x` 失败
- `+N` 该源新增代理数
- `total N` 累计去重总数

非 TTY 自动静默(不污染重定向)。

### 2. 源状态表

运行结束时,在 stderr:

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
  OK     在 `--fresh` 窗口内新鲜;代理保留
  LIVE   无年龄信息(动态 API);代理保留
  STALE  早于 `--fresh`;代理从输出中丢弃
  FAIL   抓取失败;无贡献
```

排序:OK(最新在上)→ LIVE → STALE → FAIL。

### 3. 摘要框

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### 输出模式矩阵

| 命令 | stdout | stderr |
|---|---|---|
| `proxine -p http` | 代理列表 | 逐源日志 + 进度 → 状态表 → 摘要 |
| `proxine -p http -o f.lst` | (空) | 逐源日志 + 进度 → 表格 |
| `proxine -p http -s` | 代理列表 | (空) |
| `proxine -p http -o f.lst -s` | (空) | (空) |

------------------------------------------------------------

## 源清单

共 **86 个独立源**,**220 个协议端点**。全部定义在 `sources.py`,新增一
源仅需一行修改。

### GitHub raw 列表(77 个仓库)

| 仓库 | 协议 |
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

### GitLab 列表(1 个仓库)

| 仓库 | 协议 |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### 动态 API 与 HTML 源(8 个端点)

| 端点 | 类型 | 协议 |
|---|---|---|
| `api.proxyscrape.com` | 公开 API | http, https, socks4, socks5 |
| `free-proxy-list.net` | HTML 抓取 | http |
| `proxyspace.pro` | 纯文本列表 | https, socks5 |
| `pubproxy.com` | 公开 API | http, https, socks4, socks5 |
| `www.google-proxy.net` | HTML 抓取 | http, https |
| `www.ipaddress.com` | HTML 抓取 | http, https |
| `www.socks-proxy.net` | HTML 抓取 | socks4 |
| `www.sslproxies.org` | HTML 抓取 | https |

------------------------------------------------------------

## 自动化

Proxine 面向单次运行设计;若需定期更新,请用 cron / systemd-timer /
GitHub Actions 包装。管道使用时推荐 `-s` 与 `-o`:

```bash
# Cron:每小时更新 SOCKS5 列表
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# 每夜构建 elite HTTP(proxine + profiler 链)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst
```

------------------------------------------------------------

## 相关工具

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** ——
  多线程测试器,涵盖存活、匿名性(Elite/Anonymous/Transparent)、
  CloudFlare 与 Google 通行。
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** ——
  Windows 图形界面代理轮换工具。
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** ——
  Windows 列表校验工具。

------------------------------------------------------------

## 许可证

开源。您可重新分发、修改、商用或私人使用。在衍生作品中保留原作者署名
(Özgür Koca)。软件按「原样」提供,使用风险由用户自担。

## 作者

**Özgür Koca** —— [职业学校](https://samsuneml.meb.k12.tr/)教师。
GitHub:[enseitankado](https://github.com/enseitankado) · 博客:
[tankado.com](https://www.tankado.com)

## 支持

觉得有用就点 ⭐。想请喝咖啡?
[这边请](https://www.buymeacoffee.com/ozgurkoca)。

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
