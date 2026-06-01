#!/usr/bin/env python3
"""
Proxine — aggregate free proxy lists from dozens of public sources.

Usage:
    proxine.py -p <http|https|socks4|socks5> [options]

Example:
    proxine.py -p https > https_proxies.lst
    proxine.py -p socks5 -f url -c 32

Stdout : unique, sorted `IP:PORT` lines (or `<proto>://IP:PORT` with --format url).
Stderr : per-source log lines, animated progress bar (TTY), freshness table, and
         summary (all suppressed by --silent).
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import NamedTuple

from sources import SOURCES
from i18n import t, set_language, SUPPORTED as LANGS

DEFAULT_TIMEOUT = 15
DEFAULT_CONCURRENCY = 1
DEFAULT_RETRIES = 2
DEFAULT_FRESH = 24 * 60 * 60  # 24 hours, in seconds
DEFAULT_MAX_PORTS = 5  # Aynı IP için >N port duyuran kaynaklar genelde port tarayıcı / honeypot.
# Token yokken GitHub commits API saatlik 60 isteğe sınırlı. Tek runde 55'i aşma;
# 5 isteklik buffer aynı saatte başka GitHub erişimleri için (gh CLI, başka tool) kalsın.
GITHUB_UNAUTHED_BUDGET = 55

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
)

# IPv4 (her oktet 0–255) + port (1–65535). 999.x.x.x veya port=99999 elenir.
_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
IP_PORT_RE = re.compile(rf"\b({_OCTET}(?:\.{_OCTET}){{3}}):([1-9]\d{{0,4}})\b")


# ---------------------------------------------------------------------------
# Parsers — her biri (text, proto) → Iterable[str ("ip:port")]
# ---------------------------------------------------------------------------

def parse_regex(text: str, proto: str) -> Iterable[str]:
    for m in IP_PORT_RE.finditer(text):
        ip, port_str = m.group(1), m.group(2)
        port = int(port_str)
        if 1 <= port <= 65535:
            yield f"{ip}:{port}"


def parse_ndjson(text: str, proto: str) -> Iterable[str]:
    """fate0/proxyBEE şeması: satır satır JSON."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("type") == proto and j.get("anonymity") == "high_anonymous":
            host, port = j.get("host"), j.get("port")
            if host and port:
                yield f"{host}:{port}"


def parse_stamparm(text: str, proto: str) -> Iterable[str]:
    """stamparm/aux: tek JSON dizisi."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    if not isinstance(data, list):
        return
    for item in data:
        if (
            isinstance(item, dict)
            and item.get("proto") == proto
            and item.get("type") == "elite"
        ):
            ip, port = item.get("ip"), item.get("port")
            if ip and port:
                yield f"{ip}:{port}"


def parse_geonode(text: str, proto: str) -> Iterable[str]:
    """proxylist.geonode.com: satır satır {"data": {...}} zarfı."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError:
            continue
        j = envelope.get("data") if isinstance(envelope, dict) else None
        if not isinstance(j, dict):
            continue
        if j.get("type") == proto and j.get("anonymity") == "high_anonymous":
            host, port = j.get("host"), j.get("port")
            if host and port:
                yield f"{host}:{port}"


PARSERS = {
    "regex": parse_regex,
    "ndjson": parse_ndjson,
    "stamparm": parse_stamparm,
    "geonode": parse_geonode,
}


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

class SourceResult(NamedTuple):
    url: str
    proxies: list[str]
    last_modified: datetime | None  # None if header missing OR fetch failed
    error: str | None               # None on success


def _parse_http_date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except (TypeError, ValueError):
        return None


def fetch(url: str, timeout: int, retries: int) -> tuple[str, datetime | None]:
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                enc = resp.headers.get_content_charset() or "utf-8"
                last_mod = _parse_http_date(resp.headers.get("Last-Modified"))
                return raw.decode(enc, errors="replace"), last_mod
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    assert last_err is not None
    raise last_err


# Parse-time port filtresi: 2026-05 audit'inde tespit edildiği üzere bazı kaynaklar
# yanlış protokol etiketiyle listeleniyor (örn. SOCKS5 dosyası ama içeriği port 80
# HTTP proxy'leri). Aşağıdaki setler "neredeyse her zaman X ailesinde" portları
# kapsar; bir kaynak SOCKS beyan edip port 80'de proxy veriyorsa eleminir.
# Not: kullanıcı --no-strict-ports ile bu filtreyi kapatabilir.
HTTP_FAMILY_PORTS = frozenset({
    80, 81, 88, 443, 808, 999, 3128, 3129, 4443, 8000, 8001, 8008, 8080,
    8081, 8085, 8088, 8090, 8118, 8181, 8443, 8888, 8889, 8989, 9080, 9090, 9999,
})
SOCKS_FAMILY_PORTS = frozenset({
    1080, 1081, 1085, 1086, 1087, 1088, 1090, 1091, 1888, 4145, 4153,
    5678, 7777, 7890, 9050, 9051,
})
# Sadece "diğer ailenin" portlarındaysa eler; bilinmeyen portlara dokunmaz.
_EXCLUDE_FOR_PROTO = {
    "http":   SOCKS_FAMILY_PORTS,
    "https":  SOCKS_FAMILY_PORTS,
    "socks4": HTTP_FAMILY_PORTS,
    "socks5": HTTP_FAMILY_PORTS,
}


def _port_matches_proto(proxy: str, proto: str) -> bool:
    """Proxy'nin portu beyan edilen protokol ailesiyle çelişiyor mu?

    True döner → kabul; False → at. Sadece kesin yanlış-aile portlarını
    dışlar; nadir/özel portlar (örn. 8443'te SOCKS) kabul edilir."""
    try:
        port = int(proxy.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return False
    excluded = _EXCLUDE_FOR_PROTO.get(proto, frozenset())
    return port not in excluded


def _task(
    url: str,
    parser_name: str,
    proto: str,
    timeout: int,
    retries: int,
    strict_ports: bool = True,
) -> SourceResult:
    try:
        text, last_modified = fetch(url, timeout=timeout, retries=retries)
    except Exception as e:  # noqa: BLE001  fetch hatası tek tek raporlanır
        return SourceResult(url=url, proxies=[], last_modified=None,
                            error=f"{type(e).__name__}: {e}")
    parser = PARSERS.get(parser_name, parse_regex)
    proxies = list(parser(text, proto))
    if strict_ports:
        proxies = [p for p in proxies if _port_matches_proto(p, proto)]
    return SourceResult(url=url, proxies=proxies,
                        last_modified=last_modified, error=None)


# raw.githubusercontent.com Last-Modified header'ı vermez. Bu URL'ler için commit
# zamanını GitHub API'den çekip yaşı doldururuz. Token ile 5000 req/h, token'sız
# yalnızca 60 req/h vardır; tek bir Proxine çalışmasında 60'tan fazla GitHub
# kaynağına bakıldığı için token olmadan büyük olasılıkla rate limit'e takılır.
GITHUB_RAW_RE = re.compile(
    r"^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)$"
)


def resolve_github_token(cli_token: str | None) -> str | None:
    """Token öncelik sırası: --github-token > $GITHUB_TOKEN > `gh auth token`."""
    if cli_token:
        return cli_token.strip() or None
    env = os.environ.get("GITHUB_TOKEN")
    if env:
        return env.strip() or None
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode == 0:
        token = result.stdout.strip()
        return token or None
    return None


class GithubAPIState:
    """Thread-safe GitHub API durum izleyici. 401 (bad token) veya 403/429
    (rate limit) alındığında flag set edilir; sonraki çağrılar gereksiz istek
    atmamak için bunu kontrol eder."""

    def __init__(self, token: str | None) -> None:
        self.token = token
        # Token yoksa bir runde atılabilecek API isteği üst sınırı; None = sınırsız.
        self.budget: int | None = None if token else GITHUB_UNAUTHED_BUDGET
        self._rate_limited = False
        self._bad_token = False
        self._budget_skipped = 0
        self._lock = threading.Lock()

    @property
    def rate_limited(self) -> bool:
        return self._rate_limited

    @property
    def bad_token(self) -> bool:
        return self._bad_token

    @property
    def blocked(self) -> bool:
        return self._rate_limited or self._bad_token

    @property
    def budget_skipped(self) -> int:
        return self._budget_skipped

    def mark_rate_limited(self) -> None:
        with self._lock:
            self._rate_limited = True

    def mark_bad_token(self) -> None:
        with self._lock:
            self._bad_token = True

    def set_budget_skipped(self, n: int) -> None:
        with self._lock:
            self._budget_skipped = n


def _github_commit_time(
    url: str, timeout: int, state: GithubAPIState
) -> datetime | None:
    if state.blocked:
        return None
    m = GITHUB_RAW_RE.match(url)
    if not m:
        return None
    owner, repo, branch, path = m.groups()
    api = (
        f"https://api.github.com/repos/{owner}/{repo}/commits"
        f"?path={urllib.parse.quote(path)}"
        f"&sha={urllib.parse.quote(branch)}&per_page=1"
    )
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    if state.token:
        headers["Authorization"] = f"Bearer {state.token}"
    try:
        req = urllib.request.Request(api, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            state.mark_bad_token()
        elif e.code in (403, 429) and e.headers.get("X-RateLimit-Remaining") == "0":
            state.mark_rate_limited()
        return None
    except (urllib.error.URLError, TimeoutError, OSError,
            json.JSONDecodeError, ValueError):
        return None
    if isinstance(data, list) and data and isinstance(data[0], dict):
        ts = data[0].get("commit", {}).get("committer", {}).get("date")
        if ts:
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                return None
    return None


def enrich_github_freshness(
    results: list[SourceResult],
    timeout: int,
    concurrency: int,
    state: GithubAPIState,
    progress: "Progress | None" = None,
) -> list[SourceResult]:
    """Last-Modified vermeyen raw.githubusercontent.com kaynaklarını commit zamanıyla doldur.

    Token yoksa state.budget ile sınırlanır (saatlik 60'lık limiti aşmamak için);
    sınır üstündeki adaylar LIVE'da kalır ve state.budget_skipped'a sayılır."""
    candidates = [
        i for i, r in enumerate(results)
        if r.error is None and r.last_modified is None and GITHUB_RAW_RE.match(r.url)
    ]
    if not candidates:
        return results
    if state.budget is not None and len(candidates) > state.budget:
        state.set_budget_skipped(len(candidates) - state.budget)
        candidates = candidates[: state.budget]
    if progress is not None:
        progress.start_phase(t("progress.enriching"), len(candidates), show_contrib=False)
    with cf.ThreadPoolExecutor(max_workers=concurrency) as pool:
        future_to_idx = {
            pool.submit(_github_commit_time, results[i].url, timeout, state): i
            for i in candidates
        }
        for fut in cf.as_completed(future_to_idx):
            i = future_to_idx[fut]
            ts = fut.result()
            if ts is not None:
                results[i] = results[i]._replace(last_modified=ts)
            if progress is not None:
                progress.update(results[i])
    return results


# Progress satırını ANSI içerebileceği için truncate/ljust işlemlerinin
# yalnızca GÖRÜNÜR karakterleri sayması gerekir. Aksi halde line_width sınırı
# ANSI ortasında kesip terminali bozar veya gereksiz wrap oluşur.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _visible_len(s: str) -> int:
    return len(_ANSI_RE.sub("", s))


def _visible_truncate(s: str, max_visible: int) -> str:
    """ANSI escape'leri sayılmadan max_visible görünür karaktere kes."""
    out: list[str] = []
    seen = 0
    i = 0
    n = len(s)
    while i < n and seen < max_visible:
        m = _ANSI_RE.match(s, i)
        if m:
            out.append(m.group(0))
            i = m.end()
        else:
            out.append(s[i])
            seen += 1
            i += 1
    # Sonda kalan ANSI'leri de ekle (reset escape'in dışarıda kalması terminali bozar).
    while i < n:
        m = _ANSI_RE.match(s, i)
        if not m:
            break
        out.append(m.group(0))
        i = m.end()
    return "".join(out)


def _visible_ljust(s: str, width: int) -> str:
    v = _visible_len(s)
    return s if v >= width else s + " " * (width - v)


def _load_existing_proxies(path: str) -> set[str]:
    """Mevcut -o çıktı dosyasını oku, `IP:PORT` setine normalize et.

    Hem 'ip:port' hem 'proto://ip:port' formatlarını kabul eder; geçersiz veya
    boş satırları atlar. Dosya yoksa ya da okunamazsa boş set döner — hata değil
    bilgi sinyali (ilk runde dosya henüz olmayabilir)."""
    out: set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "://" in line:
                    line = line.split("://", 1)[1]
                # Hafif sağlamlık kontrolü: IP:PORT şeklinde mi?
                if IP_PORT_RE.fullmatch(line):
                    out.add(line)
    except (OSError, UnicodeDecodeError):
        return set()
    return out


class Progress:
    """Çok fazlı tek satır TTY ilerleme göstergesi (\\r ile yenilenir).

    Faz 1 (fetching) — `-o` verilmemişse:
        [████████████░░░░░░░░]  60%  24/40  fetching  ✓ github.com/x/y  +1,234  total 56,789
    Faz 1 (fetching) — `-o FILE` verilmişse (sol tarafta canlı diff):
        [████████████░░░░░░░░]  60%  24/40  =55,300 -1,400 +1,489  fetching  ✓ github.com/x/y  +1,234
            (dosya yoksa: prior=∅ → =0 -0 +N şeklinde başlar)
    Faz 2 (enriching commit times): fetch fazındaki tail (total veya diff) dondurulup gösterilir.
    """

    BAR_WIDTH = 20
    SOURCE_WIDTH = 38
    LABEL_WIDTH = 9   # "fetching " / "enriching"
    # LINE_WIDTH artık dinamik (init'te terminal genişliğine göre belirlenir).
    # 140 minimum tasarım hedefi; daha dar terminallerde source ismi kısaltılır.

    def __init__(
        self,
        enabled: bool,
        file=sys.stderr,
        prior: set[str] | None = None,
        compare: bool = False,
        log_enabled: bool = True,
    ) -> None:
        self.file = file
        # Yalnızca etkin VE stderr bir TTY ise animasyon göster. Pipe/dosyada sessiz.
        self.enabled = enabled and file.isatty()
        # Her source için "[ ok ]/[fail] N URL" kalıcı log satırı bas. Silent'ta kapat.
        self.log_enabled = log_enabled
        # Log satırlarındaki [ ok ]/[fail] etiketlerini ve =/-/+ sayaçlarını renklendir.
        self.color_enabled = _color_enabled(file)
        # Progress'in üzerinde 1 boşluk satırı tutmak için flag: ilk render'dan
        # sonra her log akışında \033[A ile boşluğa çıkıp orayı log ile dolduruyor,
        # eski progress satırını temizleyip yeni boşluk + progress yazıyoruz.
        self._rendered_once = False
        # Terminal genişliği: \r ile satır yenileyeceğimiz için bu sınırı aşmamak şart;
        # aksi halde satır wrap olur ve önceki fiziksel satır eski içerikle kalır
        # ("yapıtğın değişiklikler gözükmüyor" tipik semptomu budur).
        try:
            cols = shutil.get_terminal_size(fallback=(120, 24)).columns
        except (AttributeError, OSError, ValueError):
            cols = 120
        self.line_width = max(60, cols - 1)
        # < 140 col: compact mod. `fetching` label'ı ve `+contrib` sütununu at,
        # bar'ı küçült, source ismini terminale göre kıs. Diff/total sütunlarının
        # her zaman görünmesini garanti et.
        self.compact = self.line_width < 140
        if self.compact:
            self.bar_width = 12
            # Compact sabit: `[12bar] NNN% NN/NN  =  {7}  -  {7}  +  {7}  ✓ ` + source
            # ≈ 1+12+1+1+3+1+2+5+2+34+2+1+1 = 66. Source en az 12 char.
            self.source_width = max(12, self.line_width - 66)
        else:
            self.bar_width = self.BAR_WIDTH
            self.source_width = self.SOURCE_WIDTH
        self.matches = 0           # birikmiş gross proxy katkıları (dedup'sız, fetch boyunca)
        self.label = ""
        self.total = 0
        self.done = 0
        # Faz "fetching" mi yoksa "enriching" mi: +N sütununu kontrol eder.
        self.show_contrib = True
        # -o ile baseline karşılaştırması açık mı? (Dosya boş/eksik olsa bile açık.)
        self.compare = compare
        # Baseline IP:PORT seti. Dosya yoksa boş.
        self.prior: set[str] = prior or set()
        # Şu ana kadar görülen benzersiz proxy seti (dedup).
        self.seen: set[str] = set()

    @staticmethod
    def _short(url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            return url
        label = _GIT_HOSTS.get(parsed.netloc)
        if label:
            parts = parsed.path.lstrip("/").split("/", 2)
            if len(parts) >= 2:
                return f"{label}/{parts[0]}/{parts[1]}"
        return parsed.netloc or url

    def start_phase(self, label: str, total: int, show_contrib: bool = True) -> None:
        self.label = label
        self.total = total
        self.done = 0
        self.show_contrib = show_contrib

    def _c(self, text: str, color: str) -> str:
        """ANSI renkle sar; renk kapalıysa düz metin döner."""
        if self.color_enabled:
            return f"{_ANSI[color]}{text}{_ANSI['reset']}"
        return text

    def _format_log(self, result: SourceResult, contributed: int) -> str:
        """Source başına kalıcı log satırı: `[ ok ] N [=S -G +N] URL` veya `[fail] URL: err`.

        Sayı formatı: contributed `>7,` (100,661 gibi 7-char değerler taşmaz, satırlar
        arası `=` kolonu kaymaz). Diff sayaçları `>7,` + işaretten sonra 2 boşluk.
        """
        if result.error:
            return f"{self._c('[fail]', 'red')} {result.url}: {result.error}"
        ok = self._c("[ ok ]", "green")
        if self.compare:
            same = len(self.seen & self.prior)
            new_n = len(self.seen) - same
            gone = len(self.prior) - same
            same_part = self._c(f"=  {same:>7,}", "green")
            gone_part = self._c(f"-  {gone:>7,}", "red")
            new_part = self._c(f"+  {new_n:>7,}", "yellow")
            return (
                f"{ok} {contributed:>7,}  "
                f"{same_part}  {gone_part}  {new_part}  {result.url}"
            )
        return f"{ok} {contributed:>7,}  {result.url}"

    def _render(self, result: SourceResult, contributed: int) -> None:
        """Animasyonlu progress satırını mevcut konuma yaz (\\r ile)."""
        if not self.enabled or self.total == 0:
            return

        pct = self.done / self.total
        filled = int(self.bar_width * pct)
        bar = "█" * filled + "░" * (self.bar_width - filled)
        marker = "x" if result.error else "✓"

        short = self._short(result.url)
        if len(short) > self.source_width:
            short = short[: self.source_width - 1] + "…"

        digits = len(str(self.total))

        # Sol-orta info: -o varsa diff (=aynı -gitmiş +yeni), yoksa "total <gross>".
        # İşaretten sonra 2 boşluk + `>7,` field → büyük sayılarda hizalama bozulmaz.
        # Log satırlarıyla AYNI renk kuralı: = yeşil, - kırmızı, + sarı, total sarı.
        # gitmiş sayacı koşan değerdir — sonraki kaynaklar getirirse düşer.
        if self.compare:
            same = len(self.seen & self.prior)
            new_n = len(self.seen - self.prior)
            gone = len(self.prior) - same
            info = (
                f"{self._c(f'=  {same:>7,}', 'green')}  "
                f"{self._c(f'-  {gone:>7,}', 'red')}  "
                f"{self._c(f'+  {new_n:>7,}', 'yellow')}"
            )
        else:
            info = self._c(f"{t('progress.total')} {self.matches:>9,}", "yellow")

        if self.compact:
            # Compact: label ve contrib yok. Diff/total sol tarafta, source sağda kalır.
            line = (
                f"\r[{bar}] {pct * 100:3.0f}%  "
                f"{self.done:>{digits}}/{self.total}  "
                f"{info}  "
                f"{marker} {short:<{self.source_width}}"
            )
        else:
            contrib = (
                ""
                if not self.show_contrib
                else (t("progress.fail") if result.error else f"+{contributed:,}")
            )
            line = (
                f"\r[{bar}] {pct * 100:3.0f}%  "
                f"{self.done:>{digits}}/{self.total}  "
                f"{info}  "
                f"{self.label:<{self.LABEL_WIDTH}} "
                f"{marker} {short:<{self.source_width}}  "
                f"{contrib:>10}"
            )
        # ANSI-aware truncate ve ljust: görünür uzunluk üzerinden, escape ortasında
        # kesme/wrap riski yok. line_width+1 → \r dahil.
        truncated = _visible_truncate(line, self.line_width + 1)
        padded = _visible_ljust(truncated, self.line_width + 1)
        self.file.write(padded)
        self.file.flush()

    def update(self, result: SourceResult) -> None:
        """State güncelle + progress'i re-render. Kalıcı log basMA (enrichment fazı için)."""
        self.done += 1
        contributed = 0 if result.error else len(result.proxies)
        if self.show_contrib and result.error is None:
            self.matches += contributed
            self.seen.update(result.proxies)
        self._render(result, contributed)

    def report(self, result: SourceResult) -> None:
        """State güncelle + kalıcı log satırı bas + progress'i alt satıra re-render.

        Akış (TTY + log_enabled):
          • İlk çağrı:  \\r\\033[K{log}\\n\\n  → log + 1 boşluk + _render progress
          • Sonraki:    \\033[A\\r\\033[K{log}\\n\\033[K\\n  → boşluğu log ile değiştir,
                        eski progress satırını temizle, yeni boşluk için \\n,
                        sonra _render alt satıra yeni progress yazar.
        Sonuç: log akışı yukarı kayar, progress bar'ın TAM ÜZERİNDE 1 boş satır kalır.
        """
        self.done += 1
        contributed = 0 if result.error else len(result.proxies)
        if self.show_contrib and result.error is None:
            self.matches += contributed
            self.seen.update(result.proxies)

        if self.log_enabled:
            log_line = self._format_log(result, contributed)
            if self.enabled:
                if self._rendered_once:
                    self.file.write(f"\033[A\r\033[K{log_line}\n\033[K\n")
                else:
                    self.file.write(f"\r\033[K{log_line}\n\n")
            else:
                # TTY değil (pipe/redirect): saf log satırı, ANSI yok, blank yok.
                self.file.write(f"{log_line}\n")

        self._render(result, contributed)
        if self.enabled and self.log_enabled:
            self._rendered_once = True
        if self.log_enabled or self.enabled:
            self.file.flush()

    def finish(self) -> None:
        if not self.enabled:
            return
        # Progress satırını temizle. _rendered_once ise üstündeki boşluk satırını
        # da kaldır ki sonraki stderr çıktısı (status table, summary) loglardan
        # hemen sonra başlasın — fazladan boş satır kalmasın.
        self.file.write("\r\033[K")
        if self._rendered_once:
            self.file.write("\033[A\r\033[K")
        self.file.flush()


def collect(
    protocol: str,
    timeout: int,
    concurrency: int,
    retries: int,
    progress: Progress | None = None,
    strict_ports: bool = True,
) -> list[SourceResult]:
    sources = SOURCES[protocol]
    results: list[SourceResult] = []

    with cf.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(_task, url, parser, protocol, timeout, retries, strict_ports)
            for url, parser in sources
        ]
        for fut in cf.as_completed(futures):
            r = fut.result()
            results.append(r)
            if progress is not None:
                # report() kalıcı log satırını basar VE progress'i alt satıra re-render eder.
                progress.report(r)

    # finish() ÇAĞIRMA — enrichment fazı için bar açık kalsın; main yönetir.
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _sort_key(s: str) -> tuple[tuple[int, int, int, int], int]:
    ip, _, port = s.partition(":")
    a, b, c, d = (int(o) for o in ip.split("."))
    try:
        port_i = int(port)
    except ValueError:
        port_i = 0
    return (a, b, c, d), port_i


def _fmt_age(now: datetime, lm: datetime | None, error: str | None) -> str:
    if error is not None:
        return "FAIL"
    if lm is None:
        return "live"
    delta = max(0.0, (now - lm).total_seconds())
    if delta < 90:
        return f"{int(delta)}s"
    if delta < 5400:
        return f"{int(delta / 60)}m"
    if delta < 86400:
        return f"{int(delta / 3600)}h"
    if delta < 7 * 86400:
        return f"{int(delta / 86400)}d"
    return f"{int(delta / (7 * 86400))}w"


def is_stale(r: SourceResult, now: datetime, fresh_seconds: int) -> bool:
    """Kaynak --fresh eşiğine göre eskimiş mi? error veya last_modified yoksa False."""
    if fresh_seconds <= 0 or r.error is not None or r.last_modified is None:
        return False
    return (now - r.last_modified).total_seconds() > fresh_seconds


# Tabloda tanınan git host'lar; raw URL şeması "host.com/<owner>/<repo>/.../path".
_GIT_HOSTS = {
    "raw.githubusercontent.com": "github.com",
    "gitee.com": "gitee.com",
    "codeberg.org": "codeberg.org",
    "gitverse.ru": "gitverse.ru",
    "gitflic.ru": "gitflic.ru",
    "atomgit.com": "atomgit.com",
    "gitlab.com": "gitlab.com",
    "git.sr.ht": "git.sr.ht",
    "bitbucket.org": "bitbucket.org",
}


def _short_source(url: str) -> str:
    """Tabloda gösterilecek kısa kaynak adı: '<host>/<owner>/<repo>' veya hostname."""
    try:
        p = urllib.parse.urlparse(url)
    except ValueError:
        return url
    label = _GIT_HOSTS.get(p.netloc)
    if label:
        parts = p.path.lstrip("/").split("/")
        if len(parts) >= 2:
            return f"{label}/{parts[0]}/{parts[1]}"
    return p.netloc or url


def _classify(r: SourceResult, now: datetime, fresh_seconds: int) -> str:
    if r.error is not None:
        return "FAIL"
    if is_stale(r, now, fresh_seconds):
        return "STALE"
    if r.last_modified is None:
        return "LIVE"
    return "OK"


def print_status_table(
    results: list[SourceResult],
    fresh_seconds: int,
    file=sys.stderr,
) -> None:
    """Kaynak durumunu Unicode kutu-çizimi tablosu olarak yaz."""
    now = datetime.now(timezone.utc)

    def sort_key(r: SourceResult) -> tuple:
        # OK (en taze üstte) → LIVE → STALE → FAIL
        status = _classify(r, now, fresh_seconds)
        order = {"OK": 0, "LIVE": 1, "STALE": 2, "FAIL": 3}[status]
        age = (now - r.last_modified).total_seconds() if r.last_modified else 0.0
        return (order, age, r.url)

    rows: list[tuple[str, str, str, str]] = []
    for r in sorted(results, key=sort_key):
        status = _classify(r, now, fresh_seconds)
        age = "—" if (r.error or r.last_modified is None) else _fmt_age(now, r.last_modified, None)
        count = "—" if r.error else f"{len(r.proxies):,}"
        rows.append((status, age, count, _short_source(r.url)))

    headers = (
        t("status.col.status"),
        t("status.col.age"),
        t("status.col.proxies"),
        t("status.col.source"),
    )
    w = [max(len(h), max((len(row[i]) for row in rows), default=0)) for i, h in enumerate(headers)]

    def line(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (c + 2) for c in w) + right

    def row(cells: tuple[str, str, str, str]) -> str:
        # STATUS sola, AGE/PROXIES sağa, SOURCE sola yaslı
        return (
            f"│ {cells[0]:<{w[0]}} "
            f"│ {cells[1]:>{w[1]}} "
            f"│ {cells[2]:>{w[2]}} "
            f"│ {cells[3]:<{w[3]}} │"
        )

    print(line("┌", "┬", "┐"), file=file)
    print(row(headers), file=file)
    print(line("├", "┼", "┤"), file=file)
    for r_row in rows:
        print(row(r_row), file=file)
    print(line("└", "┴", "┘"), file=file)
    print(
        t("status.legend.ok") + "\n"
        + t("status.legend.live") + "\n"
        + t("status.legend.stale") + "\n"
        + t("status.legend.fail"),
        file=file,
    )


def _human_secs(s: int) -> str:
    """Saniyeyi insan dostu kısa biçime çevir: 90→'1m', 3600→'1h', 86400→'1d'."""
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


def print_settings_box(
    args: argparse.Namespace,
    github_state: "GithubAPIState",
    prior_count: int,
    n_sources: int,
    file=sys.stderr,
) -> None:
    """Run başlamadan önce parsed CLI argümanlarını + ortam durumunu 2-sütun kutuda yaz."""
    auth = (
        t("settings.value.token_auth")
        if github_state.token
        else t("settings.value.unauthed", budget=GITHUB_UNAUTHED_BUDGET)
    )
    off = t("settings.value.off")
    stdout_v = t("settings.value.stdout")

    # CLI flag'leri uzun formda gösterilir (-p yerine --protocol vs.). sources/baseline
    # CLI argümanı değil — runtime info — `t()` ile çevriliyor.
    # CLI parametreleri (-- prefix) önce, runtime info (sources/baseline) sonra.
    rows: list[tuple[str, str]] = [
        ("--protocol",        args.protocol),
        ("--output",          args.output or stdout_v),
        ("--format",          args.format),
        ("--concurrency",     str(args.concurrency)),
        ("--timeout",         f"{args.timeout}s"),
        ("--retries",         str(args.retries)),
        ("--fresh",           off if args.fresh == 0 else _human_secs(args.fresh)),
        ("--max-ports",       off if args.max_ports == 0
                              else t("settings.value.drop_thresh", n=args.max_ports)),
        ("--strict-ports",    t("settings.value.on") if args.strict_ports else off),
        ("--github-token",    auth),
        (t("settings.sources"), str(n_sources)),
    ]
    if args.output:
        baseline = (
            t("settings.value.baseline_loaded", n=prior_count)
            if prior_count
            else t("settings.value.baseline_empty")
        )
        rows.append((t("settings.baseline"), baseline))

    w_key = max(len(k) for k, _ in rows)
    w_val = max(len(v) for _, v in rows)

    def hline(left: str, mid: str, right: str) -> str:
        return left + "─" * (w_key + 2) + mid + "─" * (w_val + 2) + right

    def fmt_row(k: str, v: str) -> str:
        return f"│ {k:<{w_key}} │ {v:<{w_val}} │"

    print(hline("┌", "┬", "┐"), file=file)
    for k, v in rows:
        print(fmt_row(k, v), file=file)
    print(hline("└", "┴", "┘"), file=file)


def print_summary_box(
    protocol: str,
    proxy_count: int,
    output_path: str | None,
    n_ok: int,
    n_live: int,
    n_stale: int,
    n_fail: int,
    elapsed: float,
    dropped_ips: int = 0,
    dropped_proxies: int = 0,
    max_ports: int = 0,
    file=sys.stderr,
) -> None:
    """Çalışma özetini 2-sütun dikdörtgen kutuda yaz."""
    n_total = n_ok + n_live + n_stale + n_fail
    dest = t("summary.proxies_dest", path=output_path) if output_path else ""
    rows = [
        (t("summary.protocol"), protocol),
        (t("summary.proxies"),  t("summary.proxies_unique", n=proxy_count) + dest),
        (t("summary.sources"),  t("summary.sources_value",
                                  total=n_total, ok=n_ok, live=n_live,
                                  stale=n_stale, fail=n_fail)),
    ]
    if dropped_ips > 0:
        rows.append((
            t("summary.filtered"),
            t("summary.filtered_value",
              ips=dropped_ips, entries=dropped_proxies, max=max_ports),
        ))
    rows.append((t("summary.elapsed"), f"{elapsed:.1f}s"))
    w_key = max(len(k) for k, _ in rows)
    w_val = max(len(v) for _, v in rows)

    def line(left: str, mid: str, right: str) -> str:
        return left + "─" * (w_key + 2) + mid + "─" * (w_val + 2) + right

    def row(k: str, v: str) -> str:
        return f"│ {k:<{w_key}} │ {v:<{w_val}} │"

    print(line("┌", "┬", "┐"), file=file)
    for k, v in rows:
        print(row(k, v), file=file)
    print(line("└", "┴", "┘"), file=file)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# ANSI renkleri yardım çıktısı için. Genişlik hesabı argparse'in orijinal
# (renksiz) metni üzerinde yapıldıktan SONRA renk uygulanır, böylece kolon
# hizaları bozulmaz.
_ANSI = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "red":    "\033[31m",
    "green":  "\033[32m",
    "yellow": "\033[33m",
    "blue":   "\033[34m",
    "cyan":   "\033[36m",
}


def _color_enabled(stream) -> bool:
    """NO_COLOR > FORCE_COLOR > stream.isatty() önceliği."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def _colorize_help(text: str) -> str:
    R = _ANSI["reset"]

    # Bölüm başlıkları: satır başında "word ...:" (örn. "options:", "positional arguments:")
    text = re.sub(
        r"(?m)^([a-zA-Z][\w ]*?:)$",
        f"{_ANSI['bold']}{_ANSI['cyan']}\\1{R}",
        text,
    )
    # "usage:" prefix'i
    text = re.sub(
        r"(?m)^(usage:)",
        f"{_ANSI['bold']}{_ANSI['cyan']}\\1{R}",
        text,
    )
    # "Examples:" (epilog başlığı — sonunda iki nokta, satır içinde)
    text = re.sub(
        r"(?m)^(Examples:)$",
        f"{_ANSI['bold']}{_ANSI['cyan']}\\1{R}",
        text,
    )
    # Option flag'leri: -x veya --xxx (kelime/dash öncesi hariç, URL/Last-Modified vb. yanlış eşleşmesin)
    text = re.sub(
        r"(?<![-\w])(--?[a-zA-Z][\w-]*)",
        f"{_ANSI['yellow']}\\1{R}",
        text,
    )
    # (default: ...) — argparse satır sarmalı boşluğu \n'e çevirebilir, \s+ kullan.
    text = re.sub(
        r"\(default:\s+[^)]+\)",
        lambda m: f"{_ANSI['dim']}{m.group(0)}{R}",
        text,
    )
    # 'proxine.py ...' örnek komutları — yeşil
    text = re.sub(
        r"'(proxine\.py[^']+)'",
        lambda m: f"{_ANSI['green']}'{m.group(1)}'{R}",
        text,
    )
    return text


class ColorHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """RawDescriptionHelpFormatter + son adımda ANSI renklendirme.

    Argparse genişlik/hizalama hesabını bitirdikten sonra renkler eklenir,
    bu yüzden ANSI kodlarının görünmez genişliği kolonları bozmaz.
    """

    def format_help(self) -> str:
        text = super().format_help()
        if not _color_enabled(sys.stdout):
            return text
        return _colorize_help(text)


def _early_lang_scan(argv: list[str] | None) -> str | None:
    """Pre-scan argv for --lang/-L before argparse runs.

    Argparse builds help strings at parser-construction time, so we need
    the active language set BEFORE we add_argument(... help=t(...)) calls.
    Returns the explicit code if present, else None (triggers auto-detect).
    """
    args = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(args):
        if a in ("--lang", "-L"):
            if i + 1 < len(args):
                return args[i + 1]
        elif a.startswith("--lang="):
            return a.split("=", 1)[1]
    return None


def main(argv: list[str] | None = None) -> int:
    # i18n: --lang flag varsa onu, yoksa env/locale'i kullan. Bu set_language()
    # argparse parser inşasından ÖNCE çağrılmalı; help/desc/epilog metinleri
    # buradaki dile göre üretilir.
    set_language(_early_lang_scan(argv))

    # Epilog: (komut, açıklama-key) çiftlerinden dile özgü inşa et.
    _examples = [
        ("proxine.py -p http",                   "cli.example.basic"),
        ("proxine.py -p https > https.lst",      "cli.example.save"),
        ("proxine.py -p socks5 -f url",          "cli.example.url_format"),
        ("proxine.py -p socks4 -c 32",           "cli.example.parallel"),
        ("proxine.py -p http -t 5 -r 0",         "cli.example.impatient"),
        ("proxine.py -p socks5 -F 3600",         "cli.example.lasthour"),
        ("proxine.py -p socks4 -F 0",            "cli.example.fresh_off"),
        ("proxine.py -p http -o http.lst",       "cli.example.tofile"),
        ("proxine.py -p https -s -o proxies.txt", "cli.example.silent_file"),
    ]
    _cmd_width = max(len(c) for c, _ in _examples) + 4
    epilog = t("cli.examples_header") + "\n" + "\n".join(
        f"  {cmd:<{_cmd_width}}{t(key)}" for cmd, key in _examples
    ) + "\n"

    p = argparse.ArgumentParser(
        prog="proxine",
        description=t("cli.description"),
        epilog=epilog,
        formatter_class=ColorHelpFormatter,
    )
    p.add_argument(
        "-p", "--protocol",
        choices=sorted(SOURCES.keys()),
        required=True,
        metavar="PROTO",
        help=t("cli.help.protocol"),
    )
    p.add_argument(
        "-f", "--format",
        choices=("ip-port", "url"),
        default="ip-port",
        help=t("cli.help.format"),
    )
    p.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=t("cli.help.timeout", default=DEFAULT_TIMEOUT),
    )
    p.add_argument(
        "-c", "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        metavar="N",
        help=t("cli.help.concurrency", default=DEFAULT_CONCURRENCY),
    )
    p.add_argument(
        "-r", "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        metavar="N",
        help=t("cli.help.retries", default=DEFAULT_RETRIES),
    )
    p.add_argument(
        "-m", "--max-ports",
        type=int,
        default=DEFAULT_MAX_PORTS,
        metavar="N",
        help=t("cli.help.max_ports", default=DEFAULT_MAX_PORTS),
    )
    p.add_argument(
        "-F", "--fresh",
        type=int,
        default=DEFAULT_FRESH,
        metavar="SECONDS",
        help=t("cli.help.fresh", default=DEFAULT_FRESH),
    )
    p.add_argument(
        "-g", "--github-token",
        metavar="TOKEN",
        help=t("cli.help.github_token", budget=GITHUB_UNAUTHED_BUDGET),
    )
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        help=t("cli.help.output"),
    )
    p.add_argument(
        "-L", "--lang",
        choices=sorted(LANGS),
        metavar="CODE",
        help=t("cli.help.lang"),
    )
    p.add_argument(
        "--strict-ports",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=t("cli.help.strict_ports"),
    )
    p.add_argument(
        "-s", "--silent",
        action="store_true",
        help=t("cli.help.silent"),
    )
    args = p.parse_args(argv)

    # parse_args sonrası --lang açıkça verilmişse erken algılamanın üstüne yaz
    # (Argparse seçilen değeri doğruladıktan sonra). Bu, yardım metni zaten
    # üretildiği için yalnızca runtime stringlerini etkiler — kabul edilebilir.
    if getattr(args, "lang", None):
        set_language(args.lang)

    # -s/--silent her şeyi susturur. Aksi halde: kalıcı log satırları + alt
    # tarafta animasyonlu progress bar (TTY ise) + freshness tablosu + özet.
    show_summary = not args.silent
    show_freshness = not args.silent
    show_progress = not args.silent
    show_logs = not args.silent

    github_state = GithubAPIState(token=resolve_github_token(args.github_token))

    # -o verildiyse karşılaştırma modunu aç (dosya yoksa baseline boş set olur,
    # =0 -0 +N şeklinde başlar). Stdout modunda eski "total" sayacı kalır.
    compare_mode = bool(args.output)
    prior_set = _load_existing_proxies(args.output) if args.output else set()

    # Run başlamadan önce parsed argümanları + ortam durumunu özetle.
    if not args.silent:
        print_settings_box(
            args=args,
            github_state=github_state,
            prior_count=len(prior_set),
            n_sources=len(SOURCES[args.protocol]),
        )

    progress = Progress(
        enabled=show_progress,
        prior=prior_set,
        compare=compare_mode,
        log_enabled=show_logs,
    )
    progress.start_phase(t("progress.fetching"), len(SOURCES[args.protocol]))

    started = time.monotonic()
    results = collect(
        protocol=args.protocol,
        timeout=args.timeout,
        concurrency=args.concurrency,
        retries=args.retries,
        progress=progress,
        strict_ports=args.strict_ports,
    )

    # --fresh filtresi yaşlara baktığı için commit zamanlarını HER ZAMAN doldur.
    # Progress bar ikinci faza geçer ve enrichment süresince ekranda kalır.
    results = enrich_github_freshness(
        results,
        timeout=args.timeout,
        concurrency=args.concurrency,
        state=github_state,
        progress=progress,
    )
    progress.finish()
    elapsed = time.monotonic() - started

    now = datetime.now(timezone.utc)
    proxies: set[str] = set()
    for r in results:
        if r.error:
            continue
        if is_stale(r, now, args.fresh):
            continue
        proxies.update(r.proxies)

    dropped_ips = 0
    dropped_proxies = 0
    if args.max_ports > 0:
        ports_by_ip: dict[str, int] = {}
        for pp in proxies:
            ip = pp.partition(":")[0]
            ports_by_ip[ip] = ports_by_ip.get(ip, 0) + 1
        bad_ips = {ip for ip, n in ports_by_ip.items() if n > args.max_ports}
        if bad_ips:
            before = len(proxies)
            proxies = {pp for pp in proxies if pp.partition(":")[0] not in bad_ips}
            dropped_ips = len(bad_ips)
            dropped_proxies = before - len(proxies)

    sorted_proxies = sorted(proxies, key=_sort_key)

    if args.output:
        try:
            out_fh = open(args.output, "w", encoding="utf-8")
        except OSError as e:
            print(t("error.open_output", path=args.output, err=e), file=sys.stderr)
            return 1
    else:
        out_fh = sys.stdout

    try:
        if args.format == "url":
            prefix = f"{args.protocol}://"
            for pp in sorted_proxies:
                print(prefix + pp, file=out_fh)
        else:
            for pp in sorted_proxies:
                print(pp, file=out_fh)
    finally:
        if args.output:
            out_fh.close()

    if show_freshness:
        print_status_table(results, args.fresh)

    if show_summary:
        now = datetime.now(timezone.utc)
        n_ok = sum(1 for r in results if _classify(r, now, args.fresh) == "OK")
        n_live = sum(1 for r in results if _classify(r, now, args.fresh) == "LIVE")
        n_stale = sum(1 for r in results if _classify(r, now, args.fresh) == "STALE")
        n_fail = sum(1 for r in results if _classify(r, now, args.fresh) == "FAIL")
        print_summary_box(
            protocol=args.protocol,
            proxy_count=len(sorted_proxies),
            output_path=args.output,
            n_ok=n_ok,
            n_live=n_live,
            n_stale=n_stale,
            n_fail=n_fail,
            elapsed=elapsed,
            dropped_ips=dropped_ips,
            dropped_proxies=dropped_proxies,
            max_ports=args.max_ports,
        )
        if github_state.bad_token:
            print(t("warning.gh_bad_token"), file=sys.stderr)
        elif github_state.rate_limited:
            print(t("warning.gh_rate_limit"), file=sys.stderr)
        elif github_state.budget_skipped > 0:
            print(
                t("warning.gh_budget_skip",
                  n=github_state.budget_skipped,
                  budget=GITHUB_UNAUTHED_BUDGET),
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
