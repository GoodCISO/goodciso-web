#!/usr/bin/env python3
"""Write per-site Netlify configs.

The corporate site's redirects are the load-bearing part: the live site has
16 URLs in its sitemap with accumulated inbound value. Every one of them must
either resolve to the equivalent new page or 301 to it. Anything dropped is
search equity thrown away, so the mapping is explicit rather than implied.
"""
import json
from pathlib import Path

ROOT = Path("/Users/alfie/projects/goodciso-web")
DIST = ROOT / "dist"

# ---------------------------------------------------------------------------
# Corporate: live URL -> new URL. Anything not listed is a 404.
# ---------------------------------------------------------------------------
CORPORATE_REDIRECTS = [
    # Live URL (old)                     -> New destination              Status
    ("/pricing.html", "/services/regulatory-readiness", 301),
    ("/pricing", "/services/regulatory-readiness", 301),
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
    ("/blog/what-we-learned-building-agentic-security-workflows.html", "/insights", 301),
    ("/blog/2026-06-08-container-security-gap-nobody-talks-about.html", "/insights", 301),
    ("/blog/2026-06-08-why-llm-threat-models-fail.html", "/insights", 301),
    ("/blog/2026-06-08-devsecops-dead-long-live-devops.html", "/insights", 301),
    # These three exist on the new site under clean paths, so the .html
    # variants 301 to them rather than to something else.
    ("/contact.html", "/contact", 301),
    ("/privacy.html", "/privacy", 301),
    ("/terms.html", "/terms", 301),
]

# The AI-agent surface on the live site is deliberate and well built. It is
# preserved verbatim rather than rewritten — it was a deliberate, recent
# decision and there is no reason to regress it.
CORPORATE_PRESERVED = ["llms.txt", "llms-full.txt", "agent-instructions.txt", "robots.txt", "sitemap.xml"]

# Netlify's deploy API does not ingest dot-directories from a zipped upload:
# .well-known/security.txt was silently dropped from the file list. RFC 9116
# wants that file at /.well-known/security.txt, and the live site already
# solves this the same way — a redirect rule that serves the content from a
# normal path. The file is written to /security.txt and served from there.
SECURITY_TXT_PATH = "security.txt"

BASE_HEADERS = """
[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "SAMEORIGIN"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    Strict-Transport-Security = "max-age=63072000; includeSubDomains; preload"

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
    # Copy the preserved AI-agent surface from the live repo if present.
    live = Path("/Users/alfie/projects/goodciso-website")
    d = DIST / "corporate"
    copied = []
    for f in CORPORATE_PRESERVED:
        src = live / f
        if src.exists() and not (d / f).exists():
            (d / f).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            copied.append(f)
    # .well-known/security.txt — RFC 9116. A security company that drops its
    # own disclosure contact has a credibility problem, and security researchers
    # look for it first.
    wk = live / ".well-known" / "security.txt"
    if wk.exists():
        (d / SECURITY_TXT_PATH).write_text(wk.read_text(encoding="utf-8"), encoding="utf-8")
        copied.append(SECURITY_TXT_PATH)
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
