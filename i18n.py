"""Proxine i18n: dictionary-based translation catalogs.

Detection order (called once at startup; --lang flag overrides everything):
  1. CLI --lang/-L (resolved outside this module, before parser build)
  2. $PROXINE_LANG
  3. $LC_ALL → $LC_MESSAGES → $LANG
  4. locale.getlocale()
  5. fallback "en"

Supported codes: tr, en, de, es, ru, zh
Missing keys in a non-English catalog fall back to the English value;
missing in English falls back to the key name itself.

Catalog entries with `{name}` placeholders are passed through str.format();
literal braces must be escaped as `{{ }}`. Callers MUST pass all placeholders
the string declares (see proxine.py call sites for the mapping).
"""
from __future__ import annotations

import locale
import os

SUPPORTED: tuple[str, ...] = ("tr", "en", "de", "es", "ru", "zh")
DEFAULT_LANG = "en"

_current = DEFAULT_LANG


def detect_language() -> str:
    """Return a SUPPORTED code from env / locale; fallback DEFAULT_LANG."""
    for var in ("PROXINE_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(var)
        if v:
            code = v.split(".", 1)[0].split("_", 1)[0].lower()
            if code in SUPPORTED:
                return code
    try:
        loc = locale.getlocale()[0]
        if loc:
            code = loc.split("_", 1)[0].lower()
            if code in SUPPORTED:
                return code
    except (ValueError, TypeError):
        pass
    return DEFAULT_LANG


def set_language(code: str | None) -> str:
    """Set the active language. None / unsupported → auto-detect. Returns active."""
    global _current
    if code and code.lower() in SUPPORTED:
        _current = code.lower()
    else:
        _current = detect_language()
    return _current


def current_language() -> str:
    return _current


def t(key: str, **fmt: object) -> str:
    """Translate a key. Missing → English. Always runs .format() so `{{ }}` escapes."""
    cat = CATALOGS.get(_current, CATALOGS[DEFAULT_LANG])
    text = cat.get(key)
    if text is None:
        text = CATALOGS[DEFAULT_LANG].get(key, key)
    try:
        return text.format(**fmt)
    except (KeyError, IndexError):
        # Caller forgot a placeholder — return raw template; better than a crash.
        return text


# ---------------------------------------------------------------------------
# Catalogs
# ---------------------------------------------------------------------------

CATALOGS: dict[str, dict[str, str]] = {}

# ---------- English (canonical) ----------
CATALOGS["en"] = {
    # argparse
    "cli.description": (
        "Aggregate fresh proxy lists from dozens of public sources, "
        "deduplicate them, and print a sorted IP:PORT list."
    ),
    "cli.examples_header": "Examples:",
    "cli.example.basic":        "Collect HTTP proxies to stdout",
    "cli.example.save":         "Save HTTPS proxies to a file",
    "cli.example.url_format":   "Emit 'socks5://1.2.3.4:1080' lines",
    "cli.example.parallel":     "32 parallel fetches",
    "cli.example.impatient":    "Impatient mode: 5s, no retry",
    "cli.example.lasthour":     "Only sources updated in the last hour",
    "cli.example.fresh_off":    "Disable the freshness filter",
    "cli.example.tofile":       "Write proxies to file; progress on stderr",
    "cli.example.silent_file":  "Silent + file: nothing on stderr or stdout",
    "cli.help.protocol": (
        "Proxy protocol to collect; one of {{http, https, socks4, socks5}}. "
        "Required. Example: 'proxine.py -p socks5'."
    ),
    "cli.help.format": (
        "Output format. 'ip-port' (default) prints '1.2.3.4:8080'; "
        "'url' prefixes the protocol scheme. "
        "Example: 'proxine.py -p socks5 -f url'."
    ),
    "cli.help.timeout": (
        "Per-source HTTP timeout in seconds (default: {default}). "
        "Slow upstreams are abandoned so one bad host can't stall the run."
    ),
    "cli.help.concurrency": (
        "Number of source URLs fetched in parallel (default: {default}). "
        "Higher values finish faster but use more bandwidth and sockets."
    ),
    "cli.help.retries": (
        "How many times to retry a failed source before giving up "
        "(default: {default}). Set 0 to fail fast."
    ),
    "cli.help.max_ports": (
        "Drop an IP entirely if it appears with more than N distinct ports "
        "across the aggregated, deduplicated output (default: {default}). "
        "Such hosts are usually port scanners or honeypots rather than real "
        "proxies. Set 0 to disable."
    ),
    "cli.help.fresh": (
        "Drop proxies from sources older than this many seconds "
        "(default: {default} = 24h). Sources with no Last-Modified / commit "
        "info (e.g. live APIs) are always kept. Set 0 to disable."
    ),
    "cli.help.github_token": (
        "GitHub PAT for commit-time lookups on raw.githubusercontent.com URLs "
        "(so source ages show real values instead of 'LIVE'). Without a token "
        "the API limit is 60 req/h; proxine caps unauthenticated runs at "
        "{budget} lookups to stay safely under it, and remaining github.com "
        "rows fall back to 'LIVE'. With a token the limit is 5,000 req/h. "
        "Resolution order: this flag → $GITHUB_TOKEN → `gh auth token`."
    ),
    "cli.help.output": (
        "Write the proxy list to FILE (one IP:PORT per line) instead of "
        "stdout. The file contains only proxies — progress, freshness, and "
        "summary stay on stderr."
    ),
    "cli.help.silent": (
        "Print only the proxy list. Suppress ALL stderr output (per-source "
        "log lines, progress bar, freshness report, summary)."
    ),
    "cli.help.lang": (
        "UI language override. One of {{tr, en, de, es, ru, zh}}. Without "
        "this flag, language is auto-detected from $PROXINE_LANG, $LC_*/$LANG, "
        "or the system locale; falls back to English."
    ),
    "cli.help.strict_ports": (
        "Drop proxies whose port doesn't match the declared protocol family "
        "(e.g. a SOCKS-declared proxy on port 80 is dropped as almost certainly "
        "HTTP). On by default; disable with --no-strict-ports if you want raw "
        "source output. Useful when source lists are mis-categorized."
    ),

    # status table
    "status.col.status":  "STATUS",
    "status.col.age":     "AGE",
    "status.col.proxies": "PROXIES",
    "status.col.source":  "SOURCE",
    "status.legend.ok":    "  OK     fresh enough (within --fresh window); proxies kept",
    "status.legend.live":  "  LIVE   no Last-Modified / commit info (dynamic API); proxies kept",
    "status.legend.stale": "  STALE  older than --fresh; proxies dropped from output",
    "status.legend.fail":  "  FAIL   fetch error; no proxies contributed",

    # settings box
    "settings.sources":  "sources",
    "settings.baseline": "baseline",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "off",
    "settings.value.on":               "on",
    "settings.value.drop_thresh":      ">{n} → drop",
    "settings.value.token_auth":       "token (5,000 req/h)",
    "settings.value.unauthed":         "unauthed (cap {budget}/run, limit 60/h)",
    "settings.value.baseline_loaded":  "{n:,} entries loaded",
    "settings.value.baseline_empty":   "(file missing/empty — starting from zero)",

    # summary box
    "summary.protocol":  "protocol",
    "summary.proxies":   "proxies",
    "summary.sources":   "sources",
    "summary.filtered":  "filtered",
    "summary.elapsed":   "elapsed",
    "summary.proxies_unique":  "{n:,} unique",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "{total} total  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} IPs / {entries:,} entries  (>{max} ports per IP)",

    # progress
    "progress.fetching":   "fetching",
    "progress.enriching":  "enriching",
    "progress.total":      "total",
    "progress.fail":       "(fail)",

    # errors / warnings
    "error.open_output": "proxine: cannot open '{path}': {err}",
    "warning.gh_bad_token": (
        "warning: GitHub API rejected the supplied token (401) — "
        "github.com sources fell back to 'LIVE' instead of real ages.\n"
        "         Check that the token is valid; no scopes are required "
        "for public-repo reads."
    ),
    "warning.gh_rate_limit": (
        "warning: GitHub API rate-limited during this run — some "
        "github.com sources fell back to 'LIVE' instead of a real age.\n"
        "         Pass --github-token TOKEN, set $GITHUB_TOKEN, or "
        "run `gh auth login` to raise the limit to 5,000 req/h."
    ),
    "warning.gh_budget_skip": (
        "warning: {n} github.com source(s) skipped during enrichment to "
        "stay under GitHub's 60/h\n"
        "         unauthenticated API limit (capped at {budget} requests "
        "this run); they fell back to 'LIVE'.\n"
        "         Pass --github-token TOKEN, set $GITHUB_TOKEN, or "
        "run `gh auth login` to enrich them all (5,000 req/h with a token)."
    ),
}

# ---------- Turkish ----------
CATALOGS["tr"] = {
    "cli.description": (
        "Onlarca açık kaynaktan taze proxy listelerini topla, deduplike et ve "
        "sıralı IP:PORT listesi yazdır."
    ),
    "cli.examples_header": "Örnekler:",
    "cli.example.basic":        "HTTP proxy'leri stdout'a topla",
    "cli.example.save":         "HTTPS proxy'leri dosyaya kaydet",
    "cli.example.url_format":   "'socks5://1.2.3.4:1080' satırları yaz",
    "cli.example.parallel":     "32 paralel çekim",
    "cli.example.impatient":    "Sabırsız mod: 5s, tekrar yok",
    "cli.example.lasthour":     "Yalnızca son 1 saatte güncellenen kaynaklar",
    "cli.example.fresh_off":    "Tazelik filtresini kapat",
    "cli.example.tofile":       "Proxy'leri dosyaya yaz; progress stderr'de",
    "cli.example.silent_file":  "Silent + dosya: stderr/stdout boş kalır",
    "cli.help.protocol": (
        "Toplanacak proxy protokolü; {{http, https, socks4, socks5}} biri. "
        "Zorunlu. Örnek: 'proxine.py -p socks5'."
    ),
    "cli.help.format": (
        "Çıktı formatı. 'ip-port' (varsayılan) '1.2.3.4:8080' yazar; "
        "'url' protokol şemasını öne ekler. Örnek: 'proxine.py -p socks5 -f url'."
    ),
    "cli.help.timeout": (
        "Kaynak başına HTTP timeout, saniye (varsayılan: {default}). "
        "Yavaş hostlar terk edilir, bir kötü kaynak run'u kilitlemez."
    ),
    "cli.help.concurrency": (
        "Eşzamanlı çekilecek kaynak sayısı (varsayılan: {default}). "
        "Yüksek değer daha hızlı bitirir ama daha çok bant genişliği ve soket harcar."
    ),
    "cli.help.retries": (
        "Başarısız bir kaynağı vazgeçmeden önce kaç kez yeniden denesin "
        "(varsayılan: {default}). 0 = hızlı başarısızlık."
    ),
    "cli.help.max_ports": (
        "Birikmiş, deduplike edilmiş çıktıda N'den fazla farklı port ile "
        "görünen IP'yi tamamen at (varsayılan: {default}). Bu tür hostlar "
        "genelde port tarayıcı ya da honeypot olur; gerçek proxy değil. "
        "0 = devre dışı."
    ),
    "cli.help.fresh": (
        "Bu kadar saniyeden eski kaynaklardaki proxy'leri at (varsayılan: "
        "{default} = 24s). Last-Modified / commit bilgisi olmayan kaynaklar "
        "(canlı API'ler) her zaman tutulur. 0 = filtre kapalı."
    ),
    "cli.help.github_token": (
        "raw.githubusercontent.com URL'lerinin commit zamanlarını öğrenmek "
        "için GitHub PAT (yaşlar 'LIVE' yerine gerçek değer gösterir). Token "
        "yokken API saatlik 60 istekle sınırlı; proxine bunun altında kalmak "
        "için token'sız run'ları {budget} commit sorgusuyla kısıtlar, geri "
        "kalan github.com satırları 'LIVE' kalır. Token ile limit 5,000 req/saat. "
        "Sıra: bu flag → $GITHUB_TOKEN → `gh auth token`."
    ),
    "cli.help.output": (
        "Proxy listesini stdout yerine FILE'a yaz (her satırda IP:PORT). "
        "Dosyaya yalnızca proxy'ler gider; progress, tazelik ve özet stderr'de kalır."
    ),
    "cli.help.silent": (
        "Yalnızca proxy listesini yazdır. TÜM stderr çıktısını sustur "
        "(kaynak başına log, progress bar, tazelik raporu, özet)."
    ),
    "cli.help.lang": (
        "Arayüz dili. {{tr, en, de, es, ru, zh}} biri. Bu flag olmadan dil "
        "$PROXINE_LANG, $LC_*/$LANG veya sistem locale'inden otomatik algılanır; "
        "bulunmazsa İngilizce."
    ),
    "cli.help.strict_ports": (
        "Beyan edilen protokol ailesine uymayan portlardaki proxy'leri at "
        "(örn. SOCKS olarak listelenmiş port 80 büyük olasılıkla HTTP'dir, atılır). "
        "Varsayılan açık; ham kaynak çıktısı istiyorsan --no-strict-ports ile kapat. "
        "Yanlış kategorize edilmiş kaynak listelerine karşı koruma."
    ),

    "status.col.status":  "DURUM",
    "status.col.age":     "YAŞ",
    "status.col.proxies": "PROXY",
    "status.col.source":  "KAYNAK",
    "status.legend.ok":    "  OK     yeterince taze (--fresh penceresi içinde); proxy'ler dahil",
    "status.legend.live":  "  LIVE   Last-Modified / commit yok (dinamik API); proxy'ler dahil",
    "status.legend.stale": "  STALE  --fresh eşiğinden eski; proxy'ler çıktıdan düşer",
    "status.legend.fail":  "  FAIL   çekim hatası; proxy katkısı yok",

    "settings.sources":  "kaynaklar",
    "settings.baseline": "temel",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "kapalı",
    "settings.value.on":               "açık",
    "settings.value.drop_thresh":      ">{n} → at",
    "settings.value.token_auth":       "token (5,000 req/saat)",
    "settings.value.unauthed":         "tokensız (run başına {budget} sınır, saatlik 60)",
    "settings.value.baseline_loaded":  "{n:,} kayıt yüklü",
    "settings.value.baseline_empty":   "(dosya yok/boş — sıfırdan başlanıyor)",

    "summary.protocol":  "protokol",
    "summary.proxies":   "proxy'ler",
    "summary.sources":   "kaynaklar",
    "summary.filtered":  "filtrelendi",
    "summary.elapsed":   "süre",
    "summary.proxies_unique":  "{n:,} benzersiz",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "toplam {total}  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} IP / {entries:,} kayıt  (IP başına >{max} port)",

    "progress.fetching":   "çekiliyor",
    "progress.enriching":  "zenginleştiriliyor",
    "progress.total":      "toplam",
    "progress.fail":       "(hata)",

    "error.open_output": "proxine: '{path}' açılamıyor: {err}",
    "warning.gh_bad_token": (
        "uyarı: GitHub API verilen token'ı reddetti (401) — "
        "github.com kaynakları gerçek yaş yerine 'LIVE' oldu.\n"
        "       Token geçerliliğini kontrol et; public-repo okumaları "
        "için scope gerekmiyor."
    ),
    "warning.gh_rate_limit": (
        "uyarı: Bu run'da GitHub API rate-limit oldu — bazı github.com "
        "kaynakları gerçek yaş yerine 'LIVE' oldu.\n"
        "       --github-token TOKEN ver, $GITHUB_TOKEN tanımla veya "
        "`gh auth login` ile limiti 5,000 req/saate çıkar."
    ),
    "warning.gh_budget_skip": (
        "uyarı: GitHub'ın saatlik 60'lık tokensız API limitinin altında "
        "kalmak için {n} github.com kaynağı enrichment'tan atlandı\n"
        "       (bu run'da {budget} istek tavanı); 'LIVE' kaldılar.\n"
        "       --github-token TOKEN ver, $GITHUB_TOKEN tanımla veya "
        "`gh auth login` ile hepsini zenginleştir (token ile 5,000 req/saat)."
    ),
}

# ---------- German ----------
CATALOGS["de"] = {
    "cli.description": (
        "Aktuelle Proxy-Listen aus Dutzenden öffentlicher Quellen sammeln, "
        "deduplizieren und als sortierte IP:PORT-Liste ausgeben."
    ),
    "cli.examples_header": "Beispiele:",
    "cli.example.basic":        "HTTP-Proxys nach stdout sammeln",
    "cli.example.save":         "HTTPS-Proxys in eine Datei speichern",
    "cli.example.url_format":   "Zeilen 'socks5://1.2.3.4:1080' ausgeben",
    "cli.example.parallel":     "32 parallele Abrufe",
    "cli.example.impatient":    "Ungeduldig: 5s, kein Retry",
    "cli.example.lasthour":     "Nur in der letzten Stunde aktualisierte Quellen",
    "cli.example.fresh_off":    "Frischefilter deaktivieren",
    "cli.example.tofile":       "Proxys in Datei schreiben; Fortschritt auf stderr",
    "cli.example.silent_file":  "Stumm + Datei: nichts auf stderr/stdout",
    "cli.help.protocol": (
        "Zu sammelndes Proxy-Protokoll; eines von {{http, https, socks4, socks5}}. "
        "Erforderlich. Beispiel: 'proxine.py -p socks5'."
    ),
    "cli.help.format": (
        "Ausgabeformat. 'ip-port' (Standard) gibt '1.2.3.4:8080' aus; "
        "'url' stellt das Protokoll-Schema voran."
    ),
    "cli.help.timeout": (
        "HTTP-Timeout pro Quelle in Sekunden (Standard: {default}). "
        "Langsame Upstreams werden abgebrochen, damit ein schlechter Host "
        "den Lauf nicht blockiert."
    ),
    "cli.help.concurrency": (
        "Anzahl parallel abgerufener Quellen (Standard: {default}). "
        "Höhere Werte sind schneller, brauchen aber mehr Bandbreite und Sockets."
    ),
    "cli.help.retries": (
        "Wie oft eine fehlgeschlagene Quelle erneut versucht wird, bevor sie "
        "aufgegeben wird (Standard: {default}). 0 = schneller Fehlschlag."
    ),
    "cli.help.max_ports": (
        "Verwirft eine IP komplett, wenn sie in der deduplizierten Ausgabe "
        "mit mehr als N verschiedenen Ports erscheint (Standard: {default}). "
        "Solche Hosts sind meist Port-Scanner oder Honeypots, keine echten "
        "Proxys. 0 = deaktiviert."
    ),
    "cli.help.fresh": (
        "Verwerfen von Proxys aus Quellen, die älter als so viele Sekunden "
        "sind (Standard: {default} = 24h). Quellen ohne Last-Modified / "
        "Commit-Info (z.B. Live-APIs) bleiben immer enthalten. 0 = deaktiviert."
    ),
    "cli.help.github_token": (
        "GitHub PAT zum Abruf der Commit-Zeit für raw.githubusercontent.com-"
        "URLs (damit das Alter echte Werte statt 'LIVE' zeigt). Ohne Token "
        "gilt 60 req/h; proxine begrenzt nicht authentifizierte Läufe auf "
        "{budget} Lookups, um sicher darunter zu bleiben, übrige github.com-"
        "Zeilen fallen auf 'LIVE' zurück. Mit Token: 5.000 req/h. "
        "Reihenfolge: dieses Flag → $GITHUB_TOKEN → `gh auth token`."
    ),
    "cli.help.output": (
        "Schreibt die Proxy-Liste in DATEI (eine IP:PORT pro Zeile) statt "
        "stdout. Die Datei enthält nur Proxys; Fortschritt, Frische und "
        "Zusammenfassung bleiben auf stderr."
    ),
    "cli.help.silent": (
        "Gibt nur die Proxy-Liste aus. Unterdrückt ALLE stderr-Ausgaben "
        "(Quellen-Log, Fortschrittsbalken, Frischebericht, Zusammenfassung)."
    ),
    "cli.help.lang": (
        "UI-Sprache. Eines von {{tr, en, de, es, ru, zh}}. Ohne dieses Flag "
        "wird die Sprache aus $PROXINE_LANG, $LC_*/$LANG oder dem System-"
        "Locale ermittelt; Fallback Englisch."
    ),
    "cli.help.strict_ports": (
        "Proxys verwerfen, deren Port nicht zur deklarierten Protokoll-Familie "
        "passt (z.B. ein als SOCKS deklarierter Proxy auf Port 80 ist fast "
        "sicher HTTP). Standardmäßig aktiv; mit --no-strict-ports deaktivieren, "
        "wenn du die Roh-Ausgabe willst. Schützt vor falsch kategorisierten Quellen."
    ),

    "status.col.status":  "STATUS",
    "status.col.age":     "ALTER",
    "status.col.proxies": "PROXYS",
    "status.col.source":  "QUELLE",
    "status.legend.ok":    "  OK     frisch genug (im --fresh-Fenster); Proxys behalten",
    "status.legend.live":  "  LIVE   keine Last-Modified / Commit-Info (Live-API); Proxys behalten",
    "status.legend.stale": "  STALE  älter als --fresh; Proxys aus Ausgabe entfernt",
    "status.legend.fail":  "  FAIL   Abruf fehlgeschlagen; kein Beitrag",

    "settings.sources":  "Quellen",
    "settings.baseline": "Basis",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "aus",
    "settings.value.on":               "an",
    "settings.value.drop_thresh":      ">{n} → verwerfen",
    "settings.value.token_auth":       "Token (5.000 req/h)",
    "settings.value.unauthed":         "ohne Token (max. {budget}/Lauf, Limit 60/h)",
    "settings.value.baseline_loaded":  "{n:,} Einträge geladen",
    "settings.value.baseline_empty":   "(Datei fehlt/leer — Start bei null)",

    "summary.protocol":  "Protokoll",
    "summary.proxies":   "Proxys",
    "summary.sources":   "Quellen",
    "summary.filtered":  "gefiltert",
    "summary.elapsed":   "Dauer",
    "summary.proxies_unique":  "{n:,} eindeutig",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "{total} gesamt  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} IPs / {entries:,} Einträge  (>{max} Ports pro IP)",

    "progress.fetching":   "Abruf",
    "progress.enriching":  "Anreicherung",
    "progress.total":      "gesamt",
    "progress.fail":       "(Fehler)",

    "error.open_output": "proxine: kann '{path}' nicht öffnen: {err}",
    "warning.gh_bad_token": (
        "Warnung: GitHub API hat den Token abgelehnt (401) — "
        "github.com-Quellen fielen auf 'LIVE' statt echtes Alter zurück.\n"
        "         Prüfe die Token-Gültigkeit; für öffentliche Repos sind "
        "keine Scopes nötig."
    ),
    "warning.gh_rate_limit": (
        "Warnung: GitHub API hat in diesem Lauf das Rate-Limit erreicht — "
        "einige github.com-Quellen fielen auf 'LIVE' statt echtes Alter zurück.\n"
        "         --github-token TOKEN, $GITHUB_TOKEN setzen oder "
        "`gh auth login` ausführen, um das Limit auf 5.000 req/h anzuheben."
    ),
    "warning.gh_budget_skip": (
        "Warnung: {n} github.com-Quelle(n) wurden bei der Anreicherung "
        "übersprungen, um unter dem 60/h-Limit\n"
        "         (max. {budget} Anfragen in diesem Lauf) zu bleiben; sie "
        "fielen auf 'LIVE' zurück.\n"
        "         --github-token TOKEN, $GITHUB_TOKEN setzen oder "
        "`gh auth login` ausführen, um alle anzureichern (5.000 req/h mit Token)."
    ),
}

# ---------- Spanish ----------
CATALOGS["es"] = {
    "cli.description": (
        "Agregar listas de proxies frescos desde docenas de fuentes públicas, "
        "deduplicarlos e imprimir una lista IP:PORT ordenada."
    ),
    "cli.examples_header": "Ejemplos:",
    "cli.example.basic":        "Recopilar proxies HTTP a stdout",
    "cli.example.save":         "Guardar proxies HTTPS en archivo",
    "cli.example.url_format":   "Emitir líneas 'socks5://1.2.3.4:1080'",
    "cli.example.parallel":     "32 descargas paralelas",
    "cli.example.impatient":    "Modo impaciente: 5s, sin reintento",
    "cli.example.lasthour":     "Solo fuentes actualizadas en la última hora",
    "cli.example.fresh_off":    "Desactivar filtro de frescura",
    "cli.example.tofile":       "Escribir proxies a archivo; progreso en stderr",
    "cli.example.silent_file":  "Silencioso + archivo: nada en stderr/stdout",
    "cli.help.protocol": (
        "Protocolo proxy a recopilar; uno de {{http, https, socks4, socks5}}. "
        "Obligatorio. Ejemplo: 'proxine.py -p socks5'."
    ),
    "cli.help.format": (
        "Formato de salida. 'ip-port' (predet.) imprime '1.2.3.4:8080'; "
        "'url' antepone el esquema del protocolo."
    ),
    "cli.help.timeout": (
        "Timeout HTTP por fuente en segundos (predet.: {default}). "
        "Las fuentes lentas se abandonan para que un mal host no detenga "
        "la ejecución."
    ),
    "cli.help.concurrency": (
        "Número de fuentes descargadas en paralelo (predet.: {default}). "
        "Valores altos terminan más rápido pero usan más ancho de banda y sockets."
    ),
    "cli.help.retries": (
        "Cuántas veces reintentar una fuente fallida antes de rendirse "
        "(predet.: {default}). 0 = fallar rápido."
    ),
    "cli.help.max_ports": (
        "Descartar una IP por completo si aparece con más de N puertos "
        "distintos en la salida deduplicada (predet.: {default}). Tales "
        "hosts suelen ser escáneres de puertos o honeypots, no proxies "
        "reales. 0 = desactivar."
    ),
    "cli.help.fresh": (
        "Descartar proxies de fuentes más viejas que estos segundos "
        "(predet.: {default} = 24h). Las fuentes sin Last-Modified / info "
        "de commit (p.ej. APIs en vivo) siempre se mantienen. 0 = desactivar."
    ),
    "cli.help.github_token": (
        "Token de acceso personal de GitHub para consultar tiempos de commit "
        "en URLs raw.githubusercontent.com (para que la edad muestre valores "
        "reales en vez de 'LIVE'). Sin token el límite es 60 req/h; proxine "
        "limita las ejecuciones sin autenticar a {budget} consultas para "
        "mantenerse seguro, y las filas github.com restantes quedan en 'LIVE'. "
        "Con token: 5.000 req/h. Orden: este flag → $GITHUB_TOKEN → `gh auth token`."
    ),
    "cli.help.output": (
        "Escribir la lista de proxies en FILE (un IP:PORT por línea) en "
        "vez de stdout. El archivo contiene solo proxies; progreso, "
        "frescura y resumen siguen en stderr."
    ),
    "cli.help.silent": (
        "Imprimir solo la lista de proxies. Suprimir TODA salida stderr "
        "(log por fuente, barra de progreso, reporte de frescura, resumen)."
    ),
    "cli.help.lang": (
        "Idioma de la interfaz. Uno de {{tr, en, de, es, ru, zh}}. Sin este "
        "flag, el idioma se autodetecta desde $PROXINE_LANG, $LC_*/$LANG o "
        "el locale del sistema; fallback al inglés."
    ),
    "cli.help.strict_ports": (
        "Descartar proxies cuyo puerto no coincide con la familia del "
        "protocolo declarado (p.ej. un proxy declarado SOCKS en el puerto 80 "
        "es casi seguramente HTTP). Activo por defecto; usa --no-strict-ports "
        "para salida cruda. Protege frente a fuentes mal categorizadas."
    ),

    "status.col.status":  "ESTADO",
    "status.col.age":     "EDAD",
    "status.col.proxies": "PROXIES",
    "status.col.source":  "FUENTE",
    "status.legend.ok":    "  OK     suficientemente fresco (dentro de --fresh); proxies incluidos",
    "status.legend.live":  "  LIVE   sin Last-Modified / info de commit (API dinámica); proxies incluidos",
    "status.legend.stale": "  STALE  más viejo que --fresh; proxies descartados de la salida",
    "status.legend.fail":  "  FAIL   error de descarga; sin contribución",

    "settings.sources":  "fuentes",
    "settings.baseline": "base",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "off",
    "settings.value.on":               "on",
    "settings.value.drop_thresh":      ">{n} → descartar",
    "settings.value.token_auth":       "token (5.000 req/h)",
    "settings.value.unauthed":         "sin token (máx {budget}/ejec., límite 60/h)",
    "settings.value.baseline_loaded":  "{n:,} entradas cargadas",
    "settings.value.baseline_empty":   "(archivo no existe/vacío — empezando desde cero)",

    "summary.protocol":  "protocolo",
    "summary.proxies":   "proxies",
    "summary.sources":   "fuentes",
    "summary.filtered":  "filtrado",
    "summary.elapsed":   "tiempo",
    "summary.proxies_unique":  "{n:,} únicos",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "{total} total  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} IPs / {entries:,} entradas  (>{max} puertos por IP)",

    "progress.fetching":   "descargando",
    "progress.enriching":  "enriqueciendo",
    "progress.total":      "total",
    "progress.fail":       "(error)",

    "error.open_output": "proxine: no se puede abrir '{path}': {err}",
    "warning.gh_bad_token": (
        "advertencia: la API de GitHub rechazó el token (401) — "
        "las fuentes github.com volvieron a 'LIVE' en vez de edad real.\n"
        "             Verifica que el token sea válido; no se requieren "
        "scopes para lectura pública."
    ),
    "warning.gh_rate_limit": (
        "advertencia: rate-limit de la API de GitHub durante esta ejecución — "
        "algunas fuentes github.com volvieron a 'LIVE'.\n"
        "             Pasa --github-token TOKEN, define $GITHUB_TOKEN o "
        "ejecuta `gh auth login` para subir el límite a 5.000 req/h."
    ),
    "warning.gh_budget_skip": (
        "advertencia: {n} fuente(s) github.com saltadas durante el "
        "enriquecimiento para mantenerse bajo el límite\n"
        "             de 60/h sin autenticar ({budget} solicitudes en "
        "esta ejecución); volvieron a 'LIVE'.\n"
        "             Pasa --github-token TOKEN, define $GITHUB_TOKEN o "
        "ejecuta `gh auth login` para enriquecerlas todas (5.000 req/h con token)."
    ),
}

# ---------- Russian ----------
CATALOGS["ru"] = {
    "cli.description": (
        "Агрегировать свежие списки прокси из десятков публичных источников, "
        "удалить дубликаты и напечатать отсортированный список IP:PORT."
    ),
    "cli.examples_header": "Примеры:",
    "cli.example.basic":        "Собрать HTTP-прокси в stdout",
    "cli.example.save":         "Сохранить HTTPS-прокси в файл",
    "cli.example.url_format":   "Выводить строки 'socks5://1.2.3.4:1080'",
    "cli.example.parallel":     "32 параллельных загрузки",
    "cli.example.impatient":    "Нетерпеливый режим: 5с, без повторов",
    "cli.example.lasthour":     "Только источники, обновлённые за последний час",
    "cli.example.fresh_off":    "Отключить фильтр свежести",
    "cli.example.tofile":       "Запись прокси в файл; прогресс в stderr",
    "cli.example.silent_file":  "Тихо + файл: ничего в stderr/stdout",
    "cli.help.protocol": (
        "Протокол прокси для сбора; один из {{http, https, socks4, socks5}}. "
        "Обязательно. Пример: 'proxine.py -p socks5'."
    ),
    "cli.help.format": (
        "Формат вывода. 'ip-port' (по умолчанию) печатает '1.2.3.4:8080'; "
        "'url' добавляет префикс схемы протокола."
    ),
    "cli.help.timeout": (
        "Таймаут HTTP на источник в секундах (по умолч.: {default}). "
        "Медленные источники прерываются, чтобы один плохой хост не блокировал запуск."
    ),
    "cli.help.concurrency": (
        "Число параллельно загружаемых источников (по умолч.: {default}). "
        "Большие значения быстрее, но требуют больше пропускной способности и сокетов."
    ),
    "cli.help.retries": (
        "Сколько раз повторять неудачный источник перед отказом "
        "(по умолч.: {default}). 0 = быстрый отказ."
    ),
    "cli.help.max_ports": (
        "Полностью отбросить IP, если он встречается с более чем N разными "
        "портами в дедуплицированном выводе (по умолч.: {default}). Такие "
        "хосты обычно сканеры портов или honeypot'ы, а не настоящие прокси. "
        "0 = выключить."
    ),
    "cli.help.fresh": (
        "Отбрасывать прокси из источников старше N секунд (по умолч.: "
        "{default} = 24ч). Источники без Last-Modified / информации о коммите "
        "(напр. живые API) сохраняются всегда. 0 = выключить."
    ),
    "cli.help.github_token": (
        "GitHub PAT для запроса времён коммитов на URL raw.githubusercontent.com "
        "(чтобы возраст показывал реальные значения вместо 'LIVE'). Без токена "
        "лимит API 60 запросов/ч; proxine ограничивает запуски без аутентификации "
        "{budget} запросами, чтобы оставаться под лимитом, остальные github.com-"
        "строки остаются 'LIVE'. С токеном лимит 5,000 запросов/ч. "
        "Порядок: этот флаг → $GITHUB_TOKEN → `gh auth token`."
    ),
    "cli.help.output": (
        "Записать список прокси в FILE (один IP:PORT на строку) вместо stdout. "
        "В файле только прокси; прогресс, свежесть и сводка остаются в stderr."
    ),
    "cli.help.silent": (
        "Печатать только список прокси. Подавить ВСЁ в stderr (логи источников, "
        "прогресс-бар, отчёт свежести, сводку)."
    ),
    "cli.help.lang": (
        "Язык интерфейса. Один из {{tr, en, de, es, ru, zh}}. Без этого флага "
        "язык определяется из $PROXINE_LANG, $LC_*/$LANG или системной локали; "
        "fallback — английский."
    ),
    "cli.help.strict_ports": (
        "Отбрасывать прокси, чей порт не соответствует объявленному семейству "
        "протоколов (напр. SOCKS-объявленный прокси на порту 80 почти "
        "наверняка HTTP). По умолчанию включено; --no-strict-ports отключает "
        "для сырого вывода. Защищает от неверно категоризированных источников."
    ),

    "status.col.status":  "СТАТУС",
    "status.col.age":     "ВОЗР",
    "status.col.proxies": "ПРОКСИ",
    "status.col.source":  "ИСТОЧНИК",
    "status.legend.ok":    "  OK     достаточно свежий (в окне --fresh); прокси сохранены",
    "status.legend.live":  "  LIVE   нет Last-Modified / commit info (живой API); прокси сохранены",
    "status.legend.stale": "  STALE  старше --fresh; прокси удалены из вывода",
    "status.legend.fail":  "  FAIL   ошибка загрузки; вклада нет",

    "settings.sources":  "источники",
    "settings.baseline": "базис",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "выкл",
    "settings.value.on":               "вкл",
    "settings.value.drop_thresh":      ">{n} → отброс",
    "settings.value.token_auth":       "токен (5,000 запросов/ч)",
    "settings.value.unauthed":         "без токена (лимит {budget}/запуск, 60/ч)",
    "settings.value.baseline_loaded":  "{n:,} записей загружено",
    "settings.value.baseline_empty":   "(файл отсутствует/пуст — старт с нуля)",

    "summary.protocol":  "протокол",
    "summary.proxies":   "прокси",
    "summary.sources":   "источники",
    "summary.filtered":  "отфильтровано",
    "summary.elapsed":   "время",
    "summary.proxies_unique":  "{n:,} уникальных",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "{total} всего  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} IP / {entries:,} записей  (>{max} портов на IP)",

    "progress.fetching":   "загрузка",
    "progress.enriching":  "обогащение",
    "progress.total":      "всего",
    "progress.fail":       "(ошибка)",

    "error.open_output": "proxine: не удаётся открыть '{path}': {err}",
    "warning.gh_bad_token": (
        "предупреждение: GitHub API отклонил токен (401) — "
        "источники github.com показали 'LIVE' вместо реального возраста.\n"
        "                Проверьте валидность токена; для чтения публичных "
        "репозиториев scope не нужен."
    ),
    "warning.gh_rate_limit": (
        "предупреждение: GitHub API ограничил скорость в этом запуске — "
        "некоторые github.com показали 'LIVE'.\n"
        "                Передайте --github-token TOKEN, задайте "
        "$GITHUB_TOKEN или выполните `gh auth login` для лимита 5,000 запросов/ч."
    ),
    "warning.gh_budget_skip": (
        "предупреждение: {n} источник(а/ов) github.com пропущено при "
        "обогащении, чтобы остаться под лимитом 60/ч\n"
        "                без токена ({budget} запросов в этом запуске); "
        "они остались 'LIVE'.\n"
        "                Передайте --github-token TOKEN, задайте "
        "$GITHUB_TOKEN или выполните `gh auth login` для обогащения всех."
    ),
}

# ---------- Chinese (Simplified) ----------
CATALOGS["zh"] = {
    "cli.description": (
        "从数十个公开源聚合新鲜的代理列表，去重后输出排序的 IP:PORT 列表。"
    ),
    "cli.examples_header": "示例：",
    "cli.example.basic":        "采集 HTTP 代理到 stdout",
    "cli.example.save":         "将 HTTPS 代理保存到文件",
    "cli.example.url_format":   "输出 'socks5://1.2.3.4:1080' 行",
    "cli.example.parallel":     "32 并行抓取",
    "cli.example.impatient":    "急速模式：5 秒，不重试",
    "cli.example.lasthour":     "仅最近 1 小时内更新的源",
    "cli.example.fresh_off":    "禁用新鲜度过滤器",
    "cli.example.tofile":       "将代理写入文件；进度在 stderr",
    "cli.example.silent_file":  "静默 + 文件：stderr/stdout 上无输出",
    "cli.help.protocol": (
        "要采集的代理协议；{{http, https, socks4, socks5}} 之一。必填。"
        "示例: 'proxine.py -p socks5'。"
    ),
    "cli.help.format": (
        "输出格式。'ip-port'（默认）打印 '1.2.3.4:8080'；"
        "'url' 在前面加上协议方案。"
    ),
    "cli.help.timeout": (
        "每个源的 HTTP 超时秒数（默认: {default}）。慢的上游会被放弃，"
        "避免单个坏主机阻塞整次运行。"
    ),
    "cli.help.concurrency": (
        "并行抓取的源数量（默认: {default}）。值越大越快，"
        "但占用更多带宽和套接字。"
    ),
    "cli.help.retries": (
        "放弃前对失败源的重试次数（默认: {default}）。设为 0 = 快速失败。"
    ),
    "cli.help.max_ports": (
        "如果一个 IP 在聚合去重输出中出现超过 N 个不同端口，则整体丢弃"
        "（默认: {default}）。这类主机通常是端口扫描器或蜜罐，而非真正的代理。"
        "0 = 禁用。"
    ),
    "cli.help.fresh": (
        "丢弃来源超过指定秒数的代理（默认: {default} = 24h）。"
        "无 Last-Modified / commit 信息的源（如实时 API）总是保留。0 = 禁用。"
    ),
    "cli.help.github_token": (
        "用于查询 raw.githubusercontent.com URL 的 commit 时间的 GitHub PAT"
        "（让源年龄显示真实值而非 'LIVE'）。无 token 时 API 限额为 60 req/h；"
        "为安全起见，proxine 将无 token 的运行限制为 {budget} 次 commit 查询，"
        "其余 github.com 行回退为 'LIVE'。有 token 时限额为 5,000 req/h。"
        "顺序：此标志 → $GITHUB_TOKEN → `gh auth token`。"
    ),
    "cli.help.output": (
        "将代理列表写入 FILE（每行一个 IP:PORT）而非 stdout。"
        "文件只包含代理；进度、新鲜度和摘要仍在 stderr。"
    ),
    "cli.help.silent": (
        "仅打印代理列表。抑制所有 stderr 输出（每源日志、进度条、新鲜度报告、摘要）。"
    ),
    "cli.help.lang": (
        "界面语言。{{tr, en, de, es, ru, zh}} 之一。不指定时从 $PROXINE_LANG、"
        "$LC_*/$LANG 或系统区域自动检测；回退到英语。"
    ),
    "cli.help.strict_ports": (
        "丢弃端口不符合声明协议族的代理（例如声明为 SOCKS 但在 80 端口的"
        "代理几乎肯定是 HTTP）。默认启用；用 --no-strict-ports 禁用以获取"
        "原始输出。可防止源列表错误分类。"
    ),

    "status.col.status":  "状态",
    "status.col.age":     "年龄",
    "status.col.proxies": "代理数",
    "status.col.source":  "来源",
    "status.legend.ok":    "  OK     足够新鲜（在 --fresh 窗口内）；代理保留",
    "status.legend.live":  "  LIVE   无 Last-Modified / commit 信息（动态 API）；代理保留",
    "status.legend.stale": "  STALE  超过 --fresh；代理从输出中移除",
    "status.legend.fail":  "  FAIL   抓取错误；无贡献",

    "settings.sources":  "来源数",
    "settings.baseline": "基线",
    "settings.value.stdout":           "(stdout)",
    "settings.value.off":              "关闭",
    "settings.value.on":               "启用",
    "settings.value.drop_thresh":      ">{n} → 丢弃",
    "settings.value.token_auth":       "token（5,000 req/h）",
    "settings.value.unauthed":         "无 token（每次最多 {budget}，限额 60/h）",
    "settings.value.baseline_loaded":  "已载入 {n:,} 条",
    "settings.value.baseline_empty":   "（文件缺失/为空 — 从零开始）",

    "summary.protocol":  "协议",
    "summary.proxies":   "代理",
    "summary.sources":   "来源",
    "summary.filtered":  "已过滤",
    "summary.elapsed":   "耗时",
    "summary.proxies_unique":  "{n:,} 唯一",
    "summary.proxies_dest":    "  →  {path}",
    "summary.sources_value":   "共 {total}  ({ok} ok, {live} live, {stale} stale, {fail} fail)",
    "summary.filtered_value":  "{ips:,} 个 IP / {entries:,} 条  (每 IP >{max} 个端口)",

    "progress.fetching":   "抓取中",
    "progress.enriching":  "丰富信息",
    "progress.total":      "总计",
    "progress.fail":       "（错误）",

    "error.open_output": "proxine: 无法打开 '{path}': {err}",
    "warning.gh_bad_token": (
        "警告: GitHub API 拒绝了提供的 token (401) — "
        "github.com 来源回退为 'LIVE' 而非真实年龄。\n"
        "       请检查 token 有效性；公开仓库读取不需要任何 scope。"
    ),
    "warning.gh_rate_limit": (
        "警告: 本次运行 GitHub API 触发了限流 — "
        "部分 github.com 来源回退为 'LIVE' 而非真实年龄。\n"
        "       传入 --github-token TOKEN、设置 $GITHUB_TOKEN，或运行 "
        "`gh auth login` 将限额提升至 5,000 req/h。"
    ),
    "warning.gh_budget_skip": (
        "警告: 为保持在 GitHub 无 token 60/h 限额之下，{n} 个 github.com "
        "来源在丰富信息阶段被跳过\n"
        "       （本次运行 {budget} 次请求上限）；它们保持为 'LIVE'。\n"
        "       传入 --github-token TOKEN、设置 $GITHUB_TOKEN，或运行 "
        "`gh auth login` 以丰富全部（带 token 5,000 req/h）。"
    ),
}
