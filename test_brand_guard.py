#!/usr/bin/env python3
"""Prove the brand guard in qa.py can fail.

A check that cannot fail is not a check. This deliberately breaks each
condition the guard covers, in turn, and asserts that the guard reports
the error. It then restores the build output.

The failure this guards against is specific: from 2026-11-16 to
2026-11-18 goodciso.org served AWARE's mark — a green shield-and-check —
as its corporate favicon, because the build copied one favicon file to
every site. The brand was fixed; this test is what stops it coming back.

Run it after changing anything in qa.py's brand guard:

    python3.12 test_brand_guard.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
CORP = DIST / "corporate"
AWARE = DIST / "aware"

sys.path.insert(0, str(ROOT))
import qa  # noqa: E402


def main() -> int:
    if not CORP.exists():
        print("no build output — run `python3.12 build_all.py` first")
        return 2

    backup = Path("/tmp/brand-guard-backup")
    shutil.rmtree(backup, ignore_errors=True)
    shutil.copytree(DIST, backup)

    failures: list[str] = []

    def corporate_clean(label: str) -> None:
        errors = qa.check_brand("corporate")
        if errors:
            print(f"  FAIL  {label}: {errors[0]}")
            failures.append(label)
        else:
            print(f"  PASS  {label}")

    def corporate_fails(label: str) -> None:
        errors = qa.check_brand("corporate")
        if errors:
            print(f"  PASS  {label}")
            print(f"          -> {errors[0]}")
        else:
            print(f"  FAIL  {label}: the guard reported nothing")
            failures.append(label)

    try:
        corporate_clean("baseline: the real corporate build is clean")

        # 1. The AWARE mark served as the corporate favicon.
        shutil.copy(AWARE / "favicon.svg", CORP / "favicon.png")
        corporate_fails("corporate favicon replaced with the AWARE mark")
        shutil.copy(backup / "corporate/favicon.png", CORP / "favicon.png")

        # 2. The corporate favicon missing entirely.
        (CORP / "favicon.png").unlink()
        corporate_fails("corporate favicon missing")
        shutil.copy(backup / "corporate/favicon.png", CORP / "favicon.png")

        # 3. The corporate accent repointed at AWARE's Signal green.
        brand = CORP / "assets/brand.css"
        original = brand.read_text()
        brand.write_text(original.replace("--gc-accent:      #00A896;", "--gc-accent:      #22C55E;"))
        corporate_fails("corporate accent repointed at AWARE's Signal green")
        brand.write_text(original)

        # 4. The AWARE mark missing from the AWARE site.
        shutil.copy(backup / "corporate/favicon.png", AWARE / "favicon.svg")
        aware_errors = qa.check_brand("aware")
        if aware_errors:
            print("  PASS  AWARE favicon replaced with the corporate mark")
            print(f"          -> {aware_errors[0]}")
        else:
            print("  FAIL  AWARE favicon replaced with the corporate mark: "
                  "the guard reported nothing")
            failures.append("aware favicon")
        shutil.copy(backup / "aware/favicon.svg", AWARE / "favicon.svg")

        # 5. The hero glow hard-coded to AWARE's Signal green. This is the
        #    exact bug that put a green glow behind a teal logomark: the
        #    glow was a literal in the shared token layer, so the corporate
        #    ramp override could not reach it.
        tokens = CORP / "assets/tokens.css"
        tok_original = tokens.read_text()
        tokens.write_text(tok_original.replace(
            "--gc-hero-glow:   color-mix(in srgb, var(--gc-accent) 10%, transparent);",
            "--gc-hero-glow:   rgba(34, 197, 94, 0.14);",
        ))
        corporate_fails("hero glow hard-coded to AWARE's Signal green")
        tokens.write_text(tok_original)

        # 6. The hero glow hard-coded to a colour that is not derived from
        #    the accent at all. The brand ramp cannot reach a literal, so
        #    a future brand or theme change would silently miss it.
        tokens.write_text(tok_original.replace(
            "--gc-hero-glow:   color-mix(in srgb, var(--gc-accent) 10%, transparent);",
            "--gc-hero-glow:   rgba(0, 168, 150, 0.12);",
        ))
        corporate_fails("hero glow hard-coded instead of derived from the accent")
        tokens.write_text(tok_original)

        # 7. The corporate social card replaced with AWARE's. The card is
        #    what a shared goodciso.org link shows before a word is read, so
        #    this is the favicon defect on the surface that reaches
        #    further: a link pasted into a chat or a post.
        shutil.copy(AWARE / "og.png", CORP / "og.png")
        corporate_fails("corporate social card replaced with the AWARE card")
        shutil.copy(backup / "corporate/og.png", CORP / "og.png")

        # 8. The corporate social card missing entirely. A shared link
        #    with no card renders as a bare URL — the brand never arrives.
        (CORP / "og.png").unlink()
        corporate_fails("corporate social card missing")
        shutil.copy(backup / "corporate/og.png", CORP / "og.png")

        # 9. The AWARE site carrying the corporate card. The mirror of
        #    condition 7, and the one that would put GoodCISO's mark on
        #    every AWARE link.
        shutil.copy(backup / "corporate/og.png", AWARE / "og.png")
        aware_errors = qa.check_brand("aware")
        if aware_errors:
            print("  PASS  AWARE social card replaced with the corporate card")
            print(f"          -> {aware_errors[0]}")
        else:
            print("  FAIL  AWARE social card replaced with the corporate card: "
                  "the guard reported nothing")
            failures.append("aware social card")
        shutil.copy(backup / "aware/og.png", AWARE / "og.png")
    finally:
        shutil.rmtree(DIST, ignore_errors=True)
        shutil.copytree(backup, DIST)

    print()
    if failures:
        print(f"THE GUARD FAILED TO FIRE on: {failures}")
        return 1
    print("Every brand-guard condition fired as expected. Build output restored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
