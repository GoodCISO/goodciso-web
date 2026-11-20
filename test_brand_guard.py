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
