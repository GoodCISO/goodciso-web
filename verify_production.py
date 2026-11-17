#!/usr/bin/env python3
"""Final production verification across all four live domains.

Checks, per domain:
  - HTTPS works and the certificate verifies
  - the home page serves the expected content
  - every URL in the sitemap resolves (200 or a redirect that lands on 200)
  - robots.txt and sitemap.xml exist
  - security headers are present

Run:  python3.12 verify_production.py
"""
from __future__ import annotations

import re
import ssl
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

DOMAINS = {
    "goodciso.org": "https://goodciso.org",
    "aware.goodciso.org": "https://aware.goodciso.org",
    "docs.aware.goodciso.org": "https://docs.aware.goodciso.org",
    "demo.aware.goodciso.org": "https://demo.aware.goodciso.org",
}

REQUIRED_HEADERS = [
    "x-content-type-options",
    "strict-transport-security",
    "referrer-policy",
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def fetch(url, method="GET", timeout=30):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), ""
    except Exception as e:  # noqa: BLE001
        return 0, {}, f"ERROR {e}"


def check_domain(host, base):
    print(f"\n{'=' * 68}\n{host}\n{'=' * 68}")
    ok = True

    # 1. TLS
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=20) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
                print(f"  TLS        OK  (valid for {host})")
    except Exception as e:  # noqa: BLE001
        print(f"  TLS        FAIL {e}")
        ok = False

    # 2. home page
    st, hdrs, body = fetch(base)
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
    print(f"  HOME       {st}  {title.group(1).strip()[:60] if title else '(no title)'}")
    if st != 200:
        ok = False

    # 3. headers
    # A deploy is not finished when the command exits 0. It is finished when
    # production has been read back and shown to carry what was intended.
    # The Content-Security-Policy in particular has been lost before: a
    # deploy that shipped no CSP still exited 0 and still rendered every
    # page, so nothing noticed. An absent CSP is a FAILED deploy.
    present = {k.lower() for k in hdrs}
    missing = [h for h in REQUIRED_HEADERS if h not in present]
    if missing:
        print(f"  HEADERS    MISSING: {missing}")
        ok = False
    else:
        print(f"  HEADERS    OK  (security headers present)")

    csp = hdrs.get("Content-Security-Policy", "")
    if not csp:
        print("  CSP        FAIL  no Content-Security-Policy on production")
        ok = False
    else:
        print(f"  CSP        OK   ({len(csp)} chars)")

    xfo = hdrs.get("X-Frame-Options", "")
    # SAMEORIGIN is Netlify's platform default, so SAMEORIGIN proves nothing.
    # Only our own configured value proves our netlify.toml was applied.
    if xfo.upper() != "DENY":
        print(f"  X-FRAME    FAIL  X-Frame-Options is {xfo or '(absent)'}, expected DENY "
              f"(SAMEORIGIN is the Netlify default and means our config did not land)")
        ok = False
    else:
        print("  X-FRAME    OK   DENY (our config landed)")

    # 4. robots + sitemap
    for path in ("/robots.txt", "/sitemap.xml"):
        s, _, b = fetch(base + path)
        print(f"  {path:11} {s}")
        if s != 200:
            ok = False

    # 5. every sitemap URL resolves
    _, _, sm = fetch(base + "/sitemap.xml")
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    bad = []
    for loc in locs:
        s, h, _ = fetch(loc, method="GET")
        if s != 200:
            # follow one redirect hop
            if s in (301, 302, 308) and h.get("Location"):
                s2, _, _ = fetch(urljoin(loc, h["Location"]))
                s = s2
            if s != 200:
                bad.append(f"{loc} -> {s}")
    print(f"  SITEMAP    {len(locs)} URLs, {len(bad)} broken")
    for b in bad[:10]:
        print(f"               BROKEN {b}")
        ok = False

    print(f"  -> {'PASS' if ok else 'FAIL'}")
    return ok


import socket  # noqa: E402

if __name__ == "__main__":
    all_ok = True
    for host, base in DOMAINS.items():
        all_ok &= check_domain(host, base)
    print(f"\n{'=' * 68}")
    print(f"OVERALL: {'ALL FOUR PRODUCTION SITES PASS' if all_ok else 'FAILURES PRESENT'}")
    print("=" * 68)
    sys.exit(0 if all_ok else 1)
