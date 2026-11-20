#!/usr/bin/env python3
"""Measure the real contrast of the built CSS.

This resolves the custom properties through the actual cascade — the same
way a browser would — rather than reading a value in isolation. A token's
value depends on which rule wins for the theme, and on what it references.

Used because the corporate brand was repointed from AWARE's green to
GoodCISO's teal, and a teal that fails AA as text would be a regression
in the very thing the redesign was meant to improve.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# The build output, resolved relative to THIS FILE so the script runs
# wherever the repository is checked out. It used to hardcode
# /Users/alfie/projects/goodciso-web/dist, which cannot exist on a CI
# runner and made this script host-only.
DIST = Path(os.environ.get("DIST_DIR") or (Path(__file__).parent.resolve() / "dist"))


def strip_comments(css: str) -> str:
    out = []
    i = 0
    while i < len(css):
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            if j < 0:
                break
            out.append(" ")
            i = j + 2
        else:
            out.append(css[i])
            i += 1
    return "".join(out)


def rules(css: str) -> list[tuple[str, dict]]:
    css = strip_comments(css)
    out = []
    i = 0
    while True:
        m = re.compile(r"([^{}]+)\{").search(css, i)
        if not m:
            break
        sel = " ".join(m.group(1).split())
        j = m.end()
        depth = 1
        while depth > 0 and j < len(css):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[m.end() : j - 1]
        d = {
            dm.group(1): dm.group(2).strip()
            for dm in re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);", body)
        }
        if d:
            out.append((sel, d))
        i = j
    return out


# The raw palette (--gc-slate-*, --gc-green-*) is declared on :root and
# applies in BOTH themes. Only the semantic tokens are theme-scoped, so
# :root must be merged for the dark theme too — otherwise a dark value of
# var(--gc-slate-950) resolves to nothing.
def applies(sel: str, theme: str) -> bool:
    """Does this ONE selector part match in the given theme?

    Only the theme attribute decides, because the raw palette lives on
    :root in BOTH themes while the semantic tokens are theme-scoped.

    A `:not([data-theme="X"])` constraint is honoured: the part cannot
    match when the theme is X. That is how the light-theme fallback in
    the component layer stays out of the dark theme.
    """
    if not sel:
        return False
    excluded = re.findall(r':not\(\s*\[data-theme="([a-z]+)"\]\s*\)', sel)
    if theme in excluded:
        return False
    positive = re.findall(
        r'\[data-theme="([a-z]+)"\]', re.sub(r":not\([^()]*\)", "", sel)
    )
    if positive and theme not in positive:
        return False
    return True


def specificity(sel: str) -> tuple[int, int, int]:
    """The (a, b, c) specificity a browser computes for one selector part.

    Needed because the cascade is not source order alone: two rules with
    different specificity compete, and the more specific one wins even if
    it comes first.
    """
    # `:not(X)` contributes X's specificity and nothing of its own, so it
    # is replaced by its argument before counting.
    s = re.sub(r":not\(([^()]*)\)", r"\1", sel)
    ids = len(re.findall(r"#[A-Za-z_][\w-]*", s))
    s = re.sub(r"#[A-Za-z_][\w-]*", "", s)
    attrs = len(re.findall(r"\[[^\]]*\]", s))
    s = re.sub(r"\[[^\]]*\]", "", s)
    classes = len(re.findall(r"\.[A-Za-z_][\w-]*", s))
    s = re.sub(r"\.[A-Za-z_][\w-]*", "", s)
    pseudos = len(re.findall(r":(?!:)[A-Za-z-]+", s))
    s = re.sub(r":(?!:)[A-Za-z-]+", "", s)
    types = len(re.findall(r"(?:^|[\s>+~])([A-Za-z][\w-]*)", s))
    return (ids, attrs + classes + pseudos, types)


def page_stylesheets(site: str) -> list[Path]:
    """The stylesheets the BUILT page loads, in document order.

    They are read from the built page rather than from a hardcoded list.
    A stylesheet the page loads but the checker does not read is measured
    wrong, and that is exactly how the button text colour escaped this
    check: `base.css` declared a fallback for `--gc-accent-on-solid` and
    the checker only read `tokens.css` and `brand.css`, so it measured a
    value the browser never used.
    """
    page = DIST / site / "index.html"
    if not page.exists():
        return []
    hrefs = re.findall(
        r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', page.read_text()
    )
    out: list[Path] = []
    for href in hrefs:
        if href.startswith(("http://", "https://", "//")):
            continue  # a third-party sheet, not ours to resolve
        out.append((DIST / site / href.lstrip("/")).resolve())
    return out


def theme_vars(site: str, theme: str) -> dict:
    """Resolve every custom property the page would have, for one theme."""
    merged: dict = {}
    best: dict = {}
    order = 0
    for path in page_stylesheets(site):
        if not path.exists():
            continue
        for sel, d in rules(path.read_text()):
            for part in [x.strip() for x in sel.split(",")]:
                if not applies(part, theme):
                    continue
                spec = specificity(part)
                for prop, val in d.items():
                    prev = best.get(prop)
                    if prev is None or (spec, order) >= prev:
                        best[prop] = (spec, order)
                        merged[prop] = val
            order += 1
    return merged


def resolve(vars_: dict, name: str, depth: int = 0):
    if depth > 12:
        return None
    v = vars_.get(name) or vars_.get("--" + name)
    if v is None:
        return None
    m = re.match(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*(.*))?\)$", v.strip())
    if not m:
        return v.strip()
    inner = resolve(vars_, m.group(1), depth + 1) or (m.group(2) or "").strip()
    return inner


def srgb(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(hexs: str) -> float:
    h = hexs.lstrip("#").strip()
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def contrast(a: str, b: str) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


NAMES = [
    "gc-bg", "gc-surface", "gc-surface-2", "gc-text", "gc-text-muted", "gc-text-subtle",
    "gc-accent", "gc-accent-text", "gc-accent-solid", "gc-accent-on-solid",
    "gc-link", "gc-focus", "gc-border-strong",
]


def main() -> int:
    failures = 0
    checked = 0
    missing = []
    for site in ("corporate", "aware", "docs", "demo"):
        if not (DIST / site / "assets" / "tokens.css").exists():
            # A missing site is a FAILURE, not a skip. Skipping it would let
            # a build that produced nothing report "ALL CONTRAST CHECKS
            # PASS" — a check that cannot fail is not a check.
            missing.append(site)
            continue
        print(f"\n{'=' * 64}\n{site.upper()}\n{'=' * 64}")
        checked += 1
        for theme in ("light", "dark"):
            vars_ = theme_vars(site, theme)
            v = {n: resolve(vars_, n) for n in NAMES}
            print(f"\n  --- {theme} ---")
            print(
                "   bg={} surface={} accent={} accent-text={} accent-solid={} on-solid={}".format(
                    v["gc-bg"], v["gc-surface"], v["gc-accent"], v["gc-accent-text"],
                    v["gc-accent-solid"], v["gc-accent-on-solid"],
                )
            )
            bg, surf, s2 = v["gc-bg"], v["gc-surface"], v["gc-surface-2"]
            on_solid = v["gc-accent-on-solid"] or "#FFFFFF"
            checks = [
                ("text on bg", v["gc-text"], bg, 4.5),
                ("text on surface", v["gc-text"], surf, 4.5),
                ("text on surface-2", v["gc-text"], s2, 4.5),
                ("muted on bg", v["gc-text-muted"], bg, 4.5),
                ("subtle on bg", v["gc-text-subtle"], bg, 4.5),
                ("accent-text on bg", v["gc-accent-text"], bg, 4.5),
                ("accent-text on surface", v["gc-accent-text"], surf, 4.5),
                ("link on bg", v["gc-link"], bg, 4.5),
                ("on-solid on accent-solid", on_solid, v["gc-accent-solid"], 4.5),
                ("focus vs bg (>=3)", v["gc-focus"], bg, 3.0),
                ("border-strong vs bg (>=3)", v["gc-border-strong"], bg, 3.0),
                # The focus ring is painted where the focused element SITS,
                # not necessarily on the page background. `outline-offset: 2px`
                # puts the ring outside the element's border box, so a link
                # in a card is ringed against the card's surface, and a
                # button in the header against the header's translucent
                # surface. Checking the ring against --gc-bg alone would
                # pass a ring that vanishes on the surface it is actually
                # drawn on, so every surface a focusable element can sit on
                # is checked. WCAG 2.2 SC 1.4.11 Non-text Contrast.
                ("focus vs surface (>=3)", v["gc-focus"], surf, 3.0),
                ("focus vs surface-2 (>=3)", v["gc-focus"], s2, 3.0),
            ]
            for label, fg, b, need in checks:
                if not fg or not b:
                    print(f"     SKIP  {label} (unresolved: {fg} on {b})")
                    failures += 1
                    continue
                r = contrast(fg, b)
                ok = r >= need
                if not ok:
                    failures += 1
                print(f"     {'PASS' if ok else 'FAIL'} {r:6.2f} (need {need})  {label}")
    print(f"\n{'=' * 64}")
    if missing:
        print(f"MISSING BUILT SITES: {', '.join(missing)} — run build_all.py first")
    if checked == 0:
        print("NOTHING WAS CHECKED — this is not a pass")
    elif failures == 0:
        print(f"ALL CONTRAST CHECKS PASS ({checked} sites)")
    else:
        print(f"{failures} FAILURES")
    print("=" * 64)
    return 1 if (failures or missing or checked == 0) else 0


if __name__ == "__main__":
    sys.exit(main())
