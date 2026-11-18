#!/usr/bin/env python3
"""
goodciso-web — the static site builder.

One builder, four sites:
    apps/corporate  -> goodciso.org
    apps/aware      -> aware.goodciso.org
    apps/docs       -> docs.aware.goodciso.org
    apps/demo       -> demo.aware.goodciso.org

Design principle: the corporate site and the AWARE site share the token layer
and the component layer, and differ only by brand overrides and content.
That is what makes two brands that look related without looking identical.

Every page is generated from a Python dict. No page is hand-written HTML.
Run:  python3.12 build.py [--site corporate|aware|docs|demo|all]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
PKG_TOKENS = ROOT / "packages/design-tokens/src/tokens.css"
PKG_BASE = ROOT / "packages/ui/src/base.css"
BRAND_DIR = ROOT / "assets/brand"


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def md(text: str) -> str:
    """Minimal inline markdown: **bold**, *italic*, `code`, [text](url)."""
    t = esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+?)\]\(([^)]+?)\)", r'<a href="\2">\1</a>', t)
    return t


@dataclass
class Nav:
    label: str
    href: str
    external: bool = False


@dataclass
class Page:
    slug: str
    title: str
    description: str
    body: str
    canonical: str
    status: str = ""
    nav_label: str = ""
    extra_head: str = ""
    body_class: str = ""


@dataclass
class Site:
    key: str
    out_dir: Path | None = None
    domain: str = ""
    title_suffix: str = ""
    nav: list[Nav] = field(default_factory=list)
    footer_links: list = field(default_factory=list)
    brand_css: str = ""
    logo_svg: str = ""
    tagline: str = ""
    robots: str = "index, follow"
    theme_default: str = "dark"


# --------------------------------------------------------------------------
# brand assets
# --------------------------------------------------------------------------
AWARE_LOGO = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
<path d="M12 2.5 4 6v6.2c0 4.7 3.4 9.1 8 9.3 4.6-.2 8-4.6 8-9.3V6l-8-3.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
<path d="M8.5 12.2l2.6 2.6 4.7-5.2" stroke="var(--gc-accent)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

# The GoodCISO mark: the established teal shield with a G, restored from
# the previous live site rather than redesigned. The colour is baked in
# because it is the brand's identity, not a theme token — AWARE's accent
# must never appear in it.
GOODCISO_LOGO = """<svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden="true">
<path d="M16 3 L27 8.4 L27 18 Q27 24.6 16 29 Q5 24.6 5 18 L5 8.4 Z" fill="#00A896"/>
<path d="M16 7.6 L23.5 12 L23.5 18 Q23.5 22.4 16 25.8 Q8.5 22.4 8.5 18 L8.5 12 Z" fill="#030712"/>
<circle cx="16" cy="17" r="3.1" fill="#00A896"/>
</svg>"""


def brand_css_for(site: Site) -> str:
    """Brand expression. Only token overrides — never forked component CSS."""
    if site.key == "aware":
        return """
/* ---- AWARE: developer infrastructure. Dense, technical, precise. ---- */
:root { --gc-header-h: 56px; }
body { font-feature-settings: "cv02","cv03","cv04","ss01"; }
.gc-brand-eyebrow { color: var(--gc-accent-text); }
.gc-mono-label { font-family: var(--gc-font-mono); font-size: var(--gc-text-xs); letter-spacing: var(--gc-tracking-wide); text-transform: uppercase; color: var(--gc-text-subtle); }
.gc-term { font-family: var(--gc-font-mono); font-size: var(--gc-text-sm); background: var(--gc-surface-2); border: 1px solid var(--gc-border); border-radius: var(--gc-radius-md); padding: var(--gc-space-1) var(--gc-space-2); }
.gc-hero { padding-top: var(--gc-space-16); }
.gc-hero h1 { max-width: 20ch; }
"""
    if site.key == "corporate":
        return """
/* ---- GoodCISO: the established corporate brand.
       Teal #00a896, navy #030712, amber #F5A623. These are GoodCISO's
       colours, not AWARE's: the two brands share typography and the
       component layer, and are otherwise distinct. AWARE's Signal green
       does not appear here. ---- */
:root {
  --gc-header-h: 72px;

  /* The brand teal #00A896 is 2.85:1 on the light background — it fails
     AA as text. So it stays the brand accent for FILLS and the logomark,
     and the ramp carries darker steps for text and solid buttons.
     Contrast measured, not assumed:
       #00A896 on #F8FAFC  2.85  fill/icon only
       #007669 on #F8FAFC  5.29  accent text, link      (AA)
       #FFFFFF on #007669 5.53  solid button           (AA) */
  --gc-green-50:  #F0FDFA;
  --gc-green-100: #CCFBF1;
  --gc-green-200: #99F6E4;
  --gc-green-300: #5EEAD4;
  --gc-green-400: #2DD4BF;
  --gc-green-500: #14B8A6;
  --gc-green-600: #00A896;   /* GoodCISO teal — the brand colour */
  --gc-green-700: #007669;   /* 5.29:1 on --gc-bg — accent as text */
  --gc-green-800: #00685D;
  --gc-green-900: #005248;

  /* The focus ring needs 3:1 against the background. The brand teal
     #00A896 is 2.85:1 on --gc-bg and fails, so the focus token uses the
     accessible teal-700 (4.55:1). The brand colour still drives the
     logomark and the accent fill. */
  --gc-focus: #007669;

  --gc-slate-950: #030712;   /* GoodCISO navy */
}

/* The corporate dark theme: GoodCISO navy with teal accents. The solid
   button uses navy text on the teal fill (8.09:1) — white on teal is
   2.49:1 and fails. */
[data-theme="dark"] {
  --gc-bg:          #030712;
  --gc-surface:     #0A1220;
  --gc-surface-2:   #111C2E;
  --gc-border:      #1E2D44;
  --gc-border-strong: #94A3B8;

  --gc-text:        #E2E8F0;
  --gc-text-muted:  #94A3B8;
  --gc-text-subtle: #94A3B8;

  --gc-accent:      #00A896;
  --gc-accent-text: #2DD4BF;             /* 10.82:1 on --gc-bg */
  --gc-accent-solid:#14B8A6;
  --gc-accent-on-solid: #030712;        /* 8.09:1 on --gc-accent-solid */
  --gc-accent-hover:#2DD4BF;
  --gc-accent-soft: rgba(0, 168, 150, 0.14);

  --gc-link:        #2DD4BF;
  --gc-focus:       #14B8A6;             /* 8.09:1 — non-text contrast */
  --gc-danger:      #F87171;
  --gc-danger-bg:   #2A1416;
  --gc-warn-text:   #FBBF24;
  --gc-warn-bg:     #2A1F0C;
  --gc-ok-text:     #2DD4BF;
  --gc-ok-bg:       #0E2418;
  --gc-code-bg:     #010409;
  --gc-code-text:   #E2E8F0;
  --gc-hero-glow:   rgba(0, 168, 150, 0.12);
}

body { font-size: 1.0625rem; }
.gc-hero { padding-top: var(--gc-space-24); }
.gc-hero h1 { max-width: 16ch; font-size: clamp(2.25rem, 1.5rem + 3vw, 3.5rem); }
.gc-section { padding: var(--gc-space-24) 0; }
.gc-prose { max-width: 68ch; }
.gc-prose p { margin-bottom: var(--gc-space-5); }
"""
    if site.key == "docs":
        return """
/* ---- Docs: reading-first, low chrome, generous measure. ---- */
:root { --gc-header-h: 56px; }
.gc-docs-layout { display: grid; grid-template-columns: 240px minmax(0,1fr); gap: var(--gc-space-10); align-items: start; }
.gc-docs-nav { position: sticky; top: calc(var(--gc-header-h) + var(--gc-space-6)); font-size: var(--gc-text-sm); }
.gc-docs-nav ul { list-style: none; padding: 0; margin: 0 0 var(--gc-space-6); }
.gc-docs-nav li { margin-bottom: var(--gc-space-2); }
.gc-docs-nav a { color: var(--gc-text-muted); text-decoration: none; }
.gc-docs-nav a:hover, .gc-docs-nav a[aria-current="page"] { color: var(--gc-accent-text); }
.gc-docs-nav .gc-nav-group { font-weight: var(--gc-weight-semibold); color: var(--gc-text); margin-top: var(--gc-space-4); font-size: var(--gc-text-xs); text-transform: uppercase; letter-spacing: var(--gc-tracking-wide); }
.gc-docs-body { max-width: 76ch; }
.gc-docs-body h2 { margin-top: var(--gc-space-10); padding-top: var(--gc-space-2); }
.gc-docs-body h3 { margin-top: var(--gc-space-8); }
@media (max-width: 900px) { .gc-docs-layout { grid-template-columns: 1fr; } .gc-docs-nav { position: static; } }
"""
    if site.key == "demo":
        return """
/* ---- Playground: instrument panel. Dark by default, dense readouts. ---- */
body { font-feature-settings: "tnum"; }
.gc-play { display: grid; grid-template-columns: 300px minmax(0,1fr); gap: var(--gc-space-6); align-items: start; }
.gc-play-side { position: sticky; top: calc(var(--gc-header-h) + var(--gc-space-4)); display: flex; flex-direction: column; gap: var(--gc-space-2); }
.gc-scenario { text-align: left; background: var(--gc-surface); border: 1px solid var(--gc-border); border-radius: var(--gc-radius-md); padding: var(--gc-space-3) var(--gc-space-4); cursor: pointer; color: var(--gc-text); font-size: var(--gc-text-sm); font-family: inherit; }
.gc-scenario:hover { border-color: var(--gc-border-strong); }
.gc-scenario[aria-pressed="true"] { border-color: var(--gc-accent); background: var(--gc-accent-soft); }
.gc-readout { font-family: var(--gc-font-mono); font-size: var(--gc-text-sm); }
.gc-readout-row { display: grid; grid-template-columns: 190px minmax(0,1fr); gap: var(--gc-space-3); padding: var(--gc-space-2) 0; border-bottom: 1px solid var(--gc-border); }
.gc-readout-row dt { color: var(--gc-text-subtle); }
.gc-readout-row dd { margin: 0; color: var(--gc-text); overflow-wrap: anywhere; }
@media (max-width: 900px) { .gc-play { grid-template-columns: 1fr; } .gc-play-side { position: static; } }
"""
    return ""


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------
def render_page(site: Site, page: Page, nav_current: str = "") -> str:
    nav_items = []
    for n in site.nav:
        cur = ' aria-current="page"' if n.label == nav_current else ""
        ext = ' rel="noopener"' if n.external else ""
        nav_items.append(f'<a href="{esc(n.href)}"{cur}{ext}>{esc(n.label)}</a>')

    footer_cols = []
    for head, links in site.footer_links:
        items = "".join(
            f'<li><a href="{esc(l.href)}"{(" rel=\"noopener\"" if l.external else "")}>{esc(l.label)}</a></li>'
            for l in links
        )
        footer_cols.append(f"<div><h4>{esc(head)}</h4><ul>{items}</ul></div>")

    logo = site.logo_svg
    logo_text = "GoodCISO" if site.key == "corporate" else "AWARE"
    # The header CTA must exist on the site it is rendered into. "/contact"
    # only exists on the corporate site; the product sites have their own
    # entry point, and a 404 in the primary CTA is not a small defect.
    cta = {
        "aware": ("/get-started", "Get started"),
        "corporate": ("/contact", "Contact us"),
        "docs": ("/quick-start", "Quick start"),
        "demo": ("/", "Playground"),
    }.get(site.key, ("/get-started", "Get started"))

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{site.theme_default}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page.title)} | {esc(site.title_suffix)}</title>
<meta name="description" content="{esc(page.description)}">
<link rel="canonical" href="{esc(page.canonical)}">
<meta name="robots" content="{site.robots}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site.title_suffix)}">
<meta property="og:title" content="{esc(page.title)} | {esc(site.title_suffix)}">
<meta property="og:description" content="{esc(page.description)}">
<meta property="og:url" content="{esc(page.canonical)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page.title)} | {esc(site.title_suffix)}">
<meta name="twitter:description" content="{esc(page.description)}">
<meta name="theme-color" content="#0B1220">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/tokens.css">
<link rel="stylesheet" href="/assets/base.css">
<link rel="stylesheet" href="/assets/brand.css">
{page.extra_head}
</head>
<body class="{page.body_class}">
<a class="skip-link" href="#main">Skip to content</a>
<header class="gc-header">
  <div class="gc-container gc-header-inner">
    <a class="gc-logo" href="/">{logo}<span>{esc(logo_text)}</span></a>
    <nav class="gc-nav" id="nav" data-open="false" aria-label="Main">
      {"".join(nav_items)}
    </nav>
    <div class="gc-header-actions">
      <button class="gc-theme-toggle" type="button" aria-label="Toggle colour theme" data-theme-toggle>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4m0-12.8-1.4 1.4m-10 10-1.4 1.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8"/></svg>
      </button>
      <a class="gc-btn gc-btn-primary" href="{esc(cta[0])}">{esc(cta[1])}</a>
      <button class="gc-nav-toggle" type="button" aria-expanded="false" aria-controls="nav" data-nav-toggle>Menu</button>
    </div>
  </div>
</header>
<main id="main">
{page.body}
</main>
<footer class="gc-footer">
  <div class="gc-container">
    <div class="gc-footer-grid">
      <div>
        <a class="gc-logo" href="/">{logo}<span>{esc(logo_text)}</span></a>
        {f'<p class="gc-muted gc-mt-4" style="font-size:var(--gc-text-sm)">{md(site.tagline)}</p>' if site.tagline else ''}
      </div>
      {"".join(footer_cols)}
    </div>
    <div class="gc-footer-bottom">
      <span>&copy; 2026 Good CISO Limited. Registered in England &amp; Wales, company no. 16294946.</span>
      <span>AWARE is licensed under Apache-2.0. &ldquo;{esc(logo_text)}&rdquo; and the shield mark are trademarks of Good CISO Limited.</span>
    </div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
