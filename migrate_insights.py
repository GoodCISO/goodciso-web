#!/usr/bin/env python3
"""Migrate the four published blog posts into the new Insights section.

The posts are real, substantial technical writing that earned its URLs. Their
URLs now 301 to /insights, but a 301 to a page that does not contain the
article is a poor experience and wastes the content. So the articles are
rebuilt as native pages under /insights/<slug>/ and the old URLs redirect to
them directly rather than to the index.

Two things happen here beyond extraction:

1. Structural rebuild. The legacy markup uses source newlines to separate
   paragraphs and list items, so block boundaries are made explicit before
   tags are stripped, and section headings are restored to real h2/h3.

2. A claim-correction pass. The posts were written before the 2.12.2 README
   correction and contain exactly the claims that correction retracted —
   "cryptographic identity", T0-T4 as enforcement tiers, revocation cascade.
   The capability register governs every published sentence, so those
   statements are rewritten here rather than carried across unchanged.
"""
from __future__ import annotations

import html
import os
import re
from pathlib import Path

OLD = Path(
    os.environ.get("LEGACY_BLOG_DIR")
    or Path.home() / "projects/goodciso-website/blog"
)
OUT = Path(__file__).parent.resolve() / "apps" / "insights"

SLUGS = {
    "2026-06-08-container-security-gap-nobody-talks-about.html": "container-security-gap",
    "2026-06-08-devsecops-dead-long-live-devops.html": "devsecops-is-dead",
    "2026-06-08-why-llm-threat-models-fail.html": "why-llm-threat-models-fail",
    "what-we-learned-building-agentic-security-workflows.html": "what-we-learned-building-agentic-security-workflows",
}

# Claims the capability register does not support, and the supported phrasing.
CLAIM_FIXES = [
    (
        r"Every agent has a cryptographic identity",
        "Every agent has a non-human identity with a hashed, revocable credential",
    ),
    (
        r"enforcing cryptographic identity for every agent",
        "issuing a non-human identity with a hashed, revocable credential to every agent",
    ),
    (
        r"By enforcing cryptographic identity for every agent, tiered constraints \(T0-T4\) on every action, and full decision-chain traceability",
        "By issuing every agent a non-human identity with a hashed, revocable credential, enforcing policies on every tool call, and keeping full decision-chain traceability",
    ),
    (
        r"tiered constraints \(T0-T4\) on every action",
        "policy evaluation on every tool call",
    ),
    (
        r"Revocation cascades automatically",
        "Revocation applies to the named agent",
    ),
    (
        r"kill the parent, the children go too",
        "the named agent is invalidated",
    ),
]


def extract(path: Path) -> tuple[str, str]:
    b = path.read_text(errors="ignore")
    t = re.search(r"<title[^>]*>(.*?)</title>", b, re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", b, re.S)
    title = html.unescape((h1 or t).group(1)).strip() if (h1 or t) else path.stem

    body = re.sub(r"<(script|style|nav|header|footer|aside).*?</\1>", "", b, flags=re.S | re.I)
    m = re.search(r"<article[^>]*>(.*?)</article>", body, re.S | re.I)
    if not m:
        m = re.search(r"<main[^>]*>(.*?)</main>", body, re.S | re.I)
    art = m.group(1) if m else body

    art = re.sub(
        r'<div[^>]*class="[^"]*(meta|date|author|tag|share|byline)[^"]*"[^>]*>.*?</div>',
        "",
        art,
        flags=re.S | re.I,
    )
    art = re.sub(r"<h1[^>]*>.*?</h1>", "", art, flags=re.S | re.I)

    # Explicit block boundaries before the tags come off.
    art = re.sub(r"</(p|div|li|h[1-6]|blockquote|pre|section|tr|ul|ol)>", r"</\1>\n", art, flags=re.I)
    art = re.sub(r"<(br|hr)[^>]*>", "\n", art, flags=re.I)
    art = re.sub(r"<li[^>]*>", "\n- ", art, flags=re.I)
    art = re.sub(r"</(h[1-6])>", r"</\1>\n\n", art, flags=re.I)
    art = re.sub(r"<h([2-4])[^>]*>(.*?)</h\1>", r"\n\n## \2\n\n", art, flags=re.S | re.I)
    art = re.sub(r"<blockquote[^>]*>", "\n\n> ", art, flags=re.I)
    art = re.sub(r"</blockquote>", "\n\n", art, flags=re.I)
    art = re.sub(r'<pre[^>]*>', '\n\n```\n', art, flags=re.I)
    art = re.sub(r"</pre>", "\n```\n\n", art, flags=re.I)
    art = re.sub(r"<code[^>]*>", "`", art, flags=re.I)
    art = re.sub(r"</code>", "`", art, flags=re.I)
    # The LinkedIn company URL was wrong in the legacy posts
    # ("company/good-ciso"). The real page is "company/goodciso". Fix it
    # here as well as at source, so a re-migration cannot reintroduce it.
    art = art.replace("linkedin.com/company/good-ciso", "linkedin.com/company/goodciso")

    # The legacy posts linked to pages of the OLD site that no longer
    # exist. The mapping lives in insights_loader.LEGACY_LINK_FIXES,
    # which is applied to the RENDERED html and is the correct layer for
    # it: it can fix a link whatever produced it.
    #
    # It was previously duplicated here, and the two disagreed about the
    # trailing slash, which is how an article ended up linking to
    # "/contact" while the site serves "/contact/".
    #
    # The only correction needed here is the LinkedIn URL below.

    # Links become markdown, KEEPING their label.
    #
    # This was `r"[\1](\1)"`, which replaced the link text with the URL.
    # Every labelled link in the legacy posts therefore rendered as its
    # own address: "building
    # https://github.com/GoodCISO/aware AWARE". The label is the point of
    # a link, so it is captured and restored.
    art = re.sub(
        r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        lambda mm: f"[{mm.group(2).strip()}]({mm.group(1)})",
        art,
        flags=re.S | re.I,
    )
    art = re.sub(r"<strong[^>]*>", "**", art, flags=re.I)
    art = re.sub(r"</strong>", "**", art, flags=re.I)
    art = re.sub(r"<em[^>]*>", "*", art, flags=re.I)
    art = re.sub(r"</em>", "*", art, flags=re.I)
    art = re.sub(r"<[^>]+>", "", art)
    art = html.unescape(art)

    # Collapse the whitespace the legacy markup left behind.
    art = re.sub(r"[ \t]{2,}", " ", art)
    art = re.sub(r"\n{3,}", "\n\n", art)
    art = "\n".join(line.strip() for line in art.split("\n"))
    art = re.sub(r"\n{3,}", "\n\n", art).strip()

    # Restore section headings. The legacy posts mark headings as short
    # standalone lines, so a line that is a heading becomes a real h2.
    out_lines = []
    for line in art.split("\n"):
        s = line.strip()
        if (
            3 < len(s) < 80
            and not s.endswith((".", ",", ";", ":", "?", "!", ")"))
            and re.match(r"^[A-Z0-9][\w &'\-—:]*$", s)
            and s[0].isupper()
            and not s.startswith("-")
            and " " in s
        ):
            out_lines.append(f"\n## {s}\n")
        else:
            out_lines.append(line)
    art = "\n".join(out_lines)
    art = re.sub(r"\n{3,}", "\n\n", art).strip()

    # The capability register governs every published sentence.
    for pattern, replacement in CLAIM_FIXES:
        art = re.sub(pattern, replacement, art, flags=re.I)

    return title, art


def build_page(title: str, body: str) -> str:
    return f"""
<section class="gc-hero gc-hero-sm">
  <div class="gc-container gc-container-narrow">
    <span class="gc-eyebrow">Insight</span>
    <h1>{title}</h1>
    <p class="gc-hero-sub">Technical writing from the GoodCISO team.</p>
  </div>
</section>
<section class="gc-section">
  <div class="gc-container gc-container-narrow">
    <div class="gc-prose">
{body}
    </div>
    <div class="gc-callout gc-mt-12">
      <strong>Talk to us about this</strong>
      If this raises a question about your own environment, <a href="/contact">start a conversation</a>.
    </div>
  </div>
</section>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, slug in SLUGS.items():
        p = OLD / fn
        if not p.exists():
            print("MISSING", p)
            continue
        title, body = extract(p)
        (OUT / f"{slug}.html").write_text(build_page(title, body), encoding="utf-8")
        print(f"{slug:48} {len(body):6} chars  {title[:46]}")
