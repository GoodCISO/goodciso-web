#!/usr/bin/env python3
"""Build all four sites and write the deploy plan."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import build as B
from build import Nav, Page, Site

ROOT = B.ROOT
OUT = ROOT / "dist"

import sys
sys.path.insert(0, str(ROOT / "apps"))
from aware.pages import NAV as AWARE_NAV, FOOTER as AWARE_FOOTER, TAGLINE as AWARE_TAGLINE, PAGES as AWARE_PAGES
from other import C_NAV, C_FOOTER, C_TAGLINE, CORPORATE
from insights_loader import INSIGHT_PAGES
from other import D_NAV, D_FOOTER, D_TAGLINE, DOCS
from other import M_NAV, M_FOOTER, M_TAGLINE, DEMO


def write_site(site: Site, pages: list[Page], extra_assets: dict[str, str] | None = None):
    out = site.out_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copy(B.PKG_TOKENS, assets / "tokens.css")
    shutil.copy(B.PKG_BASE, assets / "base.css")
    (assets / "brand.css").write_text(site.brand_css)

    # The original GoodCISO artwork. The corporate header uses it; the
    # AWARE sites keep their own mark, but the assets are copied to all
    # four so a shared component can reach them.
    for asset in B.BRAND_DIR.glob("goodciso-*.png"):
        shutil.copy(asset, out / "assets" / asset.name)

    # Favicon — per site. The AWARE shield-and-checkmark is AWARE's mark
    # and must never be served on the corporate site: a corporate favicon
    # that is the product's logo misrepresents the relationship between
    # the two brands.
    #
    # The corporate favicon is the ORIGINAL brand artwork on a navy tile.
    # An SVG of it could not be traced faithfully — the trace lost the
    # G-shaped counter — so the original pixels are what ship. The tile is
    # not decoration: the artwork's counter is knocked out to transparency
    # for the header, so without a fixed backdrop the G would read
    # differently depending on the browser tab's colour.
    if site.key == "corporate":
        for asset in ("favicon-goodciso.png", "favicon-goodciso.ico", "apple-touch-icon.png"):
            src = B.BRAND_DIR / asset
            if src.exists():
                shutil.copy(src, out / asset)
        # The names build.py links to. /favicon.png and /favicon.ico are
        # the paths browsers and crawlers ask for by convention; the
        # brand-named copies sit alongside them so the asset set is
        # self-describing in the repo.
        png = B.BRAND_DIR / "favicon-goodciso.png"
        if png.exists():
            shutil.copy(png, out / "favicon.png")
        ico = B.BRAND_DIR / "favicon-goodciso.ico"
        if ico.exists():
            shutil.copy(ico, out / "favicon.ico")
    else:
        fav = B.BRAND_DIR / "favicon-aware.svg"
        if fav.exists():
            shutil.copy(fav, out / "favicon.svg")

    # The GoodCISO logo artwork, served from the corporate site. Both are
    # cut from the original 1024x1024 file, so the mark on the site is the
    # original mark.
    for asset in ("goodciso-logo.png", "goodciso-shield.png"):
        src = B.BRAND_DIR / asset
        if src.exists():
            shutil.copy(src, out / "assets" / asset)

    written = []
    for page in pages:
        html = B.render_page(site, page, nav_current=page.nav_label)
        path = out / (page.slug if page.slug != "index" else "index.html")
        if page.slug == "index":
            path = out / "index.html"
        elif not page.slug.endswith(".html"):
            path = out / page.slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        written.append(path)

    # site.js
    (assets / "site.js").write_text(SITE_JS, encoding="utf-8")

    for name, content in (extra_assets or {}).items():
        p = out / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    return written


SITE_JS = r"""
(function () {
  var root = document.documentElement;

  // Theme: persisted, respects system preference on first visit.
  var stored = null;
  try { stored = localStorage.getItem('gc-theme'); } catch (e) {}
  if (stored) {
    root.setAttribute('data-theme', stored);

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('gc-theme', next); } catch (e) {}
    });
  });

  // Mobile nav
  var toggle = document.querySelector('[data-nav-toggle]');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.getAttribute('data-open') === 'true';
      nav.setAttribute('data-open', String(!open));
      toggle.setAttribute('aria-expanded', String(!open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }
})();
"""


def sitemap_xml(domain: str, pages: list[Page], out: Path):
    rows = []
    for p in pages:
        pri = "1.0" if p.slug == "index" else ("0.8" if p.slug.count("/") == 0 else "0.6")
        rows.append(
            f"  <url>\n    <loc>{p.canonical}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    (out / "sitemap.xml").write_text(xml, encoding="utf-8")


def robots_txt(domain: str, out: Path, allow_all=True):
    txt = f"""User-agent: *
{'Allow: /' if allow_all else 'Disallow: /'}

# AI and search crawlers are welcome; this site is written for machines to read too.
User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: GoogleExtended
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: AnthropicAI
Allow: /
User-agent: OAI-SearchBot
Allow: /

Sitemap: {domain}/sitemap.xml
"""
    (out / "robots.txt").write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="all")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    sites = [
        Site(
            key="aware",
            out_dir=OUT / "aware",
            domain="https://aware.goodciso.org",
            title_suffix="AWARE",
            nav=AWARE_NAV,
            footer_links=AWARE_FOOTER,
            brand_css=B.brand_css_for(Site(key="aware", out_dir=None, domain="", title_suffix="", nav=[], footer_links=[])),
            logo_svg=B.AWARE_LOGO,
            tagline=AWARE_TAGLINE,
            logo_label="AWARE — by GoodCISO, home",
        ),
        Site(
            key="corporate",
            out_dir=OUT / "corporate",
            domain="https://goodciso.org",
            title_suffix="GoodCISO",
            nav=C_NAV,
            footer_links=C_FOOTER,
            brand_css=B.brand_css_for(Site(key="corporate", out_dir=None, domain="", title_suffix="", nav=[], footer_links=[])),
            logo_svg=B.GOODCISO_LOGO,
            tagline=C_TAGLINE,
            logo_label="Good CISO — home",
            theme_default="light",
        ),
        Site(
            key="docs",
            out_dir=OUT / "docs",
            domain="https://docs.aware.goodciso.org",
            title_suffix="AWARE Docs",
            nav=D_NAV,
            footer_links=D_FOOTER,
            brand_css=B.brand_css_for(Site(key="docs", out_dir=None, domain="", title_suffix="", nav=[], footer_links=[])),
            logo_svg=B.AWARE_LOGO,
            tagline=D_TAGLINE,
        ),
        Site(
            key="demo",
            out_dir=OUT / "demo",
            domain="https://demo.aware.goodciso.org",
            title_suffix="AWARE Playground",
            nav=M_NAV,
            footer_links=M_FOOTER,
            brand_css=B.brand_css_for(Site(key="demo", out_dir=None, domain="", title_suffix="", nav=[], footer_links=[])),
            logo_svg=B.AWARE_LOGO,
            tagline=M_TAGLINE,
        ),
    ]

    page_sets = {
        "aware": AWARE_PAGES,
        "corporate": CORPORATE + INSIGHT_PAGES,
        "docs": DOCS,
        "demo": DEMO,
    }

    plan = []
    for site in sites:
        if args.only not in ("all", site.key):
            continue
        pages = page_sets[site.key]
        extra = {"assets/playground.js": (ROOT / "apps/demo/playground.js").read_text(encoding="utf-8")} if site.key == "demo" else {}
        written = write_site(site, pages, extra)
        sitemap_xml(site.domain, pages, site.out_dir)
        robots_txt(site.domain, site.out_dir)
        # 404
        (site.out_dir / "404.html").write_text(
            B.render_page(
                site,
                Page(
                    slug="404",
                    title="Page not found",
                    description="That page could not be found. Use the navigation above, or the XML sitemap to find the section you were looking for.",
                    body="<section class='gc-hero'><div class='gc-container'><h1>Page not found</h1>"
                    "<p class='gc-hero-sub'>That page does not exist. The links below will get you back.</p>"
                    "<div class='gc-hero-actions'><a class='gc-btn gc-btn-primary' href='/'>Home</a>"
                    "<a class='gc-btn gc-btn-secondary' href='/sitemap.xml'>Sitemap</a></div></div></section>",
                    canonical=site.domain + "/404",
                ),
            ),
            encoding="utf-8",
        )
        plan.append(
            {
                "key": site.key,
                "domain": site.domain,
                "pages": len(written),
                "dir": str(site.out_dir),
            }
        )
        print(f"[build] {site.key:10} {len(written):3} pages -> {site.out_dir}")

    (ROOT / "deploy-plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print("[build] plan ->", ROOT / "deploy-plan.json")


if __name__ == "__main__":
    main()
