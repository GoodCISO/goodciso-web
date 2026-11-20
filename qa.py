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
        self.icon_hrefs = []
        self.html = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag == "img" and "alt" not in a:
            self.imgs_no_alt.append(a.get("src", "?"))
        elif tag == "link" and a.get("rel") in ("icon", "apple-touch-icon", "shortcut icon"):
            # The favicon set. A link to a file that was never copied is a
            # 404, and a 404 favicon means the browser draws its own
            # broken default icon — so the link exists but the mark does
            # not. That is the same defect as the wrong mark.
            if a.get("href"):
                self.icon_hrefs.append(a["href"])
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


# --- brand guard -------------------------------------------------------
#
# GoodCISO and AWARE are distinct brands that share a component layer. The
# failure mode that matters is not a wrong colour in a stylesheet — it is
# one brand's MARK being served on the other's site, because a corporate
# favicon that is the product's logo misrepresents the relationship between
# the two companies.
#
# The mark is what a visitor sees before they read a word, and it is what
# ends up in a browser history, a bookmark, and a shared link. So the
# checks below run on the BUILT output, not the source: a file that exists
# in assets/ but is never copied is exactly the bug this catches.

# AWARE's Signal green. GoodCISO is teal; this green must never be the
# resolved accent on the corporate site. It was the colour of the mark
# wrongly served on goodciso.org from 2026-11-16 to 2026-11-18.
AWARE_GREENS = {"#22c55e", "#16a34a"}

# The tokens whose RESOLVED value decides the site's accent colour.
ACCENT_TOKENS = ("--gc-accent", "--gc-accent-text", "--gc-accent-solid")


def _css_rules(css: str) -> list[tuple[str, dict]]:
    """(selector, {custom-property: value}) for every rule that declares one."""
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel = " ".join(m.group(1).split())
        decls = {
            d.group(1): d.group(2).strip()
            for d in re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);", m.group(2))
        }
        if decls:
            out.append((sel, decls))
    return out


def _applies(sel: str, theme: str) -> bool:
    """Does this selector apply in the given theme?

    The custom properties are declared on :root, on [data-theme="light"]
    and on [data-theme="dark"]. A rule for one theme must not be read as
    the value for the other.
    """
    if "data-theme" in sel:
        m = re.search(r'data-theme=["\']?(\w+)', sel)
        return m is not None and m.group(1) == theme
    # :root applies in both themes; a bare element selector applies in both.
    return True


def _resolve(vars_: dict, name: str, depth: int = 0):
    """Resolve a custom property through var() references."""
    if depth > 12:
        return None
    v = vars_.get(name)
    if v is None:
        return None
    v = v.strip()
    m = re.fullmatch(r"var\(\s*(--[A-Za-z0-9_-]+)\s*\)", v)
    if m:
        return _resolve(vars_, m.group(1), depth + 1)
    return v


def check_brand(site: str) -> list[str]:
    """Brand bleed between the corporate site and the AWARE product sites."""
    root = DIST / site
    errors: list[str] = []
    if not root.exists():
        return errors

    if site == "corporate":
        # 1. The AWARE mark must not be served as the corporate favicon.
        fav_png = root / "favicon.png"
        if not fav_png.exists():
            errors.append("corporate: no /favicon.png — the corporate mark is missing")
        else:
            # The corporate favicon is a PNG, so its bytes are compared to
            # the committed brand asset rather than pattern-matched.
            brand = Path(__file__).resolve().parent / "assets/brand/favicon-goodciso.png"
            if brand.exists() and fav_png.read_bytes() != brand.read_bytes():
                errors.append(
                    "corporate: /favicon.png is not the GoodCISO brand asset — "
                    "the corporate site must never serve the AWARE mark"
                )

        # 2. The corporate site's RESOLVED accent must be teal, in BOTH
        # themes. The check resolves the cascade rather than grepping for a
        # hex string: tokens.css is the shared base layer and legitimately
        # carries a green ramp, which the corporate brand.css overrides.
        # Grepping the bytes would flag the shared layer forever; resolving
        # it catches the thing that actually reaches the screen.
        assets = root / "assets"
        try:
            css = (assets / "tokens.css").read_text() + "\n" + (assets / "brand.css").read_text()
        except OSError:
            css = ""
        if css:
            rules = _css_rules(css)
            for theme in ("light", "dark"):
                merged: dict = {}
                for sel, decls in rules:
                    if _applies(sel, theme):
                        merged.update(decls)
                for token in ACCENT_TOKENS:
                    resolved = _resolve(merged, token)
                    if resolved and resolved.lower() in AWARE_GREENS:
                        errors.append(
                            f"corporate: {token} resolves to {resolved} in the "
                            f"{theme} theme — that is AWARE's Signal green. "
                            f"GoodCISO is teal."
                        )
    else:
        # 3. The AWARE sites must serve the AWARE mark.
        fav = root / "favicon.svg"
        if not fav.exists():
            errors.append(f"{site}: no /favicon.svg — the AWARE mark is missing")
        elif b"22c55e" not in fav.read_bytes().lower():
            errors.append(f"{site}: /favicon.svg is not the AWARE mark")

    return errors


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

        # --- favicons ---
        # Every icon the page links to must exist in the build output. A
        # link to a missing file is a 404, and a 404 favicon means the
        # browser draws its own broken default icon in place of the mark.
        for href in p.icon_hrefs:
            if not href.startswith("/"):
                continue
            if not (root / href.lstrip("/")).exists():
                errors.append(f"{url}: favicon {href} does not exist in the build")

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

    # --- brand ---
    errors.extend(check_brand(site))

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
