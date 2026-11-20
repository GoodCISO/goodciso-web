#!/usr/bin/env python3
"""Prove the shipped JavaScript is syntactically valid.

`site.js` shipped with an unclosed `if` block for its entire life. The
browser rejected the whole file with "Unexpected token ')'", so the theme
toggle and the mobile navigation did nothing on every page of every
site — and nothing in the QA gate looked at JavaScript at all, so the
build was green throughout.

The fix is a check that runs against the BUILT output, because that is
what ships: every `<script>` the built page loads is parsed, and a
syntax error fails the build.

It needs a JavaScript parser. `node --check` is used when node is
available, which is the case on the CI runner. When node is not
available the check reports that it could not run rather than passing
silently — a check that cannot fail is not a check.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"
SITES = ("corporate", "aware", "docs", "demo")


def script_srcs(site: str) -> list[Path]:
    """The local scripts the built page loads."""
    page = DIST / site / "index.html"
    if not page.exists():
        return []
    out = []
    for src in re.findall(r'<script[^>]+src="([^"]+)"', page.read_text()):
        if src.startswith(("http://", "https://", "//")):
            continue
        out.append((DIST / site / src.lstrip("/")).resolve())
    return out


def main() -> int:
    if shutil.which("node") is None:
        print("FAIL: node is not available, so the JavaScript cannot be parsed.")
        print("      A check that cannot run is not a check. Install node, or")
        print("      run this on the CI runner where node is present.")
        return 1

    errors: list[str] = []
    checked = 0

    for site in SITES:
        if not (DIST / site).exists():
            errors.append(f"{site}: the site was not built")
            continue
        for script in script_srcs(site):
            if not script.exists():
                errors.append(f"{site}: {script.name} is linked but not built")
                continue
            checked += 1
            proc = subprocess.run(
                ["node", "--check", str(script)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                first = (proc.stderr.strip().split("\n") or ["?"])[0]
                errors.append(f"{site}: {script.name} is not valid JavaScript — {first}")

    if checked == 0:
        print("FAIL: no JavaScript was checked — that is not a pass")
        return 1

    if errors:
        print(f"[FAIL] javascript syntax  {len(errors)} errors")
        for e in errors:
            print("    ERROR  ", e)
        return 1

    print(f"[PASS] javascript syntax  {checked} scripts across {len(SITES)} sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
