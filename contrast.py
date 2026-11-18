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

import re
import sys
from pathlib import Path

DIST = Path("/Users/alfie/projects/goodciso-web/dist")


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
    for p in [x.strip() for x in sel.split(",")]:
        if p == ":root":
            return True
        if theme == "light" and p == '[data-theme="light"]':
            return True
        if theme == "dark" and p == '[data-theme="dark"]':
            return True
    return False


def theme_vars(site: str, theme: str) -> dict:
    assets = DIST / site / "assets"
    all_rules = rules((assets / "tokens.css").read_text()) + rules((assets / "brand.css").read_text())
    merged: dict = {}
    for sel, d in all_rules:
        if applies(sel, theme):
            merged.update(d)
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
    for site in ("corporate", "aware", "docs", "demo"):
        if not (DIST / site / "assets" / "tokens.css").exists():
            continue
        print(f"\n{'=' * 64}\n{site.upper()}\n{'=' * 64}")
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
    print("ALL CONTRAST CHECKS PASS" if failures == 0 else f"{failures} FAILURES")
    print("=" * 64)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
