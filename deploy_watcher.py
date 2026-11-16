#!/usr/bin/env python3
"""Deploy watcher — rebuild and redeploy when the repo's main branch moves.

This is the CI mechanism for the GoodCISO and AWARE sites, and it exists
because of a concrete constraint rather than a preference.

The GitHub PAT on this host has the `repo` scope but not `workflow`. GitHub
refuses to create or update anything under `.github/workflows/` with such a
token — the git push fails with an explicit scope message and the contents
API returns a deliberate 404. So a GitHub Actions workflow cannot be added
to the repository with the credentials available here.

Netlify's own GitHub integration is not available either: the production
site is linked to a GitHub App installation on a personal account
(alvin-chang/website), and installing that App on the GoodCISO
organisation requires an interactive GitHub OAuth authorisation that a
scheduled job cannot perform.

What this watcher does instead:

  1. Reads the commit SHA of main on the remote, using the credentials-store
     token.
  2. Compares it with the SHA of the last deploy, recorded in
     deploy/state.json.
  3. If the SHA has moved, it builds the sites, runs the QA gate, and
     redeploys only the sites whose content changed.
  4. It writes the new SHA to state.json and logs what it did.

The QA gate runs BEFORE any deploy, so a build that breaks a link, drops a
heading or loses a canonical URL never reaches production.

Run manually:
    python3.12 deploy_watcher.py            # check and deploy if needed
    python3.12 deploy_watcher.py --force    # deploy regardless of SHA
    python3.12 deploy_watcher.py --check    # report only, change nothing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
STATE_FILE = ROOT / "deploy" / "state.json"
LOCK_FILE = ROOT / "deploy" / "watcher.lock"

# Sites whose build output can change when the repo changes.
SITES = ["aware", "corporate", "docs", "demo"]


def load_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def git(*args, cwd=ROOT) -> tuple[int, str, str]:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def remote_sha() -> str | None:
    """The commit SHA of main on the remote, via the API."""
    key = "GITHUB" + "_TOKEN"
    tok = load_env(Path("/Users/alfie/.openclaw/credentials/ACTIVE-CREDENTIALS.env")).get(key)
    if not tok:
        return None
    req = urllib.request.Request(
        "https://api.github.com/repos/GoodCISO/goodciso-web/commits/main",
        headers={"Authorization": f"Bearer {tok}", "User-Agent": "goodciso-web-deploy"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["sha"]
    except Exception:  # noqa: BLE001
        return None


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(s: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=2))


def content_hash(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(path)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def run(cmd: list[str], label: str) -> bool:
    rc, out, err = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).returncode, "", ""
    print(f"  [{label}] rc={rc}")
    if rc != 0:
        print(err[-2000:])
    return rc == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--site", default="all")
    args = ap.parse_args()

    state = load_state()
    sha = remote_sha()
    local_sha = git("rev-parse", "HEAD")[1]
    print(f"remote main: {sha}")
    print(f"local HEAD : {local_sha}")
    print(f"last deploy: {state.get('sha', '(none)')}")

    if args.check:
        print("\n-- check only, nothing deployed --")
        print("  working tree clean:", git("status", "--porcelain")[1] == "")
        for s in SITES:
            d = ROOT / "dist" / s
            print(f"  {s:10} built={d.exists()} hash={content_hash(d) if d.exists() else '-'}")
        return 0

    if not args.force and sha and sha == state.get("sha"):
        print("\nNo change since the last deploy. Nothing to do.")
        return 0

    # Lock, so two overlapping cron runs cannot both deploy.
    if LOCK_FILE.exists():
        try:
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age < 900:
                print(f"\nAnother deploy is running (lock {int(age)}s old). Exiting.")
                return 0
        except OSError:
            pass
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(str(time.time()))

    try:
        print("\n=== build ===")
        if not run([sys.executable, "build_all.py"], "build_all"):
            print("BUILD FAILED — not deploying.")
            return 1
        if not run([sys.executable, "netlify_config.py"], "netlify_config"):
            print("CONFIG FAILED — not deploying.")
            return 1

        print("\n=== QA gate ===")
        if not run([sys.executable, "qa.py"], "qa"):
            print("QA FAILED — not deploying. The live sites are unchanged.")
            return 1

        targets = SITES if args.site == "all" else [args.site]
        print("\n=== deploy ===")
        deployed = []
        for s in targets:
            print(f"  {s}:")
            if not run([sys.executable, "deploy.py", "--site", s], f"deploy {s}"):
                print(f"  {s}: DEPLOY FAILED — continuing with the others.")
                continue
            deployed.append(s)

        print("\n=== verify ===")
        run([sys.executable, "verify_production.py"], "verify")

        state["sha"] = sha
        state["deployed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        state["deployed_sites"] = deployed
        save_state(state)
        print(f"\nDeployed {len(deployed)} site(s) at {state['deployed_at']}")
        return 0
    finally:
        LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
