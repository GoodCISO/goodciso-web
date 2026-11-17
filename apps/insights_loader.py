#!/usr/bin/env python3
"""Load the migrated Insight articles into the corporate page set.

The article bodies are written by migrate_insights.py into apps/insights/*.html
as standalone fragments. This module wraps each fragment in the standard page
chrome and returns them as Page objects so the normal build path — sitemap,
canonical, metadata, QA gate — applies to them like any other page.
"""
from __future__ import annotations

from pathlib import Path

import re

from build import Page, md


# Links carried over from the legacy posts point at URLs that the new site
# 301s rather than serves. They are rewritten to their new homes so the
# articles never link to a redirect.
LEGACY_LINK_FIXES = {
    "/demo": "/aware",
    "/book.html": "/contact",
    "/pricing.html": "/services/regulatory-readiness",
    "/services.html": "/services",
}


def article_html(markdown_body: str) -> str:
    """Convert the article fragment's markdown block structure to HTML."""
    # The fragment carries its own hero block, including an <h1>. The page
    # chrome supplies the page's single <h1>, so the fragment's is removed
    # here rather than producing a second one.
    markdown_body = re.sub(r"<section[^>]*>.*?</section>", "", markdown_body, count=1, flags=re.S | re.I)
    # The fragment's remaining wrapper markup (<section>, <div>) would
    # otherwise be rendered as visible text by the markdown pass.
    markdown_body = re.sub(r"</?(?:section|div)[^>]*>", "", markdown_body, flags=re.I)
    out = []
    in_list = False
    in_code = False
    for line in markdown_body.split("\n"):
        s = line.rstrip()

        if s.strip().startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                if in_list:
                    out.append("</ul>")
                    in_list = False
                out.append('<pre class="gc-code"><code>')
                in_code = True
            continue

        if in_code:
            out.append(line + "\n")
            continue

        if not s.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("")
            continue

        # Heading
        m = re.match(r"^(#{2,4})\s+(.*)$", s)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(m.group(1))
            out.append(f"<h{level}>{md(m.group(2))}</h{level}>")
            continue

        # List item
        m = re.match(r"^\s*-\s+(.*)$", s)
        if m:
            if not in_list:
                out.append("<ul class=\"gc-list\">")
                in_list = True
            out.append(f"<li>{md(m.group(1))}</li>")
            continue

        if in_list:
            out.append("</ul>")
            in_list = False

        # Blockquote
        m = re.match(r"^>\s+(.*)$", s)
        if m:
            out.append(f"<blockquote><p>{md(m.group(1))}</p></blockquote>")
            continue

        out.append(f"<p>{md(s)}</p>")

    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")

    body = "\n".join(x for x in out if x is not None)
    # md() has already rendered the links, so the fix-up targets the rendered
    # href attribute rather than the markdown form.
    for old_path, new_path in LEGACY_LINK_FIXES.items():
        body = body.replace(f'href="{old_path}"', f'href="{new_path}"')
    return body

ROOT = Path(__file__).parent.parent.resolve()
ARTICLE_DIR = ROOT / "apps" / "insights"
DOMAIN = "https://goodciso.org"

# slug -> (title, description)
META = {
    "container-security-gap": (
        "The Container Security Gap Nobody Talks About",
        "Image scanning and admission control are the wrong half of container security. "
        "A practitioner argument about what actually causes catastrophic breaches.",
    ),
    "devsecops-is-dead": (
        "DevSecOps is Dead; Long Live DevOps",
        "Why DevSecOps was never a separate discipline, and what the next shift in "
        "application security actually looks like for teams shipping at speed.",
    ),
    "why-llm-threat-models-fail": (
        "Why LLM Threat Models Fail (And How to Fix Them)",
        "STRIDE assumes a fixed attack surface. An LLM's surface is its prompt space. "
        "A practical reframing for threat-modelling agentic systems.",
    ),
    "what-we-learned-building-agentic-security-workflows": (
        "What We Learned Building Agentic Security Workflows",
        "What building AWARE taught us about governing autonomous agents, and why "
        "traditional compliance tooling could not be adapted to the problem.",
    ),
}

INSIGHT_PAGES = []
for slug, (title, desc) in META.items():
    f = ARTICLE_DIR / f"{slug}.html"
    if not f.exists():
        continue
    body = (
        '<section class="gc-hero gc-hero-sm"><div class="gc-container gc-container-narrow">'
        '<span class="gc-eyebrow">Insight</span>'
        f"<h1>{title}</h1>"
        '<p class="gc-hero-sub">Technical writing from the GoodCISO team.</p>'
        "</div></section>"
        + article_html(f.read_text(encoding="utf-8"))
    )
    INSIGHT_PAGES.append(
        Page(
            slug=f"insights/{slug}",
            title=title,
            description=desc,
            body=body,
            canonical=f"{DOMAIN}/insights/{slug}",
        )
    )
