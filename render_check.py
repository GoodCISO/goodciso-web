#!/usr/bin/env python3
"""Check that every built page actually renders.

A page can pass a link check, a heading check and a metadata check and
still be broken on screen: the CSS may not load, the markup may be
unbalanced, the content may be empty, or a component may be missing.

This walks every built HTML page and asserts the things that make a page
a page:

  - the stylesheet it references exists in the build
  - the document has a balanced <html>/<head>/<body> structure
  - the body has real visible prose, not an empty shell
  - the main landmark exists and is not empty
  - the primary heading is present exactly once
  - no unrendered markup leaked into the text (a literal "<section>" in
    the prose means the renderer emitted source instead of HTML)
  - the images it references exist in the build
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"
SITES = ("corporate", "aware", "docs", "demo")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Structure(HTMLParser):
    """Track open/close balance and collect visible text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.text: list[str] = []
        self.in_script = 0
        self.in_style = 0
        self.main_text = ""
        self.main_depth = 0
        self.h1_count = 0
        self.has_main = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            if tag == "script":
                self.in_script += 1
            else:
                self.in_style += 1
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "main":
            self.has_main = True
            self.main_depth = len(self.stack)
        if tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.in_script -= 1
        if tag == "style" and self.in_style:
            self.in_style -= 1
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            # Find it deeper in the stack; report the mismatch.
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.errors.append(f"unclosed <{self.stack.pop()}>")
                if self.stack:
                    self.stack.pop()
            else:
                self.errors.append(f"unexpected </{tag}>")
        if tag == "main" and self.main_depth == 0:
            self.main_text = " ".join(self.text)

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        s = data.strip()
        if not s:
            return
        self.text.append(s)
        if self.has_main:
            self.main_text += " " + s


def check_page(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(root)
    html = path.read_text(errors="ignore")

    # 1. The stylesheet exists.
    for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html):
        if href.startswith(("http://", "https://", "//")):
            continue
        target = root / href.lstrip("/")
        if not target.exists():
            errors.append(f"{rel}: stylesheet {href} is not in the build")

    # 2. Images exist.
    for src in re.findall(r"<img[^>]+src=\"([^\"]+)\"", html):
        if src.startswith(("http://", "https://", "data:", "//")):
            continue
        target = root / src.lstrip("/")
        if not target.exists():
            errors.append(f"{rel}: image {src} is not in the build")

    # 3. Structure and visible text.
    p = Structure()
    p.feed(html)
    for e in p.errors[:4]:
        errors.append(f"{rel}: {e}")
    if p.stack:
        errors.append(f"{rel}: unclosed <{p.stack[-1]}> at end of document")

    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S)
    if not body:
        errors.append(f"{rel}: no <body>")
        return errors

    text = p.main_text or " ".join(p.text)
    visible = re.sub(r"\s+", " ", text).strip()
    if len(visible) < 200:
        errors.append(f"{rel}: only {len(visible)} chars of visible text — the page looks empty")

    # 4. Exactly one h1.
    if p.h1_count != 1:
        errors.append(f"{rel}: {p.h1_count} <h1> elements, expected 1")

    # 5. The main landmark.
    if not p.has_main:
        errors.append(f"{rel}: no <main> landmark")

    # 6. Unrendered markup leaked into the prose.
    for bad in ("<section", "<div class=", "&lt;section", "&lt;div", "</p>"):
        if bad in visible:
            errors.append(f"{rel}: unrendered markup in visible text: {bad!r}")

    # 7. No obviously broken placeholder.
    for bad in ("TODO", "Lorem ipsum", "undefined", "NaN", "[object Object]"):
        if bad in visible:
            errors.append(f"{rel}: placeholder or broken value in visible text: {bad!r}")

    return errors


def main() -> int:
    total = 0
    pages = 0
    for site in SITES:
        root = DIST / site
        if not root.exists():
            continue
        site_errors: list[str] = []
        site_pages = 0
        for path in sorted(root.rglob("*.html")):
            site_pages += 1
            site_errors.extend(check_page(path, root))
        pages += site_pages
        total += len(site_errors)
        status = "FAIL" if site_errors else "PASS"
        print(f"[{status}] {site:10} {site_pages:3} pages  {len(site_errors)} errors")
        for e in site_errors[:12]:
            print("    ERROR  ", e)

    print(f"\n{pages} pages checked, {total} errors")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
