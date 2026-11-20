#!/usr/bin/env python3
"""Prove the component-spec check in qa.py can fail.

A check that cannot fail is not a check. This deliberately breaks each
condition the check covers, in turn, and asserts the check reports the
error. It then restores the files.

The failure this guards against is specific: the previous site shipped four
components — `arch-flow`, `stats-bar`, `compliance-grid` and
`.trust-badge-note` — that existed in the stylesheet and in no document.
Nobody could tell whether they were correct, and a coder could not know
when it was safe to use one. `packages/ui/README.md` is the component
spec, and this test is what stops it drifting away from the layer.

Run it after changing anything in qa.py's component-spec check:

    python3.12 test_component_spec.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAYER = ROOT / "packages/ui/src/base.css"
SPEC = ROOT / "packages/ui/README.md"

sys.path.insert(0, str(ROOT))
import qa  # noqa: E402


def main() -> int:
    if not LAYER.exists() or not SPEC.exists():
        print("the layer or the spec is missing — nothing to prove")
        return 2

    backup = Path("/tmp/component-spec-backup")
    shutil.rmtree(backup, ignore_errors=True)
    backup.mkdir(parents=True)
    layer_backup = backup / "base.css"
    spec_backup = backup / "README.md"
    shutil.copy(LAYER, layer_backup)
    shutil.copy(SPEC, spec_backup)

    failures: list[str] = []

    def clean(label: str) -> None:
        errors = qa.check_component_spec()
        if errors:
            print(f"  FAIL  {label}: {errors[0]}")
            failures.append(label)
        else:
            print(f"  PASS  {label}")

    def fires(label: str) -> None:
        errors = qa.check_component_spec()
        if errors:
            print(f"  PASS  {label}")
            print(f"          -> {errors[0]}")
        else:
            print(f"  FAIL  {label}: the check reported nothing")
            failures.append(label)

    try:
        clean("baseline: every component in the layer is specified")

        # 1. A component added to the layer with no spec.
        original_layer = LAYER.read_text()
        LAYER.write_text(original_layer + "\n.gc-unspecified-widget { color: red; }\n")
        fires("a component added to the layer with no specification")
        LAYER.write_text(original_layer)

        # 2. A component removed from the spec but still in the layer.
        #    The class name is replaced with a form that cannot survive as a
        #    substring of another word in the prose, so the check must
        #    notice the removal rather than find the name elsewhere.
        original_spec = SPEC.read_text()
        SPEC.write_text(original_spec.replace("gc-checklist", "checklist-REMOVED"))
        fires("a component removed from the specification")
        SPEC.write_text(original_spec)

        # 3. The spec file missing entirely.
        SPEC.unlink()
        fires("the specification file is missing")
        shutil.copy(spec_backup, SPEC)

        # 4. The layer missing entirely.
        LAYER.unlink()
        fires("the component layer is missing")
        shutil.copy(layer_backup, LAYER)

        # 5. A component added MID-LINE.
        #    The check used to match only classes at the start of a line,
        #    so a component declared next to another one shipped with no
        #    specification and no error. Two classes in the layer were
        #    invisible to the check for exactly this reason.
        LAYER.write_text(original_layer + "\n.gc-probe-first { color: red; } .gc-probe-second { color: blue; }\n")
        errors = qa.check_component_spec()
        if any("gc-probe-second" in e for e in errors):
            print("  PASS  a component added mid-line")
        else:
            print("  FAIL  a component added mid-line: the check reported nothing")
            failures.append("a component added mid-line")
        LAYER.write_text(original_layer)

        # 6. A class in a CSS COMMENT must not be demanded in the spec.
        #    The layer's own comments name classes that the layer does not
        #    define, and a check that read comments would ask for a spec
        #    for a class that does not exist.
        LAYER.write_text(original_layer + "\n/* .gc-commented-only is not a component */\n")
        errors = qa.check_component_spec()
        if any("gc-commented-only" in e for e in errors):
            print("  FAIL  a class named only in a comment: the check reported it")
            failures.append("a class named only in a comment")
        else:
            print("  PASS  a class named only in a comment is not demanded")
        LAYER.write_text(original_layer)

        # 7. A class SPECIFIED but not in the layer.
        #    The other direction: the spec must not document a component
        #    that does not exist, or a coder would use it and it would do
        #    nothing.
        SPEC.write_text(original_spec + "\n\n| `gc-ghost-component` | Not in the layer |\n")
        errors = qa.check_component_spec()
        if any("gc-ghost-component" in e for e in errors):
            print("  PASS  a component specified but not in the layer")
        else:
            print("  FAIL  a component specified but not in the layer: the check reported nothing")
            failures.append("a component specified but not in the layer")
        SPEC.write_text(original_spec)
    finally:
        shutil.copy(layer_backup, LAYER)
        shutil.copy(spec_backup, SPEC)
        shutil.rmtree(backup, ignore_errors=True)

    print()
    if failures:
        print(f"THE CHECK FAILED TO FIRE on: {failures}")
        return 1
    print("Every component-spec condition fired as expected. Files restored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
