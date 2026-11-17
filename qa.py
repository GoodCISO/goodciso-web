#!/usr/bin/env python3
"""Pre-deploy QA: internal link integrity, accessibility basics, SEO fields.

Runs against the built output, not the source, because that is what ships.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIST = Path(__file__).parent.resolve() / "dist"

SITE_ROOTS = {
    "aware": "https://aware.goodciso.org",
    "corporate": "https://goodciso.org",
    "docs": "https://docs.aware.goodciso.org",
    "demo": "https://demo.aware.goodciso.org",
}

# Sites that exist on other origins, so a relative link to them is a 404.
EXTERNAL_HOSTS = {
    "aware.goodciso.org", "docs.aware.goodciso.org", "demo.aware.goodciso.org",
    "goodciso.org", "www.goodciso.org", "github.com", "www.npmjs.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.imgs_no_alt = []
        self.h1 = 0
        self.h_levels = []
        self.title = None
        self.meta_desc = None
        self.canonical = None
        self.lang = None
        self.inputs = 0
        self.labels = 0
        self.html = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag == "img" and "alt" not in a:
            self.imgs_no_alt.append(a.get("src", "?"))
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.h_levels.append(int(tag[1]))
            if tag == "h1":
                self.h1 += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta":
            if a.get("name") == "description":
                self.meta_desc = a.get("content")
            if a.get("property") == "og:description":
                self.meta_desc = self.meta_desc or a.get("content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag in ("input", "textarea", "select"):
            self.inputs += 1
        elif tag == "label":
            self.labels += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if getattr(self, "_in_title", False) and self.title is None:
            self.title = data.strip()


def page_files(site: str) -> list[Path]:
    root = DIST / site
    return sorted(p for p in root.rglob("*.html"))


def check_site(site: str) -> dict:
    root = DIST / site
    origin = SITE_ROOTS[site]
    errors, warnings = [], []
    pages = page_files(site)

    for pf in pages:
        rel = pf.relative_to(root)
        url = "/" if str(rel) == "index.html" else "/" + str(rel).replace("index.html", "").rstrip("/")
        html = pf.read_text(encoding="utf-8")
        p = Page()
        p.feed(html)

        # --- SEO ---
        if not p.title or len(p.title) < 10:
            errors.append(f"{url}: missing or thin <title>")
        if not p.meta_desc or len(p.meta_desc) < 50:
            errors.append(f"{url}: missing or thin meta description")
        if not p.canonical:
            errors.append(f"{url}: no canonical")
        elif not p.canonical.startswith(origin):
            errors.append(f"{url}: canonical points off-site: {p.canonical}")
        if p.lang != "en":
            errors.append(f"{url}: lang={p.lang}")

        # --- headings ---
        if p.h1 != 1:
            errors.append(f"{url}: h1 count = {p.h1} (expected 1)")
        prev = 0
        for lv in p.h_levels:
            if prev and lv > prev + 1:
                warnings.append(f"{url}: heading jump h{prev}->h{lv}")
            prev = lv

        # --- images ---
        if p.imgs_no_alt:
            errors.append(f"{url}: img without alt: {p.imgs_no_alt}")

        # --- links ---
        for href in p.links:
            if href.startswith(("http://", "https://")):
                if "goodciso.org" in href and href.split("/")[2] not in EXTERNAL_HOSTS:
                    errors.append(f"{url}: unknown-goodciso host {href}")
                continue
            if href.startswith(("mailto:", "tel:", "#")):
                continue
            if href.startswith("/"):
                clean = href.split("#")[0].split("?")[0]
                if not clean:
                    continue
                target = (root / clean.lstrip("/"))
                if clean.endswith("/"):
                    target = target / "index.html"
                elif not target.suffix:
                    target = target / "index.html"
                if not target.exists():
                    errors.append(f"{url}: broken internal link -> {href}")
            else:
                errors.append(f"{url}: relative link {href} (should be root-absolute)")

        # --- form labels ---
        if p.inputs and p.labels < p.inputs:
            warnings.append(f"{url}: {p.inputs} inputs but {p.labels} labels")

    # --- sitemap integrity ---
    sm = root / "sitemap.xml"
    if sm.exists():
        for loc in re.findall(r"<loc>(.*?)</loc>", sm.read_text()):
            path = loc.replace(origin, "").lstrip("/")
            target = root / path if path else root / "index.html"
            if path and not target.exists():
                target = root / path / "index.html"
            if not target.exists():
                errors.append(f"sitemap: {loc} has no file")
    else:
        errors.append("no sitemap.xml")

    if not (root / "robots.txt").exists():
        errors.append("no robots.txt")

    return {"site": site, "pages": len(pages), "errors": errors, "warnings": warnings}


def main():
    all_res = []
    for site in SITE_ROOTS:
        if not (DIST / site).exists():
            continue
        r = check_site(site)
        all_res.append(r)
        status = "FAIL" if r["errors"] else ("WARN" if r["warnings"] else "PASS")
        print(f"[{status}] {site:10} {r['pages']:3} pages  {len(r['errors'])} errors, {len(r['warnings'])} warnings")
        for e in r["errors"][:25]:
            print("    ERROR  ", e)
        for w in r["warnings"][:10]:
            print("    WARN   ", w)

    total_err = sum(len(r["errors"]) for r in all_res)
    print(f"\nTOTAL ERRORS: {total_err}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
