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
# Legacy link targets, mapped to the pages that replaced them.
#
# The trailing slash matters: the corporate site serves "/contact/" and
# "/contact" redirects to it. A canonical link points at the resolved URL,
# so the values here carry the slash.
LEGACY_LINK_FIXES = {
    # The legacy posts linked to pages of the old site. Each maps to the
    # page that replaced it, WITH the trailing slash the site serves, so
    # the link points at the resolved URL rather than at a redirect.
    "/demo": "/aware/",
    "/book.html": "/contact/",
    "/pricing.html": "/pricing/",
    "/services.html": "/services/",
    "/contact.html": "/contact/",
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

    # Inline HTML inside the prose. md() escapes markup, so a literal
    # <strong> or <a href> in the fragment would render as visible source
    # text - which is exactly what happened to the closing callout in all
    # four migrated articles: "Talk to us about this" and the link after
    # it appeared as tags on screen rather than as a bold line and a link.
    #
    # Converting them to markdown before rendering lets the same markdown
    # pass handle them, so bold and links work as the author intended.
    markdown_body = re.sub(
        r"<strong[^>]*>(.*?)</strong>",
        r"**\1**",
        markdown_body,
        flags=re.S | re.I,
    )
    markdown_body = re.sub(
        r"<b[^>]*>(.*?)</b>",
        r"**\1**",
        markdown_body,
        flags=re.S | re.I,
    )
    markdown_body = re.sub(
        r"<em[^>]*>(.*?)</em>",
        r"*\1*",
        markdown_body,
        flags=re.S | re.I,
    )
    markdown_body = re.sub(
        r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        r"[\2](\1)",
        markdown_body,
        flags=re.S | re.I,
    )

    # The legacy link targets are corrected AFTER the inline-HTML pass, so
    # that it catches links written as markdown AND links written as
    # <a href>. Applying it before left the callout's "/contact" pointing
    # at a redirect rather than at the resolved URL.
    for old_path, new_path in LEGACY_LINK_FIXES.items():
        markdown_body = markdown_body.replace(f"]({old_path})", f"]({new_path})")
        markdown_body = markdown_body.replace(f"({old_path})", f"({new_path})")
    # A numbered sequence written as bold paragraphs - "1. Title",
    # "2. Title" - is a real ordered list, and should be one. The legacy
    # posts wrote them that way, and the migration preserved it, which
    # left the numbers outside the document structure: a screen reader
    # announced each as an ordinary sentence, and nothing could re-number
    # or style them.
    #
    # A run of consecutive paragraphs whose whole content is
    # "<n>. <title>" becomes a single ordered list, with each title kept
    # in the strong role it was written in.
    # The sequence is "title, body paragraphs, title, body paragraphs".
    # So the match has to span from the first numbered title to the last
    # one in the run, taking the body paragraphs with it.
    def _to_ol(mm):
        run = mm.group(0)
        # Each item: the numbered title, then everything up to the next
        # numbered title (or the end of the run).
        parts = re.split(r"\*\*(\d+\. [^*]+?)\*\*", run)
        items = []
        for n in range(1, len(parts), 2):
            title = parts[n]
            body = parts[n + 1].strip() if n + 1 < len(parts) else ""
            items.append((title, body))
        out = ["<<<OL>>>"]
        for title, body in items:
            # The body is folded into the marker as one unit, so the item
            # is a single line and can be rendered as a single <li>. If
            # the body were emitted separately, the paragraphs would fall
            # outside the list.
            body_lines = [b for b in body.split("\n") if b.strip()]
            # The typed number goes: the list marker owns it now. Keeping
            # both would render "1. 1. Prompt Injection".
            title = re.sub(r"^\d+\.\s*", "", title)
            out.append("@@ITEM@@" + title + "\x1f" + "\x1e".join(body_lines))
        out.append("<<<ENDOL>>>")
        return "\n\n" + "\n".join(out) + "\n\n"

    # The run is matched as a whole: a numbered title, then any number of
    # body paragraphs, then another numbered title, and so on.
    #
    # Two things the body pattern must NOT accept:
    #   - another numbered title, or the run would end after one item
    #   - a markdown heading, or the run would swallow the next section
    markdown_body = re.sub(
        r"(?:\*\*\d+\. [^*]+\*\*"
        r"(?:\n\n(?![#]{1,4}\s)[^\n]*)*)+",
        _to_ol,
        markdown_body,
    )

    out = []
    in_list = False
    in_ol = False
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

        # An ordered list: the marker block written by the numbered-
        # sequence pass above.
        if s.strip() == "<<<OL>>>":
            if in_list:
                out.append("</ul>" if in_ol is False else "</ol>")
                in_list = False
            out.append('<ol class="gc-ol">')
            in_list = True
            in_ol = True
            continue
        if s.strip() == "<<<ENDOL>>>":
            if in_list:
                out.append("</ol>")
                in_list = False
            in_ol = False
            continue

        # An item inside an ordered list. The title and the body were
        # folded together by the numbered-sequence pass, separated by a
        # control character that cannot occur in the prose.
        if s.startswith("@@ITEM@@") and in_list and in_ol:
            payload = s[len("@@ITEM@@"):]
            title, _, body = payload.partition("\x1f")
            title_html = md(title)
            body_html = ""
            if body:
                paras = [md(b) for b in body.split("\x1e") if b.strip()]
                body_html = "".join(f"<p>{p}</p>" for p in paras)
            out.append(f"<li><strong>{title_html}</strong>{body_html}</li>")
            continue

        # List item
        m = re.match(r"^\s*-\s+(.*)$", s)
        if m:
            if not in_list:
                out.append("<ul class=\"gc-list\">")
                in_list = True
                in_ol = False
            out.append(f"<li>{md(m.group(1))}</li>")
            continue

        if in_list:
            out.append("</ol>" if in_ol else "</ul>")
            in_list = False

        # Blockquote
        m = re.match(r"^>\s+(.*)$", s)
        if m:
            out.append(f"<blockquote><p>{md(m.group(1))}</p></blockquote>")
            continue

        # A paragraph that opens with a bold label and then continues with
        # prose is a definition, not a sentence with emphasis. The design
        # system has the component for it: gc-callout, whose strong is the
        # title and is displayed as a block above the body.
        #
        # As prose, "Traditional STRIDE on the infrastructure: the API
        # gateway, ..." runs on as one line, and the reader cannot find
        # the three parallel analyses the paragraph introduces.
        m = re.match(r"^\*\*(.+?)\*\*\s+(.+)$", s.strip(), re.S)
        if m:
            title = md(m.group(1))
            # The body continued the label's sentence, so it began in
            # lower case. The label is now a title on its own line, so
            # the body has to start a sentence of its own.
            rest_text = m.group(2)
            if rest_text[:1].islower():
                rest_text = rest_text[0].upper() + rest_text[1:]
            rest = md(rest_text)
            out.append(
                f'<div class="gc-callout"><strong>{title}</strong>'
                f"<p>{rest}</p></div>"
            )
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
