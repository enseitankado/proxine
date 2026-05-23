#!/usr/bin/env python3
"""
Proxine — aggregate free proxy lists from dozens of public sources.

Usage:
    proxine.py <http|https|socks4|socks5> [options]

Example:
    proxine.py https > https_proxies.lst
    proxine.py socks5 -f url -c 32 -v

Stdout : unique, sorted `IP:PORT` lines (or `<proto>://IP:PORT` with --format url).
Stderr : a summary line + per-source freshness report (suppressed by --silent).
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
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

DEFAULT_TIMEOUT = 15
DEFAULT_CONCURRENCY = 1
DEFAULT_RETRIES = 2
DEFAULT_FRESH = 24 * 60 * 60  # 24 hours, in seconds

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


def _task(url: str, parser_name: str, proto: str, timeout: int, retries: int) -> SourceResult:
    try:
        text, last_modified = fetch(url, timeout=timeout, retries=retries)
    except Exception as e:  # noqa: BLE001  fetch hatası tek tek raporlanır
        return SourceResult(url=url, proxies=[], last_modified=None,
                            error=f"{type(e).__name__}: {e}")
    parser = PARSERS.get(parser_name, parse_regex)
    return SourceResult(url=url, proxies=list(parser(text, proto)),
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
        self._rate_limited = False
        self._bad_token = False
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

    def mark_rate_limited(self) -> None:
        with self._lock:
            self._rate_limited = True

    def mark_bad_token(self) -> None:
        with self._lock:
            self._bad_token = True


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
    """Last-Modified vermeyen raw.githubusercontent.com kaynaklarını commit zamanıyla doldur."""
    candidates = [
        i for i, r in enumerate(results)
        if r.error is None and r.last_modified is None and GITHUB_RAW_RE.match(r.url)
    ]
    if not candidates:
        return results
    if progress is not None:
        progress.start_phase("enriching", len(candidates), show_contrib=False)
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


class Progress:
    """Çok fazlı tek satır TTY ilerleme göstergesi (\\r ile yenilenir).

    Faz 1 (fetching):
        [████████████░░░░░░░░]  60%  24/40  fetching  ✓ github.com/x/y  +1,234  total 56,789
    Faz 2 (enriching commit times):
        [████████████░░░░░░░░]  60%  15/25  enriching ✓ github.com/x/y                   total 56,789
    """

    BAR_WIDTH = 20
    SOURCE_WIDTH = 38
    LABEL_WIDTH = 9   # "fetching " / "enriching"
    LINE_WIDTH = 120

    def __init__(self, enabled: bool, file=sys.stderr) -> None:
        self.file = file
        # Yalnızca etkin VE stderr bir TTY ise animasyon göster. Pipe/dosyada sessiz.
        self.enabled = enabled and file.isatty()
        self.matches = 0           # birikmiş benzersiz proxy katkıları (tüm fazlar boyunca)
        self.label = ""
        self.total = 0
        self.done = 0
        # Faz "fetching" mi yoksa "enriching" mi: +N sütununu kontrol eder.
        self.show_contrib = True

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

    def update(self, result: SourceResult) -> None:
        self.done += 1
        contributed = 0 if result.error else len(result.proxies)
        if self.show_contrib and result.error is None:
            self.matches += contributed
        if not self.enabled or self.total == 0:
            return

        pct = self.done / self.total
        filled = int(self.BAR_WIDTH * pct)
        bar = "█" * filled + "░" * (self.BAR_WIDTH - filled)
        marker = "x" if result.error else "✓"

        short = self._short(result.url)
        if len(short) > self.SOURCE_WIDTH:
            short = short[: self.SOURCE_WIDTH - 1] + "…"

        contrib = (
            ""
            if not self.show_contrib
            else ("(fail)" if result.error else f"+{contributed:,}")
        )

        digits = len(str(self.total))
        line = (
            f"\r[{bar}] {pct * 100:3.0f}%  "
            f"{self.done:>{digits}}/{self.total}  "
            f"{self.label:<{self.LABEL_WIDTH}} "
            f"{marker} {short:<{self.SOURCE_WIDTH}}  "
            f"{contrib:>10}  total {self.matches:>9,}"
        )
        self.file.write(line[: self.LINE_WIDTH + 1].ljust(self.LINE_WIDTH + 1))
        self.file.flush()

    def finish(self) -> None:
        if self.enabled:
            self.file.write("\r" + " " * self.LINE_WIDTH + "\r")
            self.file.flush()


def collect(
    protocol: str,
    timeout: int,
    concurrency: int,
    retries: int,
    verbose: bool,
    progress: Progress | None = None,
) -> list[SourceResult]:
    sources = SOURCES[protocol]
    results: list[SourceResult] = []

    with cf.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(_task, url, parser, protocol, timeout, retries)
            for url, parser in sources
        ]
        for fut in cf.as_completed(futures):
            r = fut.result()
            results.append(r)
            if verbose:
                if r.error:
                    print(f"[fail] {r.url}: {r.error}", file=sys.stderr)
                else:
                    print(f"[ ok ] {len(r.proxies):>5}  {r.url}", file=sys.stderr)
            elif progress is not None:
                progress.update(r)

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

    headers = ("STATUS", "AGE", "PROXIES", "SOURCE")
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
        "  OK     fresh enough (within --fresh window); proxies kept\n"
        "  LIVE   no Last-Modified / commit info (dynamic API); proxies kept\n"
        "  STALE  older than --fresh; proxies dropped from output\n"
        "  FAIL   fetch error; no proxies contributed",
        file=file,
    )


def print_summary_box(
    protocol: str,
    proxy_count: int,
    output_path: str | None,
    n_ok: int,
    n_live: int,
    n_stale: int,
    n_fail: int,
    elapsed: float,
    file=sys.stderr,
) -> None:
    """Çalışma özetini 2-sütun dikdörtgen kutuda yaz."""
    n_total = n_ok + n_live + n_stale + n_fail
    dest = f"  →  {output_path}" if output_path else ""
    rows = [
        ("protocol", protocol),
        ("proxies",  f"{proxy_count:,} unique{dest}"),
        ("sources",  f"{n_total} total  ({n_ok} ok, {n_live} live, "
                     f"{n_stale} stale, {n_fail} fail)"),
        ("elapsed",  f"{elapsed:.1f}s"),
    ]
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

def main(argv: list[str] | None = None) -> int:
    epilog = (
        "Examples:\n"
        "  proxine.py http                       Collect HTTP proxies to stdout\n"
        "  proxine.py https > https.lst          Save HTTPS proxies to a file\n"
        "  proxine.py socks5 -f url              Emit 'socks5://1.2.3.4:1080' lines\n"
        "  proxine.py socks4 -c 32 -v            32 parallel fetches, log per source\n"
        "  proxine.py http -t 5 -r 0             Impatient mode: 5s, no retry\n"
        "  proxine.py socks5 -F 3600             Only sources updated in the last hour\n"
        "  proxine.py socks4 -F 0                Disable the freshness filter\n"
        "  proxine.py http -o http.lst           Write proxies to file; progress on stderr\n"
        "  proxine.py https -s -o proxies.txt    Silent + file: nothing on stderr or stdout\n"
    )
    p = argparse.ArgumentParser(
        prog="proxine",
        description=(
            "Aggregate fresh proxy lists from dozens of public sources, "
            "deduplicate them, and print a sorted IP:PORT list."
        ),
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "protocol",
        choices=sorted(SOURCES.keys()),
        help=(
            "Proxy protocol to collect; one of {http, https, socks4, socks5}. "
            "Example: 'proxine.py socks5'."
        ),
    )
    p.add_argument(
        "-f", "--format",
        choices=("ip-port", "url"),
        default="ip-port",
        help=(
            "Output format. 'ip-port' (default) prints '1.2.3.4:8080'; "
            "'url' prefixes the protocol scheme. "
            "Example: 'proxine.py socks5 -f url' yields 'socks5://1.2.3.4:1080'."
        ),
    )
    p.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=(
            f"Per-source HTTP timeout in seconds (default: {DEFAULT_TIMEOUT}). "
            "Slow upstreams are abandoned so one bad host can't stall the run. "
            "Example: 'proxine.py http -t 5'."
        ),
    )
    p.add_argument(
        "-c", "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        metavar="N",
        help=(
            f"Number of source URLs fetched in parallel (default: {DEFAULT_CONCURRENCY}). "
            "Higher values finish faster but use more bandwidth and sockets. "
            "Example: 'proxine.py https -c 32'."
        ),
    )
    p.add_argument(
        "-r", "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        metavar="N",
        help=(
            f"How many times to retry a failed source before giving up "
            f"(default: {DEFAULT_RETRIES}). Set 0 to fail fast. "
            "Example: 'proxine.py http -r 0'."
        ),
    )
    p.add_argument(
        "-F", "--fresh",
        type=int,
        default=DEFAULT_FRESH,
        metavar="SECONDS",
        help=(
            f"Drop proxies from sources older than this many seconds "
            f"(default: {DEFAULT_FRESH} = 24h). Sources with no Last-Modified / "
            f"commit info (e.g. live APIs) are always kept. Set 0 to disable. "
            "Examples: '-F 3600' (last 1h only), '-F 604800' (last 7d), '-F 0' (all)."
        ),
    )
    p.add_argument(
        "-g", "--github-token",
        metavar="TOKEN",
        help=(
            "GitHub personal access token used to look up commit times on "
            "raw.githubusercontent.com URLs (so source ages show real values "
            "instead of 'LIVE'). Without a token the GitHub API rate-limit is "
            "60 req/h and most github.com rows will fall back to 'LIVE'; with "
            "a token the limit is 5,000 req/h. Resolution order: this flag, "
            "then $GITHUB_TOKEN, then `gh auth token`. No 'repo' scope needed "
            "— public read access is enough. "
            "Example: 'proxine.py http --github-token ghp_xxx' or "
            "'GITHUB_TOKEN=ghp_xxx proxine.py http'."
        ),
    )
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        help=(
            "Write the proxy list to FILE (one IP:PORT per line) instead of "
            "stdout. The file contains only proxies — progress, freshness, and "
            "summary stay on stderr. "
            "Example: 'proxine.py http -o http.lst'."
        ),
    )
    p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help=(
            "Log each source's fetch result (ok/fail + match count) to stderr "
            "as it completes. Disables the single-line progress indicator. "
            "Example: 'proxine.py socks5 -v 2> fetch.log'."
        ),
    )
    p.add_argument(
        "-s", "--silent",
        action="store_true",
        help=(
            "Print only the proxy list. Suppress ALL stderr output (progress, "
            "summary, freshness report, verbose log). Overrides -v. "
            "Example: 'proxine.py https -s -o proxies.txt'."
        ),
    )
    args = p.parse_args(argv)

    # -s/--silent overrides verbose and suppresses both the freshness report
    # and the summary line.
    verbose = args.verbose and not args.silent
    show_summary = not args.silent
    show_freshness = not args.silent
    # Progress: only when not silent AND not verbose (verbose has its own log).
    show_progress = not args.silent and not args.verbose

    github_state = GithubAPIState(token=resolve_github_token(args.github_token))

    progress = Progress(enabled=show_progress)
    progress.start_phase("fetching", len(SOURCES[args.protocol]))

    started = time.monotonic()
    results = collect(
        protocol=args.protocol,
        timeout=args.timeout,
        concurrency=args.concurrency,
        retries=args.retries,
        verbose=verbose,
        progress=progress,
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
    sorted_proxies = sorted(proxies, key=_sort_key)

    if args.output:
        try:
            out_fh = open(args.output, "w", encoding="utf-8")
        except OSError as e:
            print(f"proxine: cannot open '{args.output}': {e}", file=sys.stderr)
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
        )
        if github_state.bad_token:
            print(
                "warning: GitHub API rejected the supplied token (401) — "
                "github.com sources fell back to 'LIVE' instead of real ages.\n"
                "         Check that the token is valid; no scopes are required "
                "for public-repo reads.",
                file=sys.stderr,
            )
        elif github_state.rate_limited:
            print(
                "warning: GitHub API rate-limited during this run — some "
                "github.com sources fell back to 'LIVE' instead of a real age.\n"
                "         Pass --github-token TOKEN, set $GITHUB_TOKEN, or "
                "run `gh auth login` to raise the limit to 5,000 req/h.",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
