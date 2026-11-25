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

# The committed brand assets. The brand guard compares the BUILT output
# against these by content, so a build that ships the wrong mark cannot
# pass by renaming the file.
BRAND_DIR = Path(__file__).parent.resolve() / "assets/brand"

# The geometry of AWARE's shield-and-checkmark, as it is written in the
# inline <svg> the AWARE header renders (build.py AWARE_LOGO).
#
# It is a signature rather than a colour, on purpose. The June 2026 defect
# put a TEAL rounded square with a white check in the corporate header —
# teal is the corporate hue, so a colour test would have passed it. The
# shape is what actually distinguishes the two marks, so the shape is what
# the guard looks for.
AWARE_SHIELD_SIGNATURE = "M12 2.5 4 6v6.2"


def pub(site: str) -> Path:
    """The published root of a site.

    The deploy root holds the published site, the Netlify function under
    netlify/, and netlify.toml. publish = ".", so the site's own files
    are at the root.
    """
    return DIST / site


def _header_logo_anchor(html: str) -> str | None:
    """The header's logo anchor, or None if the header has no logo.

    Scoped to the <header> element, then to the anchor carrying class
    "gc-logo" inside it. Both scopings are load-bearing:

    - Scoping to <header> matters because the footer repeats the logo. A
      check that searched the whole page would let a correct footer satisfy
      a wrong header — and a header with no mark at all would pass, because
      the footer's mark was still there.
    - Scoping to the anchor matters so that body copy cannot satisfy the
      check.
    """
    hm = re.search(r"<header\b.*?</header>", html, re.S)
    if not hm:
        return None
    m = re.search(
        r"<a\b[^>]*class=\"[^\"]*\bgc-logo\b[^\"]*\"[^>]*>.*?</a>", hm.group(0), re.S
    )
    return m.group(0) if m else None


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
        self.og_images = []
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
            if a.get("property") == "og:image":
                self.og_images.append(a.get("content") or "")
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
    return sorted(p for p in pub(site).rglob("*.html"))


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

# The same two colours in rgb()/rgba() notation, so a literal written in
# either form is recognised as Signal green. #22C55E is rgb(34, 197, 94) and
# #16A34A is rgb(22, 163, 74) — the guard must not report "that is not
# derived" when the real problem is "that is the other brand's green".
AWARE_GREENS_RGB = {"rgb(34,197,94)", "rgb(22,163,74)"}


def _is_aware_green(value: str) -> bool:
    """True if the colour is AWARE's Signal green, in hex or rgb notation."""
    if not value:
        return False
    low = value.lower().replace(" ", "")
    if low in AWARE_GREENS:
        return True
    # rgba(34, 197, 94, 0.14) -> rgb(34, 197, 94)
    m = re.fullmatch(r"rgba?\(([^)]+)\)", low)
    if m:
        parts = m.group(1).split(",")[:3]
        if len(parts) == 3:
            try:
                triple = ",".join(str(int(float(p))) for p in parts)
            except ValueError:
                return False
            return f"rgb({triple})" in AWARE_GREENS_RGB
    return False

# The tokens whose RESOLVED value decides the site's accent colour.
ACCENT_TOKENS = ("--gc-accent", "--gc-accent-text", "--gc-accent-solid")

# Tokens that must be DERIVED from the accent rather than written as a
# literal colour. The hero glow is a tint of the accent:
#     --gc-hero-glow: color-mix(in srgb, var(--gc-accent) 10%, transparent);
# Derived, it follows the brand ramp in every theme and cannot be a stale
# literal from the other brand. Hard-coded, it can be — and was: it was a
# literal of AWARE's Signal green in the shared token layer, and a literal
# teal in the corporate brand block, which is the same value written twice
# in two places that could drift apart.
DERIVED_FROM_ACCENT = "--gc-hero-glow"


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


# Superseded GoodCISO logo assets, and the reason each is retired.
#
# The byte-comparison guards catch a mark crossing between BRANDS. They do
# not catch a SUPERSEDED asset being picked up within one brand, which is
# how AWARE's teal square-and-check stayed on goodciso.org for roughly
# eighteen months: it was a goodciso.org file, on goodciso.org, and every
# check that only asked "is this the right brand?" was satisfied.
#
# A guard that only knows the current answer cannot see a regression to a
# previous one. These names are the previous answers.
#
# The full history, with dates and the evidence for each, is in
# docs/LOGO-HISTORY.md.
#
# NOTE on generic names. "favicon.ico" is NOT in this list, and must not
# be: the corporate site legitimately serves /favicon.ico, and that file
# currently holds the CORRECT GoodCISO icon (byte-identical to
# assets/brand/favicon-goodciso.ico). The AWARE tick that once lived at
# that path was a CONTENT defect, and content is exactly what the
# byte-comparison guards already cover. Retiring a generic FILENAME would
# flag every page.
#
# So this set holds names that are retired AS NAMES: a superseded file
# that would be picked up again wholesale if it were still in the tree.
RETIRED_ASSETS = {
    # The 2024 vector wordmark: "Good CISO" in black with no mark at all,
    # generated by Matplotlib and referenced by nothing.
    "Good_CISO_Wordmark.svg": "type-only lockup, no mark",
    # A gradient texture that was never a logo.
    "logo.webp": "gradient texture, never a mark",
    # Stock platform logos.
    "linkedin-icon.png": "stock LinkedIn glyph",
    "linkedin-icon.webp": "stock LinkedIn glyph",
    "twitter-icon.png": "stock Twitter glyph",
    "twitter-icon.webp": "stock Twitter glyph",
    # AWARE's mark, installed as GoodCISO's PWA icons.
    "icon-192x192.png": "AWARE mark, wrong brand",
    "icon-512x512.png": "AWARE mark, wrong brand",
    "maskable-icon-192x192.png": "AWARE mark, wrong brand",
    "maskable-icon-512x512.png": "AWARE mark, wrong brand",
    # The hand-drawn approximation: correct shield, but a TEAL centre dot
    # and a navy counter where the original has an amber dot and a white
    # G-shaped counter. Close enough to look deliberate, which is worse.
    "favicon-goodciso.svg": "approximation - teal dot, navy counter",
    # The Matplotlib-generated wordmark, under the name the guard uses.
    "goodciso-wordmark.svg": "type-only lockup, no mark",
}


def check_retired_assets(site: str) -> list[str]:
    """No built page may reference a superseded logo asset.

    This is the check that would have caught the eighteen-month window.
    """
    root = DIST / site
    errors: list[str] = []
    if not root.exists():
        return errors

    for page in sorted(pub(site).rglob("*.html")):
        html = page.read_text(errors="ignore")
        # Match the asset NAME as a whole, not as a substring.
        # "favicon.ico" is a substring of the current
        # "favicon-goodciso.ico", and "/favicon.ico" is a legitimate href
        # for it, so a plain `in` test flagged every page.
        referenced = set()
        for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
            referenced.add(m.group(1).rsplit("/", 1)[-1])
        for name, why in RETIRED_ASSETS.items():
            if name in referenced:
                errors.append(
                    f"{site}: {page.relative_to(root)} references the retired "
                    f"asset {name} ({why})"
                )
    return errors


def check_analytics() -> list[str]:
    """The first-party collector must be deployed, declared and privacy-safe.

    Three things can silently break: the function not shipping, its
    config block going missing so it is never mounted, and the client
    growing an identifier. The first two are invisible in a link check,
    and the third would be invisible in every check.
    """
    errors: list[str] = []
    fn_src = Path(__file__).resolve().parent / "netlify" / "functions" / "analytics.mjs"
    if not fn_src.exists():
        errors.append("the analytics function is not in the repository")
        return errors

    fn_text = fn_src.read_text(errors="ignore")
    # Comments are stripped before the privacy check. The function
    # documents that it does NOT record a user agent, and a check that
    # matched the documentation would fail on the guarantee itself.
    fn_code = re.sub(r"/\*.*?\*/", "", fn_text, flags=re.S)
    fn_code = re.sub(r"//[^\n]*", "", fn_code)

    # 1. It must record no identifier. This is the whole reason the
    #    collector is acceptable on a security company's site.
    for forbidden in (
        "x-forwarded-for",
        "req.ip",
        "user-agent",
        "userAgent",
        "set-cookie",
        "document.cookie",
        "localStorage",
        "sessionStorage",
    ):
        if forbidden.lower() in fn_code.lower():
            errors.append(
                f"the analytics function references {forbidden!r} - it must not "
                f"record an identifier"
            )

    # 2. It must declare the function directory for every site.
    for site in SITE_ROOTS:
        root = DIST / site
        if not root.exists():
            continue
        fn = root / "netlify" / "functions" / "analytics.mjs"
        if not fn.exists():
            errors.append(f"{site}: the analytics function is not in the deploy root")
            continue
        cfg = root / "netlify.toml"
        if not cfg.exists() or "[functions]" not in cfg.read_text(errors="ignore"):
            errors.append(
                f"{site}: netlify.toml does not declare [functions] - the "
                f"collector would not be mounted"
            )
        # Each site's copy must be self-identifying, so the four never
        # share a log file.
        if f'"{site}"' not in fn.read_text(errors="ignore"):
            errors.append(
                f"{site}: the deployed function does not carry the site key, so "
                f"its log could collide with another site's"
            )

    # 3. Every page must load the client, and the client must set no
    #    identifier.
    for site in SITE_ROOTS:
        root = DIST / site
        if not root.exists():
            continue
        js = root / "assets" / "site.js"
        if not js.exists():
            errors.append(f"{site}: assets/site.js is missing")
            continue
        text = js.read_text(errors="ignore")
        js_code = re.sub(r"//[^\n]*", "", text)
        if "sendBeacon" not in text:
            errors.append(f"{site}: the page does not send an analytics beacon")
        if "netlify/functions/analytics" not in text:
            errors.append(f"{site}: the beacon does not target the collector")
        for forbidden in ("document.cookie", "localStorage.setItem('gc-id",
                          "crypto.randomUUID", "Math.random"):
            if forbidden in js_code:
                errors.append(
                    f"{site}: the analytics client uses {forbidden!r} - it must "
                    f"not generate or persist an identifier"
                )
    return errors


def check_redirect_shadows() -> list[str]:
    """No redirect may shadow a page that actually exists.

    The legacy redirect table was written when the old site had no
    /pricing page, so "/pricing" pointed at the page that had replaced it.
    The new site HAS a /pricing/ page, and the redirect shadowed it: a
    reader clicking "Pricing" in the navigation landed on Regulatory
    Readiness instead, with no indication that anything was wrong.

    The failure is silent and invisible in a link check, because the
    link resolves - to the wrong page. This compares every redirect's
    source path against the built pages and fails if one is a real page.
    """
    errors: list[str] = []
    cfg = Path(__file__).resolve().parent / "netlify_config.py"
    if not cfg.exists():
        return errors
    text = cfg.read_text()
    pairs = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*\d+\)', text)
    if not pairs:
        return errors

    root = DIST / "corporate"
    if not root.exists():
        return errors
    pub = root

    for source, target in pairs:
        src_path = pub / source.strip("/")
        if src_path.exists() or (src_path / "index.html").exists():
            errors.append(
                f"redirect {source} shadows a real page (it redirects to "
                f"{target}) - readers following it never reach the page "
                f"they asked for"
            )
        # The target must also exist, or the redirect lands on a 404.
        tgt = pub / target.strip("/").rstrip("/")
        if not (tgt.exists() or (tgt / "index.html").exists()):
            errors.append(f"redirect {source} -> {target} has no target page")
    return errors


def check_brand(site: str) -> list[str]:
    """Brand bleed between the corporate site and the AWARE product sites."""
    root = DIST / site
    errors: list[str] = []
    if not root.exists():
        return errors

    if site == "corporate":
        # 1. The AWARE mark must not be served as the corporate favicon.
        fav_png = pub(site) / "favicon.png"
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
        assets = pub(site) / "assets"
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
                    if resolved and _is_aware_green(resolved):
                        errors.append(
                            f"corporate: {token} resolves to {resolved} in the "
                            f"{theme} theme — that is AWARE's Signal green. "
                            f"GoodCISO is teal."
                        )
                # The hero glow must be derived from the accent. Two ways it
                # can go wrong, and both are caught here:
                #   1. it is a literal of AWARE's Signal green — the exact
                #      bug that put a green glow behind a teal logomark;
                #   2. it is a literal of ANY colour rather than derived,
                #      which means the brand ramp cannot reach it and a
                #      future theme or brand change silently misses it.
                glow = _resolve(merged, DERIVED_FROM_ACCENT)
                if glow:
                    low = glow.lower()
                    if _is_aware_green(glow):
                        errors.append(
                            f"corporate: {DERIVED_FROM_ACCENT} resolves to {glow}"
                            f" in the {theme} theme — that is AWARE's Signal green. "
                            f"GoodCISO is teal."
                        )
                    elif "var(--gc-accent" not in low:
                        errors.append(
                            f"corporate: {DERIVED_FROM_ACCENT} is the literal {glow} "
                            f"in the {theme} theme. It must be derived from the accent "
                            f"(color-mix(in srgb, var(--gc-accent) …)) so the brand "
                            f"ramp reaches it in every theme."
                        )
    else:
        # 3. The AWARE sites must serve the AWARE mark.
        fav = pub(site) / "favicon.svg"
        if not fav.exists():
            errors.append(f"{site}: no /favicon.svg — the AWARE mark is missing")
        elif b"22c55e" not in fav.read_bytes().lower():
            errors.append(f"{site}: /favicon.svg is not the AWARE mark")

    # 4. The Open Graph card must belong to THIS brand. The card is what a
    # shared link shows before a word is read, so a corporate link carrying
    # AWARE's card is the same defect as a corporate favicon carrying
    # AWARE's mark — one brand's identity on the other's surface.
    #
    # The two cards are compared by CONTENT, not by filename: the build
    # copies each to /og.png, so the name is the same on every site and
    # only the bytes can tell them apart.
    og = pub(site) / "og.png"
    if not og.exists():
        errors.append(f"{site}: no /og.png — the social card is missing")
    else:
        og_bytes = og.read_bytes()
        if site == "corporate":
            brand_og = BRAND_DIR / "generated" / "og-corporate.png"
            if brand_og.exists() and og_bytes != brand_og.read_bytes():
                errors.append(
                    "corporate: /og.png is not the GoodCISO social card — "
                    "a goodciso.org link must not carry the AWARE mark"
                )
        else:
            brand_og = BRAND_DIR / "generated" / "og-aware.png"
            if brand_og.exists() and og_bytes != brand_og.read_bytes():
                errors.append(
                    f"{site}: /og.png is not the AWARE social card — "
                    "an AWARE link must not carry the corporate mark"
                )

    # 5. The HEADER mark must belong to THIS brand.
    #
    # This check exists because of a defect the other four did not catch.
    # From 2026-05-19 the corporate header on goodciso.org carried AWARE's
    # teal square-and-check with the wordmark reading "AWARE" — for about
    # six months. The favicon stayed correct throughout, so nothing that
    # checked the favicon would ever have seen it. The header mark is a
    # brand surface like any other, and it was the one nobody checked.
    #
    # It is checked on every built page, because the header is rendered per
    # page: one page with the wrong mark is a visible defect even if every
    # other page is right.
    #
    # Both halves of the header are checked, because the June 2026 defect
    # changed both and a guard that only checks the glyph would miss a
    # header that showed the right shield under the wrong wordmark:
    #
    #   - the GLYPH: the corporate header is an <img> pointing at the
    #     committed GoodCISO artwork; the AWARE header is an inline <svg>.
    #     Each is checked for the OTHER brand's signature.
    #   - the WORDMARK: "Good CISO" on the corporate site, "AWARE" on the
    #     product sites.
    #
    # The checks read the header anchor, not the whole page, so a mention
    # of the word "AWARE" in body copy cannot trip them and a wordmark that
    # appears in the footer cannot satisfy them.
    for page in page_files(site):
        html = page.read_text(errors="replace")
        rel = page.relative_to(root)
        anchor = _header_logo_anchor(html)
        if anchor is None:
            errors.append(
                f"{site}: {rel} has no header logo — the header must carry "
                "this brand's own mark"
            )
            continue
        if site == "corporate":
            if "goodciso-shield.png" not in anchor:
                errors.append(
                    f"corporate: {rel} — the header mark is not the GoodCISO "
                    "shield. The corporate header must carry GoodCISO's own "
                    "artwork, never AWARE's."
                )
            if AWARE_SHIELD_SIGNATURE in anchor:
                errors.append(
                    f"corporate: {rel} — the header carries AWARE's shield "
                    "mark. The corporate header must carry GoodCISO's own "
                    "artwork, never the product's."
                )
            if "gc-wordmark-good" not in anchor:
                errors.append(
                    f"corporate: {rel} — the header wordmark is not "
                    '"Good CISO". The corporate wordmark is "Good" in the '
                    "heavier weight plus CISO in caps."
                )
        else:
            if "goodciso-shield" in anchor:
                errors.append(
                    f"{site}: {rel} — the header carries GoodCISO's shield. "
                    "The product sites must carry AWARE's own mark, never the "
                    "company's."
                )
            if "gc-wordmark-good" in anchor:
                errors.append(
                    f"{site}: {rel} — the header wordmark is the corporate "
                    '"Good CISO" wordmark. The product sites carry "AWARE".'
                )

    return errors


def check_site(site: str) -> dict:
    root = DIST / site
    pub_root = pub(site)
    origin = SITE_ROOTS[site]
    errors, warnings = [], []
    pages = page_files(site)

    for pf in pages:
        rel = pf.relative_to(pub_root)
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
                target = (pub_root / clean.lstrip("/"))
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
            if not (pub_root / href.lstrip("/")).exists():
                errors.append(f"{url}: favicon {href} does not exist in the build")

        # --- Open Graph card ---
        # The card is the image a shared link shows before a word is read.
        # A page with no og:image renders as a bare link; a page whose
        # og:image points at a file the build did not produce renders as a
        # broken card. Both are "the brand did not arrive", so both fail.
        #
        # The card must also belong to THIS site's origin: a corporate
        # page pointing at an AWARE-hosted card would put the product's
        # mark on the company's link.
        if not p.og_images:
            errors.append(f"{url}: no og:image — a shared link renders with no card")
        for src in p.og_images:
            if not src.startswith(origin):
                errors.append(f"{url}: og:image points off-site: {src}")
                continue
            path = src[len(origin):].lstrip("/")
            if not path or not (pub_root / path).exists():
                errors.append(f"{url}: og:image {src} does not exist in the build")

    # --- sitemap integrity ---
    sm = pub(site) / "sitemap.xml"
    if sm.exists():
        for loc in re.findall(r"<loc>(.*?)</loc>", sm.read_text()):
            path = loc.replace(origin, "").lstrip("/")
            target = pub(site) / path if path else pub(site) / "index.html"
            if path and not target.exists():
                target = root / path / "index.html"
            if not target.exists():
                errors.append(f"sitemap: {loc} has no file")
    else:
        errors.append("no sitemap.xml")

    if not (pub(site) / "robots.txt").exists():
        errors.append("no robots.txt")

    # --- brand ---
    errors.extend(check_brand(site))
    errors.extend(check_retired_assets(site))

    return {"site": site, "pages": len(pages), "errors": errors, "warnings": warnings}


def strip_css_comments(css: str) -> str:
    """Remove CSS comments.

    A comment can mention a class that the layer does not actually
    define — the layer's own comments explain the grid bug by naming
    `.gc-grid-2` — and a check that reads comments would demand a spec
    for classes that do not exist.
    """
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def css_class_selectors(css: str) -> list[str]:
    """Every class named by a SELECTOR in the stylesheet.

    Only the selector part of a rule is read, never a declaration value,
    so a decimal in a value (`.9em`) cannot be mistaken for a class.
    """
    css = strip_css_comments(css)
    found: set[str] = set()
    for selector in re.findall(r"([^{}]+)\{", css):
        # A selector list: `.a, .b` — every part counts.
        for m in re.finditer(r"\.([A-Za-z_][\w-]*)", selector):
            found.add(m.group(1))
    return sorted(found)


def check_component_spec() -> list[str]:
    """Every component in the layer must be specified.

    The previous site shipped four components with no specification at all —
    `arch-flow`, `stats-bar`, `compliance-grid` and `.trust-badge-note` —
    so nobody could tell whether they were correct and a coder could not
    know when it was safe to use one. The component spec
    (`packages/ui/README.md`) is what stops that happening again.

    A check that cannot fail is not a check, so this one is proven to fire
    by `test_component_spec.py`.
    """
    errors: list[str] = []
    repo = Path(__file__).parent.resolve()
    layer = repo / "packages/ui/src/base.css"
    spec = repo / "packages/ui/README.md"
    if not layer.exists():
        return ["component spec: packages/ui/src/base.css is missing"]
    if not spec.exists():
        return [
            "component spec: packages/ui/README.md is missing — every component "
            "in the layer must be specified, or a coder cannot know when to "
            "use one"
        ]
    css = layer.read_text(encoding="utf-8")
    text = spec.read_text(encoding="utf-8")
    # Every class in the layer, wherever it is declared.
    #
    # The first version of this check matched only classes at the START of
    # a line (`^\.(gc-...)`). Two classes in the layer — `.gc-mt-6` and
    # `.gc-mt-12` — are declared mid-line, so the check could not see
    # them, and a component added mid-line would have shipped with no
    # specification and no error. The match is now on the selector, not on
    # where it sits in the line.
    classes = css_class_selectors(css)
    # The class must appear as a WORD in the spec. A substring test would
    # pass for a class whose name is a prefix of another ("gc-list" is a
    # substring of "gc-list-item"), so removing a component from the spec
    # could still find its name elsewhere in the prose and go unreported.
    for c in classes:
        if not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(c)}(?![A-Za-z0-9_-])", text):
            errors.append(
                f"component spec: .{c} is in the layer but not specified in "
                f"packages/ui/README.md"
            )
    # And the other direction: a class the spec documents that the layer
    # does not define is a specification of something that does not exist.
    # A coder reading the spec would use it, and it would do nothing.
    for c in spec_class_names(text):
        if c not in classes:
            errors.append(
                f"component spec: .{c} is specified in packages/ui/README.md "
                f"but is not in the layer"
            )
    return errors


def spec_class_names(spec: str) -> list[str]:
    """The class names the spec documents.

    Only names written as CSS class tokens — in backticks, or at the start
    of a table cell — count. Prose that mentions a class in passing, like
    the `.gc-grid-2` in the explanation of a past bug, is not a
    specification of a component.
    """
    names: set[str] = set()
    # A table cell that names the class: `| `gc-btn` | ... |`
    for cell in re.findall(r"^\|\s*`([A-Za-z_][\w-]*)`", spec, re.M):
        names.add(cell)
    # A comma-separated list in one cell: `| `gc-mt-4`, `gc-mt-6` | ... |`
    for cell in re.findall(r"^\|\s*`([A-Za-z_][\w-]*)`\s*,\s*`([A-Za-z_][\w-]*)`", spec, re.M):
        names.update(cell)
    # A bare class token in backticks anywhere: `gc-btn-primary`
    for m in re.finditer(r"`([A-Za-z_][\w-]*)`", spec):
        names.add(m.group(1))
    return sorted(n for n in names if n.startswith("gc-") or n == "skip-link")


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

    # The component spec is a whole-repo check, not a per-site one: the layer
    # and its spec are shared by every site.
    analytics_errors = check_analytics()
    if analytics_errors:
        print(f"[FAIL] analytics      {len(analytics_errors)} errors")
        for e in analytics_errors[:25]:
            print("    ERROR  ", e)
    else:
        print("[PASS] analytics      the collector ships, is declared, and records no identifier")

    shadow_errors = check_redirect_shadows()
    if shadow_errors:
        print(f"[FAIL] redirects     {len(shadow_errors)} errors")
        for e in shadow_errors[:25]:
            print("    ERROR  ", e)
    else:
        print("[PASS] redirects     no redirect shadows a real page")

    spec_errors = check_component_spec()
    if spec_errors:
        print(f"[FAIL] component spec  {len(spec_errors)} errors")
        for e in spec_errors[:25]:
            print("    ERROR  ", e)
    else:
        print("[PASS] component spec  every component in the layer is specified")

    total_err = (
        sum(len(r["errors"]) for r in all_res)
        + len(spec_errors)
        + len(shadow_errors)
        + len(analytics_errors)
    )
    print(f"\nTOTAL ERRORS: {total_err}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
