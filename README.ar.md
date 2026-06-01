<p align="right">
<sub>
<a href="README.md">🇹🇷 Türkçe</a> ·
<a href="README.en.md">🇬🇧 English</a> ·
<a href="README.ru.md">🇷🇺 Русский</a> ·
<a href="README.de.md">🇩🇪 Deutsch</a> ·
<a href="README.ja.md">🇯🇵 日本語</a> ·
<a href="README.es.md">🇪🇸 Español</a> ·
<b>🇸🇦 العربية</b> ·
<a href="README.zh.md">🇨🇳 中文</a>
</sub>
</p>

<div dir="rtl">

# 🚀 Proxine

مُجمِّع قوائم بروكسي مفتوح المصدر. بأمر واحد يقوم بجلب البروكسيات
**HTTP / HTTPS / SOCKS4 / SOCKS5** بالتوازي من عشرات المصادر العامة،
ويُسقط تلقائياً المصادر القديمة، ويزيل التكرار، ويتحقق من الصحة، ثم يُخرج
قائمة `IP:PORT` نظيفة ومُرتَّبة.

<p align="center">
<b>60 مصدراً فريداً</b> · <b>166 نقطة نهاية</b><br>
HTTP: 51 &nbsp;·&nbsp; HTTPS: 29 &nbsp;·&nbsp; SOCKS4: 42 &nbsp;·&nbsp; SOCKS5: 44
</p>

> Proxine مُجمِّع وليس فاحص جودة. للحصول على بروكسيات تعمل فعلاً وذات
> مستوى Elite، مرِّر الخرج إلى أداة فحص مثل
> [Proxy Profiler](https://github.com/enseitankado/proxy-profiler).

------------------------------------------------------------

## الميزات

- **60 مصدراً مختلفاً**، 166 نقطة نهاية — قوائم GitHub raw + 9 موجزات
  ديناميكية API/HTML.
- **جلب HTTP متوازٍ** — الافتراضي مهذب (`-c 1`)؛ مع `-c 20`+ يصبح أسرع
  بحوالي 10×.
- **مهلة + إعادة محاولة لكل مصدر** — لن يُعطِّل مضيف بطيء التنفيذ بأكمله.
- **تتبع الحداثة.** يُبلَّغ آخر تحديث لكل مصدر؛ ولمصادر GitHub يُستخرج
  وقت الـ commit عبر الـ API. `-F SECONDS` يُسقط المصادر القديمة (افتراضياً
  24 ساعة).
- **تحقق صارم.** ثمانيات IPv4 (0–255) والمنافذ (1–65535) تُفحص بتعبير
  منتظم مُحكم.
- **خرج ذكي.** شريط تقدم في الطرفية؛ صامت في الأنابيب؛ جداول حالة ASCII؛
  `-s` للصمت الكامل؛ `-o` للكتابة إلى ملف.
- **بدون اعتماديات.** فقط مكتبة Python ≥ 3.10 القياسية.

------------------------------------------------------------

## التثبيت

```bash
git clone https://github.com/enseitankado/proxine.git
cd proxine
chmod +x proxine.py
./proxine.py --help
```

المتطلب: **Python ≥ 3.10**. اختياري: `gh` CLI أو رمز وصول شخصي من GitHub
(لاستخراج أعمار المصادر — انظر أدناه).

------------------------------------------------------------

## الاستخدام

```bash
./proxine.py -p <http|https|socks4|socks5> [خيارات]
```

### الأعلام

| الطويل | القصير | الافتراضي | الوصف |
|---|---|---|---|
| `--protocol` | `-p` | — | **إلزامي.** البروتوكول المطلوب جمعه: `http`، `https`، `socks4`، `socks5`. |
| `--format` | `-f` | `ip-port` | تنسيق الخرج. `url` يُنتج `<proto>://IP:PORT`. |
| `--timeout` | `-t` | `15` | مهلة HTTP لكل مصدر (ثواني). |
| `--concurrency` | `-c` | `1` | عدد الطلبات المتوازية. أعلى = أسرع + سوكتات أكثر. |
| `--retries` | `-r` | `2` | محاولات إعادة لكل مصدر فاشل. |
| `--max-ports` | `-m` | `5` | إسقاط IP بالكامل إذا ظهر على أكثر من N منفذاً مختلفاً (فلتر ماسحات المنافذ/honeypot). `0` يُعطِّل. |
| `--fresh` | `-F` | `86400` | إسقاط المصادر الأقدم من N ثانية. `0` يُعطِّل. |
| `--github-token` | `-g` | — | GitHub PAT. بدونه `$GITHUB_TOKEN`، ثم `gh auth token`. |
| `--output` | `-o` | — | كتابة قائمة البروكسي إلى FILE؛ stdout يبقى فارغاً. |
| `--lang` | `-L` | تلقائي | لغة الواجهة: `tr`، `en`، `de`، `es`، `ru`، `zh`. وإلا يُكتشف تلقائياً من `$PROXINE_LANG`/`$LANG`/المنطقة. |
| `--strict-ports` / `--no-strict-ports` | — | مفعَّل | إسقاط البروكسيات التي لا يتطابق منفذها مع عائلة البروتوكول المُعلَنة (مثلاً SOCKS مُعلَن على المنفذ 80). |
| `--silent` | `-s` | — | كتم كل خرج stderr. |

### أمثلة

```bash
# بروكسيات HTTPS إلى stdout (مرشح الحداثة الافتراضي: 24 ساعة)
./proxine.py -p https

# قائمة SOCKS5 إلى ملف، أسرع
./proxine.py -p socks5 -c 32 -o socks5.lst

# فقط المصادر المُحدَّثة في آخر ساعة
./proxine.py -p http -F 3600

# خرج بصيغة URL: socks5://1.2.3.4:1080
./proxine.py -p socks5 -f url

# الوضع الصامت — مثالي لخطوط الأنابيب
./proxine.py -p http -s | grep '^192\.'

# سلسلة مع Proxy Profiler
./proxine.py -p http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

### رمز GitHub (اختياري لكن موصى به)

روابط GitHub raw لا تُعيد `Last-Modified`، لذا تُستخرج أعمار المصادر عبر
GitHub API. **الحد المجهول 60 طلباً/ساعة**؛ تشغيل واحد يصل إلى 50+ رابط
GitHub، لذا بدون رمز تظهر معظم الأعمار كـ «LIVE». مع الرمز يرتفع الحد إلى
**5,000 طلب/ساعة** — لا حاجة لصلاحية `repo`، يكفي القراءة العامة.

ثلاث طرق — يختار Proxine أول متاحة:

```bash
# 1) علم صريح
./proxine.py -p socks5 -g ghp_xxx

# 2) متغير بيئة
export GITHUB_TOKEN=ghp_xxx
./proxine.py -p socks5

# 3) لا شيء — إذا كان `gh` CLI مثبتاً ومُسجَّل الدخول
./proxine.py -p socks5
```

إذا تجاوز الرمز الحد أو كان غير صالح، يظهر تحذير واضح في نهاية التقرير.

------------------------------------------------------------

## الخرج

### 1. شريط التقدم

أثناء التنفيذ، مرحلتان على stderr:

```
[████████████░░░░░░░░]  60%  24/43  fetching  ✓ github.com/komutan234/Proxy-List-Free  +10,794  total 69,749
[██████████████████░░]  90%  18/20  enriching ✓ github.com/Mohammedcha/ProxRipper                total 309,478
```

- شريط `█/░` بطول 20 محرفاً، نسبة مئوية، منجَز/الإجمالي
- تسمية المرحلة: `fetching` (HTTP) أو `enriching` (Commit API)
- `✓` نجاح، `x` فشل
- `+N` بروكسيات جديدة من هذا المصدر
- `total N` الإجمالي الفريد التراكمي

صامت تلقائياً خارج الطرفية (لا يُلوِّث المخرجات المُعاد توجيهها).

### 2. جدول حالة المصادر

في النهاية، على stderr:

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
  OK     طازج ضمن نافذة `--fresh`؛ البروكسيات مُستخدَمة
  LIVE   لا معلومات عمر (API ديناميكي)؛ البروكسيات مُستخدَمة
  STALE  أقدم من `--fresh`؛ البروكسيات مُستبعَدة من الخرج
  FAIL   خطأ في الجلب؛ لا مساهمة
```

الترتيب: OK (الأحدث في الأعلى) → LIVE → STALE → FAIL.

### 3. صندوق الملخص

```
┌──────────┬─────────────────────────────────────────────┐
│ protocol │ socks5                                      │
│ proxies  │ 205,978 unique  →  /tmp/p.lst               │
│ sources  │ 43 total  (30 ok, 1 live, 12 stale, 0 fail) │
│ elapsed  │ 33.8s                                       │
└──────────┴─────────────────────────────────────────────┘
```

### مصفوفة أوضاع الخرج

| الأمر | stdout | stderr |
|---|---|---|
| `proxine -p http` | قائمة البروكسي | سجل لكل مصدر + تقدم → جدول الحالة → ملخص |
| `proxine -p http -o f.lst` | (فارغ) | سجل لكل مصدر + تقدم → جداول |
| `proxine -p http -s` | قائمة البروكسي | (فارغ) |
| `proxine -p http -o f.lst -s` | (فارغ) | (فارغ) |

------------------------------------------------------------

## المصادر

إجمالي **60 مصدراً فريداً**، **166 نقطة نهاية للبروتوكولات**. جميعها
معرَّفة في `sources.py`؛ إضافة مصدر جديد تغيير من سطر واحد.

### قوائم GitHub raw (51 مستودعاً)

| Repo | البروتوكولات |
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

### مصادر API و HTML الديناميكية (9 نقاط)

| Endpoint | النوع | البروتوكولات |
|---|---|---|
| `api.proxyscrape.com` | API عام | http, https, socks4, socks5 |
| `pubproxy.com` | API عام | http, https, socks4, socks5 |
| `proxyspace.pro` | قائمة نصية | http, https, socks5 |
| `spys.me` | قائمة نصية | socks4, socks5 |
| `free-proxy-list.net` | كشط HTML | http |
| `www.google-proxy.net` | كشط HTML | http, https |
| `www.ipaddress.com` | كشط HTML | http, https |
| `www.socks-proxy.net` | كشط HTML | socks4 |
| `www.sslproxies.org` | كشط HTML | https |

------------------------------------------------------------

## الأتمتة

Proxine مُصمَّم للتشغيل لمرة واحدة؛ للتحديثات المُجدوَلة لُفّه بـ cron /
systemd-timer / GitHub Actions. لخطوط الأنابيب يُوصى بـ `-s` و `-o`:

```bash
# Cron: تحديث قائمة SOCKS5 كل ساعة
0 * * * * cd ~/proxine && ./proxine.py -p socks5 -s -o /var/lib/proxies/socks5.lst

# سلسلة مع Proxy Profiler (فحص الحياة + اختبار elite)
./proxine.py -p http -s | php proxy-profiler/proxyprof.php -t http -l 1 -e -o working.lst
```

------------------------------------------------------------

## أدوات ذات صلة

- **[Proxy Profiler](https://github.com/enseitankado/proxy-profiler)** —
  فاحص متعدد الخيوط للحياة والإخفاء (Elite/Anonymous/Transparent) واجتياز
  CloudFlare و Google.
- **[EliteProxySwitcher](https://www.eliteproxyswitcher.com/)** — مُدوِّر
  بروكسي ذو واجهة رسومية لويندوز.
- **[Open Proxy Checker](https://openproxy.space/software/proxy-checker)** —
  مُحقق قوائم لويندوز.

------------------------------------------------------------

## الترخيص

مفتوح المصدر. يمكنك إعادة التوزيع والتعديل والاستخدام التجاري أو الخاص.
حافظ على إسناد المؤلف الأصلي (Özgür Koca) في الأعمال المُشتقة. البرنامج
يُقدَّم «كما هو»؛ كل مخاطر الاستخدام تقع على المستخدم.

## المؤلف

**Özgür Koca** — مُدرِّس في
[مدرسة مهنية](https://samsuneml.meb.k12.tr/).
GitHub: [enseitankado](https://github.com/enseitankado) · مدونة:
[tankado.com](https://www.tankado.com)

## الدعم

إذا وجدته مفيداً، اترك ⭐. تريد أن تشتري لي قهوة؟
[تفضل](https://www.buymeacoffee.com/ozgurkoca).

[![Star History Chart](https://api.star-history.com/svg?repos=enseitankado/proxine&type=Date)](https://star-history.com/#enseitankado/proxine&Date)

</div>
