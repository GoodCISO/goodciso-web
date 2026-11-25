#!/usr/bin/env python3
"""Write per-site Netlify configs.

The corporate site's redirects are the load-bearing part: the live site has
16 URLs in its sitemap with accumulated inbound value. Every one of them must
either resolve to the equivalent new page or 301 to it. Anything dropped is
search equity thrown away, so the mapping is explicit rather than implied.
"""
import json
import os
from pathlib import Path

# The repository root is derived from this file's location, never hardcoded.
# A hardcoded absolute path made the builder work only on the machine it
# was written on — the CI build failed on a path that did not exist there.
ROOT = Path(__file__).parent.resolve()
DIST = ROOT / "dist"

# ---------------------------------------------------------------------------
# Corporate: live URL -> new URL. Anything not listed is a 404.
# ---------------------------------------------------------------------------
CORPORATE_REDIRECTS = [
    # Live URL (old)                     -> New destination              Status
    # NOTE: /pricing.html -> /services/regulatory-readiness is kept, because
    # the old site's pricing page became that page. But "/pricing" must
    # NOT redirect: the new site HAS a /pricing/ page, and the redirect
    # was shadowing it. A reader clicking "Pricing" in the navigation was
    # landing on Regulatory Readiness instead.
    ("/pricing.html", "/services/regulatory-readiness", 301),
    ("/book.html", "/contact", 301),
    ("/book", "/contact", 301),
    ("/services.html", "/services", 301),
    ("/demo", "/aware", 301),
    ("/demo/", "/aware", 301),
    ("/aws-monitor", "/services/security-architecture", 301),
    ("/aws-monitor/", "/services/security-architecture", 301),
    ("/aws-monitor/calculator", "/services/security-architecture", 301),
    ("/aws-monitor/calculator/", "/services/security-architecture", 301),
    ("/security-policy.html", "/about", 301),
    ("/blog/", "/insights", 301),
    ("/blog/what-we-learned-building-agentic-security-workflows.html", "/insights/what-we-learned-building-agentic-security-workflows", 301),
    ("/blog/2026-06-08-container-security-gap-nobody-talks-about.html", "/insights/container-security-gap", 301),
    ("/blog/2026-06-08-why-llm-threat-models-fail.html", "/insights/why-llm-threat-models-fail", 301),
    ("/blog/2026-06-08-devsecops-dead-long-live-devops.html", "/insights/devsecops-is-dead", 301),
    # These three exist on the new site under clean paths, so the .html
    # variants 301 to them rather than to something else.
    ("/contact.html", "/contact", 301),
    ("/privacy.html", "/privacy", 301),
    ("/terms.html", "/terms", 301),
]

# The AI-agent surface on the live site is deliberate and well built. It is
# preserved verbatim rather than rewritten — it was a deliberate, recent
# decision and there is no reason to regress it.
# The AI-agent surface is part of the site and must be in the repository, not
# copied from another checkout at build time. A CI runner has no access to
# the previous corporate site's tree, and a file that only exists on one
# machine is a file that silently disappears from production.
CORPORATE_PRESERVED = ["llms.txt", "agent-instructions.txt", "security.txt"]

# RFC 8461 (MTA-STS). The DNS TXT record for _mta-sts.goodciso.org says
# `v=STSv1; id=20260810232500Z` and the policy must be fetched from
# mta-sts.goodciso.org/.well-known/mta-sts.txt — that hostname is a CNAME to
# this site's Netlify host, so the policy has to be served BY this site.
#
# It was not, and the record says mode: enforce, so a sender that honours
# MTA-STS fetches the policy, gets the 404 page, and treats the domain as
# having no policy — which is exactly what the enforce record was meant to
# prevent. The policy id below must match the DNS TXT id, or senders
# re-fetch on every check.
#
# Same dot-directory problem as security.txt: Netlify's deploy API does not
# ingest dot-directories from a zipped upload, so the policy is written to a
# normal path and served at /.well-known/ through a redirect rule.
MTA_STS_POLICY_PATH = "mta-sts-policy.txt"
MTA_STS_POLICY_ID = "20260810232500Z"

# Every MX host that must appear in the policy, taken from the live DNS MX
# records for goodciso.org. These are listed EXPLICITLY, not as wildcards:
# "*.aspmx.l.google.com" matches subdomains of aspmx.l.google.com, so it
# does NOT match aspmx.l.google.com itself — the primary exchanger.
MTA_STS_EXPECTED_MX = (
    "aspmx.l.google.com",
    "alt1.aspmx.l.google.com",
    "alt2.aspmx.l.google.com",
    "alt3.aspmx.l.google.com",
    "alt4.aspmx.l.google.com",
)

# Netlify's deploy API does not ingest dot-directories from a zipped upload:
# .well-known/security.txt was silently dropped from the file list. RFC 9116
# wants that file at /.well-known/security.txt, and the live site already
# solves this the same way — a redirect rule that serves the content from a
# normal path. The file is written to /security.txt and served from there.
SECURITY_TXT_PATH = "security.txt"

# The Content-Security-Policy is not optional. The previous site's build
# shipped one, and a deploy that dropped it is a security regression even if
# every page still renders.
#
# This site loads webfonts from Google Fonts and nothing else external: no
# booking widget, no analytics script, no third-party embed. So the policy is
# tight by construction. style-src needs 'unsafe-inline' because the
# component layer sets inline styles (the grid gap, the inline CSS custom
# properties on cards).
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "object-src 'none'"
)

BASE_HEADERS = f"""
[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "DENY"
    X-XSS-Protection = "0"
    Content-Security-Policy = "{CSP}"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
    Strict-Transport-Security = "max-age=63072000; includeSubDomains; preload"
    Cross-Origin-Opener-Policy = "same-origin"
    Cross-Origin-Resource-Policy = "same-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"

[[headers]]
  for = "/assets/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/sitemap.xml"
  [headers.values]
    Cache-Control = "public, max-age=86400"

# The machine-readable rendering of each page. It must be served as
# markdown, not as a download, or an answer engine cannot read it
# directly.
[[headers]]
  for = "/*.md"
  [headers.values]
    Content-Type = "text/markdown; charset=utf-8"
    Cache-Control = "public, max-age=3600"

[[headers]]
  for = "/robots.txt"
  [headers.values]
    Cache-Control = "public, max-age=86400"
"""


def toml_redirects(pairs):
    out = []
    for src, dst, status in pairs:
        out.append(
            f'\n[[redirects]]\n  from = "{src}"\n  to = "{dst}"\n  status = {status}\n  force = true\n'
        )
    return "".join(out)


def write_site(key, name, extra=""):
    d = DIST / key
    if not d.exists():
        return None
    cfg = f"[build]\n  publish = \".\"\n\n{BASE_HEADERS}{extra}"
    (d / "netlify.toml").write_text(cfg, encoding="utf-8")
    return d


def main():
    # --- corporate ---------------------------------------------------------
    extra = toml_redirects(CORPORATE_REDIRECTS)
    extra += (
        "\n[[redirects]]\n"
        '  from = "/.well-known/security.txt"\n'
        '  to = "/security.txt"\n'
        "  status = 200\n"
        "  force = true\n"
    )
    # MTA-STS policy — RFC 8461. mta-sts.goodciso.org is a CNAME to this
    # site's Netlify host, so this rule is what serves the policy at the
    # path a sender actually fetches. It must be 200 with the policy body:
    # a redirect stub or a 404 tells the sender there is no policy.
    extra += (
        "\n[[redirects]]\n"
        '  from = "/.well-known/mta-sts.txt"\n'
        f'  to = "/{MTA_STS_POLICY_PATH}"\n'
        "  status = 200\n"
        "  force = true\n"
    )
    # Copy the preserved AI-agent surface from the live repo if present.
    # The previous corporate site's build tree, where the AI-agent surface
    # (llms.txt, agent-instructions.txt) and security.txt live. It is a
    # separate repository; when it is not present the build simply does not
    # copy those files, and the site still deploys.
    live = Path(
        os.environ.get("LEGACY_SITE_DIR")
        or Path.home() / "projects/goodciso-website"
    )
    if not live.exists():
        live = None
    d = DIST / "corporate"
    copied = []
    # The AI-agent surface and security.txt live in the repository under
    # assets/site/. They are copied from there rather than from another
    # checkout, so a CI runner produces exactly the same site as this host.
    for f in CORPORATE_PRESERVED:
        src = ROOT / "assets" / "site" / f
        if src.exists():
            (d / f).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            copied.append(f)
    # .well-known/security.txt — RFC 9116. A security company that drops its
    # own disclosure contact has a credibility problem, and security researchers
    # look for it first.
    # security.txt is copied from the previous corporate site when that
    # repository is present. It is not: the file lives in the repo now, so
    # the copy is skipped and the file in the tree is what ships.
    sec = ROOT / "assets" / "site" / SECURITY_TXT_PATH
    if sec.exists():
        (d / SECURITY_TXT_PATH).write_text(sec.read_text(encoding="utf-8"), encoding="utf-8")
        copied.append(SECURITY_TXT_PATH)
    # MTA-STS policy — RFC 8461. Served from this site because
    # mta-sts.goodciso.org is a CNAME to this site's Netlify host.
    mta = ROOT / "assets" / "site" / MTA_STS_POLICY_PATH
    if mta.exists():
        policy = mta.read_text(encoding="utf-8")
        # The policy id and the DNS TXT id must agree. If they diverge,
        # senders re-fetch the policy on every delivery attempt and the
        # record's cache is worthless — so this fails the build instead.
        if f"id: {MTA_STS_POLICY_ID}" not in policy:
            raise SystemExit(
                f"[netlify] FATAL: {MTA_STS_POLICY_PATH} does not carry id: {MTA_STS_POLICY_ID}. "
                "The DNS TXT record _mta-sts.goodciso.org must carry the same id."
            )
        # The mx list must cover every live MX host. A wildcard such as
        # *.aspmx.l.google.com matches only SUBDOMAINS, so it does not cover
        # the apex host aspmx.l.google.com — which is the primary MX. The
        # previous policy listed only wildcards and would have failed to
        # authorise the domain's primary exchanger.
        policy_mx = {
            line.split(":", 1)[1].strip()
            for line in policy.splitlines()
            if line.strip().startswith("mx:")
        }
        missing_mx = sorted(h for h in MTA_STS_EXPECTED_MX if h not in policy_mx)
        if missing_mx:
            raise SystemExit(
                f"[netlify] FATAL: {MTA_STS_POLICY_PATH} does not list these MX hosts: "
                f"{', '.join(missing_mx)}. A wildcard pattern does not cover the apex host."
            )
        (d / MTA_STS_POLICY_PATH).write_text(policy, encoding="utf-8")
        copied.append(MTA_STS_POLICY_PATH)
    else:
        raise SystemExit(
            f"[netlify] FATAL: {MTA_STS_POLICY_PATH} is missing from assets/site/. "
            "The DNS record _mta-sts.goodciso.org publishes mode: enforce, so the "
            "policy must be served."
        )
    write_site("corporate", "goodciso", extra)
    print(f"[netlify] corporate: {len(CORPORATE_REDIRECTS)} redirects, preserved {copied or 'none'}")

    for key in ("aware", "docs", "demo"):
        write_site(key, key)
        print(f"[netlify] {key}: ok")

    manifest = {
        "corporate": {
            "redirects": [{"from": a, "to": b, "status": s} for a, b, s in CORPORATE_REDIRECTS],
            "preserved": CORPORATE_PRESERVED,
        }
    }
    (ROOT / "deploy" ).mkdir(exist_ok=True)
    (ROOT / "deploy" / "redirects.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("[netlify] manifest -> deploy/redirects.json")


if __name__ == "__main__":
    main()
