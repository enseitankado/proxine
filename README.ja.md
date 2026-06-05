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
<b>86 のユニークソース</b> · <b>220 のエンドポイント</b><br>
HTTP: 72 &nbsp;·&nbsp; HTTPS: 48 &nbsp;·&nbsp; SOCKS4: 49 &nbsp;·&nbsp; SOCKS5: 51
</p>

> Proxine はアグリゲーターであり、品質チェッカーではありません。実際に動作
> する真の elite プロキシが必要な場合は、出力を
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler) のような
> テスターにパイプしてください。

------------------------------------------------------------

## 機能

- **86 種類のソース**、220 エンドポイント — GitHub raw リスト + 8 個の
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
./proxine.py -p <http|https|socks4|socks5> [オプション]
```

### フラグ

| ロング | ショート | デフォルト | 説明 |
|---|---|---|---|
| `--protocol` | `-p` | — | **必須。** 採集するプロトコル: `http`、`https`、`socks4`、`socks5`。 |
| `--format` | `-f` | `ip-port` | 出力形式。`url` で `<proto>://IP:PORT`。 |
| `--timeout` | `-t` | `15` | ソース毎の HTTP タイムアウト（秒）。 |
| `--concurrency` | `-c` | `1` | 並列リクエスト数。多いほど速くソケット消費も増加。 |
| `--retries` | `-r` | `2` | 失敗ソース毎のリトライ回数。 |
| `--max-ports` | `-m` | `5` | 1 つの IP が N 個以上の異なるポートで現れたら完全に削除（ポートスキャナ/ハニーポット除去）。`0` で無効化。 |
| `--fresh` | `-F` | `86400` | N 秒より古いソースを除外。`0` で無効化。 |
| `--github-token` | `-g` | — | GitHub PAT。なければ `$GITHUB_TOKEN`、次に `gh auth token`。 |
| `--output` | `-o` | — | プロキシリストを FILE に書き込み；stdout は空。 |
| `--lang` | `-L` | 自動 | UI 言語: `tr`、`en`、`de`、`es`、`ru`、`zh`。指定なしなら `$PROXINE_LANG`/`$LANG`/ロケールから自動検出。 |
| `--strict-ports` / `--no-strict-ports` | — | 有効 | 宣言されたプロトコルファミリに合わないポートのプロキシを削除（例: SOCKS 宣言のポート 80）。 |
| `--silent` | `-s` | — | すべての stderr 出力を抑制。 |

### 例

```bash
# HTTPS プロキシを stdout へ（デフォルト鮮度フィルタ: 24h）
./proxine.py -p https

# SOCKS5 リストをファイルへ、高速化
./proxine.py -p socks5 -c 32 -o socks5.lst

# 直近 1 時間に更新されたソースのみ
./proxine.py -p http -F 3600

# URL 形式出力: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# 静音モード — パイプライン向け
./proxine.py -p http -s | grep '^192\.'

# Proxy Profiler と連鎖 — 3 例
# 1) Elite (L1) 匿名 HTTP プロキシを抽出
./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o elite_http.lst

# 2) SOCKS5 — judge をスキップ（高速）、Cloudflare WAF を通過するライブ proxy のみ保持
./proxine.py -p socks5 -s | python3 ~/proxy-profiler/proxyprof.py -p socks5 --no-judge --access-test cloudflare -o cf_socks5.lst

# 3) HTTPS — elite + 国フィルタ (US/DE/JP) + Google アクセステスト
./proxine.py -p https -s | python3 ~/proxy-profiler/proxyprof.py -p https -l 1 --country US,DE,JP --access-test google -o elite_us_de_jp_https.lst
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
./proxine.py -p socks5 -g ghp_xxx

# 2) 環境変数
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) 何もしない — `gh` CLI がインストール済み・認証済みなら自動取得
./proxine.py -p socks5
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
| `proxine -p http` | プロキシリスト | ソース別ログ + プログレス → 状態テーブル → サマリー |
| `proxine -p http -o f.lst` | （空） | ソース別ログ + プログレス → テーブル |
| `proxine -p http -s` | プロキシリスト | （空） |
| `proxine -p http -o f.lst -s` | （空） | （空） |

------------------------------------------------------------

## ソース一覧

合計 **86 のユニークソース**、**220 のプロトコルエンドポイント**を提供します。
すべて `sources.py` に定義されており、新しいソースの追加は 1 行の変更で済みます。

### GitHub raw リスト (77 リポジトリ)

| リポジトリ | プロトコル |
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

### GitLab リスト (1 リポジトリ)

| リポジトリ | プロトコル |
|---|---|
| `gitlab.com/syedusama5556/auto-proxy-list-generator` | http |

### 動的 API および HTML ソース (8 エンドポイント)

| エンドポイント | 種類 | プロトコル |
|---|---|---|
| `api.proxyscrape.com` | 公開 API | http, https, socks4, socks5 |
| `free-proxy-list.net` | HTML スクレイパー | http |
| `proxyspace.pro` | プレーンテキストリスト | https, socks5 |
| `pubproxy.com` | 公開 API | http, https, socks4, socks5 |
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
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# 毎晩 elite HTTP ビルド (proxine + profiler チェーン)
0 3 * * * cd ~/proxine && ./proxine.py -p http -s | python3 ~/proxy-profiler/proxyprof.py -p http -l 1 -o /var/lib/proxies/elite_http.lst
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
