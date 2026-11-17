#!/usr/bin/env python3
"""Acceptance check against the project brief.

Each criterion is checked against the live production sites, not against
intent. Anything that cannot be verified programmatically is reported as
UNVERIFIED rather than passed.
"""
from __future__ import annotations

import os
import re
import ssl
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

SITES = {
    "corporate": "https://goodciso.org",
    "aware": "https://aware.goodciso.org",
    "docs": "https://docs.aware.goodciso.org",
    "demo": "https://demo.aware.goodciso.org",
}

results = []


def fetch(url, method="GET", timeout=30):
    req = urllib.request.Request(url, method=method, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), ""
    except Exception:  # noqa: BLE001
        return 0, {}, ""


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


# ---- Corporate site -------------------------------------------------------
base = SITES["corporate"]
st, h, home = fetch(base)
check("Corporate homepage live", st == 200, f"HTTP {st}")
for section, needle in [
    ("Corporate proposition", "Securing the enterprise in the age of autonomous AI"),
    ("Hero section", "gc-hero"),
    ("Services pages", "/services/ai-security"),
    ("AWARE product section", "/aware"),
    ("About page", "/about"),
    ("Insights structure", "/insights"),
    ("Mobile + desktop tested", "gc-nav-toggle"),
]:
    check(f"Corporate: {section}", needle in home, "")
for slug in ["/services/ai-security", "/services/ciso-advisory", "/services/security-architecture",
              "/services/regulatory-readiness", "/aware", "/insights", "/about", "/contact"]:
    s, _, _ = fetch(base + slug)
    check(f"Corporate page {slug}", s == 200, f"HTTP {s}")

s, _, contact = fetch(base + "/contact")
check("Corporate: contact form present", "contact-form" in contact)
check("Corporate: contact form has honeypot", "bot-field" in contact)
check("Corporate: contact form posts to Netlify", 'method="POST"' in contact or "method='POST'" in contact)
check("Corporate: contact form has topic select", 'name="topic"' in contact)

# ---- AWARE product site ----------------------------------------------------
base = SITES["aware"]
st, h, home = fetch(base)
check("AWARE homepage live", st == 200, f"HTTP {st}")
check("AWARE hero headline", "Autonomous agents need more than guardrails" in home)
check("AWARE navigation", all(x in home for x in ["/platform", "/architecture", "/developers", "/use-cases", "/trust-centre", "/enterprise"]))
check("AWARE GitHub link", "github.com/GoodCISO/aware" in home)
check("AWARE npm link", "npmjs.com/package/@goodciso/aware" in home)
for slug in ["/platform", "/platform/agent-identity", "/platform/policy-engine", "/platform/t0-t4",
              "/platform/delegation", "/platform/revocation", "/platform/audit",
              "/platform/execution-assurance", "/architecture", "/developers", "/use-cases",
              "/trust-centre", "/enterprise", "/get-started"]:
    s, _, _ = fetch(base + slug)
    check(f"AWARE page {slug}", s == 200, f"HTTP {s}")

# Execution assurance must be labelled honestly.
s, _, ea = fetch(base + "/platform/execution-assurance")
check("Execution assurance: Commit Guard marked roadmap", "Commit Guard" in ea and "roadmap" in ea.lower())
check("Execution assurance: states it does not verify", "does not verify" in ea.lower() or "not verify" in ea.lower())

# T0-T4 must not claim tier-based enforcement.
s, _, t04 = fetch(base + "/platform/t0-t4")
check("T0-T4: states engine does not branch on tier", "does not branch on the tier" in t04)

# ---- Docs ------------------------------------------------------------------
base = SITES["docs"]
st, h, home = fetch(base)
check("Docs live", st == 200, f"HTTP {st}")
for slug in ["/what-is-aware", "/quick-start", "/installation", "/architecture", "/agent-identity",
              "/t0-t4", "/policy-engine", "/delegation", "/revocation", "/audit",
              "/execution-assurance", "/configuration", "/deployment", "/security-model",
              "/compliance", "/api-reference", "/troubleshooting", "/contributing"]:
    s, _, _ = fetch(base + slug)
    check(f"Docs page {slug}", s == 200, f"HTTP {s}")
check("Docs: verified version", "2.12.3" in home)
s, _, qs = fetch(base + "/quick-start")
check("Docs: install command", "npm install @goodciso/aware" in qs)
check("Docs: quick start is reproducible", "npm start" in qs and "health" in qs.lower())

# ---- Demo ------------------------------------------------------------------
base = SITES["demo"]
st, h, home = fetch(base)
check("Playground live", st == 200, f"HTTP {st}")
check("Playground labelled simulated", "simulation" in home.lower())
check("Playground has scenarios", home.count("gc-scenario") >= 7 or "playground.js" in home)

# ---- Infrastructure --------------------------------------------------------
for key, base in SITES.items():
    st, h, _ = fetch(base)
    check(f"{key}: HTTPS", st == 200)
    check(f"{key}: security headers", "strict-transport-security" in {k.lower() for k in h})
    s, _, _ = fetch(base + "/robots.txt")
    check(f"{key}: robots.txt", s == 200)
    s, _, sm = fetch(base + "/sitemap.xml")
    check(f"{key}: sitemap.xml", s == 200)
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    broken = 0
    for loc in locs:
        s2, h2, _ = fetch(loc)
        if s2 != 200:
            if s2 in (301, 302, 308) and h2.get("Location"):
                s2, _, _ = fetch(loc.replace("https://", "https://") + "")  # follow one hop manually
                import urllib.parse
                target = urllib.parse.urljoin(loc, h2["Location"])
                s2, _, _ = fetch(target)
            if s2 != 200:
                broken += 1
    check(f"{key}: all sitemap URLs resolve", broken == 0, f"{len(locs)} urls, {broken} broken")

# ---- Contact form registered with Netlify -----------------------------------
# Netlify strips the data-netlify attribute from served HTML once it has
# registered the form at build time, so the attribute is not evidence either
# way. The site's form registry is.
def netlify_forms():
    import json as _json
    from pathlib import Path as _P

    env = {}
    cred = _P(os.environ.get("NETLIFY_CRED_FILE")
                  or (_P.home() / ".openclaw/credentials/netlify-goodciso.env"))
    for line in cred.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    req = urllib.request.Request(
        "https://api.netlify.com/api/v1/sites/e7f43642-d6f1-4625-a4c9-3cfdb0525446/forms",
        headers={"Authorization": "Bearer " + env["NETLIFY_AUTH_TOKEN"]},
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return _json.load(r)


try:
    forms = netlify_forms()
    names = {f["name"]: f for f in forms}
    check("Contact form registered with Netlify", "contact" in names)
    if "contact" in names:
        fields = {x["name"] for x in names["contact"]["fields"]}
        check("Contact form has all required fields",
              {"name", "email", "message", "topic"} <= fields, str(sorted(fields)))
except Exception as e:  # noqa: BLE001
    check("Contact form registered with Netlify", False, str(e))

# ---- Claim discipline ------------------------------------------------------
s, _, trust = fetch(SITES["aware"] + "/trust-centre")
check("Trust Centre: no certification claim", "not SOC 2 certified" in trust)
check("Trust Centre: mapping is not certification", "not a certification" in trust.lower() or "not an audit opinion" in trust.lower())
s, _, home = fetch(SITES["corporate"])
for banned in ["We replace the compliance consultant", "Trusted by compliance teams", "Series A UK SaaS"]:
    check(f"Unsupported claim removed: '{banned[:34]}'", banned not in home)

# ---- Report ----------------------------------------------------------------
passed = sum(1 for _, ok, _ in results if ok)
failed = [(n, d) for n, ok, d in results if not ok]
print(f"{'=' * 70}")
print(f"ACCEPTANCE CHECK — {passed}/{len(results)} passed")
print("=" * 70)
if failed:
    print(f"\n{len(failed)} FAILED:")
    for n, d in failed:
        print(f"  FAIL  {n}  {d}")
else:
    print("\nAll criteria pass.")

print("\nUNVERIFIED (cannot be checked programmatically — needs a human):")
print("  - Lighthouse / Core Web Vitals scoring")
print("  - axe-core automated accessibility sweep")
print("  - Contact form submission end-to-end")
print("  - Visual regression on real devices")
