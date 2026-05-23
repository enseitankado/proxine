<p align="right">
<sub>
<a href="README.md">🇹🇷 Türkçe</a> ·
<a href="README.en.md">🇬🇧 English</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<b>🇯🇵 日本語</b> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<a href="README.ar.md">🇸🇦 العربية</a> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

# 🚀 Proxine

オープンソースのプロキシリストアグリゲーター。単一のコマンドで、数十の公開
ソースから **HTTP / HTTPS / SOCKS4 / SOCKS5** プロキシを並列取得し、古い
ソースを自動的に除外、重複を排除、検証して、ソート済みのクリーンな
`IP:PORT` リストを出力します。

<p align="center">
<b>60 のユニークソース</b> · <b>166 のエンドポイント</b><br>
HTTP: 51 &nbsp;·&nbsp; HTTPS: 29 &nbsp;·&nbsp; SOCKS4: 42 &nbsp;·&nbsp; SOCKS5: 44
</p>

> Proxine はアグリゲーターであり、品質チェッカーではありません。実際に動作
> する真の elite プロキシが必要な場合は、出力を
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler) のような
> テスターにパイプしてください。

------------------------------------------------------------

## 機能

- **60 種類のソース**、166 エンドポイント — GitHub raw リスト + 9 個の
  動的 API/HTML フィード。
- **並列 HTTP 取得** — デフォルトは控えめ（`-c 1`）；`-c 20`+ で約 10 倍速。
- **ソース毎のタイムアウト + リトライ** — 遅いホストが全体を止めない。
- **鮮度追跡。** 各ソースの最終更新時刻を表示；GitHub ソースはコミット
  時刻を API から解決。`-F SECONDS` で古いソースを自動除外（デフォルト
  24 時間）。
- **厳格な検証。** IPv4 オクテット（0–255）とポート（1–65535）を堅牢な
  正規表現でチェック。
- **賢い出力。** TTY ではプログレスバー、パイプでは静音；ASCII ステータス
  テーブル；`-s` で完全静音；`-o` でファイル出力。
- **依存関係なし。** Python ≥ 3.10 標準ライブラリのみ。

------------------------------------------------------------

## インストール

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

要件：**Python ≥ 3.10**。任意：`gh` CLI または GitHub Personal Access
Token（ソースの新鮮度を解決するため — 下記参照）。

------------------------------------------------------------

## 使い方

```bash
./proxine.py <http|https|socks4|socks5> [オプション]
```

### フラグ

| ロング | ショート | デフォルト | 説明 |
|---|---|---|---|
| `--format` | `-f` | `ip-port` | 出力形式。`url` で `<proto>://IP:PORT`。 |
| `--timeout` | `-t` | `15` | ソース毎の HTTP タイムアウト（秒）。 |
| `--concurrency` | `-c` | `1` | 並列リクエスト数。多いほど速くソケット消費も増加。 |
| `--retries` | `-r` | `2` | 失敗ソース毎のリトライ回数。 |
| `--fresh` | `-F` | `86400` | N 秒より古いソースを除外。`0` で無効化。 |
| `--github-token` | `-g` | — | GitHub PAT。なければ `$GITHUB_TOKEN`、次に `gh auth token`。 |
| `--output` | `-o` | — | プロキシリストを FILE に書き込み；stdout は空。 |
| `--verbose` | `-v` | — | 各ソースの結果を行単位でログ。 |
| `--silent` | `-s` | — | すべての stderr 出力を抑制。 |

### 例

```bash
# HTTPS プロキシを stdout へ（デフォルト鮮度フィルタ: 24h）
./proxine.py https

# SOCKS5 リストをファイルへ、高速化
./proxine.py socks5 -c 32 -o socks5.lst

# 直近 1 時間に更新されたソースのみ
./proxine.py http -F 3600

# URL 形式出力: socks5://1.2.3.4:1080
./proxine.py socks5 -f url

# 静音モード — パイプライン向け
./proxine.py http -s | grep '^192\.'

# Proxy Profiler と連鎖
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

### GitHub トークン（任意、推奨）

GitHub raw URL は `Last-Modified` を返さないため、ソースの新鮮度は GitHub
API で解決されます。**匿名制限は 60 リクエスト/時**で、1 回の実行で 50+
の GitHub URL にアクセスするため、トークンなしでは大半の新鮮度が
「LIVE」と表示されます。トークンを使うと制限は **5,000 リクエスト/時**に
なります — `repo` スコープは不要、public read だけで充分です。

3 つの方法 — Proxine は利用可能な最初のものを選びます：

```bash
# 1) 明示的なフラグ
./proxine.py socks5 -g ghp_xxx

# 2) 環境変数
export GITHUB_TOKEN=ghp_xxx
./proxine.py socks5

# 3) 何もしない — `gh` CLI がインストール済み・認証済みなら自動取得
./proxine.py socks5
```

レート制限や無効トークンの場合、レポート末尾に明確な警告が表示されます。

------------------------------------------------------------

## 出力

### 1. プログレスバー

実行中、stderr に 2 フェーズで表示：

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- 20 文字の `█/░` バー、パーセンテージ、完了/全体
- フェーズラベル：`fetching`（HTTP）または `enriching`（GitHub commit API）
- `✓` 成功、`x` 失敗
- `+N` このソースからの新規プロキシ
- `total N` 累積ユニーク合計

非 TTY では自動的に静音（リダイレクト先を汚しません）。

### 2. ソース状態テーブル

実行終了時、stderr に：

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
  OK     `--fresh` 範囲内で新鮮；プロキシを使用
  LIVE   新鮮度情報なし（動的 API）；プロキシを使用
  STALE  `--fresh` より古い；プロキシを出力から除外
  FAIL   取得エラー；寄与なし
```

並び順：OK（最も新しいものが上）→ LIVE → STALE → FAIL。

### 3. サマリーボックス

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### 出力モード一覧

| コマンド | stdout | stderr |
|---|---|---|
| `proxine http` | プロキシリスト | プログレス → 状態テーブル → サマリー |
| `proxine http -v` | プロキシリスト | 行単位ログ → テーブル |
| `proxine http -o f.lst` | （空） | プログレス → テーブル |
| `proxine http -s` | プロキシリスト | （空） |
| `proxine http -o f.lst -s` | （空） | （空） |

------------------------------------------------------------

## ソース一覧

**60 のユニークソース**、**166 のプロトコルエンドポイント**を提供します。
すべて `sources.py` に定義されており、新規追加は 1 行で済みます。

### GitHub raw リスト（51 リポジトリ）

| Repo | プロトコル |
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

### 動的 API および HTML ソース（9 エンドポイント）

| Endpoint | 種別 | プロトコル |
|---|---|---|
| `api.proxyscrape.com` | 公開 API | http, https, socks4, socks5 |
| `pubproxy.com` | 公開 API | http, https, socks4, socks5 |
| `proxyspace.pro` | プレーンテキスト | http, https, socks5 |
| `spys.me` | プレーンテキスト | socks4, socks5 |
| `free-proxy-list.net` | HTML スクレイパー | http |
| `www.google-proxy.net` | HTML スクレイパー | http, https |
| `www.ipaddress.com` | HTML スクレイパー | http, https |
| `www.socks-proxy.net` | HTML スクレイパー | socks4 |
| `www.sslproxies.org` | HTML スクレイパー | https |

------------------------------------------------------------

## 自動化

Proxine は単発実行向けに設計されています。定期更新には cron /
systemd-timer / GitHub Actions でラップしてください。パイプラインには
`-s` と `-o` が推奨されます：

```bash
# Cron: 1 時間毎に SOCKS5 リストを更新
0 * * * * cd ~/proxine && ./proxine.py socks5 -s -o /var/lib/proxies/socks5.lst

# Proxy Profiler と連鎖（生存確認 + elite テスト）
./proxine.py http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

------------------------------------------------------------

## 関連ツール

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  生存確認、匿名性（Elite/Anonymous/Transparent）、CloudFlare および
  Google 通過テストのマルチスレッドツール。
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** —
  Windows 用 GUI プロキシローテーター。
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  Windows 用リスト検証ツール。

------------------------------------------------------------

## ライセンス

オープンソース。再配布、改変、商用・私的利用が可能です。派生作品では原著者
（Özgür Koca）の表示を維持してください。ソフトウェアは「現状のまま」提供さ
れ、利用に伴うリスクはすべてユーザーが負います。

## 著者

**Özgür Koca** — 職業[高校](https://samsuneml.meb.k12.tr/)の教師。
GitHub: [enseitankado](https://github.com/enseitankado) · ブログ:
[tankado.com](https://www.tankado.com)

## サポート

役に立ったら ⭐ をどうぞ。コーヒーを奢ってくれる方は
[こちら](https://www.buymeacoffee.com/ozgurkoca)。

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)
