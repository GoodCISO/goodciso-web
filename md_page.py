#!/usr/bin/env python3
"""Render a machine-readable markdown version of every page.

An answer engine reading goodciso.org/pricing/ gets HTML: navigation,
styles, a script tag, and a footer. What it can cite is buried in
markup. Coframe's AEO product publishes an agent-readable rendering of
each page for exactly this reason.

This produces that rendering, from the same source the HTML is built
from, so the two cannot drift. It is not a summary written by hand and it
is not a different set of claims - it is the page's own content, in a
shape an answer engine can read and quote.

What it emits per page:

  - the title as an h1, and the description
  - the headings, in order, as h2/h3
  - the prose, as paragraphs
  - lists as markdown lists
  - tables as markdown tables
  - links as markdown links
  - the canonical URL

What it deliberately does NOT emit:

  - the navigation, footer, or any chrome
  - anything that is not in the page's own body

The output is written next to the HTML as <slug>.md and served with
Content-Type: text/markdown, so it can be fetched by path.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

# Tags whose entire content is chrome or metadata, not page content.
DROP_TAGS = ("script", "style", "nav", "header", "footer", "aside", "svg", "form")

# Block-level tags that force a line break in the markdown.
BLOCKS = (
    "p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "table", "tr", "blockquote", "pre", "br", "hr",
)


def strip_chrome(body: str) -> str:
    """Remove chrome, scripts and styles from a page body."""
    for tag in DROP_TAGS:
        body = re.sub(rf"<{tag}\b.*?</{tag}>", "", body, flags=re.S | re.I)
        body = re.sub(rf"<{tag}\b[^>]*/>", "", body, flags=re.I)

    # An eyebrow is a section label that sits above a heading. In markdown
    # it becomes a level-3 heading above the level-2, which reads as a
    # label and keeps the hierarchy an answer engine can cite.
    body = re.sub(
        r'<span class="gc-eyebrow">(.*?)</span>',
        lambda mm: f"\n\n#### {inline(mm.group(1))}\n\n",
        body,
        flags=re.S | re.I,
    )
    return body


def inline(text: str) -> str:
    """Convert inline HTML to markdown, preserving the links."""
    # Links first: the label may itself contain emphasis.
    def link(mm: re.Match) -> str:
        href = mm.group(1)
        label = re.sub(r"<[^>]+>", "", mm.group(2)).strip()
        if not label:
            return ""
        if href.startswith("#"):
            return label
        return f"[{label}]({href})"

    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', link, text, flags=re.S | re.I)
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.S | re.I)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.S | re.I)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def render(body: str, title: str, description: str, canonical: str) -> str:
    """Render a page body as markdown."""
    body = strip_chrome(body)

    lines: list[str] = []
    # A table is captured whole, because splitting it into cells loses the
    # header and the row structure.
    pos = 0
    for m in re.finditer(r"<table\b.*?</table>", body, flags=re.S | re.I):
        lines.extend(_blocks(body[pos : m.start()]))
        lines.append(_table(m.group(0)))
        pos = m.end()
    lines.extend(_blocks(body[pos:]))

    out: list[str] = [f"# {title}", ""]
    if description:
        out += [f"> {description}", ""]
    for line in lines:
        if line:
            out.append(line)
    out += ["", f"Canonical: {canonical}", ""]
    return "\n".join(out)


def _table(html_src: str) -> str:
    rows = re.findall(r"<tr\b.*?</tr>", html_src, flags=re.S | re.I)
    parsed: list[list[str]] = []
    for row in rows:
        cells = re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", row, flags=re.S | re.I)
        parsed.append([inline(c).replace("|", "\\|") for c in cells])
    if not parsed:
        return ""
    width = max(len(r) for r in parsed)
    parsed = [r + [""] * (width - len(r)) for r in parsed]
    head, *rest = parsed
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join(["---"] * width) + " |"]
    for r in rest:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def _blocks(chunk: str) -> list[str]:
    """Convert a run of block-level HTML to markdown lines."""
    out: list[str] = []

    # Lists are captured whole so their items stay together.
    pos = 0
    for m in re.finditer(r"<(ul|ol)\b.*?</\1>", chunk, flags=re.S | re.I):
        out.extend(_blocks(chunk[pos : m.start()]))
        out.append(_list(m.group(0), ordered=m.group(1).lower() == "ol"))
        pos = m.end()
    out.extend(_paras(chunk[pos:]))
    return out


def _list(html_src: str, ordered: bool) -> str:
    items = re.findall(r"<li\b[^>]*>(.*?)</li>", html_src, flags=re.S | re.I)
    lines = []
    for n, item in enumerate(items, 1):
        text = inline(item)
        if not text:
            continue
        marker = f"{n}." if ordered else "-"
        lines.append(f"{marker} {text}")
    return "\n".join(lines)


def _paras(chunk: str) -> list[str]:
    """Convert remaining block content to markdown paragraphs."""
    # Split on block-level boundaries.
    chunk = re.sub(
        r"</?(?:p|div|section|h[1-6]|blockquote|pre|table|tr|ul|ol|li|br|hr)\b[^>]*>",
        "\n",
        chunk,
        flags=re.I,
    )
    chunk = re.sub(r"<[^>]+>", "", chunk)
    chunk = html.unescape(chunk)

    lines: list[str] = []
    for raw in chunk.split("\n"):
        text = re.sub(r"[ \t]+", " ", raw).strip()
        if not text:
            continue
        # A heading tag was consumed above; recover it from the original.
        lines.append(text)

    # Headings are re-detected from the source in a second pass.
    return lines


def render_with_headings(body: str, title: str, description: str, canonical: str) -> str:
    """Render, preserving heading levels.

    The heading structure is the part an answer engine most wants, so it
    is extracted from the source rather than inferred from the text.

    The hero block is handled separately: its h1 becomes the page title
    and its sub-paragraph becomes the summary under it, so the reader
    gets "what this page is" before the body rather than part-way
    through it.
    """
    body = strip_chrome(body)

    hero_sub = ""
    hero_match = re.search(
        r"<h1\b[^>]*>.*?</h1>\s*<p class=\"gc-hero-sub\"[^>]*>(.*?)</p>",
        body,
        flags=re.S | re.I,
    )
    if hero_match:
        hero_sub = inline(hero_match.group(1))
        body = body[: hero_match.start()] + body[hero_match.end() :]

    chunks: list[str] = []
    pos = 0
    pattern = (
        r"<table\b.*?</table>"
        r"|<(?P<list>ul|ol)\b.*?</(?P=list)>"
        r"|<h(?P<level>[1-6])\b[^>]*>(?P<htext>.*?)</h(?P=level)>"
    )
    for m in re.finditer(pattern, body, flags=re.S | re.I):
        chunks.extend(_blocks(body[pos : m.start()]))
        if m.group(0).lower().startswith("<table"):
            chunks.append(_table(m.group(0)))
        elif m.group("list"):
            chunks.append(_list(m.group(0), ordered=m.group("list").lower() == "ol"))
        else:
            level = int(m.group("level"))
            text = inline(m.group("htext"))
            if text:
                # The page's own h1 is the title, already emitted.
                if level == 1:
                    chunks.append("")
                else:
                    chunks.append("#" * min(level, 4) + " " + text)
        pos = m.end()
    chunks.extend(_blocks(body[pos:]))

    # An eyebrow that repeats the title adds nothing.
    if chunks and chunks[0].strip() == f"#### {title}":
        chunks = chunks[1:]

    out: list[str] = [f"# {title}", ""]
    if description:
        out += [f"> {description}", ""]
    if hero_sub:
        out += [hero_sub, ""]
    prev_blank = False
    for line in chunks:
        if not line.strip():
            if not prev_blank:
                out.append("")
            prev_blank = True
            continue
        prev_blank = False
        out.append(line)
    out += ["", f"Canonical: {canonical}", ""]
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from apps.other import CORPORATE

    p = [x for x in CORPORATE if x.slug == "pricing"][0]
    print(render_with_headings(p.body, p.title, p.description, p.canonical)[:2000])
